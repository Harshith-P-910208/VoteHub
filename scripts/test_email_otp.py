"""
Email OTP System - Manual Test Script
This script will help you test the email sending functionality directly.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_voting.settings')
django.setup()

from accounts.utils import send_otp_email, generate_otp

def test_email_to_different_domains():
    """Test sending OTP to different email domains"""
    print("=" * 60)
    print("EMAIL OTP SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    print()
    
    # Get email from user
    email = input("Enter your email address to test (any domain): ").strip()
    
    if not email or '@' not in email:
        print("❌ Invalid email address!")
        return
    
    print(f"\n📧 Testing email delivery to: {email}")
    print("-" * 60)
    
    # Generate OTP
    otp = generate_otp()
    print(f"✅ Generated OTP: {otp}")
    
    # Test registration email
    print("\n1️⃣ Testing REGISTRATION email...")
    try:
        send_otp_email(email, otp, purpose='registration')
        print(f"✅ Registration email sent successfully!")
        print(f"   Check your inbox at: {email}")
        print(f"   OTP Code: {otp}")
    except Exception as e:
        print(f"❌ Failed to send registration email: {e}")
        return
    
    # Wait and test password reset email
    input("\n⏸️  Press Enter to test PASSWORD RESET email...")
    
    otp2 = generate_otp()
    print(f"\n2️⃣ Testing PASSWORD RESET email...")
    print(f"✅ Generated new OTP: {otp2}")
    try:
        send_otp_email(email, otp2, purpose='password_reset')
        print(f"✅ Password reset email sent successfully!")
        print(f"   Check your inbox at: {email}")
        print(f"   OTP Code: {otp2}")
    except Exception as e:
        print(f"❌ Failed to send password reset email: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ EMAIL TEST COMPLETED!")
    print("=" * 60)
    print("\n📋 VERIFICATION CHECKLIST:")
    print("   □ Check if emails arrived in inbox (or spam folder)")
    print("   □ Verify emails have professional HTML formatting")
    print("   □ Confirm OTP codes are clearly visible")
    print("   □ Check that emails arrived within 1 minute")
    print("   □ Verify both registration and password reset emails")
    print("\n💡 TIP: If emails are in spam, mark them as 'Not Spam'")
    print()

if __name__ == "__main__":
    test_email_to_different_domains()
