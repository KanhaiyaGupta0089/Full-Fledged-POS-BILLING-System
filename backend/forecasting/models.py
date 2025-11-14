"""
Sales Forecasting & Demand Planning Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product
from inventory.models import Warehouse


class SalesForecast(models.Model):
    """Sales forecast for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecasts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='forecasts', null=True, blank=True)
    
    # Forecast Period
    forecast_date = models.DateField()
    period_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='monthly')
    
    # Forecast Values
    predicted_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    predicted_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'),
                                          help_text="Confidence level (0-100)")
    
    # Actual Values (filled after period ends)
    actual_quantity = models.IntegerField(null=True, blank=True)
    actual_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Forecast Method
    forecast_method = models.CharField(max_length=50, blank=True,
                                      help_text="Method used for forecasting (e.g., 'moving_average', 'exponential_smoothing')")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_forecasts'
        ordering = ['-forecast_date']
        unique_together = ['product', 'warehouse', 'forecast_date', 'period_type']
        indexes = [
            models.Index(fields=['product', 'forecast_date']),
            models.Index(fields=['warehouse', 'forecast_date']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.forecast_date}"
    
    @property
    def accuracy(self):
        """Calculate forecast accuracy"""
        if self.actual_quantity and self.predicted_quantity:
            if self.actual_quantity > 0:
                error = abs(self.actual_quantity - self.predicted_quantity) / self.actual_quantity
                return (1 - error) * 100
        return None


class DemandPattern(models.Model):
    """Product demand patterns and trends"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='demand_patterns')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='demand_patterns', null=True, blank=True)
    
    # Pattern Analysis
    trend = models.CharField(max_length=20, choices=[
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing'),
        ('stable', 'Stable'),
        ('seasonal', 'Seasonal'),
    ], blank=True)
    
    seasonality_factor = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            help_text="Seasonality multiplier")
    
    # Statistics
    average_daily_sales = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    average_weekly_sales = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    average_monthly_sales = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Lead Time
    average_lead_time = models.IntegerField(default=0, help_text="Average lead time in days")
    
    # Safety Stock Recommendation
    recommended_safety_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    recommended_reorder_point = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    recommended_order_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Metadata
    last_analyzed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'demand_patterns'
        unique_together = ['product', 'warehouse']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['trend']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.trend}"


class OptimalStockLevel(models.Model):
    """Optimal stock level recommendations"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='optimal_stock_levels')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='optimal_stock_levels')
    
    # Recommendations
    optimal_min_stock = models.IntegerField(validators=[MinValueValidator(0)])
    optimal_max_stock = models.IntegerField(validators=[MinValueValidator(0)])
    optimal_reorder_point = models.IntegerField(validators=[MinValueValidator(0)])
    optimal_reorder_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Current vs Optimal
    current_stock = models.IntegerField(default=0)
    stock_status = models.CharField(max_length=20, choices=[
        ('optimal', 'Optimal'),
        ('low', 'Low'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='optimal')
    
    # Calculation Method
    calculation_method = models.CharField(max_length=50, blank=True)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'optimal_stock_levels'
        unique_together = ['product', 'warehouse']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['stock_status']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.stock_status}"





