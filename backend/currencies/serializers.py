"""
Serializers for Multi-Currency Support
"""
from rest_framework import serializers
from .models import Currency, ExchangeRateHistory


class CurrencySerializer(serializers.ModelSerializer):
    """Currency serializer"""
    class Meta:
        model = Currency
        fields = '__all__'
        read_only_fields = ['last_updated']


class ExchangeRateHistorySerializer(serializers.ModelSerializer):
    """Exchange Rate History serializer"""
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    
    class Meta:
        model = ExchangeRateHistory
        fields = '__all__'




