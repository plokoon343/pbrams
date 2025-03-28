# Generated by Django 5.0.6 on 2024-12-20 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0004_alter_profile_medical_conditions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='other_health_challenges',
            field=models.TextField(blank=True, help_text='Describe other health challenges not listed above', null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='medical_conditions',
            field=models.ManyToManyField(blank=True, help_text='Select your medical condition(s) from the list', related_name='profiles', to='userauth.medicalcondition'),
        ),
    ]
