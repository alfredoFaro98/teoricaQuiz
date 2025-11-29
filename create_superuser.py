import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@example.com'
password = 'admin'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully.")
    print(f"Username: {username}")
    print(f"Password: {password}")
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print(f"Superuser '{username}' already exists. Password reset to '{password}'.")
