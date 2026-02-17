import os
import sys
from pathlib import Path
import django

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

from accounts.models import User

def setup_student(email, password):
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': 'Harshith Student',
                'student_id': 'P03ZW24S126043',
                'is_admin': False,
                'is_active': True
            }
        )
        
        user.is_admin = False
        user.is_active = True
        user.set_password(password)
        user.save()
        
        if created:
            print(f"SUCCESS: Created new student user: {email}")
        else:
            print(f"SUCCESS: Updated existing student user: {email}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Setup the student account the user is trying to use
    setup_student('harshithp_043@sfscollege.in', 'Harshith@2003')
