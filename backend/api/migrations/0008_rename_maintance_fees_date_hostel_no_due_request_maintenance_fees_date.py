# Generated by Django 5.0.6 on 2024-08-20 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_rename_maintance_fees_date_hostel_no_due_request_maintance_fees_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hostel_no_due_request',
            old_name='maintance_fees_date',
            new_name='maintenance_fees_date',
        ),
    ]
