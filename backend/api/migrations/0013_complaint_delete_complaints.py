# Generated by Django 5.0.6 on 2024-06-08 11:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_complaints_guest_room_request_hostel_allotment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=225, null=True, verbose_name='name')),
                ('branch', models.CharField(blank=True, max_length=225, null=True, verbose_name='branch')),
                ('complaint_type', models.CharField(blank=True, choices=[('ragging related', 'Ragging Related'), ('academic fees', 'Academic Fees'), ('classes related', 'Classes Related'), ('others', 'Others')], max_length=225, null=True, verbose_name='complaint type')),
                ('complaint_description', models.TextField(blank=True, null=True, verbose_name='complaint description')),
                ('status', models.CharField(blank=True, choices=[('applied', 'Applied'), ('pending', 'Pending'), ('approved', 'Approved')], max_length=225, null=True, verbose_name='status')),
                ('registration_number', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='registration_number_or_employee_no', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Complaints',
        ),
    ]
