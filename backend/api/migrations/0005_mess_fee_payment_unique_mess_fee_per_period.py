# Generated by Django 5.0.6 on 2024-08-20 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_mess_fee_payment_college'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='mess_fee_payment',
            constraint=models.UniqueConstraint(fields=('registration_details', 'from_date', 'to_date', 'fee_type'), name='unique_mess_fee_per_period'),
        ),
    ]
