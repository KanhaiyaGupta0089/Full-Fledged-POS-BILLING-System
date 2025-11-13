"""
Billing and Invoice models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from accounts.models import User
from discounts.models import Coupon


class Customer(models.Model):
    """Enhanced Customer model with loyalty and tracking"""
    CUSTOMER_TYPES = [
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('wholesale', 'Wholesale'),
        ('retail', 'Retail'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True, unique=True, null=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    gstin = models.CharField(max_length=15, blank=True, help_text="GST Identification Number")
    pan = models.CharField(max_length=10, blank=True, help_text="PAN Number")
    
    # Customer Classification
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='regular')
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                      help_text="Maximum credit amount allowed")
    
    # Loyalty Program
    loyalty_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_orders = models.IntegerField(default=0)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    
    # Customer Details
    date_of_birth = models.DateField(null=True, blank=True)
    anniversary_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes about customer")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_blacklisted = models.BooleanField(default=False, help_text="Blacklist customer if needed")
    blacklist_reason = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['customer_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def lifetime_value(self):
        """Calculate customer lifetime value"""
        return self.total_purchases
    
    @property
    def average_order_value(self):
        """Calculate average order value"""
        if self.total_orders > 0:
            return self.total_purchases / self.total_orders
        return Decimal('0.00')
    
    @property
    def current_credit_balance(self):
        """Get current credit balance from credit ledger"""
        try:
            from credit_ledger.models import CustomerCredit
            credit = CustomerCredit.objects.get(customer=self)
            return credit.balance
        except:
            return Decimal('0.00')
    
    def add_loyalty_points(self, points):
        """Add loyalty points"""
        self.loyalty_points += points
        self.save(update_fields=['loyalty_points'])
    
    def redeem_loyalty_points(self, points):
        """Redeem loyalty points"""
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            self.save(update_fields=['loyalty_points'])
            return True
        return False


class Invoice(models.Model):
    """Invoice/Bill model"""
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('credit', 'Credit (Udhar)'),
        ('mixed', 'Mixed'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Auto-generated if not provided")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='invoices')
    customer_name = models.CharField(max_length=200, blank=True, 
                                   help_text="Walk-in customer name")
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_email = models.EmailField(blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                      validators=[MinValueValidator(Decimal('0.00'))])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Discounts
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='invoices')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='pending')
    
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def save(self, *args, **kwargs):
        """Calculate balance amount"""
        self.balance_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Invoice line items"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='invoice_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                   validators=[MinValueValidator(Decimal('0.00'))])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, 
                               validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'invoice_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate totals"""
        # Calculate subtotal
        subtotal = self.unit_price * self.quantity
        # Apply discount
        after_discount = subtotal - self.discount
        # Calculate tax
        self.tax_amount = (after_discount * self.tax_rate) / 100
        # Calculate total
        self.total = after_discount + self.tax_amount
        super().save(*args, **kwargs)

