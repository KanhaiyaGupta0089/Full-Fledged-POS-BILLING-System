"""
Views for Purchase Orders & Supplier Management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem, SupplierPayment
from .serializers import (
    SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer,
    GoodsReceiptNoteSerializer, GRNItemSerializer, SupplierPaymentSerializer
)
from .automation import check_low_stock_and_create_po, recalculate_po_totals
from common.permissions import IsAdminOrManager


class SupplierViewSet(viewsets.ModelViewSet):
    """Supplier CRUD operations"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'company_name', 'email', 'phone', 'gstin']
    filterset_fields = ['is_active', 'is_preferred']
    ordering_fields = ['name', 'created_at', 'total_purchases']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Set created_by when creating supplier"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def top_suppliers(self, request):
        """Get top suppliers by purchase volume"""
        suppliers = Supplier.objects.filter(is_active=True).order_by('-total_purchases')[:10]
        serializer = self.get_serializer(suppliers, many=True)
        return Response(serializer.data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """Purchase Order CRUD operations"""
    queryset = PurchaseOrder.objects.select_related('supplier', 'warehouse', 'created_by').prefetch_related('items')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'warehouse']
    search_fields = ['po_number', 'supplier__name']
    ordering_fields = ['created_at', 'order_date', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return PurchaseOrderSerializer
        return PurchaseOrderSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        # Totals are recalculated in serializer.create()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve purchase order"""
        po = self.get_object()
        if po.status == 'draft':
            po.status = 'approved'
            po.approved_by = request.user
            from django.utils import timezone
            po.approved_at = timezone.now()
            po.save()
            return Response({'message': 'PO approved successfully'})
        return Response({'error': 'PO cannot be approved'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def auto_create_from_low_stock(self, request):
        """Manually trigger auto PO creation for low stock items"""
        created_pos = check_low_stock_and_create_po()
        return Response({
            'message': f'Created {len(created_pos)} purchase orders',
            'pos': PurchaseOrderSerializer(created_pos, many=True).data
        })


class GoodsReceiptNoteViewSet(viewsets.ModelViewSet):
    """GRN CRUD operations"""
    queryset = GoodsReceiptNote.objects.select_related('purchase_order', 'warehouse', 'received_by').prefetch_related('items')
    serializer_class = GoodsReceiptNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_order', 'warehouse', 'is_verified']
    search_fields = ['grn_number', 'purchase_order__po_number']
    ordering_fields = ['created_at', 'received_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify GRN and update inventory"""
        grn = self.get_object()
        if not grn.is_verified:
            grn.is_verified = True
            grn.verified_by = request.user
            from django.utils import timezone
            grn.verified_at = timezone.now()
            grn.save()
            
            # Explicitly update inventory (signals will also handle this)
            from .automation import auto_receive_grn
            auto_receive_grn(grn)
            
            return Response({'message': 'GRN verified and inventory updated'})
        return Response({'error': 'GRN already verified'}, status=status.HTTP_400_BAD_REQUEST)


class SupplierPaymentViewSet(viewsets.ModelViewSet):
    """Supplier Payment operations"""
    queryset = SupplierPayment.objects.select_related('supplier', 'purchase_order')
    serializer_class = SupplierPaymentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['supplier', 'payment_method']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

