"""
Returns views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Return, ReturnItem
from .serializers import ReturnSerializer, ReturnCreateSerializer, ReturnItemSerializer
from billing.models import Invoice, InvoiceItem
from products.models import Product
from common.permissions import IsAdminOrManager, IsAdminOrManagerOrEmployee


class ReturnViewSet(viewsets.ModelViewSet):
    """Return CRUD operations"""
    queryset = Return.objects.select_related('invoice', 'created_by', 'approved_by').prefetch_related('items__product')
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filterset_fields = ['status', 'reason', 'invoice']
    search_fields = ['return_number', 'invoice__invoice_number', 'invoice__customer_name', 'invoice__customer_phone']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def search_invoice(self, request):
        """Quick search for invoice by number"""
        invoice_number = request.query_params.get('invoice_number', '').strip()
        if not invoice_number:
            return Response({'error': 'invoice_number parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invoice = Invoice.objects.get(invoice_number=invoice_number)
            from billing.serializers import InvoiceSerializer
            return Response(InvoiceSerializer(invoice).data)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReturnCreateSerializer
        return ReturnSerializer
    
    def perform_create(self, serializer):
        """Generate return number and set created_by"""
        # Generate return number with unique check
        today = timezone.now().date()
        existing_returns = Return.objects.filter(
            return_number__startswith=f"RET-{today.strftime('%Y%m%d')}-"
        )
        if existing_returns.exists():
            max_seq = 0
            for ret in existing_returns:
                try:
                    seq = int(ret.return_number.split('-')[-1])
                    max_seq = max(max_seq, seq)
                except (ValueError, IndexError):
                    pass
            count = max_seq + 1
        else:
            count = 1
        return_number = f"RET-{today.strftime('%Y%m%d')}-{count:04d}"
        
        serializer.save(
            return_number=return_number,
            created_by=self.request.user
        )
    
    def create(self, request, *args, **kwargs):
        """Create return with items"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items_data = serializer.validated_data.pop('items')
        return_order = serializer.save()
        
        total_amount = 0
        for item_data in items_data:
            invoice_item_id = item_data.get('invoice_item_id')
            quantity = item_data.get('quantity')
            
            try:
                invoice_item = InvoiceItem.objects.get(id=invoice_item_id)
                product = invoice_item.product
                
                item_total = invoice_item.unit_price * quantity
                total_amount += item_total
                
                ReturnItem.objects.create(
                    return_order=return_order,
                    invoice_item=invoice_item,
                    product=product,
                    quantity=quantity,
                    unit_price=invoice_item.unit_price,
                    total=item_total
                )
            except InvoiceItem.DoesNotExist:
                return Response(
                    {'error': f'Invoice item {invoice_item_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return_order.total_amount = total_amount
        return_order.refund_amount = total_amount
        return_order.save()
        
        return Response(ReturnSerializer(return_order).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve return (manager/admin only) - Automatically updates inventory"""
        if request.user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Only managers and admins can approve returns'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return_order = self.get_object()
        if return_order.status != 'pending':
            return Response(
                {'error': 'Only pending returns can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_order.status = 'approved'
        return_order.approved_by = request.user
        return_order.save()
        
        # Automatically update inventory
        from inventory.models import Stock, Warehouse, InventoryTransaction
        
        default_warehouse = Warehouse.objects.filter(is_active=True).first()
        if not default_warehouse:
            default_warehouse = Warehouse.objects.create(
                name='Main Warehouse',
                address='Default Location',
                is_active=True
            )
        
        for item in return_order.items.all():
            product = item.product
            if product.is_trackable:
                # Update stock
                stock, created = Stock.objects.get_or_create(
                    product=product,
                    warehouse=default_warehouse,
                    defaults={'quantity': 0, 'min_quantity': product.min_stock_level, 'max_quantity': product.max_stock_level}
                )
                stock.quantity += item.quantity
                stock.updated_by = request.user
                stock.save()
                
                # Update product stock
                product.current_stock += item.quantity
                product.save()
                
                # Create inventory transaction
                InventoryTransaction.objects.create(
                    transaction_type='return',
                    product=product,
                    warehouse=default_warehouse,
                    quantity=item.quantity,
                    reference_number=return_order.return_number,
                    notes=f"Product Return - {return_order.return_number}",
                    created_by=request.user
                )
        
        return Response(ReturnSerializer(return_order).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete return - Inventory already updated on approval"""
        return_order = self.get_object()
        if return_order.status != 'approved':
            return Response(
                {'error': 'Return must be approved first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_order.status = 'completed'
        return_order.save()
        
        return Response(ReturnSerializer(return_order).data)
    
    @action(detail=True, methods=['post'])
    def quick_complete(self, request, pk=None):
        """Quick complete - Approve and complete in one action (for employees)"""
        return_order = self.get_object()
        if return_order.status != 'pending':
            return Response(
                {'error': 'Only pending returns can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Auto-approve if user has permission, otherwise just complete
        if request.user.role in ['admin', 'manager']:
            return_order.status = 'approved'
            return_order.approved_by = request.user
            return_order.save()
            
            # Update inventory (same as approve)
            from inventory.models import Stock, Warehouse, InventoryTransaction
            
            default_warehouse = Warehouse.objects.filter(is_active=True).first()
            if not default_warehouse:
                default_warehouse = Warehouse.objects.create(
                    name='Main Warehouse',
                    address='Default Location',
                    is_active=True
                )
            
            for item in return_order.items.all():
                product = item.product
                if product.is_trackable:
                    stock, created = Stock.objects.get_or_create(
                        product=product,
                        warehouse=default_warehouse,
                        defaults={'quantity': 0, 'min_quantity': product.min_stock_level, 'max_quantity': product.max_stock_level}
                    )
                    stock.quantity += item.quantity
                    stock.updated_by = request.user
                    stock.save()
                    
                    product.current_stock += item.quantity
                    product.save()
                    
                    InventoryTransaction.objects.create(
                        transaction_type='return',
                        product=product,
                        warehouse=default_warehouse,
                        quantity=item.quantity,
                        reference_number=return_order.return_number,
                        notes=f"Product Return - {return_order.return_number}",
                        created_by=request.user
                    )
        
        return_order.status = 'completed'
        return_order.save()
        
        return Response(ReturnSerializer(return_order).data)

