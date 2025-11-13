"""
Inventory views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Q
from .models import Warehouse, Stock, InventoryTransaction
from .serializers import (
    WarehouseSerializer,
    StockSerializer,
    InventoryTransactionSerializer
)
from common.permissions import IsAdminOrManager, IsAdminOrManagerOrEmployee
from products.models import Product


class WarehouseViewSet(viewsets.ModelViewSet):
    """Warehouse CRUD operations"""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    search_fields = ['name', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class StockViewSet(viewsets.ModelViewSet):
    """Stock CRUD operations"""
    queryset = Stock.objects.select_related('product', 'warehouse')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filterset_fields = ['warehouse', 'product']
    search_fields = ['product__name', 'product__sku']
    ordering_fields = ['quantity', 'last_updated']
    ordering = ['-last_updated']
    
    def get_queryset(self):
        """Get stock queryset - optimized for performance with large datasets"""
        queryset = super().get_queryset()
        
        # Only sync missing stocks on list action, and only occasionally
        # This prevents performance issues with large datasets (20,000+ products)
        if self.action == 'list':
            try:
                from products.models import Product
                from inventory.models import Warehouse
                from django.db.models import Exists, OuterRef
                
                default_warehouse = Warehouse.objects.filter(is_active=True).first()
                
                if default_warehouse:
                    # Use a more efficient subquery to find products without stock entries
                    # Only process 50 products at a time to avoid timeout
                    trackable_products = Product.objects.filter(
                        is_trackable=True,  
                        is_active=True
                    ).exclude(
                        Exists(
                            Stock.objects.filter(
                                product=OuterRef('pk'),
                                warehouse=default_warehouse
                            )
                        )
                    )[:50]  # Process only 50 at a time for performance
                    
                    # Create Stock entries only for products that don't have them
                    if trackable_products.exists():
                        stocks_to_create = [
                            Stock(
                                product=product,
                                warehouse=default_warehouse,
                                quantity=product.current_stock,
                                min_quantity=product.min_stock_level,
                                max_quantity=product.max_stock_level
                            )
                            for product in trackable_products
                        ]
                        
                        if stocks_to_create:
                            Stock.objects.bulk_create(stocks_to_create, ignore_conflicts=True)
            except Exception as e:
                # Log error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Error syncing stock entries: {e}')
        
        # Filter by low stock if requested
        low_stock_only = self.request.query_params.get('low_stock_only', 'false').lower() == 'true'
        if low_stock_only:
            # Filter stocks that are low based on Stock quantity or Product current_stock
            # A stock is low if:
            # 1. Stock quantity <= Stock min_quantity (when min_quantity > 0), OR
            # 2. Stock quantity <= Product min_stock_level (when Stock min_quantity is 0 but Product min_stock_level > 0), OR
            # 3. Product current_stock <= Product min_stock_level (when Product min_stock_level > 0)
            queryset = queryset.filter(
                # Case 1: Stock has min_quantity set and quantity is low
                Q(min_quantity__gt=0, quantity__lte=F('min_quantity')) |
                # Case 2: Stock min_quantity is 0, but product has min_stock_level and stock quantity is low
                Q(min_quantity=0, product__min_stock_level__gt=0, quantity__lte=F('product__min_stock_level')) |
                # Case 3: Product current_stock is low (regardless of stock quantity)
                Q(product__min_stock_level__gt=0, product__current_stock__lte=F('product__min_stock_level'))
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary_stats(self, request):
        """Get inventory summary statistics - optimized single endpoint"""
        from products.models import Product
        from django.db.models import Count, Q, F
        
        # Use database aggregations for fast counting
        total_products = Product.objects.filter(is_active=True).count()
        total_stock_items = Stock.objects.count()
        
        # Count low stock items efficiently using database queries
        low_stock_items = Stock.objects.filter(
            Q(min_quantity__gt=0, quantity__lte=F('min_quantity')) |
            Q(min_quantity=0, product__min_stock_level__gt=0, quantity__lte=F('product__min_stock_level')) |
            Q(product__min_stock_level__gt=0, product__current_stock__lte=F('product__min_stock_level'))
        ).count()
        
        # Also count products that are low stock but might not have Stock entries
        products_low_count = Product.objects.filter(
            is_trackable=True,
            is_active=True,
            min_stock_level__gt=0,
            current_stock__lte=F('min_stock_level')
        ).exclude(
            id__in=Stock.objects.values_list('product_id', flat=True)
        ).count()
        
        low_stock_items += products_low_count
        
        total_transactions = InventoryTransaction.objects.count()
        
        return Response({
            'total_products': total_products,
            'total_stock_items': total_stock_items,
            'low_stock_items': low_stock_items,
            'total_transactions': total_transactions,
        })
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get low stock items - check both Stock and Product levels"""
        from products.models import Product
        from django.db.models import Q, Count
        
        # Check if count_only is requested
        count_only = request.query_params.get('count_only', 'false').lower() == 'true'
        
        # Get stocks that are low based on Stock quantity
        stocks_low = self.queryset.filter(
            Q(quantity__lte=F('min_quantity')) | 
            Q(quantity__lte=F('product__min_stock_level'))
        )
        
        # Also check products that are low stock but might not have Stock entries
        products_low = Product.objects.filter(
            is_trackable=True,
            is_active=True,
            current_stock__lte=F('min_stock_level')
        )
        
        # Get all low stock items
        stock_ids = list(stocks_low.values_list('id', flat=True))
        
        # Create Stock entries for products that don't have them
        default_warehouse = Warehouse.objects.filter(is_active=True).first()
        if default_warehouse:
            for product in products_low:
                stock, created = Stock.objects.get_or_create(
                    product=product,
                    warehouse=default_warehouse,
                    defaults={
                        'quantity': product.current_stock,
                        'min_quantity': product.min_stock_level,
                        'max_quantity': product.max_stock_level
                    }
                )
                if stock.id not in stock_ids:
                    stock_ids.append(stock.id)
        
        # If count_only, return just the count
        if count_only:
            count = len(stock_ids) if stock_ids else 0
            # Also count products that are low stock but don't have stock entries yet
            products_low_count = products_low.exclude(
                id__in=stocks_low.values_list('product_id', flat=True)
            ).count()
            return Response({'count': count + products_low_count})
        
        stocks = self.queryset.filter(id__in=stock_ids)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Inventory transaction viewset (read-only, created via signals/other views)"""
    queryset = InventoryTransaction.objects.select_related('product', 'warehouse', 'created_by')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filterset_fields = ['transaction_type', 'product', 'warehouse']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def adjust(self, request):
        """Adjust inventory manually"""
        product_id = request.data.get('product_id')
        warehouse_id = request.data.get('warehouse_id')
        quantity = request.data.get('quantity')
        notes = request.data.get('notes', '')
        
        if not all([product_id, warehouse_id, quantity]):
            return Response(
                {'error': 'product_id, warehouse_id, and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
            warehouse = Warehouse.objects.get(id=warehouse_id)
            stock, created = Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'quantity': 0}
            )
            
            # Create transaction
            transaction = InventoryTransaction.objects.create(
                transaction_type='adjustment',
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                notes=notes,
                created_by=request.user
            )
            
            # Update stock
            stock.quantity += int(quantity)
            stock.updated_by = request.user
            stock.save()
            
            # Update product stock
            product.current_stock += int(quantity)
            product.save()
            
            return Response(InventoryTransactionSerializer(transaction).data)
        except (Product.DoesNotExist, Warehouse.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
