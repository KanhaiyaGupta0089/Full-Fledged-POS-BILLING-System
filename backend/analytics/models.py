"""
Analytics models
"""
from django.db import models
from django.utils import timezone


class AnalyticsCache(models.Model):
    """Cache for analytics data"""
    cache_key = models.CharField(max_length=100, unique=True)
    data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_cache'
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return self.cache_key
    
    def is_expired(self):
        """Check if cache is expired"""
        return timezone.now() > self.expires_at







