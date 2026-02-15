import os
import sys
from pathlib import Path
import django

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

from accounts.models import User

try:
    if not User.objects.filter(email='admin@sfscollege.in').exists():
        User.objects.create_superuser(
            email='admin@sfscollege.in',
            password='admin123',
            full_name='System Admin',
            student_id='ADMIN001'
        )
        print("Superuser created successfully.")
    else:
        print("Superuser already exists.")
except Exception as e:
    print(f"Error creating superuser: {e}")
