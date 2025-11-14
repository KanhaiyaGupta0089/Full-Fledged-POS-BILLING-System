"""
Advanced Inventory Features with Maximum Automation
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from accounts.models import User
from inventory.models import Warehouse, Stock


class Batch(models.Model):
    """Batch/Lot tracking for products with expiry dates"""
    batch_number = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='batches')
    
    # Batch Details
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    mfg_license = models.CharField(max_length=100, blank=True)
    
    # Stock
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reserved_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Cost Tracking (for FIFO/LIFO)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'batches'
        unique_together = ['batch_number', 'product', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['batch_number']),
        ]
    
    def __str__(self):
        return f"{self.batch_number} - {self.product.name}"
    
    @property
    def available_quantity(self):
        """Available quantity"""
        return self.quantity - self.reserved_quantity
    
    @property
    def is_expired(self):
        """Check if batch is expired"""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False
    
    @property
    def days_to_expiry(self):
        """Days until expiry"""
        if self.expiry_date:
            from django.utils import timezone
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None


class SerialNumber(models.Model):
    """Serial number tracking for products"""
    serial_number = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serial_numbers')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='serial_numbers')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='serial_numbers')
    
    # Status
    is_available = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    sold_invoice = models.ForeignKey('billing.Invoice', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'serial_numbers'
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['product', 'warehouse']),
        ]
    
    def __str__(self):
        return self.serial_number


class StockValuation(models.Model):
    """Stock valuation using different methods"""
    VALUATION_METHODS = [
        ('fifo', 'FIFO (First In First Out)'),
        ('lifo', 'LIFO (Last In First Out)'),
        ('average', 'Weighted Average'),
        ('standard', 'Standard Cost'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='valuations')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='valuations')
    valuation_method = models.CharField(max_length=20, choices=VALUATION_METHODS, default='fifo')
    
    # Valuation
    total_quantity = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Last Calculation
    last_calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_valuations'
        unique_together = ['product', 'warehouse', 'valuation_method']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} ({self.valuation_method})"
    
    def calculate_valuation(self):
        """Calculate stock valuation based on method"""
        from django.db.models import Sum, Avg
        from django.utils import timezone
        
        if self.valuation_method == 'fifo':
            # FIFO: Use oldest batches first
            batches = Batch.objects.filter(
                product=self.product,
                warehouse=self.warehouse,
                is_active=True,
                quantity__gt=0
            ).order_by('created_at')
            
            total_value = Decimal('0.00')
            total_qty = 0
            for batch in batches:
                total_value += batch.unit_cost * batch.quantity
                total_qty += batch.quantity
            
            if total_qty > 0:
                self.average_cost = total_value / total_qty
            else:
                self.average_cost = Decimal('0.00')
            
            self.total_value = total_value
            self.total_quantity = total_qty
            
        elif self.valuation_method == 'lifo':
            # LIFO: Use newest batches first
            batches = Batch.objects.filter(
                product=self.product,
                warehouse=self.warehouse,
                is_active=True,
                quantity__gt=0
            ).order_by('-created_at')
            
            total_value = Decimal('0.00')
            total_qty = 0
            for batch in batches:
                total_value += batch.unit_cost * batch.quantity
                total_qty += batch.quantity
            
            if total_qty > 0:
                self.average_cost = total_value / total_qty
            else:
                self.average_cost = Decimal('0.00')
            
            self.total_value = total_value
            self.total_quantity = total_qty
            
        elif self.valuation_method == 'average':
            # Weighted Average
            batches = Batch.objects.filter(
                product=self.product,
                warehouse=self.warehouse,
                is_active=True,
                quantity__gt=0
            )
            
            total_value = Decimal('0.00')
            total_qty = 0
            for batch in batches:
                total_value += batch.unit_cost * batch.quantity
                total_qty += batch.quantity
            
            if total_qty > 0:
                self.average_cost = total_value / total_qty
            else:
                self.average_cost = Decimal('0.00')
            
            self.total_value = total_value
            self.total_quantity = total_qty
        
        self.last_calculated_at = timezone.now()
        self.save()


class StockAdjustment(models.Model):
    """Stock adjustments (damage, theft, found, etc.)"""
    ADJUSTMENT_TYPES = [
        ('damage', 'Damage'),
        ('theft', 'Theft/Loss'),
        ('found', 'Found'),
        ('expired', 'Expired'),
        ('returned', 'Returned to Supplier'),
        ('other', 'Other'),
    ]
    
    adjustment_number = models.CharField(max_length=50, unique=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    
    # Totals
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Notes
    reason = models.TextField()
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_adjustments')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'stock_adjustments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['adjustment_number']),
            models.Index(fields=['warehouse', 'created_at']),
        ]
    
    def __str__(self):
        return f"ADJ-{self.adjustment_number}"
    
    def save(self, *args, **kwargs):
        """Auto-generate adjustment number"""
        if not self.adjustment_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_adj = StockAdjustment.objects.filter(
                adjustment_number__startswith=f'ADJ-{date_str}'
            ).order_by('-adjustment_number').first()
            if last_adj:
                try:
                    last_num = int(last_adj.adjustment_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.adjustment_number = f"ADJ-{date_str}-{new_num:04d}"
        super().save(*args, **kwargs)


class StockAdjustmentItem(models.Model):
    """Stock adjustment line items"""
    adjustment = models.ForeignKey(StockAdjustment, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(help_text="Positive for addition, negative for deduction")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'stock_adjustment_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate total value"""
        self.total_value = abs(self.quantity) * self.unit_cost
        super().save(*args, **kwargs)


class StockTransfer(models.Model):
    """Stock transfer between warehouses"""
    transfer_number = models.CharField(max_length=50, unique=True, blank=True)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transfers_out')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transfers_in')
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dates
    transfer_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='received_transfers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_transfers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transfer_number']),
            models.Index(fields=['from_warehouse', 'to_warehouse']),
        ]
    
    def __str__(self):
        return f"TRF-{self.transfer_number}"
    
    def save(self, *args, **kwargs):
        """Auto-generate transfer number"""
        if not self.transfer_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_transfer = StockTransfer.objects.filter(
                transfer_number__startswith=f'TRF-{date_str}'
            ).order_by('-transfer_number').first()
            if last_transfer:
                try:
                    last_num = int(last_transfer.transfer_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            self.transfer_number = f"TRF-{date_str}-{new_num:04d}"
        super().save(*args, **kwargs)


class StockTransferItem(models.Model):
    """Stock transfer line items"""
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    received_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'stock_transfer_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class AutoReorderRule(models.Model):
    """Automated reorder rules for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reorder_rules')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reorder_rules')
    
    # Reorder Parameters
    reorder_point = models.IntegerField(validators=[MinValueValidator(0)],
                                       help_text="Stock level at which to reorder")
    reorder_quantity = models.IntegerField(validators=[MinValueValidator(1)],
                                          help_text="Quantity to order when reorder point is reached")
    max_stock_level = models.IntegerField(validators=[MinValueValidator(0)],
                                         help_text="Maximum stock level")
    
    # Automation
    is_active = models.BooleanField(default=True)
    auto_create_po = models.BooleanField(default=False,
                                        help_text="Automatically create PO when reorder point is reached")
    preferred_supplier = models.ForeignKey('purchases.Supplier', on_delete=models.SET_NULL,
                                          null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auto_reorder_rules'
        unique_together = ['product', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Reorder at {self.reorder_point}"
    
    def check_and_reorder(self):
        """Check stock level and create PO if needed"""
        if not self.is_active or not self.auto_create_po:
            return False
        
        try:
            stock = Stock.objects.get(product=self.product, warehouse=self.warehouse)
            if stock.quantity <= self.reorder_point:
                # Create purchase order automatically
                from purchases.models import PurchaseOrder, PurchaseOrderItem
                from purchases.automation import create_auto_po
                return create_auto_po(self)
        except Stock.DoesNotExist:
            pass
        
        return False





