import os
import sys
from pathlib import Path
import django
from django.conf import settings
from pymongo import MongoClient

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

# Get database connection settings
db_settings = settings.DATABASES['default']
client_settings = db_settings['CLIENT']
host = client_settings['host']

print(f"Connecting to MongoDB...")
client = MongoClient(host)


db_name = db_settings['NAME']
db = client[db_name]

print(f"Connected to database: {db_name}")

# Check migrations
migrations_collection = db['django_migrations']
print(f"Total migrations: {migrations_collection.count_documents({})}")

print("\nApplied migrations for 'accounts':")
for m in migrations_collection.find({'app': 'accounts'}):
    print(f" - {m['name']} (applied: {m['applied']})")

print("\nApplied migrations for 'admin':")
for m in migrations_collection.find({'app': 'admin'}):
    print(f" - {m['name']} (applied: {m['applied']})")

# Fix: If admin.0001 exists but accounts.0001 does not, insert accounts.0001
admin_0001 = migrations_collection.find_one({'app': 'admin', 'name': '0001_initial'})
accounts_0001 = migrations_collection.find_one({'app': 'accounts', 'name': '0001_initial'})

if admin_0001 and not accounts_0001:
    print("\nISSUE DETECTED: admin.0001 applied but accounts.0001 missing.")
    print("Attempting to fix by inserting fake accounts.0001 entry...")
    from django.utils import timezone
    migrations_collection.insert_one({
        'app': 'accounts',
        'name': '0001_initial',
        'applied': timezone.now()
    })
    print("Fix applied. You should now be able to run migrations.")
elif not admin_0001:
    print("\nNo admin.0001 migration found. The error might be different.")
else:
    print("\naccounts.0001 already exists. The inconsistency might be something else.")
