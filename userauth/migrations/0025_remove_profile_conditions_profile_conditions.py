# Generated by Django 5.0.6 on 2025-01-21 02:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0024_remove_profile_block_preference_alter_block_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='conditions',
        ),
        migrations.AddField(
            model_name='profile',
            name='conditions',
            field=models.ForeignKey(blank=True, help_text='Select your condition(s) from the list', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='userauth.condition'),
        ),
    ]
