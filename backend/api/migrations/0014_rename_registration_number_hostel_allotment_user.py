# Generated by Django 5.0.6 on 2024-06-08 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_complaint_delete_complaints'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hostel_allotment',
            old_name='registration_number',
            new_name='user',
        ),
    ]
