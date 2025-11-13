"""
Billing views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime
import logging
from .models import Customer, Invoice, InvoiceItem
from .serializers import (
    CustomerSerializer,
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceItemSerializer,
    InvoiceItemCreateSerializer
)
from common.permissions import IsAdminOrManagerOrEmployee
from products.models import Product
from .invoice_generator import generate_invoice_pdf
from .emailer import send_invoice_email
from credit_ledger.models import CustomerCredit, CreditTransaction
from inventory.models import InventoryTransaction, Stock, Warehouse

logger = logging.getLogger(__name__)


class CustomerViewSet(viewsets.ModelViewSet):
    """Customer CRUD operations"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'gstin', 'pan']
    filterset_fields = ['customer_type', 'is_active', 'is_blacklisted']
    ordering_fields = ['name', 'created_at', 'total_purchases']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set created_by on create"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update customer"""
        serializer.save()


class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice CRUD operations"""
    queryset = Invoice.objects.select_related('customer', 'created_by', 'coupon').prefetch_related('items__product')
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'customer']
    search_fields = ['invoice_number', 'customer_name', 'customer_phone']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Add date range filtering"""
        queryset = super().get_queryset()
        
        # Date range filtering
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        """Generate invoice number, set created_by, update inventory, and handle credit"""
        # Generate invoice number
        today = timezone.now().date()
        # Check for existing invoices with the same date prefix
        existing_invoices = Invoice.objects.filter(
            invoice_number__startswith=f"INV-{today.strftime('%Y%m%d')}-"
        )
        if existing_invoices.exists():
            # Get the maximum sequence number for today
            max_seq = 0
            for inv in existing_invoices:
                try:
                    seq = int(inv.invoice_number.split('-')[-1])
                    max_seq = max(max_seq, seq)
                except (ValueError, IndexError):
                    pass
            count = max_seq + 1
        else:
            count = 1
        invoice_number = f"INV-{today.strftime('%Y%m%d')}-{count:04d}"
        
        invoice = serializer.save(
            invoice_number=invoice_number,
            created_by=self.request.user
        )
        
        # Update inventory for each item
        for item in invoice.items.all():
            product = item.product
            if product.is_trackable:
                # Get or create default warehouse
                default_warehouse = Warehouse.objects.first()
                if not default_warehouse:
                    default_warehouse = Warehouse.objects.create(
                        name='Main Warehouse',
                        address='Default Location',
                        is_active=True
                    )
                
                # Update stock
                stock, created = Stock.objects.get_or_create(
                    product=product,
                    warehouse=default_warehouse,
                    defaults={'quantity': 0, 'min_quantity': product.min_stock_level, 'max_quantity': product.max_stock_level}
                )
                stock.quantity -= item.quantity
                if stock.quantity < 0:
                    stock.quantity = 0
                stock.save()
                
                # Update product stock
                product.current_stock -= item.quantity
                if product.current_stock < 0:
                    product.current_stock = 0
                product.save()
                
                # Create inventory transaction
                InventoryTransaction.objects.create(
                    transaction_type='sale',
                    product=product,
                    warehouse=default_warehouse,
                    quantity=-item.quantity,
                    reference_number=invoice.invoice_number,
                    notes=f"Sale - Invoice {invoice.invoice_number}",
                    created_by=self.request.user
                )
        
        # Handle credit (Udhar) - Auto-create credit ledger entry
        if invoice.payment_method == 'credit':
            customer = invoice.customer
            if customer:
                # Get or create credit account
                credit_account, created = CustomerCredit.objects.get_or_create(
                    customer=customer,
                    defaults={'total_credit': 0, 'total_paid': 0, 'balance': 0}
                )
                
                # Create credit transaction
                CreditTransaction.objects.create(
                    customer_credit=credit_account,
                    invoice=invoice,
                    transaction_type='credit',
                    amount=invoice.total_amount,
                    description=f"Credit sale - Invoice {invoice.invoice_number}",
                    created_by=self.request.user
                )
                
                # Update credit account - use Decimal for consistency
                from decimal import Decimal
                amount_decimal = Decimal(str(invoice.total_amount))
                credit_account.total_credit += amount_decimal
                credit_account.balance = credit_account.total_credit - credit_account.total_paid
                credit_account.last_transaction_date = timezone.now()
                credit_account.save()
        
        # Send email with PDF if customer email exists (automatically)
        # Only send email on creation if invoice is already paid (cash) or credit
        # For online/pending payments, email will be sent after payment verification
        # This prevents duplicate emails for online payments
        should_send_email = False
        if invoice.status == 'paid':
            # Send email for already paid invoices (cash, card, etc.)
            should_send_email = True
        elif invoice.payment_method == 'credit':
            # Send email for credit invoices (customer needs invoice even if not paid)
            should_send_email = True
        # For online/pending payments, don't send email here - it will be sent after payment verification
        
        if should_send_email and (invoice.customer_email or (invoice.customer and invoice.customer.email)):
            try:
                success, error_message = send_invoice_email(invoice)
                if success:
                    logger.info(f"Invoice email sent successfully to {invoice.customer_email or invoice.customer.email} for invoice {invoice.invoice_number}")
                else:
                    logger.warning(f"Failed to send invoice email: {error_message} for invoice {invoice.invoice_number}")
            except Exception as e:
                # Don't fail invoice creation if email fails
                logger.error(f"Error sending invoice email: {e} for invoice {invoice.invoice_number}", exc_info=True)
        
        # Return the created invoice with all fields
        # The response will be serialized with InvoiceCreateSerializer which now includes 'id'
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to invoice"""
        invoice = self.get_object()
        serializer = InvoiceItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(invoice=invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process payment for invoice"""
        invoice = self.get_object()
        amount = request.data.get('amount', 0)
        
        if amount <= 0:
            return Response(
                {'error': 'Invalid payment amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.paid_amount += float(amount)
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = 'paid'
            invoice.paid_amount = invoice.total_amount
        elif invoice.paid_amount > 0:
            invoice.status = 'partial'
        
        invoice.save()
        
        # Send email with PDF if customer email exists (automatically after payment)
        if invoice.customer_email or (invoice.customer and invoice.customer.email):
            try:
                success, error_message = send_invoice_email(invoice)
                if success:
                    logger.info(f"Invoice email sent successfully to {invoice.customer_email or invoice.customer.email} for invoice {invoice.invoice_number} after payment")
                else:
                    logger.warning(f"Failed to send invoice email after payment: {error_message} for invoice {invoice.invoice_number}")
            except Exception as e:
                # Don't fail payment processing if email fails
                logger.error(f"Error sending invoice email after payment: {e} for invoice {invoice.invoice_number}", exc_info=True)
        
        return Response(InvoiceSerializer(invoice).data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's invoices"""
        today = timezone.now().date()
        invoices = self.queryset.filter(created_at__date=today)
        serializer = self.get_serializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Download invoice as PDF"""
        invoice = self.get_object()
        pdf_buffer = generate_invoice_pdf(invoice)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send invoice PDF via email"""
        invoice = self.get_object()
        
        # Check if customer has email
        if not invoice.customer_email and not (invoice.customer and invoice.customer.email):
            return Response(
                {'error': 'Customer email address is required. Please add email to customer or invoice.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, error_message = send_invoice_email(invoice)
        
        if success:
            return Response({'message': 'Invoice sent successfully'}, status=status.HTTP_200_OK)
        else:
            error_detail = error_message or 'Failed to send invoice. Please check email configuration and customer email address.'
            return Response(
                {'error': error_detail},
                status=status.HTTP_400_BAD_REQUEST
            )

