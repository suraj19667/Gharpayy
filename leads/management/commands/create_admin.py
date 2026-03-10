"""Create admin superuser for production deployment."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Create admin superuser if it does not exist'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@gharpayy.com')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(f'✓ Superuser created: {username}'))
            else:
                # Update password if user exists (useful for production)
                user = User.objects.get(username=username)
                user.set_password(password)
                user.email = email
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Superuser updated: {username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating superuser: {str(e)}'))
            raise
