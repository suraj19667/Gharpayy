from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'
    
    def ready(self):
        """
        This method is called when Django starts.
        It creates a default admin user if it doesn't exist.
        """
        # Import here to avoid AppRegistryNotReady exception
        from django.contrib.auth.models import User
        from django.db import connection
        from django.db.utils import OperationalError
        import os
        
        # Check if we're running migrations or in a management command
        # We only want to create the user when the server is actually starting
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        try:
            # Check if database tables exist
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'"
                    if 'sqlite' in connection.settings_dict['ENGINE']
                    else "SELECT to_regclass('public.auth_user')"
                )
                if not cursor.fetchone():
                    return
            
            # Get admin credentials from environment variables or use defaults
            username = os.environ.get('ADMIN_USERNAME', 'admin')
            email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            # Check if admin user exists
            if not User.objects.filter(username=username).exists():
                # Create the superuser
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                print(f"✓ Auto-created superuser: {username} (password: {password})")
            else:
                print(f"✓ Superuser '{username}' already exists")
                
        except OperationalError:
            # Database not ready yet (e.g., during first migration)
            pass
        except Exception as e:
            # Don't crash the app if user creation fails
            print(f"⚠ Could not auto-create admin user: {str(e)}")

