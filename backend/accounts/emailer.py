"""
Email templates and functions for accounts app
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to POS System'
    message = f"""
    Hello {user.get_full_name() or user.username},
    
    Welcome to the POS Billing and Inventory System!
    
    Your account has been created with the role: {user.get_role_display()}
    
    Please keep your credentials secure.
    
    Best regards,
    POS System Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, reset_link):
    """Send password reset email"""
    subject = 'Password Reset Request - POS System'
    message = f"""
    Hello {user.get_full_name() or user.username},
    
    You have requested to reset your password.
    
    Click the following link to reset your password:
    {reset_link}
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    POS System Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

