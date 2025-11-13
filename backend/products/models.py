from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from datetime import datetime


class Category(models.Model):
    """Product categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Brand(models.Model):
    """Product brands"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'brands'
        ordering = ['name']


class Product(models.Model):
    """Product model with all necessary fields"""
    # Basic Information
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True, blank=True, help_text="Stock Keeping Unit - Auto-generated if not provided")
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    qr_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost price of the product"
    )
    selling_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Selling price of the product"
    )
    
    # Stock Information
    current_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_stock_level = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Minimum stock level for alerts")
    max_stock_level = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Maximum stock level")
    
    # Product Details
    unit = models.CharField(max_length=20, default='pcs', help_text="Unit of measurement (pcs, kg, liter, etc.)")
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, help_text="Length x Width x Height")
    
    # Images
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    additional_images = models.JSONField(default=list, blank=True, help_text="List of additional image URLs")
    
    # Tax Information
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Tax rate in percentage"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_trackable = models.BooleanField(default=True, help_text="Track inventory for this product")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_products'
    )
    
    def save(self, *args, **kwargs):
        """Auto-generate SKU, barcode, and QR code if not provided"""
        if not self.sku:
            # Generate SKU: PROD-YYYYMMDD-XXXX
            date_prefix = datetime.now().strftime('%Y%m%d')
            unique_suffix = str(uuid.uuid4())[:8].upper()
            self.sku = f"PROD-{date_prefix}-{unique_suffix}"
            # Ensure uniqueness
            while Product.objects.filter(sku=self.sku).exists():
                unique_suffix = str(uuid.uuid4())[:8].upper()
                self.sku = f"PROD-{date_prefix}-{unique_suffix}"
        
        if not self.barcode:
            # Generate barcode: BAR-XXXXXXXX (8 chars from UUID)
            barcode_suffix = str(uuid.uuid4())[:8].upper()
            self.barcode = f"BAR-{barcode_suffix}"
            # Ensure uniqueness
            while Product.objects.filter(barcode=self.barcode).exists():
                barcode_suffix = str(uuid.uuid4())[:8].upper()
                self.barcode = f"BAR-{barcode_suffix}"
        
        if not self.qr_code:
            # Generate QR code: QR-XXXXXXXX (8 chars from UUID)
            qr_suffix = str(uuid.uuid4())[:8].upper()
            self.qr_code = f"QR-{qr_suffix}"
            # Ensure uniqueness
            while Product.objects.filter(qr_code=self.qr_code).exists():
                qr_suffix = str(uuid.uuid4())[:8].upper()
                self.qr_code = f"QR-{qr_suffix}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.current_stock <= self.min_stock_level
    
    @property
    def stock_status(self):
        """Get stock status"""
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        elif self.current_stock >= self.max_stock_level:
            return 'overstock'
        return 'in_stock'
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
        

