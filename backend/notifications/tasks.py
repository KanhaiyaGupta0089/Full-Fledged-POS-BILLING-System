"""
Celery tasks for notifications
"""
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count, F
from billing.models import Invoice, InvoiceItem
from products.models import Product
from accounts.models import User
from .emailer import send_daily_summary_email


@shared_task
def send_daily_business_summary():
    """Send daily business summary at 9 AM"""
    today = timezone.now().date()  # Changed from yesterday to today for testing
    
    # Get today's data (for testing)
    invoices = Invoice.objects.filter(
        created_at__date=today,
        status__in=['paid', 'partial']
    )
    
    total_sales = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_invoices = invoices.count()
    
    # Calculate profit
    invoice_items = InvoiceItem.objects.filter(
        invoice__created_at__date=today,
        invoice__status__in=['paid', 'partial']
    )
    
    total_revenue = sum(item.total for item in invoice_items)
    total_cost = sum(
        item.product.cost_price * item.quantity 
        for item in invoice_items 
        if item.product.cost_price
    )
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Top products
    top_products = invoice_items.values('product__name').annotate(
        quantity=Sum('quantity')
    ).order_by('-quantity')[:5]
    
    # Format top products for email (convert product__name to name)
    top_products_formatted = [
        {'name': p['product__name'], 'quantity': p['quantity']}
        for p in top_products
    ]
    
    # Low stock products (get actual list)
    low_stock_products = Product.objects.filter(
        is_active=True,
        is_trackable=True,
        current_stock__lte=F('min_stock_level')
    ).order_by('current_stock', 'name')
    
    low_stock_count = low_stock_products.count()
    
    summary_data = {
        'date': today.isoformat(),
        'total_sales': float(total_sales),
        'total_invoices': total_invoices,
        'total_profit': float(total_profit),
        'profit_margin': round(profit_margin, 2),
        'top_products': top_products_formatted,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products  # Pass the queryset for PDF generation
    }
    
    # Send to admin and owner
    admins = User.objects.filter(role__in=['admin', 'owner'])
    for admin in admins:
        send_daily_summary_email(admin, summary_data)
    
    return f"Daily summary sent to {admins.count()} users"

