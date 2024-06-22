# Generated by Django 5.0.6 on 2024-06-22 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_subject_subject_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='subject',
            field=models.CharField(blank=True, max_length=225, null=True, verbose_name='subject'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='status',
            field=models.CharField(blank=True, choices=[('registered', 'Registered'), ('under investigation', 'Under Investigation'), ('resolved', 'Resolved')], max_length=225, null=True, verbose_name='status'),
        ),
    ]
