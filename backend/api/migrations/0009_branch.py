# Generated by Django 5.0.6 on 2024-08-09 11:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_bonafide_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Branch_name', models.CharField(blank=True, max_length=225, null=True)),
                ('college', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.college')),
            ],
        ),
    ]
