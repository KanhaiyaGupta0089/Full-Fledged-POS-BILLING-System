"""
Advanced Inventory Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .advanced_models import (
    Batch, SerialNumber, StockValuation, StockAdjustment,
    StockAdjustmentItem, StockTransfer, StockTransferItem, AutoReorderRule
)
from .models import Stock, Warehouse
from products.models import Product
from common.permissions import IsAdminOrManager


class BatchViewSet(viewsets.ModelViewSet):
    """Batch/Lot tracking"""
    queryset = Batch.objects.select_related('product', 'warehouse')
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'warehouse', 'is_active']
    search_fields = ['batch_number', 'product__name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        from .advanced_serializers import BatchSerializer
        return BatchSerializer


class StockValuationViewSet(viewsets.ReadOnlyModelViewSet):
    """Stock Valuation (read-only)"""
    queryset = StockValuation.objects.select_related('product', 'warehouse')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'warehouse', 'valuation_method']
    
    def get_serializer_class(self):
        from .advanced_serializers import StockValuationSerializer
        return StockValuationSerializer
    
    @action(detail=False, methods=['post'])
    def recalculate(self, request):
        """Recalculate all stock valuations"""
        from .tasks import calculate_stock_valuations_task
        task = calculate_stock_valuations_task.delay()
        return Response({'task_id': task.id, 'message': 'Recalculation started'})


class StockAdjustmentViewSet(viewsets.ModelViewSet):
    """Stock Adjustments"""
    queryset = StockAdjustment.objects.select_related('warehouse', 'created_by', 'approved_by').prefetch_related('items')
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['warehouse', 'adjustment_type', 'is_approved']
    search_fields = ['adjustment_number']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        from .advanced_serializers import StockAdjustmentSerializer
        return StockAdjustmentSerializer


class StockTransferViewSet(viewsets.ModelViewSet):
    """Stock Transfers"""
    queryset = StockTransfer.objects.select_related('from_warehouse', 'to_warehouse', 'created_by', 'received_by').prefetch_related('items')
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['from_warehouse', 'to_warehouse', 'status']
    search_fields = ['transfer_number']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        from .advanced_serializers import StockTransferSerializer
        return StockTransferSerializer


class AutoReorderRuleViewSet(viewsets.ModelViewSet):
    """Auto Reorder Rules"""
    queryset = AutoReorderRule.objects.select_related('product', 'warehouse', 'preferred_supplier')
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'warehouse', 'is_active']
    search_fields = ['product__name', 'product__sku']
    ordering = ['product__name']
    
    def get_serializer_class(self):
        from .advanced_serializers import AutoReorderRuleSerializer
        return AutoReorderRuleSerializer
    
    @action(detail=True, methods=['post'])
    def check_and_reorder(self, request, pk=None):
        """Manually check and trigger reorder"""
        rule = self.get_object()
        result = rule.check_and_reorder()
        if result:
            return Response({'message': 'Purchase order created successfully'})
        return Response({'message': 'Reorder not needed or failed'}, status=status.HTTP_400_BAD_REQUEST)

