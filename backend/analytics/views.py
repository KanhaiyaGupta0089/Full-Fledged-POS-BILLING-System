"""
Analytics views - AI insights, trending products, low stock alerts
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from products.models import Product
from billing.models import Invoice, InvoiceItem
from inventory.models import Stock
from common.permissions import IsAdminOrManager, IsAdminOrOwner


class AnalyticsViewSet(viewsets.ViewSet):
    """Analytics endpoints"""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    @action(detail=False, methods=['get'])
    def trending_products(self, request):
        """Get trending products (best sellers) - Optimized"""
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 10))
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Get top selling products with optimized query
        trending = InvoiceItem.objects.filter(
            invoice__created_at__gte=start_date,
            invoice__status__in=['paid', 'partial']
        ).select_related('product', 'invoice').values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total'),
            order_count=Count('invoice', distinct=True)
        ).order_by('-total_quantity')[:limit]
        
        return Response(list(trending))
    
    @action(detail=False, methods=['get'])
    def low_stock_alerts(self, request):
        """Get low stock alerts"""
        products = Product.objects.filter(
            is_active=True,
            is_trackable=True,
            current_stock__lte=F('min_stock_level')
        ).select_related('category', 'brand').values(
            'id', 'name', 'sku', 'current_stock', 'min_stock_level',
            'category__name', 'brand__name'
        )
        
        return Response(list(products))
    
    @action(detail=False, methods=['get'])
    def sales_insights(self, request):
        """Get sales insights - Optimized"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        invoices = Invoice.objects.filter(
            created_at__gte=start_date,
            status__in=['paid', 'partial']
        )
        
        # Single aggregation query for all metrics
        metrics = invoices.aggregate(
            total_sales=Sum('total_amount'),
            total_invoices=Count('id'),
            avg_order_value=Avg('total_amount')
        )
        
        total_sales = metrics['total_sales'] or 0
        total_invoices = metrics['total_invoices'] or 0
        avg_order_value = metrics['avg_order_value'] or 0
        
        # Daily sales breakdown - optimized with date index
        daily_sales = invoices.values('created_at__date').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('created_at__date')
        
        # Category-wise sales - optimized with select_related
        category_sales = InvoiceItem.objects.filter(
            invoice__created_at__gte=start_date,
            invoice__status__in=['paid', 'partial']
        ).select_related('product__category').values(
            'product__category__name'
        ).annotate(
            total=Sum('total'),
            quantity=Sum('quantity')
        ).order_by('-total')
        
        return Response({
            'period_days': days,
            'total_sales': float(total_sales),
            'total_invoices': total_invoices,
            'avg_order_value': float(avg_order_value),
            'daily_sales': list(daily_sales),
            'category_sales': list(category_sales)
        })
    
    @action(detail=False, methods=['get'])
    def profit_analysis(self, request):
        """Get profit analysis - Optimized with database aggregations"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Use database aggregations instead of Python loops
        invoice_items = InvoiceItem.objects.filter(
            invoice__created_at__gte=start_date,
            invoice__status__in=['paid', 'partial']
        ).select_related('product')
        
        # Calculate total revenue using database aggregation
        revenue_data = invoice_items.aggregate(
            total_revenue=Sum('total')
        )
        total_revenue = revenue_data['total_revenue'] or 0
        
        # Calculate total cost using database aggregation with F expressions
        from django.db.models import ExpressionWrapper, DecimalField
        cost_data = invoice_items.filter(
            product__cost_price__gt=0
        ).aggregate(
            total_cost=Sum(
                ExpressionWrapper(
                    F('quantity') * F('product__cost_price'),
                    output_field=DecimalField()
                )
            )
        )
        total_cost = cost_data['total_cost'] or 0
        
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Top profitable products - already optimized with aggregation
        profitable_products = invoice_items.values(
            'product__id', 'product__name'
        ).annotate(
            revenue=Sum('total'),
            quantity=Sum('quantity')
        ).order_by('-revenue')[:10]
        
        return Response({
            'period_days': days,
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'total_profit': float(total_profit),
            'profit_margin': round(profit_margin, 2),
            'top_products': list(profitable_products)
        })
    
    @action(detail=False, methods=['get'])
    def inventory_health(self, request):
        """Get inventory health metrics - Optimized with database aggregations"""
        products = Product.objects.filter(is_active=True, is_trackable=True)
        
        # Use database aggregations for counting
        total_products = products.count()
        out_of_stock = products.filter(current_stock=0).count()
        low_stock = products.filter(
            current_stock__lte=F('min_stock_level'),
            current_stock__gt=0
        ).count()
        overstock = products.filter(
            current_stock__gte=F('max_stock_level')
        ).count()
        in_stock = products.filter(
            current_stock__gt=F('min_stock_level'),
            current_stock__lt=F('max_stock_level')
        ).count()
        
        # Calculate total inventory value using database aggregation
        from django.db.models import ExpressionWrapper, DecimalField
        inventory_value_data = products.filter(
            cost_price__gt=0
        ).aggregate(
            total_value=Sum(
                ExpressionWrapper(
                    F('current_stock') * F('cost_price'),
                    output_field=DecimalField()
                )
            )
        )
        total_inventory_value = inventory_value_data['total_value'] or 0
        
        return Response({
            'total_products': total_products,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
            'overstock': overstock,
            'in_stock': in_stock,
            'total_inventory_value': float(total_inventory_value)
        })

