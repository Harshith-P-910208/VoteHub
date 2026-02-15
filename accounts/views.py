from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import LoginForm
from .models import User
from .utils import generate_otp, send_otp_email
import base64
import time
from django.core.files.base import ContentFile



def landing(request):
    """
    Landing page that displays both Student and Admin login forms side-by-side.
    """
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')
    
    form = LoginForm()
    return render(request, 'landing.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        student_id = request.POST.get('student_id')
        
        # Simple validation
        if not email or not full_name or not student_id:
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/register.html')

        if not email.endswith('@sfscollege.in'):
            messages.error(request, 'Please enter a valid college ID (@sfscollege.in)')
            return render(request, 'accounts/register.html')

        if not student_id.isalnum() or not (12 <= len(student_id) <= 14):
            messages.error(request, 'Student ID must be a 12-14 character alphanumeric UUCMS number.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'accounts/register.html')

        # Generate OTP
        otp = generate_otp()
        
        # Store registration data in session
        registration_data = {
            'email': email,
            'full_name': full_name,
            'student_id': student_id,
            'otp': otp,
            'timestamp': time.time(),
        }
        request.session['registration_data'] = registration_data
        
        # Send OTP
        try:
            send_otp_email(email, otp)
            messages.success(request, f'An OTP has been sent to {email}.')
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
    
    return render(request, 'accounts/register.html')


def verify_otp(request):
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, 'Session expired. Please start registration again.')
        return redirect('register')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        if otp_input == registration_data['otp']:
            messages.success(request, 'OTP verified! Please set your password.')
            return redirect('set_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'accounts/verify_otp.html', {'email': registration_data['email']})


def set_password(request):
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, 'Session expired. Please start registration again.')
        return redirect('register')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        image_data = request.POST.get('voter_image') # Using the same key as voting for consistency
        
        if not image_data:
            messages.error(request, 'Please capture your profile photo.')
            return render(request, 'accounts/set_password.html')
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/set_password.html')
        
        try:
            # Enforce Django password validation
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'accounts/set_password.html')
            
        try:
            # Create user with Base64 image directly
            user = User.objects.create_user(
                email=registration_data['email'],
                password=password,
                full_name=registration_data['full_name'],
                student_id=registration_data['student_id'],
                profile_image_base64=image_data
            )
            
            # Clear session
            del request.session['registration_data']
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            
    return render(request, 'accounts/set_password.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP for reset
            otp = generate_otp()
            request.session['reset_data'] = {
                'email': email,
                'otp': otp,
                'timestamp': time.time()
            }
            
            # Send OTP
            send_otp_email(email, otp, purpose='password_reset')
            messages.success(request, f'A reset code has been sent to {email}.')
            return redirect('verify_reset_otp')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            
    return render(request, 'accounts/forgot_password.html')


def verify_reset_otp(request):
    reset_data = request.session.get('reset_data')
    if not reset_data:
        messages.error(request, 'Session expired. Please request a reset again.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        if otp_input == reset_data['otp']:
            messages.success(request, 'OTP verified! Set your new password.')
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP.')
            
    return render(request, 'accounts/verify_reset_otp.html', {'email': reset_data['email']})


def reset_password(request):
    reset_data = request.session.get('reset_data')
    if not reset_data:
        messages.error(request, 'Session expired. Please request a reset again.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/reset_password.html')
            
        try:
            # Enforce Django password validation
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'accounts/reset_password.html')
            
        try:
            user = User.objects.get(email=reset_data['email'])
            user.set_password(password)
            user.save()
            
            # Clear session
            del request.session['reset_data']
            
            messages.success(request, 'Password reset successful! You can now login.')
            
            # Redirect based on user type
            if user.is_admin:
                return redirect('admin_login')
            else:
                return redirect('login')
                
        except Exception as e:
            messages.error(request, f'Error resetting password: {e}')
            
    return render(request, 'accounts/reset_password.html')
            
def resend_otp(request):
    """Handles resending OTP for both registration and password reset"""
    # Check registration flow
    registration_data = request.session.get('registration_data')
    reset_data = request.session.get('reset_data')
    
    current_time = time.time()
    data = registration_data or reset_data
    
    if not data:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('login')
        
    last_sent = data.get('timestamp', 0)
    wait_time = 60 - int(current_time - last_sent)
    
    if wait_time > 0:
        messages.error(request, f'Please wait {wait_time} seconds before resending.')
        return redirect('verify_otp' if registration_data else 'verify_reset_otp')
        
    # Generate new OTP and update timestamp
    new_otp = generate_otp()
    data['otp'] = new_otp
    data['timestamp'] = current_time
    
    if registration_data:
        request.session['registration_data'] = data
    else:
        request.session['reset_data'] = data
        
    try:
        # Determine purpose based on which flow we're in
        purpose = 'registration' if registration_data else 'password_reset'
        send_otp_email(data['email'], new_otp, purpose=purpose)
        messages.success(request, f'A new OTP has been sent to {data["email"]}.')
    except Exception as e:
        messages.error(request, f'Error sending email: {e}')
        
    return redirect('verify_otp' if registration_data else 'verify_reset_otp')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            auth_logout(request)
            messages.info(request, 'Please login with a Student account.')
            return redirect('login')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    if not user.is_admin:
                        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('student_dashboard')
                    else:
                        messages.error(request, 'Admins must use the dedicated Admin Portal.')
                        return redirect('login')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        auth_logout(request)
        messages.info(request, 'Please login with an Admin account.')
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    if user.is_admin:
                        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('admin_dashboard')
                    else:
                        messages.error(request, 'Access Denied: Student accounts must use the Student Login.')
                        return redirect('admin_login')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/admin_login.html', {'form': form})



def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
@require_POST
def update_location(request):
    """AJAX endpoint to update user's location"""
    try:
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        city = request.POST.get('city', '')
        country = request.POST.get('country', '')
        
        if not latitude or not longitude:
            return JsonResponse({'success': False, 'error': 'Missing location data'}, status=400)
        
        # Update user's location
        user = request.user
        user.latitude = float(latitude)
        user.longitude = float(longitude)
        user.city = city
        user.country = country
        user.last_location_update = timezone.now()
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Location updated successfully',
            'location': {
                'city': city,
                'country': country,
                'latitude': latitude,
                'longitude': longitude
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

