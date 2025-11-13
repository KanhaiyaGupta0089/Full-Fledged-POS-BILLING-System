"""
Purchase Orders & Supplier Management with Maximum Automation
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from accounts.models import User
from inventory.models import Warehouse


class Supplier(models.Model):
    """Supplier/Vendor model"""
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    gstin = models.CharField(max_length=15, blank=True)
    pan = models.CharField(max_length=10, blank=True)
    
    # Payment Terms
    payment_terms = models.CharField(max_length=100, blank=True, 
                                    help_text="e.g., Net 30, Net 60, COD")
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Performance Tracking
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_orders = models.IntegerField(default=0)
    average_delivery_time = models.IntegerField(default=0, 
                                                help_text="Average delivery time in days")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('5.00'),
                                 validators=[MinValueValidator(Decimal('0.00'))])
    
    # Status
    is_active = models.BooleanField(default=True)
    is_preferred = models.BooleanField(default=False, help_text="Preferred supplier")
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_preferred']),
        ]
    
    def __str__(self):
        return self.name or self.company_name


class PurchaseOrder(models.Model):
    """Purchase Order model with automation"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent to Supplier'),
        ('partially_received', 'Partially Received'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='purchase_orders')
    
    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                       validators=[MinValueValidator(Decimal('0.00'))])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Automation flags
    auto_create_on_low_stock = models.BooleanField(default=False,
                                                    help_text="Auto-created when stock is low")
    auto_approve = models.BooleanField(default=False, help_text="Auto-approve PO")
    
    # Notes
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Internal notes not visible to supplier")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pos')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_pos')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['supplier']),
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
        ]
    
    def __str__(self):
        return f"PO-{self.po_number}"
    
    def save(self, *args, **kwargs):
        """Auto-generate PO number and auto-approve if enabled"""
        if not self.po_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_po = PurchaseOrder.objects.filter(po_number__startswith=f'PO-{date_str}').order_by('-po_number').first()
            if last_po:
                try:
                    last_num = int(last_po.po_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.po_number = f"PO-{date_str}-{new_num:04d}"
        
        # Auto-approve if enabled
        if self.auto_approve and self.status == 'draft':
            self.status = 'approved'
            if not self.approved_at:
                from django.utils import timezone
                self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Purchase Order line items"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='po_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    validators=[MinValueValidator(Decimal('0.00'))])
    received_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'purchase_order_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def pending_quantity(self):
        """Calculate pending quantity"""
        return self.quantity - self.received_quantity
    
    @property
    def is_fully_received(self):
        """Check if item is fully received"""
        return self.received_quantity >= self.quantity
    
    def save(self, *args, **kwargs):
        """Calculate totals"""
        subtotal = self.unit_price * self.quantity
        after_discount = subtotal - self.discount
        tax = (after_discount * self.tax_rate) / 100
        self.total = after_discount + tax
        super().save(*args, **kwargs)


class GoodsReceiptNote(models.Model):
    """GRN - Goods Receipt Note (Auto-created when PO items are received)"""
    grn_number = models.CharField(max_length=50, unique=True, blank=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='grns')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='grns')
    
    # Totals
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[MinValueValidator(Decimal('0.00'))])
    
    # Status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='verified_grns')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    quality_check_notes = models.TextField(blank=True)
    
    # Metadata
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_grns')
    received_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'goods_receipt_notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['grn_number']),
            models.Index(fields=['purchase_order']),
        ]
    
    def __str__(self):
        return f"GRN-{self.grn_number}"
    
    def save(self, *args, **kwargs):
        """Auto-generate GRN number"""
        if not self.grn_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_grn = GoodsReceiptNote.objects.filter(grn_number__startswith=f'GRN-{date_str}').order_by('-grn_number').first()
            if last_grn:
                try:
                    last_num = int(last_grn.grn_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.grn_number = f"GRN-{date_str}-{new_num:04d}"
        super().save(*args, **kwargs)


class GRNItem(models.Model):
    """GRN line items"""
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='grn_items', help_text="Related PO item (optional)")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_received = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    validators=[MinValueValidator(Decimal('0.00'))])
    batch_number = models.CharField(max_length=100, blank=True, help_text="Batch/Lot number")
    expiry_date = models.DateField(null=True, blank=True, help_text="Product expiry date")
    
    # Quality Check
    is_quality_approved = models.BooleanField(default=True)
    quality_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'grn_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity_received}"


class SupplierPayment(models.Model):
    """Track supplier payments"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('credit', 'Credit'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='payments')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.00'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True,
                                       help_text="Cheque number, Transaction ID, etc.")
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'supplier_payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['supplier', 'payment_date']),
        ]
    
    def __str__(self):
        return f"{self.supplier.name} - {self.amount}"

