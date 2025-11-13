"""
Accounts models
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """User role model"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_roles'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Custom user model"""
    role = models.CharField(max_length=20, choices=Role.ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Attendance(models.Model):
    """User attendance tracking model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.DurationField(null=True, blank=True, help_text="Total time logged in today")
    is_active = models.BooleanField(default=True, help_text="Currently logged in")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendances'
        unique_together = ['user', 'date']
        ordering = ['-date', '-login_time']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    def calculate_duration(self):
        """Calculate total duration for the day"""
        if not self.login_time:
            return self.total_duration or timedelta(0)
        
        from django.utils import timezone
        from datetime import timedelta
        
        if self.is_active:
            # User is currently logged in - calculate current session + previous sessions
            current_time = timezone.now()
            
            # Determine when the current session started
            if self.total_duration:
                # This is a subsequent session - session started when they logged in again
                # updated_at was set to the login time in the login view
                session_start_time = self.updated_at
            else:
                # First session of the day - session started at login_time
                session_start_time = self.login_time
            
            # Calculate current active session duration
            current_session_duration = current_time - session_start_time
            
            # Add to previous sessions (if any)
            if self.total_duration:
                return self.total_duration + current_session_duration
            else:
                return current_session_duration
        elif self.logout_time:
            # User has logged out - return stored total_duration
            # total_duration should already be calculated and stored in logout view
            return self.total_duration or timedelta(0)
        else:
            # No logout time and not active - return stored duration
            return self.total_duration or timedelta(0)
