
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

from accounts.models import User

def setup_admin():
    email = "harshithpharshithp438@gmail.com"
    print(f"Checking admin account for {email}...")
    
    try:
        user = User.objects.get(email=email)
        print("User exists.")
        if not user.is_admin:
            print("Upgrading user to admin...")
            user.is_admin = True
            user.save()
            print("User upgraded to admin.")
        else:
            print("User is already an admin.")
            
    except User.DoesNotExist:
        print("User does not exist. Creating admin user...")
        # Create user with unusable password (must use forgot password)
        user = User.objects.create_user(
            email=email,
            password="TemporaryPassword123!", # Valid password initially
            full_name="System Admin",
            student_id="ADMIN001"
        )
        user.is_admin = True
        user.save()
        print("Admin user created successfully.")

if __name__ == "__main__":
    setup_admin()
