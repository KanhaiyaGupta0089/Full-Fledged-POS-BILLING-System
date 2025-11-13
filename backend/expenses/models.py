"""
Expense Management System
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User


class ExpenseCategory(models.Model):
    """Expense categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expense_categories'
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """Expense tracking"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
    ]
    
    expense_number = models.CharField(max_length=50, unique=True, blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    
    # Details
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.00'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    
    # Tax
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    is_tax_deductible = models.BooleanField(default=True, help_text="Can this expense be deducted from tax?")
    
    # Dates
    expense_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    
    # Vendor/Supplier
    vendor_name = models.CharField(max_length=200, blank=True)
    vendor_gstin = models.CharField(max_length=15, blank=True)
    bill_number = models.CharField(max_length=100, blank=True)
    
    # Recurring
    is_recurring = models.BooleanField(default=False)
    recurrence_frequency = models.CharField(max_length=20, blank=True,
                                            choices=[
                                                ('daily', 'Daily'),
                                                ('weekly', 'Weekly'),
                                                ('monthly', 'Monthly'),
                                                ('yearly', 'Yearly'),
                                            ])
    
    # Attachments
    receipt_image = models.ImageField(upload_to='expenses/receipts/', null=True, blank=True)
    bill_document = models.FileField(upload_to='expenses/bills/', null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_expenses')
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_number']),
            models.Index(fields=['category']),
            models.Index(fields=['expense_date']),
            models.Index(fields=['is_recurring']),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate expense number"""
        if not self.expense_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_expense = Expense.objects.filter(
                expense_number__startswith=f'EXP-{date_str}'
            ).order_by('-expense_number').first()
            if last_expense:
                try:
                    last_num = int(last_expense.expense_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.expense_number = f"EXP-{date_str}-{new_num:04d}"
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        """Total amount including tax"""
        return self.amount + self.tax_amount




