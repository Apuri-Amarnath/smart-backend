# Generated by Django 5.0.6 on 2024-06-25 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_alter_bonafide_status_alter_hostel_allotment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest_room_request',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='Pending', max_length=225),
        ),
    ]
