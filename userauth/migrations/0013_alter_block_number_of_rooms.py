# Generated by Django 5.0.6 on 2025-01-10 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0012_alter_profile_block_preference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='number_of_rooms',
            field=models.PositiveIntegerField(default=30),
        ),
    ]
