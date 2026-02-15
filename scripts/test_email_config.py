import os
import smtplib
from pathlib import Path
import environ

def test_smtp():
    BASE_DIR = Path(__file__).resolve().parent.parent
    env = environ.Env()
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    
    host = env('EMAIL_HOST', default='smtp.gmail.com')
    port = int(env('EMAIL_PORT', default=587))
    user = env('EMAIL_HOST_USER', default='')
    password = env('EMAIL_HOST_PASSWORD', default='')
    
    print(f"Testing SMTP for {user} at {host}:{port}...")
    
    try:
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(1)
        server.starttls()
        server.login(user, password)
        print("SUCCESS: SMTP Authentication successful!")
        server.quit()
    except Exception as e:
        print(f"FAILURE: SMTP Authentication failed: {e}")

if __name__ == "__main__":
    test_smtp()
