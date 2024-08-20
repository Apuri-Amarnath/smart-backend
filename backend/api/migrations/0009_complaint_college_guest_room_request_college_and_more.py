# Generated by Django 5.0.6 on 2024-08-20 21:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_rename_maintance_fees_date_hostel_no_due_request_maintenance_fees_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='college',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.college'),
        ),
        migrations.AddField(
            model_name='guest_room_request',
            name='college',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.college'),
        ),
        migrations.AddField(
            model_name='overall_no_dues_request',
            name='college',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.college'),
        ),
    ]
