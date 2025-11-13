"""
Forecasting Algorithms
Moving Average, Exponential Smoothing, and Seasonal Decomposition
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from billing.models import Invoice, InvoiceItem
from products.models import Product
from inventory.models import Warehouse


class ForecastingAlgorithms:
    """Forecasting algorithms for sales prediction"""
    
    @staticmethod
    def moving_average(product, warehouse=None, period_days=30, window_size=7):
        """
        Calculate moving average forecast
        
        Args:
            product: Product instance
            warehouse: Warehouse instance (optional)
            period_days: Number of days to look back
            window_size: Size of moving average window
        
        Returns:
            dict with forecast data
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # Get historical sales data
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).prefetch_related('items')
        
        # Filter by warehouse if specified
        if warehouse:
            invoices = invoices.filter(items__product=product)
        
        # Get daily sales quantities
        daily_sales = {}
        for invoice in invoices:
            for item in invoice.items.filter(product=product):
                date = invoice.created_at.date()
                if date not in daily_sales:
                    daily_sales[date] = 0
                daily_sales[date] += item.quantity
        
        # Sort by date
        sorted_dates = sorted(daily_sales.keys())
        if len(sorted_dates) < window_size:
            # Not enough data
            return {
                'forecast': 0,
                'confidence': 0,
                'method': 'moving_average',
                'error': 'Insufficient data'
            }
        
        # Calculate moving average
        values = [daily_sales[date] for date in sorted_dates[-window_size:]]
        forecast = sum(values) / len(values)
        
        # Calculate confidence based on data variance
        if len(values) > 1:
            variance = sum((x - forecast) ** 2 for x in values) / len(values)
            confidence = max(0, min(100, 100 - (variance / forecast * 100) if forecast > 0 else 0))
        else:
            confidence = 50
        
        return {
            'forecast': int(forecast),
            'confidence': round(confidence, 2),
            'method': 'moving_average',
            'window_size': window_size,
            'data_points': len(sorted_dates)
        }
    
    @staticmethod
    def exponential_smoothing(product, warehouse=None, period_days=30, alpha=0.3):
        """
        Calculate exponential smoothing forecast
        
        Args:
            product: Product instance
            warehouse: Warehouse instance (optional)
            period_days: Number of days to look back
            alpha: Smoothing factor (0-1)
        
        Returns:
            dict with forecast data
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # Get historical sales data
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).prefetch_related('items')
        
        # Get daily sales quantities
        daily_sales = {}
        for invoice in invoices:
            for item in invoice.items.filter(product=product):
                date = invoice.created_at.date()
                if date not in daily_sales:
                    daily_sales[date] = 0
                daily_sales[date] += item.quantity
        
        # Sort by date
        sorted_dates = sorted(daily_sales.keys())
        if len(sorted_dates) < 2:
            return {
                'forecast': 0,
                'confidence': 0,
                'method': 'exponential_smoothing',
                'error': 'Insufficient data'
            }
        
        # Calculate exponential smoothing
        values = [daily_sales[date] for date in sorted_dates]
        forecast = values[0]  # Initialize with first value
        
        for value in values[1:]:
            forecast = alpha * value + (1 - alpha) * forecast
        
        # Calculate confidence
        errors = [abs(v - forecast) for v in values[-7:]]  # Last 7 days
        avg_error = sum(errors) / len(errors) if errors else 0
        confidence = max(0, min(100, 100 - (avg_error / forecast * 100) if forecast > 0 else 0))
        
        return {
            'forecast': int(forecast),
            'confidence': round(confidence, 2),
            'method': 'exponential_smoothing',
            'alpha': alpha,
            'data_points': len(sorted_dates)
        }
    
    @staticmethod
    def seasonal_decomposition(product, warehouse=None, period_days=90):
        """
        Calculate seasonal decomposition forecast
        
        Args:
            product: Product instance
            warehouse: Warehouse instance (optional)
            period_days: Number of days to look back (should be at least 90 for seasonality)
        
        Returns:
            dict with forecast data
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # Get historical sales data
        invoices = Invoice.objects.filter(
            status__in=['paid', 'partial'],
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).prefetch_related('items')
        
        # Get weekly sales (group by week)
        weekly_sales = {}
        for invoice in invoices:
            for item in invoice.items.filter(product=product):
                week_num = invoice.created_at.isocalendar()[1]  # Week number
                year = invoice.created_at.year
                key = f"{year}-W{week_num}"
                if key not in weekly_sales:
                    weekly_sales[key] = 0
                weekly_sales[key] += item.quantity
        
        if len(weekly_sales) < 4:
            return {
                'forecast': 0,
                'confidence': 0,
                'method': 'seasonal_decomposition',
                'error': 'Insufficient data for seasonality analysis'
            }
        
        # Calculate average weekly sales
        values = list(weekly_sales.values())
        avg_sales = sum(values) / len(values)
        
        # Simple seasonal adjustment (use last 4 weeks average)
        recent_weeks = sorted(weekly_sales.keys())[-4:]
        recent_avg = sum(weekly_sales[w] for w in recent_weeks) / len(recent_weeks)
        
        # Forecast is recent average with trend
        forecast = recent_avg
        
        # Calculate confidence
        variance = sum((v - avg_sales) ** 2 for v in values) / len(values)
        confidence = max(0, min(100, 100 - (variance / avg_sales * 100) if avg_sales > 0 else 0))
        
        return {
            'forecast': int(forecast),
            'confidence': round(confidence, 2),
            'method': 'seasonal_decomposition',
            'seasonality_detected': len(weekly_sales) >= 8,
            'data_points': len(weekly_sales)
        }
    
    @staticmethod
    def generate_forecast(product, warehouse=None, method='moving_average', **kwargs):
        """
        Generate forecast using specified method
        
        Args:
            product: Product instance
            warehouse: Warehouse instance (optional)
            method: 'moving_average', 'exponential_smoothing', or 'seasonal_decomposition'
            **kwargs: Additional parameters for the method
        
        Returns:
            dict with forecast data
        """
        if method == 'moving_average':
            return ForecastingAlgorithms.moving_average(
                product, warehouse,
                kwargs.get('period_days', 30),
                kwargs.get('window_size', 7)
            )
        elif method == 'exponential_smoothing':
            return ForecastingAlgorithms.exponential_smoothing(
                product, warehouse,
                kwargs.get('period_days', 30),
                kwargs.get('alpha', 0.3)
            )
        elif method == 'seasonal_decomposition':
            return ForecastingAlgorithms.seasonal_decomposition(
                product, warehouse,
                kwargs.get('period_days', 90)
            )
        else:
            return {
                'forecast': 0,
                'confidence': 0,
                'method': method,
                'error': 'Unknown method'
            }




