from django.db import models
from accounts.models import User

class DashboardCache(models.Model):
    """Cache dashboard data for performance"""
    user_role = models.CharField(max_length=20)
    cache_key = models.CharField(max_length=100, unique=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_cache'