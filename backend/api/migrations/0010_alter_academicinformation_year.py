# Generated by Django 5.0.6 on 2024-08-09 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinformation',
            name='year',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='year'),
        ),
    ]
