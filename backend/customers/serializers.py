"""
Serializers for Customer Management
"""
from rest_framework import serializers
from decimal import Decimal
from billing.models import Customer
from billing.customer_extras import CustomerPurchaseHistory, CustomerCommunication


class CustomerSerializer(serializers.ModelSerializer):
    """Customer serializer"""
    current_credit_balance = serializers.SerializerMethodField()
    average_order_value = serializers.SerializerMethodField()
    lifetime_value = serializers.SerializerMethodField()
    date_of_birth = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y'])
    anniversary_date = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y'])
    
    def to_internal_value(self, data):
        """Convert empty strings to None for date fields"""
        if isinstance(data, dict):
            # Convert empty strings to None for date fields
            for field in ['date_of_birth', 'anniversary_date']:
                if field in data and data[field] == '':
                    data[field] = None
        return super().to_internal_value(data)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'loyalty_points', 'total_purchases', 'total_orders', 'last_purchase_date', 'created_by']
        extra_kwargs = {
            'phone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
        }
    
    def get_current_credit_balance(self, obj):
        """Get current credit balance safely"""
        try:
            value = obj.current_credit_balance
            if isinstance(value, Decimal):
                return float(value)
            return float(value) if value else 0.00
        except (Exception, AttributeError, TypeError, ValueError):
            return 0.00
    
    def get_average_order_value(self, obj):
        """Get average order value safely"""
        try:
            value = obj.average_order_value
            if isinstance(value, Decimal):
                return float(value)
            return float(value) if value else 0.00
        except (Exception, AttributeError, ZeroDivisionError, TypeError, ValueError):
            return 0.00
    
    def get_lifetime_value(self, obj):
        """Get lifetime value safely"""
        try:
            value = obj.lifetime_value
            if isinstance(value, Decimal):
                return float(value)
            return float(value) if value else 0.00
        except (Exception, AttributeError, TypeError, ValueError):
            return 0.00
    
    def validate_phone(self, value):
        """Validate phone number"""
        if value and len(value) > 15:
            raise serializers.ValidationError("Phone number must be 15 characters or less")
        return value
    
    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        if value:
            from datetime import date as date_class
            if value > date_class.today():
                raise serializers.ValidationError("Date of birth cannot be in the future")
        return value
    
    def validate_anniversary_date(self, value):
        """Validate anniversary date"""
        # Anniversary date can be in the future (for upcoming anniversaries)
        return value


class CustomerPurchaseHistorySerializer(serializers.ModelSerializer):
    """Customer Purchase History serializer"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = CustomerPurchaseHistory
        fields = '__all__'
        read_only_fields = ['created_at']


class CustomerCommunicationSerializer(serializers.ModelSerializer):
    """Customer Communication serializer"""
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)
    
    class Meta:
        model = CustomerCommunication
        fields = '__all__'
        read_only_fields = ['sent_at']

