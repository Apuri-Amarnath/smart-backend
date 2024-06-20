import uuid

from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models import BinaryField
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, timezone


# custom user manager
class MyUserManager(BaseUserManager):
    def create_user(self, registration_number, password=None, password2=None, role=None):
        """
        Creates and saves a User with the given registration
        number and password.
        """
        if not registration_number:
            raise ValueError("Users must have an registration number")

        user = self.model(
            registration_number=self.normalize_registration_number(registration_number),
            role=role
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, registration_number, password=None, ):
        """
        Creates and saves a superuser with the given registration
        number and password.
        """
        user = self.create_user(
            registration_number,
            password=password,
            role='Admin',
        )
        user.is_admin = True
        user.role = "admin"
        user.save(using=self._db)
        return user

    def normalize_registration_number(self, registration_number):
        # Normalization logic here
        return registration_number.strip().upper()


# custom user model
class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('office', 'Office'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
        ('principal', 'Principal'),
        ('caretaker', 'Caretaker')
    ]
    registration_number = models.CharField(verbose_name="registration number", max_length=20, unique=True,
                                           validators=[MinLengthValidator(11)])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "registration_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.registration_number

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        if self.is_admin:
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        if self.is_admin:
            return True
        return super.has_module_perms(app_label)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin or self.role in ['faculty', 'principal', 'office', 'caretaker']


def upload_path(instance, filename, folder):
    # Customize this function as per your requirement
    return f"{folder}/{filename}"


def upload_to_profile_pictures(instance, filename):
    return upload_path(instance, filename, 'profile-pictures')


class PersonalInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_information')
    first_name = models.CharField(verbose_name="first name", max_length=100, blank=True, null=True)
    last_name = models.CharField(verbose_name="last name", max_length=100, blank=True)
    father_name = models.CharField(verbose_name="father name", max_length=100, blank=True, null=True)
    middle_name = models.CharField(verbose_name="middle name", max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(verbose_name="birth", blank=True, null=True)
    gender = models.CharField(verbose_name="gender", max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(max_length=200, upload_to=upload_to_profile_pictures, blank=True, null=True)


class ContactInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contact_information')
    email = models.EmailField(verbose_name="email address", max_length=225, blank=True, null=True)
    phone_number = models.CharField(verbose_name="phone number", max_length=15, blank=True, null=True)
    alternate_phone_number = models.CharField(verbose_name="alternate phone", max_length=15, blank=True, null=True)
    address = models.TextField(verbose_name="address", blank=True, null=True, max_length=300)
    city = models.CharField(verbose_name="city", max_length=100, blank=True, null=True)
    state = models.CharField(verbose_name="state", max_length=100, blank=True, null=True)
    postal_code = models.CharField(verbose_name="postal code", max_length=10, null=True, blank=True)
    country = models.CharField(verbose_name="country", max_length=100, blank=True, null=True)


class AcademicInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_information')
    enrollment_date = models.DateField(verbose_name="enrollment date", blank=True, null=True)
    program = models.CharField(verbose_name="program", blank=True, null=True, max_length=100)
    major = models.CharField(verbose_name="major", blank=True, null=True, max_length=100)
    current_year = models.IntegerField(verbose_name="current year", blank=True, null=True)
    gpa = models.DecimalField(verbose_name="GPA", blank=True, null=True, max_digits=4, decimal_places=2)
    course_enrolled = models.TextField(verbose_name="course enrolled", blank=True, null=True)
    year_semester = models.CharField(verbose_name="year/semester", max_length=10, null=True, blank=True)
    batch = models.CharField(verbose_name="batch", max_length=10, null=True, blank=True)
    department = models.CharField(verbose_name="department", max_length=225, null=True, blank=True)
    course_start_date = models.DateField(verbose_name="course start date", null=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    personal_information = models.OneToOneField(PersonalInformation, on_delete=models.CASCADE,
                                                related_name='personal_profile')
    contact_information = models.OneToOneField(ContactInformation, on_delete=models.CASCADE,
                                               related_name='contact_profile')
    academic_information = models.OneToOneField(AcademicInformation, on_delete=models.CASCADE,
                                                related_name='academic_profile')

    def __str__(self):
        return self.user.registration_number


@receiver(post_save, sender=User)
def create_related_information(sender, instance, created, **kwargs):
    if created:
        personal_info = PersonalInformation.objects.create(user=instance)
        contact_info = ContactInformation.objects.create(user=instance)
        academic_info = AcademicInformation.objects.create(user=instance)
        UserProfile.objects.create(user=instance, personal_information=personal_info, contact_information=contact_info,
                                   academic_information=academic_info)


@receiver(post_save, sender=User)
def save_related_information(sender, instance, **kwargs):
    instance.personal_information.save()
    instance.contact_information.save()
    instance.academic_information.save()
    instance.profile.save()


def upload_college_logo(instance, filename):
    return upload_path(instance, filename, 'college-logos')


class College(models.Model):
    college_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    college_name = models.CharField(verbose_name="college_name", max_length=255, unique=True, null=True, blank=True)
    college_address = models.TextField(verbose_name="college_address", max_length=500, null=True, blank=True)
    established_date = models.DateField(verbose_name="established_date", null=True, blank=True)
    principal_name = models.CharField(verbose_name="principal_name", null=True, max_length=255, blank=True)
    phone_number = models.CharField(verbose_name="phone_number", null=True, max_length=15)
    email = models.EmailField(verbose_name="email", null=True, max_length=225)
    college_logo = models.ImageField(verbose_name="college_logo", upload_to=upload_college_logo, null=True, blank=True)

    def __str__(self):
        return self.college_name


def generate_bonafide_number():
    # Generate a unique bonafide number
    return str(uuid.uuid4().hex[:10])


class Bonafide(models.Model):
    STATUS_CHOICES = [
        ('not-applied', 'Not-applied'),
        ('applied', 'Applied'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="bonafide_college")
    student = models.ForeignKey(PersonalInformation, on_delete=models.CASCADE, related_name="bonafide_student")
    roll_no = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roll_no")
    supporting_document = models.BinaryField(verbose_name="supporting_document", null=True, blank=True)
    issue_date = models.DateField(verbose_name="issue date", null=True, blank=True)
    applied_date = models.DateField(verbose_name="applied date", null=True, blank=True)
    required_for = models.CharField(verbose_name="required for", null=True, blank=True, max_length=225)
    fee_structure = models.BooleanField(verbose_name="fee_structure", default=False, null=True, blank=True)
    bonafide_number = models.CharField(unique=True, verbose_name="bonafide number", max_length=10, null=True,
                                       blank=True)
    status = models.CharField(verbose_name="status", choices=STATUS_CHOICES, max_length=225, default=STATUS_CHOICES[0])

    def save(self, *args, **kwargs):
        if not self.bonafide_number:
            self.bonafide_number = generate_bonafide_number()
        if not self.applied_date:
            self.applied_date = date.today()
        super(Bonafide, self).save(*args, **kwargs)

    def __str__(self):
        return f" fname: {self.student.first_name} -- lname: {self.student.last_name} -- roll_no: {self.roll_no} -- bonafide no: {self.bonafide_number} -- date:  {self.issue_date}"


class Subject(models.Model):
    subject_name = models.CharField(verbose_name="subject", max_length=225, null=True, blank=True)
    subject_code = models.CharField(verbose_name="subject_id", max_length=30, null=True, unique=True)
    instructor = models.CharField(verbose_name="Instructor", max_length=100, null=True, blank=True)

    def __str__(self):
        return f"subject name: {self.subject_name} -- subject code: {self.subject_code} -- instructor: {self.instructor}"


class Semester(models.Model):
    branch = models.CharField(verbose_name="branch", max_length=225, null=True, blank=True)
    semester_name = models.CharField(verbose_name="semester_name", max_length=225)
    subjects = models.ManyToManyField(Subject, verbose_name="subjects", related_name="semester_subjects")

    def __str__(self):
        subjects_list = ", ".join([subject.name for subject in self.subjects.all()])
        return f" semester: {self.semester_name} -- subjects: {subjects_list}"

    def get_subjects_list(self):
        return self.subjects.all()


class Semester_Registration(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="semester_registrations")
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                                related_name="semester_registration_student")
    applied_date = models.DateField(verbose_name="semester_registration_date", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.applied_date:
            self.applied_date = date.today()
        super(Semester_Registration, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.semester} - {self.student}"


class Hostel_Allotment(models.Model):
    STATUS_CHOICES = [
        ('not-applied', 'Not-applied'),
        ('applied', 'Applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="hostel_allotment_registrations")
    cgpa = models.CharField(max_length=125, verbose_name="CGPA", null=True, blank=True)

    latest_marksheet = models.BinaryField(verbose_name="marksheet", null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=225, null=True, blank=True, default="not-applied")

    def __str__(self):
        return f"{self.user.registration_number} - {self.status}"

    def update_status(self, new_status):
        self.status = new_status
        self.save


class Hostel_Room_Allotment(models.Model):
    registration_details = models.OneToOneField(Hostel_Allotment, on_delete=models.CASCADE,
                                                related_name="hostel_room_allotment")
    hostel_room = models.CharField(max_length=225, null=True, blank=True, verbose_name="hostel_room", unique=True)

    def __str__(self):
        return f" room no : {self.hostel_room} -- registration No : {self.registration_details.user.registration_number}"


class Fees_model(models.Model):
    Maintainance_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="Maintainance_fees")
    Mess_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="Mess fees")
    Security_Deposit = models.CharField(max_length=225, null=True, blank=True, verbose_name="Security deposit")


class Mess_fee_payment(models.Model):
    registration_details = models.ForeignKey(Hostel_Room_Allotment, on_delete=models.CASCADE)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    mess_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="mess-fee")
    maintainance_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="maintainance-fee")
    security_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="security-fee")
    total_fees = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)


class Hostel_No_Due_request(models.Model):
    semester = models.CharField(max_length=225, verbose_name="semester", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Hostel_no_due_request")
    Maintance_fees_date = models.DateField(verbose_name="Maintance_fees", null=True, blank=True)
    Mess_fees_date = models.DateField(verbose_name="Mess_fees", null=True, blank=True)
    self_declaration = models.BooleanField(verbose_name="self_agree", null=True, blank=True, default=False)
    requested_date = models.DateField(verbose_name="requested_date", null=True, blank=True)
    approved_date = models.DateField(verbose_name="approves_date", null=True, blank=True)

    def __str__(self):
        return f"{self.user.registration_number} -- semester: {self.semester} -- requested date: {self.requested_date} -- approved date: {self.approved_date}"

    def save(self, *args, **kwargs):
        if not self.requested_date:
            self.requested_date = date.today()
            super(Hostel_No_Due_request, self).save(*args, **kwargs)


class Guest_room_request(models.Model):
    PURPOSE_CHOICES = [
        ('for staying parents', 'For Staying Parents'),
        ('for staying relatives', 'For Staying Relatives'),
        ('for staying invited delegate', 'For Staying Invited Delegate'),
        ('for staying alumni', 'For Staying Alumni')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guest_room_request")
    purpose_of_request = models.CharField(max_length=225, choices=PURPOSE_CHOICES)
    from_date = models.DateField(verbose_name="from_date", null=True, blank=True)
    to_date = models.DateField(verbose_name="to_date", null=True, blank=True)
    no_of_persons = models.IntegerField(verbose_name="no_of_persons", blank=True, null=True)

    def __str__(self):
        return f'{self.user.registration_number} -- from: {self.from_date} -- to: {self.to_date} no of: {self.no_of_persons}'


class Complaint(models.Model):
    COMPLAINT_CHOICES = [
        ('ragging related', 'Ragging Related'),
        ('academic fees', 'Academic Fees'),
        ('classes related', 'Classes Related'),
        ('others', 'Others')
    ]

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="registration_number_or_employee_no")
    name = models.CharField(max_length=225, verbose_name="name", null=True, blank=True)
    branch = models.CharField(max_length=225, verbose_name="branch", null=True, blank=True)
    complaint_type = models.CharField(choices=COMPLAINT_CHOICES, max_length=225, verbose_name="complaint type",
                                      null=True, blank=True)
    complaint_description = models.TextField(verbose_name="complaint description", null=True, blank=True)
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name="status", null=True, blank=True)
    registered_date = models.DateField(verbose_name="registered date", null=True, blank=True)

    def __str__(self):
        return f'{self.registration_number} -- Name: {self.name} -- {self.branch} -- complaint type: {self.complaint_type}'


class Overall_No_Dues_Request(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('not_applied', 'Not Applied'),
    ]

    name = models.CharField(max_length=225, verbose_name="Name", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='overall_no_due', null=True, blank=True)
    branch = models.CharField(max_length=225, verbose_name="Branch", null=True, blank=True)
    father_name = models.CharField(max_length=225, verbose_name="Father's Name", null=True, blank=True)
    category = models.CharField(max_length=225, verbose_name="Category", null=True, blank=True)
    self_declaration = models.BooleanField(default=False, verbose_name="Self Declaration")
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, default='not_applied', verbose_name="Status")
    session = models.CharField(max_length=225, verbose_name="Session", null=True, blank=True)

    def __str__(self):
        return f'{self.user.registration_number} -- Name: {self.name} -- Branch: {self.branch} -- Category: {self.category} --session {self.session}'


class Departments_for_no_Dues(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'),
                      ('approved', 'Approved'), ]
    Department_name = models.CharField(max_length=225, verbose_name="Department")
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name="status",
                              default='pending')
    approved_date = models.DateField(verbose_name="approved_date", null=True, blank=True)
    applied_date = models.DateField(auto_now=True, verbose_name="applied_date")
    approved = models.BooleanField(default=False, verbose_name="approved")

    def __str__(self):
        return f'{self.Department_name}'


class No_Dues_list(models.Model):
    request_id = models.OneToOneField(Overall_No_Dues_Request, on_delete=models.CASCADE, related_name='no_dues_list',
                                      null=True, blank=True)
    STATUS_CHOICES = [('pending', 'Pending'),
                      ('approved', 'Approved'), ]
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name='status',
                              default='pending')
    approved_date = models.DateField(verbose_name="approved_date", null=True, blank=True)
    applied_date = models.DateField(auto_now=True, verbose_name="applied_date")
    approved = models.BooleanField(default=False, verbose_name="approved")
    departments = models.ManyToManyField(Departments_for_no_Dues, related_name='no_due_lists')

    def __str__(self):
        department_names = ', '.join([department.Department_name for department in self.departments.all()])
        return f'Request: {self.request_id} -- Departments: {department_names} --  -- Approved: {self.approved}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.departments.exists():
            all_departments = Departments_for_no_Dues.objects.all()
            self.departments.set(all_departments)
