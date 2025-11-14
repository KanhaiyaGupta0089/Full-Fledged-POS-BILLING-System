"""
Credit Ledger (Udhar Khata) models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from billing.models import Customer, Invoice
from accounts.models import User


class CustomerCredit(models.Model):
    """Customer credit account"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='credit_account')
    total_credit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total credit given"
    )
    total_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Outstanding balance"
    )
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_credits'
    
    def __str__(self):
        return f"{self.customer.name} - Balance: ₹{self.balance}"
    
    def save(self, *args, **kwargs):
        """Calculate balance"""
        self.balance = self.total_credit - self.total_paid
        super().save(*args, **kwargs)


class CreditTransaction(models.Model):
    """Credit transaction history"""
    TRANSACTION_TYPES = [
        ('credit', 'Credit Given'),
        ('payment', 'Payment Received'),
        ('adjustment', 'Adjustment'),
    ]
    
    customer_credit = models.ForeignKey(CustomerCredit, on_delete=models.CASCADE, related_name='transactions')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_credit']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"







