import secrets
import string
import uuid

import pytz
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models, transaction
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models import BinaryField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from .emails import send_login_credentials, send_HOD_login_credentials
from .notifications import notify_roles, notify_same_college_users, notify_user, notify_hod
from django.db.utils import IntegrityError


def upload_college_logo(instance, filename):
    return upload_path(instance, filename, 'college-logos')


class College(models.Model):
    college_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    college_name = models.CharField(verbose_name="college_name", max_length=255, unique=True, null=True, blank=True)
    college_address = models.TextField(verbose_name="college_address", max_length=500, null=True, blank=True)
    established_date = models.DateField(verbose_name="established_date", null=True, blank=True)
    principal_name = models.CharField(verbose_name="principal_name", null=True, max_length=255, blank=True)
    phone_number = models.CharField(verbose_name="phone_number", null=True, max_length=15)
    college_email = models.EmailField(verbose_name="email", null=True, max_length=225)
    college_logo = models.ImageField(verbose_name="college_logo", upload_to=upload_college_logo, null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=225, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.college_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.college_name}'


# custom user manager
class MyUserManager(BaseUserManager):
    def create_user(self, registration_number, password=None, password2=None, **extra_fields):
        """
        Creates and saves a User with the given registration
        number and password.
        """
        if not registration_number:
            raise ValueError("Users must have an registration number")

        user = self.model(
            registration_number=self.normalize_registration_number(registration_number),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, registration_number, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given registration
        number and password.
        """
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("role", "super-admin")
        return self.create_user(registration_number, password, **extra_fields)

    def normalize_registration_number(self, registration_number):
        return registration_number.strip().upper()


# custom user model
class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('office', 'Office'),
        ('faculty', 'Faculty'),
        ('super-admin', 'Super-Admin'),
        ('hod', 'HOD'),
        ('principal', 'Principal'),
        ('caretaker', 'Caretaker'),
        ('department', 'Department'),
        ('registrar', 'Registrar'),
    ]
    registration_number = models.CharField(verbose_name="registration number", max_length=11, unique=True,
                                           validators=[MinLengthValidator(6), MaxLengthValidator(11)])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    branch = models.CharField(max_length=25, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "registration_number"
    REQUIRED_FIELDS = []

    class Meta:
        unique_together = ("registration_number", "college")

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

    def clean(self):
        super().clean()
        if self.role == 'hod' and not self.branch:
            raise ValidationError({'branch': 'Branch is required when the role is HOD.'})


def upload_path(instance, filename, folder):
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
    permanent_address = models.TextField(verbose_name="permanent address", max_length=300, blank=True, null=True)
    isCorrespndance_same = models.BooleanField(verbose_name="both address same", blank=True, null=True, default=False)
    correspndance_address = models.TextField(verbose_name="correspndance address", blank=True, null=True,
                                             max_length=300)
    profile_picture = models.ImageField(upload_to=upload_to_profile_pictures, blank=True, null=True)


class ContactInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contact_information')
    student_email = models.EmailField(verbose_name="student email address", max_length=225, blank=True, null=True)
    student_phone_number = models.CharField(verbose_name="student phone number", max_length=15, blank=True, null=True)
    fathers_mobile_number = models.CharField(verbose_name="fathers phone number", max_length=15, blank=True, null=True)


class AcademicInformation(models.Model):
    LAST_QUALIFICATION_CHOICES = [
        ('matric', 'Matric'),
        ('intermediate', 'Intermediate'),
        ('polytechnic', 'Polytechnic'),
    ]
    BOARD_CHOICES = [
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('BSEB', 'BSEB'),
        ('others', 'Others'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_information')
    last_qualification = models.CharField(choices=LAST_QUALIFICATION_CHOICES, max_length=225, blank=True, null=True)
    year = models.CharField(verbose_name="year", blank=True, null=True, max_length=20)
    school = models.CharField(verbose_name="school", max_length=225, null=True, default=None)
    board = models.CharField(choices=BOARD_CHOICES, max_length=225, null=True)
    branch = models.CharField(verbose_name="branch", max_length=225, null=True, blank=True)
    merit_serial_number = models.CharField(verbose_name="merit serial number", max_length=225, null=True, default=None)
    category = models.CharField(verbose_name="category", max_length=225, null=True, blank=True)
    date_of_admission = models.DateField(verbose_name="date of admission", null=True, blank=True)
    session = models.CharField(verbose_name="session", max_length=225, null=True, blank=True)
    university_reg_no = models.CharField(verbose_name="university registration number", max_length=225, null=True,
                                         blank=True)
    registration_year = models.DateField(verbose_name="registration year", null=True, blank=True)


class TransferCertificateInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='tc_information')
    TC_or_CL_no = models.CharField(verbose_name="TC_or_CL_no", max_length=225, null=True, blank=True)
    issuing_date_tc = models.DateField(verbose_name="issuing_date_tc", null=True, blank=True)
    purpose = models.CharField(verbose_name="purpose", max_length=225, null=True, blank=True)
    character_certificate_issued = models.BooleanField(verbose_name="character_certificate_issued", default=False)
    character_certificate_no = models.CharField(verbose_name="character_certificate_no", max_length=225, null=True,
                                                blank=True)
    issuing_date_cr = models.DateField(verbose_name="issuing_date_cr", null=True, blank=True)

    def __str__(self):
        return f"TC_or_CL_no: {self.TC_or_CL_no} -- user : {self.user.registration_number}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    personal_information = models.OneToOneField(PersonalInformation, on_delete=models.CASCADE,
                                                related_name='personal_profile')
    contact_information = models.OneToOneField(ContactInformation, on_delete=models.CASCADE,
                                               related_name='contact_profile')
    academic_information = models.OneToOneField(AcademicInformation, on_delete=models.CASCADE,
                                                related_name='academic_profile')
    tc_information = models.OneToOneField(TransferCertificateInformation, on_delete=models.CASCADE,
                                          related_name='tc_profile')

    def __str__(self):
        return self.user.registration_number


@receiver(post_save, sender=User)
def create_related_information(sender, instance, created, **kwargs):
    if created:
        personal_info = PersonalInformation.objects.create(user=instance)
        contact_info = ContactInformation.objects.create(user=instance)
        academic_info = AcademicInformation.objects.create(user=instance)
        tc_info = TransferCertificateInformation.objects.create(user=instance)
        UserProfile.objects.create(user=instance, personal_information=personal_info, contact_information=contact_info,
                                   academic_information=academic_info, tc_information=tc_info)


@receiver(post_save, sender=User)
def save_related_information(sender, instance, **kwargs):
    instance.personal_information.save()
    instance.contact_information.save()
    instance.academic_information.save()
    instance.tc_information.save()
    instance.profile.save()


class College_with_Ids(models.Model):
    id_count = models.IntegerField(verbose_name="id_count", default=0)
    college_name = models.CharField(verbose_name="college_name", max_length=255)

    def __str__(self):
        return f"{self.college_name} -- {self.id_count}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nofications_user')
    message = models.TextField(verbose_name="message", max_length=400, blank=True, null=True)
    time = models.DateTimeField(verbose_name="time", default=timezone.now)

    def __str__(self):
        return f'Notification for -- {self.user.registration_number} ---- {self.user.role} - {self.message[:20]} ---  {self.user.college} -- {self.time}'


def generate_bonafide_number():
    return str(uuid.uuid4().hex[:10])


class Bonafide(models.Model):
    STATUS_CHOICES = [
        ('not-applied', 'Not-applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="bonafide_college")
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="bonafide_student")
    roll_no = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roll_no")
    supporting_document = models.BinaryField(verbose_name="supporting_document", null=True, blank=True)
    issue_date = models.DateField(verbose_name="issue date", null=True, blank=True)
    applied_date = models.DateField(verbose_name="applied date", null=True, blank=True)
    required_for = models.CharField(verbose_name="required for", null=True, blank=True, max_length=225)
    fee_structure = models.BooleanField(verbose_name="fee_structure", default=False, null=True, blank=True)
    bonafide_number = models.CharField(unique=True, verbose_name="bonafide number", max_length=10, null=True,
                                       blank=True)
    status = models.CharField(verbose_name="status", choices=STATUS_CHOICES, max_length=225, default='not-applied')

    def save(self, *args, **kwargs):
        if not self.bonafide_number:
            self.bonafide_number = generate_bonafide_number()
        if not self.applied_date:
            self.applied_date = date.today()
        if self.status == 'not-applied':
            self.status = 'pending'
        super(Bonafide, self).save(*args, **kwargs)

    def __str__(self):
        return f" fname: {self.student.personal_information.first_name} -- lname: {self.student.personal_information.last_name} -- roll_no: {self.roll_no} -- bonafide no: {self.bonafide_number} -- date:  {self.issue_date}"


@receiver(post_save, sender=Bonafide)
def Bonafide_request_Notification(sender, instance, created, **kwargs):
    if created:
        notify_same_college_users(['registrar'],
                                  message=f"A new Bonafide has been requested from the student: {instance.roll_no}",
                                  college=instance.college)


@receiver(post_save, sender=Bonafide)
def Bonafide_approved_Notification(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'approved':
            notify_user(registration_number=instance.roll_no,
                        message=f"Your Bonafide request has been approved, please download it!")
        elif instance.status == 'rejected':
            notify_user(registration_number=instance.roll_no,
                        message=f"Your Bonafide request has been rejected, please re-apply !")


class Branch(models.Model):
    branch_name = models.CharField(max_length=225, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.branch_name} --  {self.college.college_name}"


def generate_password(length):
    import secrets, string
    alphabet = string.ascii_letters + string.digits + string.punctuation
    exclude = '/\\\'\"'
    filtered_password = ''.join(c for c in alphabet if c not in exclude)
    password = ''.join(secrets.choice(filtered_password) for i in range(length))
    return password


@receiver(post_save, sender=Branch)
def create_HOD_and_send_email(sender, instance, created, **kwargs):
    if created:
        try:
            branch_name = instance.branch_name
            college = instance.college
            registration_number = f'HOD-{branch_name.upper()[:3]}{college.college_code[:4]}'.upper()
            temporary_password = generate_password(10)
            with transaction.atomic():
                if not User.objects.filter(registration_number=registration_number, college=college).exists():
                    user = User.objects.create_user(
                        registration_number=registration_number, password=temporary_password, college=college,
                        role='hod', branch=branch_name)
                    college_with_ids = College_with_Ids.objects.get(college_name=college.slug)
                    college_with_ids.id_count += 1
                    college_with_ids.save()
                    send_HOD_login_credentials(registration_number=registration_number,
                                               college_name=college.college_name,
                                               password=temporary_password, branch=branch_name.upper(),
                                               to_email=college.college_email)
        except Exception as e:
            print(f"An error occured while user creation: {e}")


class Subject(models.Model):
    subject_name = models.CharField(verbose_name="subject_name", max_length=225, null=True, blank=True)
    subject_code = models.CharField(verbose_name="subject_id", max_length=30, null=True)
    instructor = models.CharField(verbose_name="Instructor", max_length=100, null=True, blank=True)
    college = models.ForeignKey(College, verbose_name="subjects", on_delete=models.CASCADE)

    def __str__(self):
        return f"subject name: {self.subject_name} -- subject code: {self.subject_code} -- instructor: {self.instructor}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['college', 'subject_code'], name='unique_college_subject_code')
        ]


class Semester(models.Model):
    college = models.ForeignKey(College, verbose_name="semester", on_delete=models.CASCADE)
    branch = models.CharField(verbose_name="branch", max_length=225, null=True, blank=True)
    branch_name = models.CharField(verbose_name="branch_name", max_length=225, null=True, blank=True)
    semester_name = models.CharField(verbose_name="semester_name", max_length=225)
    subjects = models.ManyToManyField(Subject, verbose_name="subjects", related_name="semester_subjects")

    def __str__(self):
        subjects_list = ", ".join([subject.subject_name for subject in self.subjects.all()])
        return f" semester: {self.semester_name} -- subjects: {subjects_list} -- {self.branch} == {self.college.college_name}"

    def get_subjects_list(self):
        return self.subjects.all()


class Semester_Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),

    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="semester_registrations_college")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="semester_registrations")
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                                related_name="semester_registration_student")
    applied_date = models.DateField(verbose_name="semester_registration_date", null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=225, null=True, blank=True, default="pending")

    def save(self, *args, **kwargs):
        if not self.applied_date:
            self.applied_date = date.today()
        super(Semester_Registration, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.semester} - {self.student} -- {self.semester.branch} --  {self.college.college_name}"


@receiver(signal=post_save, sender=Semester_Registration)
def create_semester_registration_notification(sender, instance, created, *args, **kwargs):
    if created:
        branch = instance.semester.branch
        notify_hod(role='hod', branch=branch,
                   message=f"semester registration from {instance.student.user.registration_number} for {instance.semester.semester_name} is recieved")


class VerifySemesterRegistration(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='semester_verification')
    registration_details = models.ForeignKey(Semester_Registration, on_delete=models.CASCADE,
                                             related_name='registration_details')
    remarks = models.CharField(max_length=300, verbose_name="remarks", blank=True, null=True)
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name="status")

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            try:
                previous_status = VerifySemesterRegistration.objects.get(pk=self.pk).status
            except ObjectDoesNotExist:
                pass

        super().save(*args, **kwargs)
        self.registration_details.status = self.status
        self.registration_details.save()

        if self.status == 'approved' and previous_status != 'approved':
            user = self.registration_details.student.user
            Notification.objects.create(user=user,
                                        message=f"Your semester registration has been approved")
        if self.status == 'rejected' and previous_status != 'rejected':
            user = self.registration_details.student.user
            Notification.objects.create(user=user, message=f"Your semester registration has been rejected")

    def __str__(self):
        return f'{self.registration_details} - {self.status}-- {self.college.college_name}'


class HostelRooms(models.Model):
    STATUS_CHOICES = [
        ('not-available', 'Not available'),
        ('available', 'Available'),
        ('occupied', 'Occupied')
    ]
    ROOM_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, verbose_name="hostel_rooms")
    room_no = models.IntegerField(verbose_name="room no", blank=True, null=True)
    current_occupancy = models.IntegerField(verbose_name="current occupancy", default=0, blank=True, null=True)
    capacity = models.IntegerField(verbose_name="capacity", blank=True, null=True)
    room_type = models.CharField(verbose_name="room type", max_length=20, choices=ROOM_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="room status",
                              default='not-available', blank=True, null=True)

    def __str__(self):
        return f'{self.room_no} - {self.status}-- {self.college.college_name} --  {self.room_type}'


class Hostel_Allotment(models.Model):
    ROOM_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
    ]
    STATUS_CHOICES = [
        ('not-applied', 'Not-applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="hostel_allotment_registrations")
    cgpa = models.CharField(max_length=125, verbose_name="CGPA", null=True, blank=True)
    prefered_room_type = models.CharField(choices=ROOM_CHOICES, max_length=125, verbose_name="Prefered Room",
                                          null=True, blank=True)
    latest_marksheet = models.BinaryField(verbose_name="marksheet", null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=225, null=True, blank=True, default="not-applied")

    def __str__(self):
        return f"{self.user.registration_number} - {self.status}"

    def save(self, *args, **kwargs):
        if self.status == 'not-applied':
            self.status = 'pending'
        super(Hostel_Allotment, self).save(*args, **kwargs)

    def update_status(self, new_status):
        self.status = new_status
        self.save()


@receiver(post_save, sender=Hostel_Allotment)
def Hostel_Allotment_Notification(sender, instance, created, **kwargs):
    if created:
        notify_same_college_users(["caretaker"],
                                  f"New Allotment request received from {instance.user.registration_number}",
                                  college=instance.college)


class Hostel_Room_Allotment(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    allotment_details = models.ManyToManyField(Hostel_Allotment, related_name="hostel_room_allotment")
    hostel_room = models.ForeignKey(HostelRooms, on_delete=models.CASCADE)

    def get_registration_numbers(self):
        return [
            allotment.user.registration_number.strip()
            for allotment in self.allotment_details.all()
            if hasattr(allotment, 'user') and allotment.user
        ]

    def __str__(self):
        return f"Room No: {self.hostel_room.room_no} -- Registration No: {', '.join(self.get_registration_numbers())} --"


class Fees_model(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    Maintainance_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="Maintainance_fees")
    Mess_fees = models.CharField(max_length=225, null=True, blank=True, verbose_name="Mess fees")
    Security_Deposit = models.CharField(max_length=225, null=True, blank=True, verbose_name="Security deposit")

    def __str__(self):
        return f" id : {self.id} -- Main Fees : {self.Maintainance_fees} -- Mess Fees : {self.Mess_fees} -- Security Deposit {self.Security_Deposit} "


class Mess_fee_payment(models.Model):
    FEE_TYPE_CHOICES = [
        ('mess_fee', 'Mees Fee'),
        ('maintainance_fee', 'Maintainance Fees'),
        ('security_fee', 'Security Fee')
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    registration_details = models.ForeignKey(Hostel_Room_Allotment, on_delete=models.CASCADE)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    fee_type = models.CharField(max_length=225, choices=FEE_TYPE_CHOICES, null=True, blank=True,
                                verbose_name="fee_type")
    total_fees = models.DecimalField(max_digits=30, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        allotments = self.registration_details.allotment_details.all()
        registration_numbers = []
        for allotment in allotments:
            if hasattr(allotment, 'user'):
                registration_numbers.append(allotment.user.registration_number)
        user_names = ','.join(registration_numbers)
        return f" Users : {user_names} -- {self.from_date} -- {self.to_date} -- {self.fee_type} -- {self.total_fees}"

    def clean(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError('From date cannot be later than to date.')
        if self.total_fees < 0:
            raise ValidationError('Total fees must be a positive value.')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['registration_details', 'from_date', 'to_date', 'fee_type'],
                                    name='unique_mess_fee_per_period')
        ]


class Hostel_No_Due_request(models.Model):
    STATUS_CHOICES = [
        ('not-applied', 'Not-applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.CharField(max_length=225, verbose_name="semester", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Hostel_no_due_request")
    maintenance_fees_date = models.DateField(verbose_name="Maintance_fees", null=True, blank=True)
    mess_fees_date = models.DateField(verbose_name="Mess_fees", null=True, blank=True)
    self_declaration = models.BooleanField(verbose_name="self_agree", null=True, blank=True, default=False)
    requested_date = models.DateField(verbose_name="requested_date", null=True, blank=True)
    approved_date = models.DateField(verbose_name="approved_date", null=True, blank=True)
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, default="not-applied")

    def __str__(self):
        return f"{self.user.registration_number} --{self.college.college_name} -- semester: {self.semester} -- requested date: {self.requested_date} -- approved date: {self.approved_date}"


@receiver(signal=post_save, sender=Hostel_No_Due_request)
def notify_caretakers(sender, instance, created, **kwargs):
    if created:
        notify_same_college_users(roles='caretaker',
                                  message=f"A New Hostel No Due Request has been recieved from {instance.user.registration_number}.",
                                  college=instance.college)


@receiver(signal=post_save, sender=Hostel_No_Due_request)
def notify_student(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'approved':
            notify_user(registration_number=instance.user.registration_number,
                        message=f"Your Hostel No Due Request has has been approved, please download it!")
        elif instance.status == 'rejected':
            notify_user(registration_number=instance.user.registration_number,
                        message=f"Your Hostel No Due Request has has been rejected, please re-apply !")


class Guest_room_request(models.Model):
    PURPOSE_CHOICES = [
        ('for staying parents', 'For Staying Parents'),
        ('for staying relatives', 'For Staying Relatives'),
        ('for staying invited delegate', 'For Staying Invited Delegate'),
        ('for staying alumni', 'For Staying Alumni')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guest_room_request")
    purpose_of_request = models.CharField(max_length=225, choices=PURPOSE_CHOICES)
    from_date = models.DateField(verbose_name="from_date", null=True, blank=True)
    to_date = models.DateField(verbose_name="to_date", null=True, blank=True)
    no_of_persons = models.IntegerField(verbose_name="no_of_persons", blank=True, null=True)
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f'{self.user.registration_number} -- from: {self.from_date} -- to: {self.to_date} no of: {self.no_of_persons}'


@receiver(post_save, sender=Guest_room_request)
def guest_room_notify(sender, instance, created, **kwargs):
    if created:
        notify_same_college_users('office', f"New guest room request from {instance.user.registration_number}",
                                  college=instance.college)


class Complaint(models.Model):
    COMPLAINT_CHOICES = [
        ('ragging related', 'Ragging Related'),
        ('academic fees', 'Academic Fees'),
        ('classes related', 'Classes Related'),
        ('others', 'Others')
    ]

    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('under investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="registration_number_or_employee_no")
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=225, verbose_name="name", null=True, blank=True)
    branch = models.CharField(max_length=225, verbose_name="branch", null=True, blank=True)
    complaint_type = models.CharField(choices=COMPLAINT_CHOICES, max_length=225, verbose_name="complaint type",
                                      null=True, blank=True)
    subject = models.CharField(max_length=225, verbose_name="subject", null=True, blank=True)
    complaint_description = models.TextField(verbose_name="complaint description", null=True, blank=True)
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name="status", default='registered',
                              null=True, blank=True)
    registered_date = models.DateField(verbose_name="registered date", null=True, blank=True)

    def __str__(self):
        return f'{self.registration_number} -- Name: {self.name} -- {self.branch} -- complaint type: {self.complaint_type}'


class Overall_No_Dues_Request(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('not_applied', 'Not Applied'),
    ]

    name = models.CharField(max_length=225, verbose_name="Name", null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='overall_no_due', null=True, blank=True)
    branch = models.CharField(max_length=225, verbose_name="Branch", null=True, blank=True)
    father_name = models.CharField(max_length=225, verbose_name="Father's Name", null=True, blank=True)
    category = models.CharField(max_length=225, verbose_name="Category", null=True, blank=True)
    self_declaration = models.BooleanField(default=False, verbose_name="Self Declaration")
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, default='not_applied', verbose_name="Status")
    session = models.CharField(max_length=225, verbose_name="Session", null=True, blank=True)

    def __str__(self):
        return f'{self.user.registration_number} -- Name: {self.name} -- Branch: {self.branch} -- Category: {self.category} --session {self.session}'


@receiver(post_save, sender=Overall_No_Dues_Request)
def notify_departments(sender, instance, created, **kwargs):
    if created:
        notify_roles(["admin", "department"], f"New Overall No dues Request by {instance.user.registration_number}")


class Departments_for_no_Dues(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'),
                      ('approved', 'Approved'),
                      ('rejected', 'Rejected')]
    Department_id = models.IntegerField(verbose_name="Department ID", primary_key=True)
    Department_name = models.CharField(max_length=225, verbose_name="Department")
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name="status",
                              default='pending')
    approved_date = models.DateField(verbose_name="approved_date", null=True, blank=True)
    applied_date = models.DateField(auto_now=True, verbose_name="applied_date")

    def __str__(self):
        return f'{self.Department_name} - {self.status} '

    @classmethod
    def generate_unique_department_id(cls):
        last_department = cls.objects.order_by('-Department_id').first()
        if last_department:
            return last_department.Department_id + 1
        else:
            return 1

    def save(self, *args, **kwargs):
        if not self.Department_id:
            self.Department_id = self.generate_unique_department_id()
        super().save(*args, **kwargs)


class No_Dues_list(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    request_id = models.OneToOneField(Overall_No_Dues_Request, on_delete=models.CASCADE, related_name='no_dues_list',
                                      null=True, blank=True)
    STATUS_CHOICES = [('pending', 'Pending'),
                      ('approved', 'Approved'),
                      ('rejected', 'Rejected')]
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name='status',
                              default='pending')
    approved_date = models.DateField(verbose_name="approved_date", null=True, blank=True)
    applied_date = models.DateField(auto_now=True, verbose_name="applied_date")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['request_id'], name='unique_no_dues_list')
        ]

    def __str__(self):
        department_names = ', '.join([department.Department_name for department in self.cloned_departments.all()])
        return f'Request: {self.request_id} -- Departments: {department_names} -- status: {self.status}'

    def save(self, *args, **kwargs):
        if self.request_id and self.request_id.college:
            self.college = self.request_id.college
        with transaction.atomic():
            is_new = self._state.adding
            super().save(*args, **kwargs)

            if is_new or not self.cloned_departments.exists():
                self._create_cloned_departments()

            self._update_status()

    def _create_cloned_departments(self):
        all_departments = Departments_for_no_Dues.objects.all()
        cloned_departments = []
        for department in all_departments:
            cloned_departments.append(
                Cloned_Departments_for_no_Dues(
                    no_dues_list=self,
                    college=self.college,
                    Department_name=department.Department_name,
                    Department_id=department.Department_id,
                    status='pending',
                    applied_date=timezone.now()
                )
            )
        Cloned_Departments_for_no_Dues.objects.bulk_create(cloned_departments)

    def _update_status(self):
        all_approved = all(department.status == 'approved' for department in self.cloned_departments.all())
        if all_approved:
            self.status = 'approved'
            self.approved_date = timezone.now() if not self.approved_date else self.approved_date
        else:
            self.status = 'pending'
            self.approved_date = None
        super().save(update_fields=['status', 'approved_date'])


class Cloned_Departments_for_no_Dues(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [('pending', 'Pending'),
                      ('approved', 'Approved'),
                      ('rejected', 'Rejected'),
                      ]
    no_dues_list = models.ForeignKey(No_Dues_list, on_delete=models.CASCADE, related_name="cloned_departments")
    Department_name = models.CharField(max_length=225, verbose_name="Department")
    Department_id = models.IntegerField(verbose_name="Department ID")
    status = models.CharField(max_length=225, choices=STATUS_CHOICES, verbose_name="status")
    approved_date = models.DateField(verbose_name="approved_date", null=True, blank=True)
    applied_date = models.DateField(auto_now=True, verbose_name="applied_date")

    def __str__(self):
        return f'{self.Department_name} - {self.status}'


@receiver(post_save, sender=Cloned_Departments_for_no_Dues)
def update_overall_no_dues_request_status(sender, instance, **kwargs):
    no_dues_list = instance.no_dues_list
    if all(department.status == 'approved' for department in no_dues_list.cloned_departments.all()):
        no_dues_list.status = 'approved'
        no_dues_list.approved_date = timezone.now()
        Notification.objects.create(user=no_dues_list.request_id.user,
                                    message='Your Overall no dues request has been approved')
    else:
        no_dues_list.status = 'pending'
        no_dues_list.approved_date = None
    no_dues_list.save()


@receiver(post_save, sender=No_Dues_list)
def update_overall_request_status(sender, instance, **kwargs):
    if instance.status == 'approved':
        instance.request_id.status = 'approved'
        instance.request_id.save()
    elif instance.status == 'pending':
        instance.request_id.status = 'pending'
        instance.request_id.save()
    elif instance.status == 'rejected':
        instance.request_id.status = 'rejected'
        instance.request_id.save()


@receiver(post_save, sender=User)
def create_welcome_message(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            Notification.objects.create(user=instance, message="Welcome to the SmartOne.")
            Notification.objects.create(user=instance, message="Please update your profile.")
        else:
            Notification.objects.create(user=instance, message="Welcome to SmartOne.")
            Notification.objects.create(user=instance, message="Please reset your password.")


def upload_college_requests(instance, filename):
    return upload_path(instance, filename, 'college-requests')


class CollegeRequest(models.Model):
    name = models.CharField(max_length=225, blank=True, null=True, verbose_name="name")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="email address")
    college_name = models.CharField(max_length=225, blank=True, null=True, verbose_name="college name")
    college_address = models.TextField(max_length=550, blank=True, null=True, verbose_name="college address")
    college_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="college code")
    established_date = models.DateField(verbose_name="established date", blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="phone")
    principal_name = models.CharField(verbose_name="principal_name", null=True, max_length=255, blank=True)
    college_logo = models.ImageField(verbose_name="college_logo", upload_to=upload_college_requests, null=True,
                                     blank=True)
    is_verified = models.BooleanField(verbose_name="verified", default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_verified:
            self.copy_to_college()
            registration_number = self.generate_registration_number()
            Temparory_password = self.generate_password()
            try:
                college = College.objects.get(college_name=self.college_name)
                user = User.objects.create_user(
                    registration_number=registration_number,
                    password=Temparory_password,
                    college=college,
                    role='office',
                )
                send_login_credentials(registration_number=registration_number, password=Temparory_password,
                                       to_email=self.email, college_name=self.college_name)
                College_with_Ids.objects.update_or_create(
                    college_name=slugify(self.college_name),
                    defaults={'id_count': 0}
                )
            except College.DoesNotExist:
                raise ValidationError("college Does not exist")

    def generate_registration_number(self):
        prefix = 'OFFICE-'
        college = College.objects.get(college_name=self.college_name)
        college_code = str(college.college_code[:4])
        registration_number = f'{prefix}{college_code}'.upper()
        return registration_number[:11]

    def generate_password(self, length=10):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        exclude = '/\\\'\"'
        filtered_password = ''.join(c for c in alphabet if c not in exclude)
        password = ''.join(secrets.choice(filtered_password) for i in range(length))
        return password

    def copy_to_college(self):
        if not College.objects.filter(college_name=self.college_name).exists():
            College.objects.create(college_name=self.college_name, college_address=self.college_address,
                                   established_date=self.established_date, phone_number=self.phone_number,
                                   principal_name=self.principal_name, college_logo=self.college_logo,
                                   college_email=self.email, college_code=self.college_code)
            notify_roles(["super-admin"], f"New college is added to the site")

    def __str__(self):
        return f'{self.name} - {self.email} - {self.college_name} '


@receiver(post_save, sender=CollegeRequest)
def College_request_Notification(sender, instance, created, **kwargs):
    if created:
        notify_roles(["super-admin"],
                     f"New college request is received from {instance.college_name}  -- email: {instance.email}")
