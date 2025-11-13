"""
Billing serializers
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Customer, Invoice, InvoiceItem
from products.serializers import ProductListSerializer


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


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Invoice item serializer"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 
                 'discount', 'tax_rate', 'tax_amount', 'total']
        read_only_fields = ['tax_amount', 'total']


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    """Invoice item create serializer (without nested product)"""
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'unit_price', 'discount', 'tax_rate']


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer"""
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_name_display = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['invoice_number', 'created_at', 'updated_at', 'balance_amount']
    
    def get_customer_name_display(self, obj):
        """Get customer name or walk-in customer name"""
        if obj.customer:
            return obj.customer.name
        return obj.customer_name or 'Walk-in Customer'
    
    def get_created_by_name(self, obj):
        """Get created by name safely"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Invoice create serializer"""
    items = InvoiceItemCreateSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'customer_name', 'customer_phone', 'customer_email',
                 'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
                 'paid_amount', 'coupon', 'discount_percentage', 'payment_method',
                 'status', 'notes', 'items', 'invoice_number', 'created_at']
        read_only_fields = ['id', 'invoice_number', 'created_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        
        # Create invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Refresh from database to ensure id is available
        invoice.refresh_from_db()
        return invoice

