"""
Payments serializers
"""
from rest_framework import serializers
from .models import PaymentMethod, Payment


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Payment method serializer"""
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ['created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

