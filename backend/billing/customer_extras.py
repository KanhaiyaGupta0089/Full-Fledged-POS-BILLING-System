"""
Additional Customer-related models (Purchase History, Communications)
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from .models import Customer, Invoice


class CustomerPurchaseHistory(models.Model):
    """Track customer purchase history"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchase_history')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='customer_history')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    items_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customer_purchase_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.invoice.invoice_number}"


class CustomerCommunication(models.Model):
    """Track all customer communications"""
    COMMUNICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('call', 'Phone Call'),
        ('visit', 'In-Store Visit'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='communications')
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'customer_communications'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['customer', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.communication_type}"




