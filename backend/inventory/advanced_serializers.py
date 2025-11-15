"""
Advanced Inventory Serializers
"""
from rest_framework import serializers
from .advanced_models import (
    Batch, SerialNumber, StockValuation, StockAdjustment,
    StockAdjustmentItem, StockTransfer, StockTransferItem, AutoReorderRule
)
from products.serializers import ProductListSerializer
from .serializers import WarehouseSerializer


class BatchSerializer(serializers.ModelSerializer):
    """Batch serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True, allow_null=True)
    
    class Meta:
        model = Batch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SerialNumberSerializer(serializers.ModelSerializer):
    """Serial Number serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SerialNumber
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class StockValuationSerializer(serializers.ModelSerializer):
    """Stock Valuation serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = StockValuation
        fields = '__all__'
        read_only_fields = ['last_calculated_at']


class StockAdjustmentItemSerializer(serializers.ModelSerializer):
    """Stock Adjustment Item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockAdjustmentItem
        fields = '__all__'


class StockAdjustmentSerializer(serializers.ModelSerializer):
    """Stock Adjustment serializer"""
    items = StockAdjustmentItemSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = '__all__'
        read_only_fields = ['adjustment_number', 'created_at', 'approved_at']


class StockTransferItemSerializer(serializers.ModelSerializer):
    """Stock Transfer Item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockTransferItem
        fields = '__all__'


class StockTransferSerializer(serializers.ModelSerializer):
    """Stock Transfer serializer"""
    items = StockTransferItemSerializer(many=True, read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    
    class Meta:
        model = StockTransfer
        fields = '__all__'
        read_only_fields = ['transfer_number', 'created_at', 'updated_at']


class AutoReorderRuleSerializer(serializers.ModelSerializer):
    """Auto Reorder Rule serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    preferred_supplier_name = serializers.CharField(source='preferred_supplier.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AutoReorderRule
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']






