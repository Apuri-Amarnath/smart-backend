# Generated by Django 5.0.6 on 2024-06-24 19:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_alter_hostel_no_due_request_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalinformation',
            name='profile_picture',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='registration_number',
            field=models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(6), django.core.validators.MaxLengthValidator(11)], verbose_name='registration number'),
        ),
    ]
