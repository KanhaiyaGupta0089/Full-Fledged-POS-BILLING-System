"""
Discounts serializers
"""
from rest_framework import serializers
from .models import Coupon, Discount


class CouponSerializer(serializers.ModelSerializer):
    """Coupon serializer"""
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['used_count', 'created_at', 'updated_at']


class DiscountSerializer(serializers.ModelSerializer):
    """Discount serializer"""
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']







