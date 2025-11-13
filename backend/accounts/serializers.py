"""
Accounts serializers
"""
from rest_framework import serializers
from django.utils import timezone
from .models import User, Attendance


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'phone', 'address',
            'employee_id', 'is_active', 'date_joined', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }


class AttendanceSerializer(serializers.ModelSerializer):
    """Attendance serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    total_duration_display = serializers.SerializerMethodField()
    login_time_display = serializers.SerializerMethodField()
    logout_time_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'user_name', 'date', 'login_time', 'logout_time',
            'login_time_display', 'logout_time_display',
            'total_duration', 'total_duration_display', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_duration_display(self, obj):
        """Format duration as hours:minutes"""
        if obj.total_duration:
            total_seconds = int(obj.total_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"
    
    def get_login_time_display(self, obj):
        """Format login time in local timezone"""
        if obj.login_time:
            local_time = timezone.localtime(obj.login_time)
            return local_time.strftime('%I:%M %p')
        return None
    
    def get_logout_time_display(self, obj):
        """Format logout time in local timezone"""
        if obj.logout_time:
            local_time = timezone.localtime(obj.logout_time)
            return local_time.strftime('%I:%M %p')
        return None
