"""
Credit Ledger views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import CustomerCredit, CreditTransaction
from .serializers import CustomerCreditSerializer, CreditTransactionSerializer
from billing.models import Customer, Invoice
from common.permissions import IsAdminOrManager, IsAdminOrManagerOrEmployee


class CustomerCreditViewSet(viewsets.ModelViewSet):
    """Customer credit CRUD operations"""
    queryset = CustomerCredit.objects.select_related('customer').prefetch_related('transactions')
    serializer_class = CustomerCreditSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filterset_fields = ['customer']
    search_fields = ['customer__name', 'customer__phone']
    ordering_fields = ['balance', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def add_credit(self, request, pk=None):
        """Add credit to customer account"""
        credit_account = self.get_object()
        amount = request.data.get('amount')
        invoice_id = request.data.get('invoice_id')
        description = request.data.get('description', '')
        
        if not amount or float(amount) <= 0:
            return Response(
                {'error': 'Valid amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice = None
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id)
            except Invoice.DoesNotExist:
                pass
        
        # Create transaction
        transaction = CreditTransaction.objects.create(
            customer_credit=credit_account,
            invoice=invoice,
            transaction_type='credit',
            amount=amount,
            description=description,
            created_by=request.user
        )
        
        # Update credit account - use Decimal for consistency
        from decimal import Decimal
        amount_decimal = Decimal(str(amount))
        credit_account.total_credit += amount_decimal
        credit_account.balance = credit_account.total_credit - credit_account.total_paid
        credit_account.last_transaction_date = timezone.now()
        credit_account.save()
        
        return Response(CreditTransactionSerializer(transaction).data)
    
    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record payment received from customer"""
        credit_account = self.get_object()
        amount = request.data.get('amount')
        description = request.data.get('description', '')
        
        if not amount or float(amount) <= 0:
            return Response(
                {'error': 'Valid amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if float(amount) > credit_account.balance:
            return Response(
                {'error': 'Payment amount exceeds outstanding balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create transaction
        transaction = CreditTransaction.objects.create(
            customer_credit=credit_account,
            transaction_type='payment',
            amount=amount,
            description=description,
            created_by=request.user
        )
        
        # Update credit account - use Decimal for consistency
        from decimal import Decimal
        amount_decimal = Decimal(str(amount))
        credit_account.total_paid += amount_decimal
        credit_account.balance = credit_account.total_credit - credit_account.total_paid
        credit_account.last_transaction_date = timezone.now()
        credit_account.save()
        
        return Response(CreditTransactionSerializer(transaction).data)
    
    @action(detail=False, methods=['get'])
    def outstanding(self, request):
        """Get all customers with outstanding credit"""
        credits = self.queryset.filter(balance__gt=0)
        serializer = self.get_serializer(credits, many=True)
        return Response(serializer.data)


class CreditTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Credit transaction viewset (read-only)"""
    queryset = CreditTransaction.objects.select_related('customer_credit__customer', 'invoice', 'created_by')
    serializer_class = CreditTransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filterset_fields = ['transaction_type', 'customer_credit']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

