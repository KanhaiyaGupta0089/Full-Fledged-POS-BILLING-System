"""
Views for Forecasting
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from .models import SalesForecast, DemandPattern, OptimalStockLevel
from .serializers import SalesForecastSerializer, DemandPatternSerializer, OptimalStockLevelSerializer
from .algorithms import ForecastingAlgorithms
from products.models import Product
from inventory.models import Warehouse
from common.permissions import IsAdminOrManager


class SalesForecastViewSet(viewsets.ModelViewSet):
    """Sales Forecast CRUD operations"""
    queryset = SalesForecast.objects.select_related('product', 'warehouse')
    serializer_class = SalesForecastSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse', 'period_type', 'forecast_method']
    search_fields = ['product__name', 'product__sku']
    ordering_fields = ['forecast_date', 'predicted_quantity', 'confidence_level']
    ordering = ['-forecast_date']
    
    @action(detail=False, methods=['post'])
    def generate_forecast(self, request):
        """Generate forecast for a product"""
        product_id = request.data.get('product_id')
        warehouse_id = request.data.get('warehouse_id')
        method = request.data.get('method', 'moving_average')
        period_days = request.data.get('period_days', 30)
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(pk=product_id)
            warehouse = None
            if warehouse_id:
                warehouse = Warehouse.objects.get(pk=warehouse_id)
            
            # Generate forecast
            forecast_data = ForecastingAlgorithms.generate_forecast(
                product, warehouse, method,
                period_days=period_days,
                window_size=request.data.get('window_size', 7),
                alpha=request.data.get('alpha', 0.3)
            )
            
            if 'error' in forecast_data:
                return Response(forecast_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or update forecast record
            forecast_date = timezone.now().date()
            period_type = request.data.get('period_type', 'monthly')
            
            forecast, created = SalesForecast.objects.update_or_create(
                product=product,
                warehouse=warehouse,
                forecast_date=forecast_date,
                period_type=period_type,
                defaults={
                    'predicted_quantity': forecast_data['forecast'],
                    'predicted_revenue': Decimal('0.00'),  # Will be calculated
                    'confidence_level': Decimal(str(forecast_data['confidence'])),
                    'forecast_method': method
                }
            )
            
            # Calculate predicted revenue (using average product price)
            if product.selling_price:
                forecast.predicted_revenue = Decimal(str(forecast_data['forecast'])) * product.selling_price
                forecast.save()
            
            serializer = self.get_serializer(forecast)
            return Response({
                'forecast': serializer.data,
                'algorithm_data': forecast_data
            })
            
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def product_forecasts(self, request):
        """Get all forecasts for a product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        forecasts = self.queryset.filter(product_id=product_id)
        serializer = self.get_serializer(forecasts, many=True)
        return Response(serializer.data)


class DemandPatternViewSet(viewsets.ModelViewSet):
    """Demand Pattern CRUD operations"""
    queryset = DemandPattern.objects.select_related('product', 'warehouse')
    serializer_class = DemandPatternSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'warehouse', 'trend']
    search_fields = ['product__name', 'product__sku']
    ordering = ['-last_analyzed']
    
    @action(detail=False, methods=['post'])
    def analyze_demand(self, request):
        """Analyze demand pattern for a product"""
        product_id = request.data.get('product_id')
        warehouse_id = request.data.get('warehouse_id')
        period_days = request.data.get('period_days', 90)
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(pk=product_id)
            warehouse = None
            if warehouse_id:
                warehouse = Warehouse.objects.get(pk=warehouse_id)
            
            # Get historical sales
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            from billing.models import Invoice, InvoiceItem
            invoices = Invoice.objects.filter(
                status__in=['paid', 'partial'],
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).prefetch_related('items')
            
            # Calculate statistics
            total_quantity = 0
            total_revenue = Decimal('0.00')
            daily_sales = []
            
            for invoice in invoices:
                for item in invoice.items.filter(product=product):
                    total_quantity += item.quantity
                    total_revenue += item.total
                    daily_sales.append({
                        'date': invoice.created_at.date(),
                        'quantity': item.quantity
                    })
            
            if not daily_sales:
                return Response(
                    {'error': 'No sales data found for analysis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate averages
            days_count = (end_date - start_date).days + 1
            avg_daily = total_quantity / days_count
            avg_weekly = avg_daily * 7
            avg_monthly = avg_daily * 30
            
            # Determine trend
            if len(daily_sales) >= 14:
                first_half = sum(d['quantity'] for d in daily_sales[:len(daily_sales)//2])
                second_half = sum(d['quantity'] for d in daily_sales[len(daily_sales)//2:])
                
                if second_half > first_half * 1.1:
                    trend = 'increasing'
                elif second_half < first_half * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Create or update demand pattern
            pattern, created = DemandPattern.objects.update_or_create(
                product=product,
                warehouse=warehouse,
                defaults={
                    'trend': trend,
                    'average_daily_sales': Decimal(str(avg_daily)),
                    'average_weekly_sales': Decimal(str(avg_weekly)),
                    'average_monthly_sales': Decimal(str(avg_monthly)),
                    'recommended_safety_stock': int(avg_daily * 7),  # 7 days safety stock
                    'recommended_reorder_point': int(avg_daily * 14),  # 14 days reorder point
                    'recommended_order_quantity': int(avg_monthly),  # Monthly order quantity
                }
            )
            
            serializer = self.get_serializer(pattern)
            return Response(serializer.data)
            
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OptimalStockLevelViewSet(viewsets.ModelViewSet):
    """Optimal Stock Level CRUD operations"""
    queryset = OptimalStockLevel.objects.select_related('product', 'warehouse')
    serializer_class = OptimalStockLevelSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'warehouse', 'stock_status']
    search_fields = ['product__name', 'product__sku']
    ordering = ['product__name']
    
    @action(detail=False, methods=['post'])
    def calculate_optimal(self, request):
        """Calculate optimal stock levels for a product"""
        product_id = request.data.get('product_id')
        warehouse_id = request.data.get('warehouse_id')
        
        if not product_id or not warehouse_id:
            return Response(
                {'error': 'product_id and warehouse_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(pk=product_id)
            warehouse = Warehouse.objects.get(pk=warehouse_id)
            
            # Get current stock
            from inventory.models import Stock
            stock = Stock.objects.filter(product=product, warehouse=warehouse).first()
            current_stock = stock.quantity if stock else 0
            
            # Get demand pattern
            pattern = DemandPattern.objects.filter(product=product, warehouse=warehouse).first()
            
            if not pattern:
                return Response(
                    {'error': 'Demand pattern not found. Please analyze demand first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate optimal levels
            avg_daily = float(pattern.average_daily_sales)
            lead_time = pattern.average_lead_time or 7
            safety_stock = int(avg_daily * 7)  # 7 days safety stock
            reorder_point = int(avg_daily * lead_time) + safety_stock
            reorder_quantity = int(avg_daily * 30)  # 30 days supply
            max_stock = reorder_point + reorder_quantity
            
            # Determine stock status
            if current_stock < safety_stock:
                stock_status = 'critical'
            elif current_stock < reorder_point:
                stock_status = 'low'
            elif current_stock > max_stock:
                stock_status = 'high'
            else:
                stock_status = 'optimal'
            
            # Create or update optimal stock level
            optimal, created = OptimalStockLevel.objects.update_or_create(
                product=product,
                warehouse=warehouse,
                defaults={
                    'optimal_min_stock': safety_stock,
                    'optimal_max_stock': max_stock,
                    'optimal_reorder_point': reorder_point,
                    'optimal_reorder_quantity': reorder_quantity,
                    'current_stock': current_stock,
                    'stock_status': stock_status,
                    'calculation_method': 'demand_based'
                }
            )
            
            serializer = self.get_serializer(optimal)
            return Response(serializer.data)
            
        except (Product.DoesNotExist, Warehouse.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

