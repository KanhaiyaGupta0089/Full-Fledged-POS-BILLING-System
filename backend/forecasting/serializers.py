"""
Serializers for Forecasting
"""
from rest_framework import serializers
from decimal import Decimal
from .models import SalesForecast, DemandPattern, OptimalStockLevel
from products.serializers import ProductListSerializer
from inventory.serializers import WarehouseSerializer


class SalesForecastSerializer(serializers.ModelSerializer):
    """Sales Forecast serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True, allow_null=True)
    accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, allow_null=True)
    predicted_quantity = serializers.IntegerField()
    predicted_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    confidence_level = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        model = SalesForecast
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DemandPatternSerializer(serializers.ModelSerializer):
    """Demand Pattern serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DemandPattern
        fields = '__all__'
        read_only_fields = ['last_analyzed', 'created_at']


class OptimalStockLevelSerializer(serializers.ModelSerializer):
    """Optimal Stock Level serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = OptimalStockLevel
        fields = '__all__'
        read_only_fields = ['calculated_at', 'created_at']




