import random
import logging
import time
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp, purpose='registration'):
    """
    Send OTP email with retry logic and comprehensive error handling.
    
    Args:
        email: Recipient email address (accepts all domains)
        otp: 6-digit OTP code
        purpose: 'registration' or 'password_reset'
    
    Returns:
        bool: True if email sent successfully, raises exception otherwise
    """
    # Email subject based on purpose
    if purpose == 'password_reset':
        subject = f'Password Reset Code: {otp}'
        action = 'reset your password'
    else:
        subject = f'Email Verification Code: {otp}'
        action = 'complete your registration'
    
    # Professional HTML email template
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 30px;
                color: white;
            }}
            .otp-box {{
                background: rgba(255, 255, 255, 0.95);
                color: #333;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin: 20px 0;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
                color: #667eea;
                margin: 10px 0;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 14px;
                opacity: 0.9;
            }}
            .warning {{
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 5px;
                margin-top: 15px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="margin-top: 0;">VoteHub</h2>
            <p>Hello,</p>
            <p>You requested to {action}. Please use the verification code below:</p>
            
            <div class="otp-box">
                <p style="margin: 0; font-size: 14px; color: #666;">Your Verification Code</p>
                <div class="otp-code">{otp}</div>
                <p style="margin: 0; font-size: 12px; color: #999;">Valid for 10 minutes</p>
            </div>
            
            <p>Enter this code on the verification page to continue.</p>
            
            <div class="warning">
                <strong>⚠️ Security Notice:</strong><br>
                If you did not request this code, please ignore this email. Do not share this code with anyone.
            </div>
            
            <div class="footer">
                <p>This is an automated message from VoteHub.<br>
                Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    # Plain text fallback
    plain_message = f'''
VoteHub - Verification Code

Hello,

You requested to {action}.
Your verification code is: {otp}

Please use this code to verify your email and continue.
This code will expire in 10 minutes.

SECURITY NOTICE:
If you did not request this code, please ignore this email.
Do not share this code with anyone.

---
This is an automated message from VoteHub.
Please do not reply to this email.
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # Retry logic: Try up to 3 times with exponential backoff
    max_retries = 3
    retry_delay = 1  # Start with 1 second
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Sending OTP to {email} (attempt {attempt + 1}/{max_retries})")
            
            # Create email message with both HTML and plain text
            email_message = EmailMessage(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=[email],
            )
            email_message.content_subtype = 'html'  # Set primary content to HTML
            email_message.body = html_message
            
            # Send email with timeout
            email_message.send(fail_silently=False)
            
            logger.info(f"OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed to send OTP to {email}: {str(e)}")
            
            # If this was the last attempt, raise the exception
            if attempt == max_retries - 1:
                logger.error(f"All {max_retries} attempts failed for {email}")
                raise Exception(
                    f"Failed to send email after {max_retries} attempts. "
                    f"Please check your email address and try again. "
                    f"Error: {str(e)}"
                )
            
            # Wait before retrying (exponential backoff)
            time.sleep(retry_delay)
            retry_delay *= 2  # Double the delay for next attempt
    
    return False
