# Generated by Django 5.0.6 on 2024-06-29 14:23

import api.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('registration_number', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(6), django.core.validators.MaxLengthValidator(11)], verbose_name='registration number')),
                ('role', models.CharField(choices=[('student', 'Student'), ('office', 'Office'), ('faculty', 'Faculty'), ('admin', 'Admin'), ('principal', 'Principal'), ('caretaker', 'Caretaker')], max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('college_code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('college_name', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='college_name')),
                ('college_address', models.TextField(blank=True, max_length=500, null=True, verbose_name='college_address')),
                ('established_date', models.DateField(blank=True, null=True, verbose_name='established_date')),
                ('principal_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='principal_name')),
                ('phone_number', models.CharField(max_length=15, null=True, verbose_name='phone_number')),
                ('email', models.EmailField(max_length=225, null=True, verbose_name='email')),
                ('college_logo', models.ImageField(blank=True, null=True, upload_to=api.models.upload_college_logo, verbose_name='college_logo')),
            ],
        ),
        migrations.CreateModel(
            name='Departments_for_no_Dues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Department_name', models.CharField(max_length=225, verbose_name='Department')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending', max_length=225, verbose_name='status')),
                ('approved_date', models.DateField(blank=True, null=True, verbose_name='approved_date')),
                ('applied_date', models.DateField(auto_now=True, verbose_name='applied_date')),
                ('approved', models.BooleanField(default=False, verbose_name='approved')),
            ],
        ),
        migrations.CreateModel(
            name='Fees_model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Maintainance_fees', models.CharField(blank=True, max_length=225, null=True, verbose_name='Maintainance_fees')),
                ('Mess_fees', models.CharField(blank=True, max_length=225, null=True, verbose_name='Mess fees')),
                ('Security_Deposit', models.CharField(blank=True, max_length=225, null=True, verbose_name='Security deposit')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(blank=True, max_length=225, null=True, verbose_name='subject_name')),
                ('subject_code', models.CharField(max_length=30, null=True, unique=True, verbose_name='subject_id')),
                ('instructor', models.CharField(blank=True, max_length=100, null=True, verbose_name='Instructor')),
            ],
        ),
        migrations.CreateModel(
            name='AcademicInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_qualification', models.CharField(blank=True, choices=[('matric', 'Matric'), ('intermediate', 'Intermediate'), ('polytechnic', 'Polytechnic')], max_length=225, null=True)),
                ('year', models.IntegerField(blank=True, null=True, verbose_name='year')),
                ('school', models.CharField(default=None, max_length=225, null=True, verbose_name='school')),
                ('board', models.CharField(choices=[('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('BSEB', 'BSEB'), ('others', 'Others')], max_length=225, null=True)),
                ('merit_serial_number', models.CharField(default=None, max_length=225, null=True, verbose_name='merit serial number')),
                ('category', models.CharField(blank=True, max_length=225, null=True, verbose_name='category')),
                ('college_name', models.CharField(blank=True, max_length=225, null=True, verbose_name='college name')),
                ('date_of_admission', models.DateField(blank=True, null=True, verbose_name='date of admission')),
                ('session', models.CharField(blank=True, max_length=225, null=True, verbose_name='session')),
                ('university_reg_no', models.CharField(blank=True, max_length=225, null=True, verbose_name='university registration number')),
                ('registration_year', models.DateField(blank=True, null=True, verbose_name='registration year')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='academic_information', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=225, null=True, verbose_name='name')),
                ('branch', models.CharField(blank=True, max_length=225, null=True, verbose_name='branch')),
                ('complaint_type', models.CharField(blank=True, choices=[('ragging related', 'Ragging Related'), ('academic fees', 'Academic Fees'), ('classes related', 'Classes Related'), ('others', 'Others')], max_length=225, null=True, verbose_name='complaint type')),
                ('subject', models.CharField(blank=True, max_length=225, null=True, verbose_name='subject')),
                ('complaint_description', models.TextField(blank=True, null=True, verbose_name='complaint description')),
                ('status', models.CharField(blank=True, choices=[('registered', 'Registered'), ('under investigation', 'Under Investigation'), ('resolved', 'Resolved')], max_length=225, null=True, verbose_name='status')),
                ('registered_date', models.DateField(blank=True, null=True, verbose_name='registered date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_number_or_employee_no', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_email', models.EmailField(blank=True, max_length=225, null=True, verbose_name='student email address')),
                ('student_phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='student phone number')),
                ('fathers_mobile_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='fathers phone number')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contact_information', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Guest_room_request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purpose_of_request', models.CharField(choices=[('for staying parents', 'For Staying Parents'), ('for staying relatives', 'For Staying Relatives'), ('for staying invited delegate', 'For Staying Invited Delegate'), ('for staying alumni', 'For Staying Alumni')], max_length=225)),
                ('from_date', models.DateField(blank=True, null=True, verbose_name='from_date')),
                ('to_date', models.DateField(blank=True, null=True, verbose_name='to_date')),
                ('no_of_persons', models.IntegerField(blank=True, null=True, verbose_name='no_of_persons')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='Pending', max_length=225)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_room_request', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Hostel_Allotment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cgpa', models.CharField(blank=True, max_length=125, null=True, verbose_name='CGPA')),
                ('latest_marksheet', models.BinaryField(blank=True, null=True, verbose_name='marksheet')),
                ('status', models.CharField(blank=True, choices=[('not-applied', 'Not-applied'), ('applied', 'Applied'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='not-applied', max_length=225, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hostel_allotment_registrations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Hostel_No_Due_request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(blank=True, max_length=225, null=True, verbose_name='semester')),
                ('Maintance_fees_date', models.DateField(blank=True, null=True, verbose_name='Maintance_fees')),
                ('Mess_fees_date', models.DateField(blank=True, null=True, verbose_name='Mess_fees')),
                ('self_declaration', models.BooleanField(blank=True, default=False, null=True, verbose_name='self_agree')),
                ('requested_date', models.DateField(blank=True, null=True, verbose_name='requested_date')),
                ('approved_date', models.DateField(blank=True, null=True, verbose_name='approves_date')),
                ('status', models.CharField(choices=[('not-applied', 'Not-applied'), ('applied', 'Applied'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='not-applied', max_length=225)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Hostel_no_due_request', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Hostel_Room_Allotment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostel_room', models.CharField(blank=True, max_length=225, null=True, unique=True, verbose_name='hostel_room')),
                ('registration_details', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hostel_room_allotment', to='api.hostel_allotment')),
            ],
        ),
        migrations.CreateModel(
            name='Mess_fee_payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateField(blank=True, null=True)),
                ('to_date', models.DateField(blank=True, null=True)),
                ('mess_fees', models.CharField(blank=True, max_length=225, null=True, verbose_name='mess-fee')),
                ('maintainance_fees', models.CharField(blank=True, max_length=225, null=True, verbose_name='maintainance-fee')),
                ('security_fees', models.CharField(blank=True, max_length=225, null=True, verbose_name='security-fee')),
                ('total_fees', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True)),
                ('registration_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.hostel_room_allotment')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, max_length=400, null=True, verbose_name='message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nofications_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Overall_No_Dues_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=225, null=True, verbose_name='Name')),
                ('branch', models.CharField(blank=True, max_length=225, null=True, verbose_name='Branch')),
                ('father_name', models.CharField(blank=True, max_length=225, null=True, verbose_name="Father's Name")),
                ('category', models.CharField(blank=True, max_length=225, null=True, verbose_name='Category')),
                ('self_declaration', models.BooleanField(default=False, verbose_name='Self Declaration')),
                ('status', models.CharField(choices=[('applied', 'Applied'), ('pending', 'Pending'), ('approved', 'Approved'), ('not_applied', 'Not Applied')], default='not_applied', max_length=225, verbose_name='Status')),
                ('session', models.CharField(blank=True, max_length=225, null=True, verbose_name='Session')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='overall_no_due', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='No_Dues_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending', max_length=225, verbose_name='status')),
                ('approved_date', models.DateField(blank=True, null=True, verbose_name='approved_date')),
                ('applied_date', models.DateField(auto_now=True, verbose_name='applied_date')),
                ('approved', models.BooleanField(default=False, verbose_name='approved')),
                ('departments', models.ManyToManyField(related_name='no_due_lists', to='api.departments_for_no_dues')),
                ('request_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='no_dues_list', to='api.overall_no_dues_request')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='last name')),
                ('father_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='father name')),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='middle name')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='birth')),
                ('gender', models.CharField(blank=True, max_length=10, null=True, verbose_name='gender')),
                ('permanent_address', models.TextField(blank=True, max_length=300, null=True, verbose_name='permanent address')),
                ('isCorrespndance_same', models.BooleanField(blank=True, default=False, null=True, verbose_name='both address same')),
                ('correspndance_address', models.TextField(blank=True, max_length=300, null=True, verbose_name='correspndance address')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to=api.models.upload_to_profile_pictures)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personal_information', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bonafide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supporting_document', models.BinaryField(blank=True, null=True, verbose_name='supporting_document')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='issue date')),
                ('applied_date', models.DateField(blank=True, null=True, verbose_name='applied date')),
                ('required_for', models.CharField(blank=True, max_length=225, null=True, verbose_name='required for')),
                ('fee_structure', models.BooleanField(blank=True, default=False, null=True, verbose_name='fee_structure')),
                ('bonafide_number', models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='bonafide number')),
                ('status', models.CharField(choices=[('not-applied', 'Not-applied'), ('applied', 'Applied'), ('pending', 'Pending'), ('rejected', 'Rejected'), ('approved', 'Approved'), ('rejected', 'Rejected')], default=('not-applied', 'Not-applied'), max_length=225, verbose_name='status')),
                ('roll_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roll_no', to=settings.AUTH_USER_MODEL)),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonafide_college', to='api.college')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonafide_student', to='api.personalinformation')),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(blank=True, max_length=225, null=True, verbose_name='branch')),
                ('semester_name', models.CharField(max_length=225, verbose_name='semester_name')),
                ('subjects', models.ManyToManyField(related_name='semester_subjects', to='api.subject', verbose_name='subjects')),
            ],
        ),
        migrations.CreateModel(
            name='TransferCertificateInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TC_or_CL_no', models.CharField(blank=True, max_length=225, null=True, verbose_name='TC_or_CL_no')),
                ('issuing_date_tc', models.DateField(blank=True, null=True, verbose_name='issuing_date_tc')),
                ('purpose', models.CharField(blank=True, max_length=225, null=True, verbose_name='purpose')),
                ('character_certificate_issued', models.BooleanField(default=False, verbose_name='character_certificate_issued')),
                ('character_certificate_no', models.CharField(blank=True, max_length=225, null=True, verbose_name='character_certificate_no')),
                ('issuing_date_cr', models.DateField(blank=True, null=True, verbose_name='issuing_date_cr')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tc_information', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='academic_profile', to='api.academicinformation')),
                ('contact_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contact_profile', to='api.contactinformation')),
                ('personal_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personal_profile', to='api.personalinformation')),
                ('tc_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tc_profile', to='api.transfercertificateinformation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Semester_Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applied_date', models.DateField(blank=True, null=True, verbose_name='semester_registration_date')),
                ('status', models.CharField(blank=True, choices=[('Pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='Pending', max_length=225, null=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semester_registrations', to='api.semester')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semester_registration_student', to='api.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='VerifySemesterRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remarks', models.CharField(max_length=300, verbose_name='remarks')),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('rejected', 'Rejected')], max_length=225, verbose_name='status')),
                ('registration_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_details', to='api.semester_registration')),
            ],
        ),
    ]
