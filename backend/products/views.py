from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import Q, F
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, FileResponse
from django.core.files.storage import default_storage
from celery.result import AsyncResult
from .models import Product, Category, Brand
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductSearchSerializer,
    CategorySerializer,
    BrandSerializer
)
from common.permissions import IsAdminOrManager, IsAdminOrManagerOrEmployee
from .label_generator import generate_labels_pdf
from .tasks import generate_labels_pdf_task


class CategoryViewSet(viewsets.ModelViewSet):
    """Category CRUD operations"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BrandViewSet(viewsets.ModelViewSet):
    """Brand CRUD operations"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """Product CRUD operations"""
    queryset = Product.objects.select_related('category', 'brand', 'created_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'barcode', 'qr_code', 'description']
    filterset_fields = ['category', 'brand', 'is_active', 'is_trackable']
    ordering_fields = ['name', 'created_at', 'selling_price', 'current_stock']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'search':
            return ProductSearchSerializer
        return ProductDetailSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context for building absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminOrManager]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set created_by on product creation and create Stock entry"""
        product = serializer.save(created_by=self.request.user)
        
        # Create Stock entry in default warehouse if product is trackable
        if product.is_trackable:
            from inventory.models import Stock, Warehouse
            
            # Get or create default warehouse
            default_warehouse = Warehouse.objects.filter(is_active=True).first()
            if not default_warehouse:
                default_warehouse = Warehouse.objects.create(
                    name='Main Warehouse',
                    address='Default warehouse',
                    is_active=True
                )
            
            # Create or update Stock entry
            stock, created = Stock.objects.get_or_create(
                product=product,
                warehouse=default_warehouse,
                defaults={
                    'quantity': product.current_stock,
                    'min_quantity': product.min_stock_level,
                    'max_quantity': product.max_stock_level,
                    'updated_by': self.request.user
                }
            )
            
            # If stock already exists, update it
            if not created:
                stock.quantity = product.current_stock
                stock.min_quantity = product.min_stock_level
                stock.max_quantity = product.max_stock_level
                stock.updated_by = self.request.user
                stock.save()
    
    def perform_update(self, serializer):
        """Update product and sync Stock entry"""
        product = serializer.save()
        
        # Update Stock entry if product is trackable
        if product.is_trackable:
            from inventory.models import Stock, Warehouse
            
            # Get default warehouse
            default_warehouse = Warehouse.objects.filter(is_active=True).first()
            if default_warehouse:
                stock, created = Stock.objects.get_or_create(
                    product=product,
                    warehouse=default_warehouse,
                    defaults={
                        'quantity': product.current_stock,
                        'min_quantity': product.min_stock_level,
                        'max_quantity': product.max_stock_level,
                        'updated_by': self.request.user
                    }
                )
                
                # Update existing stock
                if not created:
                    stock.quantity = product.current_stock
                    stock.min_quantity = product.min_stock_level
                    stock.max_quantity = product.max_stock_level
                    stock.updated_by = self.request.user
                    stock.save()
    
    def perform_destroy(self, instance):
        """Handle product deletion - check for related invoices/returns"""
        from billing.models import InvoiceItem
        from returns.models import ReturnItem
        from inventory.models import Stock, InventoryTransaction
        from django.db.models.deletion import ProtectedError
        
        # Check if product has been used in invoices or returns
        invoice_items_count = InvoiceItem.objects.filter(product=instance).count()
        return_items_count = ReturnItem.objects.filter(product=instance).count()
        
        if invoice_items_count > 0 or return_items_count > 0:
            # Product has been used in invoices or returns - soft delete instead
            instance.is_active = False
            instance.save()
            
            # Delete related Stock entries (these can be safely deleted)
            Stock.objects.filter(product=instance).delete()
            
            # Raise a validation error to inform the user
            raise ValidationError({
                'detail': f'Cannot delete product "{instance.name}" because it has been used in {invoice_items_count} invoice(s) and {return_items_count} return(s). The product has been deactivated instead.'
            })
        else:
            # Product hasn't been used - safe to hard delete
            try:
                # Delete related Stock entries first (CASCADE)
                Stock.objects.filter(product=instance).delete()
                
                # Delete related InventoryTransaction entries (CASCADE)
                InventoryTransaction.objects.filter(product=instance).delete()
                
                # Delete the product
                instance.delete()
            except ProtectedError as e:
                # If there are any other protected relationships, soft delete instead
                instance.is_active = False
                instance.save()
                raise ValidationError({
                    'detail': f'Cannot delete product "{instance.name}" due to existing relationships. The product has been deactivated instead.'
                })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search(self, request):
        """Search products by name, SKU, barcode, or QR code"""
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'detail': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search in multiple fields
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(barcode__icontains=query) |
            Q(qr_code__icontains=query)
        ).filter(is_active=True).select_related('category')[:20]
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def low_stock(self, request):
        """Get products with low stock"""
        products = Product.objects.filter(
            current_stock__lte=F('min_stock_level'),
            is_active=True,
            is_trackable=True
        ).select_related('category', 'brand')
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_barcode(self, request):
        """Get product by barcode"""
        barcode = request.query_params.get('barcode', '').strip()
        
        if not barcode:
            return Response(
                {'detail': 'Barcode is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(barcode=barcode, is_active=True)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_qr(self, request):
        """Get product by QR code
        
        QR code format: QR-XXXXXXXX (e.g., QR-E82146AB)
        The QR code should contain the exact qr_code field value from the product.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        qr_code = request.query_params.get('qr', '').strip()
        
        if not qr_code:
            return Response(
                {'detail': 'QR code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f'QR code lookup requested: {qr_code}')
        
        try:
            # Try exact match first
            product = Product.objects.get(qr_code=qr_code, is_active=True)
            serializer = ProductDetailSerializer(product, context={'request': request})
            logger.info(f'Product found: {product.name} (ID: {product.id})')
            return Response(serializer.data)
        except Product.DoesNotExist:
            # Try case-insensitive match as fallback
            try:
                product = Product.objects.get(qr_code__iexact=qr_code, is_active=True)
                serializer = ProductDetailSerializer(product, context={'request': request})
                logger.info(f'Product found (case-insensitive): {product.name} (ID: {product.id})')
                return Response(serializer.data)
            except Product.DoesNotExist:
                logger.warning(f'Product not found for QR code: {qr_code}')
                return Response(
                    {'detail': f'Product not found with QR code: {qr_code}'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Product.MultipleObjectsReturned:
            # Should not happen due to unique constraint, but handle it
            logger.error(f'Multiple products found for QR code: {qr_code}')
            product = Product.objects.filter(qr_code=qr_code, is_active=True).first()
            if product:
                serializer = ProductDetailSerializer(product, context={'request': request})
                return Response(serializer.data)
            return Response(
                {'detail': 'Multiple products found with same QR code'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def print_labels(self, request):
        """Generate printable labels PDF with QR codes and barcodes (async)
        
        Query parameters:
        - product_ids: Comma-separated list of product IDs (optional, if not provided, all active products)
        - limit: Limit number of products (optional, for testing - e.g., limit=10)
        - labels_per_page: Number of labels per page (default: 6)
        - async: Set to 'true' to use async processing (default: false for <=10 products, true for >10)
        """
        # Get product IDs from query params
        product_ids_param = request.query_params.get('product_ids', '').strip()
        use_async = request.query_params.get('async', '').lower() == 'true'
        limit = request.query_params.get('limit')
        
        # Get labels_per_page from query params
        labels_per_page = int(request.query_params.get('labels_per_page', 6))
        
        # Parse product IDs if provided
        product_ids = None
        if product_ids_param:
            try:
                product_ids = [int(id.strip()) for id in product_ids_param.split(',') if id.strip()]
            except ValueError:
                return Response(
                    {'error': 'Invalid product_ids format. Use comma-separated integers.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if products exist
        if product_ids:
            products = Product.objects.filter(id__in=product_ids, is_active=True).order_by('name')
        else:
            products = Product.objects.filter(is_active=True).order_by('name')
        
        # Apply limit if specified (for testing)
        if limit:
            try:
                limit_int = int(limit)
                products = products[:limit_int]
            except ValueError:
                return Response(
                    {'error': 'Invalid limit format. Use an integer.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not products.exists():
            return Response(
                {'error': 'No products found to generate labels'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use async for heavy operations (more than 10 products) or if explicitly requested
        product_count = products.count()
        # For testing: use sync for <= 10 products, async for > 10 (unless explicitly requested)
        # Default: sync for <= 10, async for > 10
        # If async is explicitly set to true, always use async
        if use_async or product_count > 10:
            # Start async task
            task = generate_labels_pdf_task.delay(product_ids, labels_per_page)
            return Response({
                'task_id': task.id,
                'status': 'processing',
                'message': 'Label generation started. Use task_id to check status.',
                'product_count': product_count
            }, status=status.HTTP_202_ACCEPTED)
        else:
            # Synchronous generation for small batches
            try:
                pdf_buffer = generate_labels_pdf(products, labels_per_page=labels_per_page)
                response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="product_labels_{product_count}_products.pdf"'
                return response
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error generating labels PDF: {e}", exc_info=True)
                return Response(
                    {'error': f'Failed to generate labels PDF: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='print_labels/status')
    def print_labels_status(self, request):
        """Check status of label generation task
        
        Query parameters:
        - task_id: Task ID from print_labels endpoint
        
        Returns:
        - PENDING: Task is waiting to be processed
        - PROGRESS: Task is being processed (includes progress and status message)
        - SUCCESS: Task completed (includes file_path and filename)
        - FAILURE: Task failed (includes error message)
        """
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'pending',
                'message': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'processing',
                'progress': task_result.info.get('progress', 0),
                'message': task_result.info.get('status', 'Processing...')
            }
        elif task_result.state == 'SUCCESS':
            result = task_result.info
            if result.get('status') == 'success':
                response = {
                    'task_id': task_id,
                    'state': task_result.state,
                    'status': 'success',
                    'file_path': result.get('file_path'),
                    'filename': result.get('filename'),
                    'product_count': result.get('product_count'),
                    'file_size': result.get('file_size'),
                    'download_url': f'/products/products/print_labels/download/?task_id={task_id}'
                }
            else:
                response = {
                    'task_id': task_id,
                    'state': task_result.state,
                    'status': 'error',
                    'error': result.get('error', 'Unknown error occurred')
                }
        else:  # FAILURE or other states
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'error',
                'error': str(task_result.info) if task_result.info else 'Task failed'
            }
        
        return Response(response)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='print_labels/download')
    def print_labels_download(self, request):
        """Download generated labels PDF
        
        Query parameters:
        - task_id: Task ID from print_labels endpoint
        """
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task_result = AsyncResult(task_id)
        
        if task_result.state != 'SUCCESS':
            return Response(
                {'error': f'Task is not completed. Current state: {task_result.state}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = task_result.info
        if result.get('status') != 'success':
            return Response(
                {'error': result.get('error', 'Task failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        file_path = result.get('file_path')
        if not file_path or not default_storage.exists(file_path):
            return Response(
                {'error': 'Generated file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            file = default_storage.open(file_path, 'rb')
            response = FileResponse(file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{result.get("filename", "product_labels.pdf")}"'
            
            # Clean up file after download (optional, can be done by a cleanup task)
            # default_storage.delete(file_path)
            
            return response
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error downloading labels PDF: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to download file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
