# Generated by Django 5.0.6 on 2024-06-02 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_bonafide_roll_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(blank=True, max_length=225, null=True, verbose_name='subject')),
                ('subject_code', models.CharField(blank=True, max_length=30, null=True, verbose_name='subject_id')),
            ],
        ),
        migrations.AddField(
            model_name='bonafide',
            name='applied_date',
            field=models.DateField(blank=True, null=True, verbose_name='applied date'),
        ),
    ]
