# Generated by Django 5.0.6 on 2024-05-29 00:12

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
                ('registration_number', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(11)], verbose_name='registration number')),
                ('role', models.CharField(choices=[('student', 'Student'), ('office', 'Office'), ('faculty', 'Faculty'), ('admin', 'Admin'), ('principal', 'Principal')], max_length=10)),
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
            name='AcademicInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrollment_date', models.DateField(blank=True, null=True, verbose_name='enrollment date')),
                ('program', models.CharField(blank=True, max_length=100, null=True, verbose_name='program')),
                ('major', models.CharField(blank=True, max_length=100, null=True, verbose_name='major')),
                ('current_year', models.IntegerField(blank=True, null=True, verbose_name='current year')),
                ('gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='GPA')),
                ('course_enrolled', models.TextField(blank=True, null=True, verbose_name='course enrolled')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='academic_information', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=225, null=True, verbose_name='email address')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='phone number')),
                ('alternate_phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='alternate phone')),
                ('address', models.TextField(blank=True, max_length=300, null=True, verbose_name='address')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='city')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='state')),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='postal code')),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name='country')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contact_information', to=settings.AUTH_USER_MODEL)),
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
                ('profile_picture', models.ImageField(blank=True, max_length=200, null=True, upload_to=api.models.upload_to_profile_pictures)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personal_information', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bonafide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_semester', models.CharField(blank=True, max_length=10, null=True, verbose_name='year/semester')),
                ('batch', models.CharField(blank=True, max_length=10, null=True, verbose_name='batch')),
                ('department', models.CharField(blank=True, max_length=225, null=True, verbose_name='department')),
                ('course_start_date', models.DateField(blank=True, null=True, verbose_name='course start date')),
                ('issue_date', models.DateField(blank=True, null=True, verbose_name='issue date')),
                ('required_for', models.CharField(blank=True, max_length=225, null=True, verbose_name='required for')),
                ('bonafide_number', models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='bonafide number')),
                ('roll_no', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='roll_no', to=settings.AUTH_USER_MODEL)),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonafide_college', to='api.college')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonafide_student', to='api.personalinformation')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='academic_profile', to='api.academicinformation')),
                ('contact_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contact_profile', to='api.contactinformation')),
                ('personal_information', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personal_profile', to='api.personalinformation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
