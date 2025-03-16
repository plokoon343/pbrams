# myapp/management/commands/create_superuser_if_not_exists.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Creates a superuser if one does not exist, using environment variables"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not email or not password:
            self.stdout.write("Superuser credentials not provided in environment variables.")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write("Superuser already exists.")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write("Superuser created successfully!")
