import os
import sys
from pathlib import Path
import django

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

from accounts.models import User

email = 'harshithp_043@sfscollege.in'

try:
    user = User.objects.get(email=email)
    user.is_admin = True
    user.save()
    print(f"SUCCESS: {email} is now an Admin!")
except User.DoesNotExist:
    print(f"ERROR: User {email} not found. Please register first.")
except Exception as e:
    print(f"ERROR: {e}")
