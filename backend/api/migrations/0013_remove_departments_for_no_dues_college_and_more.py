# Generated by Django 5.0.6 on 2024-08-24 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_no_dues_list_college'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='departments_for_no_dues',
            name='college',
        ),
        migrations.AlterField(
            model_name='subject',
            name='subject_code',
            field=models.CharField(max_length=30, null=True, verbose_name='subject_id'),
        ),
    ]
