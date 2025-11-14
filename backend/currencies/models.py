"""
Multi-Currency Support
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Currency(models.Model):
    """Currency model"""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code (e.g., USD, INR, EUR)")
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, help_text="Currency symbol (e.g., $, ₹, €)")
    is_base_currency = models.BooleanField(default=False, help_text="Base currency for the system")
    is_active = models.BooleanField(default=True)
    decimal_places = models.IntegerField(default=2, validators=[MinValueValidator(0)])
    
    # Exchange Rate
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('1.000000'),
                                       help_text="Exchange rate relative to base currency")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'currencies'
        verbose_name_plural = 'Currencies'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} ({self.symbol})"
    
    def convert_to_base(self, amount):
        """Convert amount to base currency"""
        if self.is_base_currency:
            return amount
        return amount * self.exchange_rate
    
    def convert_from_base(self, amount):
        """Convert amount from base currency"""
        if self.is_base_currency:
            return amount
        if self.exchange_rate > 0:
            return amount / self.exchange_rate
        return Decimal('0.00')


class ExchangeRateHistory(models.Model):
    """Historical exchange rates"""
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rate_history')
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    date = models.DateField()
    source = models.CharField(max_length=100, blank=True, help_text="Source of exchange rate (e.g., API, Manual)")
    
    class Meta:
        db_table = 'exchange_rate_history'
        ordering = ['-date']
        unique_together = ['currency', 'date']
        indexes = [
            models.Index(fields=['currency', 'date']),
        ]
    
    def __str__(self):
        return f"{self.currency.code} - {self.rate} on {self.date}"





