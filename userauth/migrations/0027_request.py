# Generated by Django 5.0.6 on 2025-01-21 22:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0026_remove_profile_conditions_profile_conditions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('Medical', 'Medical Priority'), ('BUSA', 'BUSA Executive'), ('Other', 'Other')], default='Other', help_text='The priority level of the request', max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Allocated', 'Allocated'), ('Rejected', 'Rejected')], default='Pending', help_text='The status of the request', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('block', models.ForeignKey(help_text='The requested block', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='userauth.block')),
                ('hostel', models.ForeignKey(help_text='The requested hostel', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='userauth.hostel')),
                ('room', models.ForeignKey(help_text='The requested room', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='userauth.room')),
                ('student', models.ForeignKey(help_text='The student making the request', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-priority', 'created_at'],
            },
        ),
    ]
