# Generated by Django 5.0.6 on 2024-12-20 21:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0003_alter_profile_mobile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='medical_conditions',
            field=models.ManyToManyField(related_name='profiles', to='userauth.medicalcondition'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='registration_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
