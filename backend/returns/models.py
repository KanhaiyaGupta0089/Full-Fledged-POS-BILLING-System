"""
Product Returns models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from billing.models import Invoice, InvoiceItem
from products.models import Product
from accounts.models import User


class Return(models.Model):
    """Product return model"""
    RETURN_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    RETURN_REASONS = [
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item'),
        ('damaged', 'Damaged in Transit'),
        ('not_satisfied', 'Not Satisfied'),
        ('other', 'Other'),
    ]
    
    return_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Auto-generated if not provided")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='returns')
    reason = models.CharField(max_length=20, choices=RETURN_REASONS)
    reason_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS, default='pending')
    
    # Amounts
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    refund_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    refund_method = models.CharField(max_length=20, default='cash', 
                                    choices=[('cash', 'Cash'), ('card', 'Card'), ('credit', 'Credit Note')])
    
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_returns')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_returns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'returns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['return_number']),
            models.Index(fields=['invoice']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Return {self.return_number}"


class ReturnItem(models.Model):
    """Return line items"""
    return_order = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='items')
    invoice_item = models.ForeignKey(InvoiceItem, on_delete=models.PROTECT, related_name='return_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='return_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'return_items'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

