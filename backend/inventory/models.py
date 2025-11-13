"""
Inventory management models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from accounts.models import User


class Warehouse(models.Model):
    """Warehouse/Location model"""
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'warehouses'
        ordering = ['name']


class Stock(models.Model):
    """Stock model for tracking inventory"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reserved_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], 
                                            help_text="Quantity reserved for pending orders")
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_updates')
    
    class Meta:
        db_table = 'stocks'
        unique_together = ['product', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Available quantity (total - reserved)"""
        return self.quantity - self.reserved_quantity
    
    @property
    def is_low_stock(self):
        """Check if stock is low - check both Stock quantity and Product current_stock"""
        # Use product's current_stock if available, otherwise use stock quantity
        effective_quantity = self.product.current_stock if self.product else self.quantity
        
        # Determine min stock level - prefer Stock's min_quantity, fallback to Product's min_stock_level
        min_stock = self.min_quantity if self.min_quantity > 0 else (self.product.min_stock_level if self.product else 0)
        
        # If min_stock is 0, no low stock alert
        if min_stock <= 0:
            return False
        
        # Check if quantity is less than or equal to min stock
        return effective_quantity <= min_stock


class InventoryTransaction(models.Model):
    """Track all inventory movements"""
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('damage', 'Damage'),
        ('expired', 'Expired'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_transactions')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_transactions')
    quantity = models.IntegerField(help_text="Positive for addition, negative for deduction")
    reference_number = models.CharField(max_length=100, blank=True, 
                                        help_text="Invoice ID, Purchase Order, etc.")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.product.name}: {self.quantity}"

