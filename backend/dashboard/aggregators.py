from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from inventory.models import Stock
from billing.models import Invoice, InvoiceItem
from accounts.models import Attendance

def get_admin_dashboard_stats():
    """Get statistics for admin dashboard"""
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Total sales (this month) - Only paid and partial invoices
    total_sales = Invoice.objects.filter(
        created_at__date__gte=this_month_start,
        status__in=['paid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Last month sales for growth calculation - Only paid and partial invoices
    last_month_sales = Invoice.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end,
        status__in=['paid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate growth
    if last_month_sales > 0:
        growth = ((total_sales - last_month_sales) / last_month_sales) * 100
    else:
        growth = 0 if total_sales == 0 else 100
    
    # Total orders (this month) - Only paid and partial invoices
    total_orders = Invoice.objects.filter(
        created_at__date__gte=this_month_start,
        status__in=['paid', 'partial']
    ).count()
    
    # Total products
    total_products = Product.objects.count()
    
    # Low stock items
    low_stock = Product.objects.filter(
        is_active=True,
        is_trackable=True,
        current_stock__lte=F('min_stock_level')
    ).count()
    
    # Sales data for last 7 days - Only paid and partial invoices
    sales_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_sales = Invoice.objects.filter(
            created_at__date=date,
            status__in=['paid', 'partial']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        day_orders = Invoice.objects.filter(
            created_at__date=date,
            status__in=['paid', 'partial']
        ).count()
        sales_data.append({
            'name': date.strftime('%a'),
            'sales': float(day_sales),
            'orders': day_orders,
        })
    
    # Top selling products (by revenue) - Only paid and partial invoices
    top_products = InvoiceItem.objects.filter(
        invoice__created_at__date__gte=this_month_start,
        invoice__status__in=['paid', 'partial']
    ).values('product__id', 'product__name').annotate(
        total_revenue=Sum('total'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')[:5]
    
    return {
        'total_sales': float(total_sales),
        'total_orders': total_orders,
        'total_products': total_products,
        'low_stock': low_stock,
        'growth': round(growth, 2),
        'sales_data': sales_data,
        'top_products': list(top_products),
    }

def get_owner_dashboard_stats():
    """Get statistics for owner dashboard - Consistent with admin dashboard"""
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # This month revenue - Only paid and partial invoices
    this_month_revenue = Invoice.objects.filter(
        created_at__date__gte=this_month_start,
        status__in=['paid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Last month revenue - Only paid and partial invoices
    last_month_revenue = Invoice.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end,
        status__in=['paid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate growth
    if last_month_revenue > 0:
        growth = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
    else:
        growth = 0 if this_month_revenue == 0 else 100
    
    # Calculate actual profit from invoice items
    from billing.models import InvoiceItem
    from django.db.models import ExpressionWrapper, DecimalField
    
    invoice_items = InvoiceItem.objects.filter(
        invoice__created_at__date__gte=this_month_start,
        invoice__status__in=['paid', 'partial']
    )
    
    total_revenue = invoice_items.aggregate(total=Sum('total'))['total'] or 0
    total_cost = invoice_items.filter(
        product__cost_price__gt=0
    ).aggregate(
        total_cost=Sum(
            ExpressionWrapper(
                F('quantity') * F('product__cost_price'),
                output_field=DecimalField()
            )
        )
    )['total_cost'] or 0
    
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'total_revenue': float(this_month_revenue),
        'profit': float(total_profit),
        'profit_margin': round(profit_margin, 2),
        'growth': round(growth, 2),
    }

def get_manager_dashboard_stats():
    """Get statistics for manager dashboard - Consistent filtering"""
    today = timezone.now().date()
    
    # Today's sales - Only paid and partial invoices
    today_sales = Invoice.objects.filter(
        created_at__date=today,
        status__in=['paid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Low stock items
    low_stock_items = Product.objects.filter(
        is_active=True,
        is_trackable=True,
        current_stock__lte=F('min_stock_level')
    ).select_related('category', 'brand')
    
    # Pending orders (invoices with pending status)
    pending_orders = Invoice.objects.filter(
        status='pending'
    ).count()
    
    return {
        'total_products': Product.objects.count(),
        'low_stock': low_stock_items.count(),
        'pending_orders': pending_orders,
        'today_sales': float(today_sales),
        'low_stock_items': [
            {
                'name': item.name,
                'current': item.current_stock,
                'min': item.min_stock_level
            }
            for item in low_stock_items[:5]
        ]
    }

def get_employee_dashboard_stats(user=None):
    """Get statistics for employee dashboard - Consistent filtering"""
    today = timezone.now().date()
    
    # Today's bills - Only paid and partial invoices
    today_bills = Invoice.objects.filter(
        created_at__date=today,
        status__in=['paid', 'partial']
    )
    if user:
        today_bills = today_bills.filter(created_by=user)
    
    # Today's revenue
    today_revenue = today_bills.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Items sold today
    items_sold = InvoiceItem.objects.filter(
        invoice__created_at__date=today,
        invoice__in=today_bills
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Recent bills
    recent_bills = today_bills.order_by('-created_at')[:5]
    
    # Get attendance info
    attendance_info = None
    if user:
        try:
            attendance = Attendance.objects.get(user=user, date=today)
            if attendance.is_active and attendance.login_time:
                attendance.total_duration = attendance.calculate_duration()
                attendance.save()
            
            total_seconds = int(attendance.total_duration.total_seconds()) if attendance.total_duration else 0
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            # Convert UTC times to local timezone (Asia/Kolkata) before formatting
            login_time_local = timezone.localtime(attendance.login_time) if attendance.login_time else None
            logout_time_local = timezone.localtime(attendance.logout_time) if attendance.logout_time else None
            
            attendance_info = {
                'login_time': login_time_local.strftime('%I:%M %p') if login_time_local else None,
                'logout_time': logout_time_local.strftime('%I:%M %p') if logout_time_local else None,
                'is_active': attendance.is_active,
                'total_duration': f"{hours}h {minutes}m",
                'total_seconds': total_seconds
            }
        except Attendance.DoesNotExist:
            attendance_info = {
                'login_time': None,
                'logout_time': None,
                'is_active': False,
                'total_duration': '0h 0m',
                'total_seconds': 0
            }
    
    return {
        'bills': today_bills.count(),
        'revenue': float(today_revenue),
        'items': items_sold or 0,
        'attendance': attendance_info,
        'recent_bills': [
            {
                'id': bill.id,
                'customer': bill.customer_name or 'Walk-in Customer',
                'amount': float(bill.total_amount),
                'time': timezone.localtime(bill.created_at).strftime('%I:%M %p')
            }
            for bill in recent_bills
        ]
    }
