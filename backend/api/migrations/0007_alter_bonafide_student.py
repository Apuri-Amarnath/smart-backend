# Generated by Django 5.0.6 on 2024-08-07 10:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_bonafide_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonafide',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonafide_student', to='api.userprofile'),
        ),
    ]
