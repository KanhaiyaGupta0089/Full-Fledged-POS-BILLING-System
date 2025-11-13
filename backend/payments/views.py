"""
Payments views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal
from .models import PaymentMethod, Payment
from .serializers import PaymentMethodSerializer, PaymentSerializer
from billing.models import Invoice
from common.permissions import IsAdminOrManager, IsAdminOrManagerOrEmployee
from .razorpay_service import RazorpayService
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """Payment method CRUD operations"""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class PaymentViewSet(viewsets.ModelViewSet):
    """Payment CRUD operations"""
    queryset = Payment.objects.select_related('invoice', 'payment_method', 'processed_by')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filterset_fields = ['status', 'payment_method', 'invoice']
    search_fields = ['transaction_id', 'payment_reference']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set processed_by on payment creation"""
        serializer.save(processed_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create Razorpay order for payment"""
        invoice_id = request.data.get('invoice_id')
        
        logger.info(f"Creating Razorpay order for invoice_id: {invoice_id}")
        
        if not invoice_id:
            return Response(
                {'error': 'invoice_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            logger.info(f"Invoice found: {invoice.invoice_number}, Total: {invoice.total_amount}, Balance: {invoice.balance_amount}, Paid: {invoice.paid_amount}")
            
            # Refresh invoice to ensure latest data
            invoice.refresh_from_db()
            
            # Calculate amount to be paid (balance amount or total amount if not paid)
            # For online payments, invoice is created with paid_amount=0, so balance = total
            from decimal import Decimal
            balance = Decimal(str(invoice.balance_amount))
            total = Decimal(str(invoice.total_amount))
            amount_to_pay = float(balance if balance > 0 else total)
            
            if amount_to_pay <= 0:
                return Response(
                    {'error': 'Invoice is already fully paid'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Minimum amount check (Razorpay requires at least 1 rupee = 100 paise)
            if amount_to_pay < 1:
                return Response(
                    {'error': 'Payment amount must be at least ₹1.00'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create Razorpay order
            try:
                # Ensure receipt is valid (max 40 characters, alphanumeric and hyphens only)
                receipt = f'INV-{invoice.invoice_number}'[:40]
                
                order_data = RazorpayService.create_order(
                    amount=amount_to_pay,
                    currency='INR',
                    receipt=receipt,
                    notes={
                        'invoice_id': str(invoice.id),
                        'invoice_number': invoice.invoice_number,
                        'customer_name': invoice.customer_name or (invoice.customer.name if invoice.customer else 'Walk-in'),
                    }
                )
                
                return Response({
                    'order_id': order_data['order_id'],
                    'amount': order_data['amount'],
                    'currency': order_data['currency'],
                    'key_id': request.data.get('key_id'),  # Frontend will send this
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'amount_to_pay': amount_to_pay,
                })
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"Failed to create Razorpay order: {e}\n{error_trace}")
                error_message = str(e)
                # Provide more helpful error messages
                if 'Razorpay client not initialized' in error_message:
                    error_message = 'Payment gateway not configured. Please contact administrator.'
                elif 'Bad Request' in error_message or '400' in error_message:
                    error_message = 'Invalid payment request. Please check invoice details.'
                elif 'amount' in error_message.lower() or 'paise' in error_message.lower():
                    error_message = f'Invalid payment amount: {error_message}'
                return Response(
                    {
                        'error': f'Failed to create payment order: {error_message}',
                        'details': str(e) if DEBUG else None
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_order: {e}", exc_info=True)
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """Verify Razorpay payment and update invoice"""
        invoice_id = request.data.get('invoice_id')
        order_id = request.data.get('order_id')
        payment_id = request.data.get('payment_id')
        signature = request.data.get('signature')
        
        if not all([invoice_id, order_id, payment_id, signature]):
            return Response(
                {'error': 'invoice_id, order_id, payment_id, and signature are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            
            # Verify payment signature
            is_valid = RazorpayService.verify_payment_signature(
                order_id=order_id,
                payment_id=payment_id,
                signature=signature
            )
            
            if not is_valid:
                return Response(
                    {'error': 'Invalid payment signature'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Fetch payment details from Razorpay
            try:
                payment_details = RazorpayService.fetch_payment(payment_id)
                
                # Get or create payment method
                payment_method = PaymentMethod.objects.get_or_create(
                    code='razorpay',
                    defaults={'name': 'Razorpay (Online)', 'is_active': True}
                )[0]
                
                # Calculate amount paid (convert from paise to rupees)
                amount_paid = float(payment_details['amount']) / 100
                
                # Create payment record
                payment = Payment.objects.create(
                    invoice=invoice,
                    payment_method=payment_method,
                    amount=Decimal(str(amount_paid)),
                    transaction_id=payment_id,
                    payment_reference=order_id,
                    status='completed',
                    processed_by=request.user,
                    notes=f"Razorpay Payment - Order: {order_id}"
                )
                
                # Update invoice payment
                invoice.paid_amount += Decimal(str(amount_paid))
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = 'paid'
                    invoice.paid_amount = invoice.total_amount
                else:
                    invoice.status = 'partial'
                
                # Update payment method if needed
                if invoice.payment_method == 'cash':
                    invoice.payment_method = 'upi'  # Online payment via UPI/Card
                elif invoice.payment_method not in ['upi', 'card']:
                    invoice.payment_method = 'mixed'
                
                invoice.save()
                
                # Send email with PDF if customer email exists (automatically after payment)
                from billing.emailer import send_invoice_email
                if invoice.customer_email or (invoice.customer and invoice.customer.email):
                    try:
                        success, error_message = send_invoice_email(invoice)
                        if success:
                            logger.info(f"Invoice email sent successfully to {invoice.customer_email or invoice.customer.email} for invoice {invoice.invoice_number} after payment")
                        else:
                            logger.warning(f"Failed to send invoice email after payment: {error_message} for invoice {invoice.invoice_number}")
                    except Exception as e:
                        # Don't fail payment verification if email fails
                        logger.error(f"Error sending invoice email after payment: {e} for invoice {invoice.invoice_number}", exc_info=True)
                
                return Response({
                    'success': True,
                    'message': 'Payment verified and processed successfully',
                    'payment': PaymentSerializer(payment).data,
                    'invoice': {
                        'id': invoice.id,
                        'invoice_number': invoice.invoice_number,
                        'status': invoice.status,
                        'paid_amount': float(invoice.paid_amount),
                        'balance_amount': float(invoice.balance_amount),
                    }
                })
            except Exception as e:
                logger.error(f"Failed to fetch payment from Razorpay: {e}")
                return Response(
                    {'error': f'Failed to verify payment: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def process_upi(self, request):
        """Process UPI payment (manual entry)"""
        invoice_id = request.data.get('invoice_id')
        amount = request.data.get('amount')
        transaction_id = request.data.get('transaction_id')
        
        if not all([invoice_id, amount, transaction_id]):
            return Response(
                {'error': 'invoice_id, amount, and transaction_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            payment_method = PaymentMethod.objects.get_or_create(
                code='upi',
                defaults={'name': 'UPI', 'is_active': True}
            )[0]
            
            payment = Payment.objects.create(
                invoice=invoice,
                payment_method=payment_method,
                amount=Decimal(str(amount)),
                transaction_id=transaction_id,
                status='completed',
                processed_by=request.user
            )
            
            # Update invoice payment
            invoice.paid_amount += Decimal(str(amount))
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'paid'
                invoice.paid_amount = invoice.total_amount
            else:
                invoice.status = 'partial'
            invoice.save()
            
            return Response(PaymentSerializer(payment).data)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['POST'])
@permission_classes([AllowAny])  # Razorpay webhook doesn't use JWT
@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook callbacks"""
    try:
        # Get webhook data
        webhook_data = request.data
        event = webhook_data.get('event')
        payload = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
        
        payment_id = payload.get('id')
        order_id = payload.get('order_id')
        status = payload.get('status')
        
        if event == 'payment.captured' and status == 'captured':
            # Payment successful - find invoice by order_id
            # Order receipt format: INV-{invoice_number}
            receipt = payload.get('receipt', '')
            
            if receipt.startswith('INV-'):
                invoice_number = receipt.replace('INV-', '')
                try:
                    invoice = Invoice.objects.get(invoice_number=invoice_number)
                    
                    # Check if payment already processed
                    existing_payment = Payment.objects.filter(transaction_id=payment_id).first()
                    if existing_payment:
                        return Response({'status': 'already_processed'})
                    
                    # Get or create payment method
                    payment_method = PaymentMethod.objects.get_or_create(
                        code='razorpay',
                        defaults={'name': 'Razorpay (Online)', 'is_active': True}
                    )[0]
                    
                    # Calculate amount paid (convert from paise to rupees)
                    amount_paid = float(payload.get('amount', 0)) / 100
                    
                    # Create payment record
                    Payment.objects.create(
                        invoice=invoice,
                        payment_method=payment_method,
                        amount=Decimal(str(amount_paid)),
                        transaction_id=payment_id,
                        payment_reference=order_id,
                        status='completed',
                        notes=f"Razorpay Webhook - {event}"
                    )
                    
                    # Update invoice payment
                    invoice.paid_amount += Decimal(str(amount_paid))
                    if invoice.paid_amount >= invoice.total_amount:
                        invoice.status = 'paid'
                        invoice.paid_amount = invoice.total_amount
                    else:
                        invoice.status = 'partial'
                    invoice.save()
                    
                    return Response({'status': 'success'})
                except Invoice.DoesNotExist:
                    logger.error(f"Invoice not found for webhook: {invoice_number}")
                    return Response({'status': 'invoice_not_found'}, status=404)
        
        return Response({'status': 'ignored'})
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return Response({'status': 'error', 'message': str(e)}, status=500)

