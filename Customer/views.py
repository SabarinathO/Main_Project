from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django.core.cache import cache
from .models import Customer
import random

ALLOWED_DOMAIN = "cea.ac.in"

# Utility Functions
def validate_email_domain(email):
    """Validate that the email belongs to the allowed domain."""
    if email.split("@")[-1] != ALLOWED_DOMAIN:
        raise ValidationError(f"Only emails ending with @{ALLOWED_DOMAIN} are allowed.")

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Send the OTP to the user's email."""
    subject = "Your Account Verification OTP"
    message = f"Your OTP is {otp}. It is valid for 5 minutes."
    send_mail(subject, message, 'your_email@example.com', [email])

# View for Registration
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # Check if password and confirm password match
        if password != confirm_password:
            return render(request, "signup.html", {"error": "Passwords do not match."})

        try:
            validate_email_domain(email)  # Validate the email domain
        except ValidationError as e:
            return render(request, "signup.html", {"error": str(e)})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists."})

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email is already registered."})

        # Save the user temporarily as inactive without saving to DB yet
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        request.session['phone'] = phone
        request.session['address'] = address

        # Generate OTP and send it to the email
        otp = generate_otp()
        cache.set(f"otp_{email}", otp, timeout=300)  # Store OTP in cache for 5 minutes
        send_otp_email(email, otp)

        return render(request, "otp_verify.html", {"email": email})

    return render(request, "signup.html")

# View for OTP Verification
def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp = request.POST.get("otp")

        # Retrieve OTP from cache
        cached_otp = cache.get(f"otp_{email}")

        if cached_otp and cached_otp == otp:
            # OTP is valid, now store the user credentials in the database
            username = request.session.get('username')
            password = request.session.get('password')
            phone = request.session.get('phone')
            address = request.session.get('address')

            # Create the user and customer
            user = User.objects.create_user(username=username, email=email, password=password, is_active=True)
            user.save()

            customer = Customer(user=user, phone=phone, address=address, name=username)
            customer.save()

            # Clear session data after successful registration
            del request.session['username']
            del request.session['email']
            del request.session['password']
            del request.session['phone']
            del request.session['address']

            # Redirect to login page
            return redirect("signin")

        else:
            # OTP is invalid or expired
            return render(request, "otp_verify.html", {"error": "Invalid OTP.", "email": email})

    return render(request, "otp_verify.html")

# View for Resending OTP
def resend_otp(request):
    email = request.GET.get("email")  # Get the email from the query string

    if email:
        try:
            # Generate a new OTP
            otp = generate_otp()

            # Store the new OTP in the cache for 5 minutes
            cache.set(f"otp_{email}", otp, timeout=300)

            # Send the new OTP to the user's email
            send_otp_email(email, otp)

            # Return a response indicating that the OTP was resent
            return render(request, "otp_verify.html", {"email": email, "success": "OTP has been resent."})

        except Exception as e:
            # Handle any errors
            return render(request, "otp_verify.html", {"error": f"An error occurred: {str(e)}", "email": email})

    return HttpResponseForbidden("Email is required.")


def signin(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email")
        password = request.POST.get("password")

        # Check if the user exists by username or email
        if '@' in username_or_email:  # Email login
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
                return render(request, "signin.html")
        else:  # Username login
            username = username_or_email

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Log the user in
                login(request, user)
                return redirect("main")  
            else:
                messages.error(request, "Your account is not active. Please verify your email.")
                return render(request, "signin.html")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "signin.html")

    return render(request, "signin.html")


def logout(request):
    auth_logout(request)
    return redirect("signin")


