import os
import sys
from pathlib import Path
import django

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

from accounts.models import User

def setup_admin(email, password):
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': 'Admin User',
                'student_id': 'ADMIN001',
                'is_admin': True,
                'is_active': True
            }
        )
        
        user.is_admin = True
        user.is_active = True
        user.set_password(password)
        user.save()
        
        if created:
            print(f"SUCCESS: Created new admin user: {email}")
        else:
            print(f"SUCCESS: Updated existing user and promoted to admin: {email}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    setup_admin('harshithpharshithp438@gmail.com', 'Harshith@2003')
