"""
Inventory serializers
"""
from rest_framework import serializers
from .models import Warehouse, Stock, InventoryTransaction
from products.serializers import ProductListSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    """Warehouse serializer"""
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class StockSerializer(serializers.ModelSerializer):
    """Stock serializer"""
    product = ProductListSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)
    warehouse_id = serializers.IntegerField(write_only=True, required=False)
    # Add product-level low stock check
    product_is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['last_updated', 'available_quantity', 'is_low_stock']
    
    def get_product_is_low_stock(self, obj):
        """Check if product itself is low stock"""
        if obj.product:
            return obj.product.is_low_stock
        return False
    
    def to_representation(self, instance):
        """Override to ensure is_low_stock is correctly calculated"""
        data = super().to_representation(instance)
        # Ensure is_low_stock is calculated correctly based on product's current_stock
        if instance.product:
            product_min = instance.product.min_stock_level or 0
            product_current = instance.product.current_stock or 0
            stock_quantity = instance.quantity or 0
            stock_min = instance.min_quantity or 0
            
            # Use product's current_stock as source of truth (prefer product.current_stock)
            # If product.current_stock is None or 0, use stock.quantity
            if product_current > 0:
                effective_quantity = product_current
            elif stock_quantity > 0:
                effective_quantity = stock_quantity
            else:
                effective_quantity = 0
            
            # Determine min stock level - prefer Stock's min_quantity, fallback to Product's min_stock_level
            if stock_min > 0:
                effective_min = stock_min
            elif product_min > 0:
                effective_min = product_min
            else:
                effective_min = 0
            
            # Calculate is_low_stock - only if min_stock is set (> 0)
            if effective_min > 0 and effective_quantity <= effective_min:
                data['is_low_stock'] = True
            else:
                data['is_low_stock'] = False
        else:
            # If no product, use stock's own quantity and min_quantity
            stock_quantity = instance.quantity or 0
            stock_min = instance.min_quantity or 0
            if stock_min > 0 and stock_quantity <= stock_min:
                data['is_low_stock'] = True
            else:
                data['is_low_stock'] = False
        return data


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Inventory transaction serializer"""
    product = ProductListSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ['created_at']

