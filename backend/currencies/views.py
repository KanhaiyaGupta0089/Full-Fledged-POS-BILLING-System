"""
Views for Multi-Currency Support
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Currency, ExchangeRateHistory
from .serializers import CurrencySerializer, ExchangeRateHistorySerializer
from common.permissions import IsAdminOrManager


class CurrencyViewSet(viewsets.ModelViewSet):
    """Currency CRUD operations"""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    search_fields = ['code', 'name']
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """Convert amount from/to this currency"""
        currency = self.get_object()
        amount = request.data.get('amount', 0)
        to_base = request.data.get('to_base', True)
        
        if to_base:
            converted = currency.convert_to_base(amount)
        else:
            converted = currency.convert_from_base(amount)
        
        return Response({
            'original_amount': amount,
            'converted_amount': converted,
            'currency': currency.code
        })


class ExchangeRateHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Exchange Rate History (read-only)"""
    queryset = ExchangeRateHistory.objects.select_related('currency')
    serializer_class = ExchangeRateHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['currency', 'date']





