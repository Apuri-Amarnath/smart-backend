# Generated by Django 5.0.6 on 2024-08-20 17:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_hostel_room_allotment_college'),
    ]

    operations = [
        migrations.AddField(
            model_name='fees_model',
            name='college',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.college'),
        ),
    ]
