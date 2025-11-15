"""
Returns serializers
"""
from rest_framework import serializers
from .models import Return, ReturnItem
from billing.serializers import InvoiceSerializer
from products.serializers import ProductListSerializer


class ReturnItemSerializer(serializers.ModelSerializer):
    """Return item serializer"""
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = ReturnItem
        fields = '__all__'


class ReturnSerializer(serializers.ModelSerializer):
    """Return serializer"""
    invoice = InvoiceSerializer(read_only=True)
    items = ReturnItemSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Return
        fields = '__all__'
        read_only_fields = ['return_number', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        """Get created by name safely"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
    
    def get_approved_by_name(self, obj):
        """Get approved by name safely"""
        if obj.approved_by:
            return obj.approved_by.get_full_name() or obj.approved_by.username
        return None


class ReturnCreateSerializer(serializers.ModelSerializer):
    """Return create serializer"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Return
        fields = ['invoice', 'reason', 'reason_description', 'notes', 'items']








