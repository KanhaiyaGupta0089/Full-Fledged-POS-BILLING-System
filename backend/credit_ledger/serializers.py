"""
Credit Ledger serializers
"""
from rest_framework import serializers
from .models import CustomerCredit, CreditTransaction
from billing.serializers import CustomerSerializer


class CreditTransactionSerializer(serializers.ModelSerializer):
    """Credit transaction serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = CreditTransaction
        fields = '__all__'
        read_only_fields = ['created_at']


class CustomerCreditSerializer(serializers.ModelSerializer):
    """Customer credit serializer"""
    customer = CustomerSerializer(read_only=True)
    transactions = CreditTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomerCredit
        fields = '__all__'
        read_only_fields = ['balance', 'created_at', 'updated_at', 'last_transaction_date']








