"""
Day Book models - Auto-generated daily transaction records
"""
from django.db import models
from decimal import Decimal


class DayBookEntry(models.Model):
    """Day Book entry - auto-generated from invoices"""
    ENTRY_TYPES = [
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('payment', 'Payment'),
        ('credit', 'Credit'),
        ('expense', 'Expense'),
    ]
    
    date = models.DateField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='daybook_entries')
    description = models.CharField(max_length=500)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daybook_entries'
        ordering = ['date', 'created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['entry_type']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.entry_type}: {self.description}"

