"""
Razorpay Payment Gateway Integration Service
"""
import razorpay
from razorpay import errors as razorpay_errors

from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Initialize Razorpay client
razorpay_client = None
try:
    RAZORPAY_KEY_ID = getattr(settings, 'RAZORPAY_KEY_ID', None)
    RAZORPAY_KEY_SECRET = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
    
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and RAZORPAY_KEY_ID.strip() and RAZORPAY_KEY_SECRET.strip():
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        logger.info("Razorpay client initialized successfully")
    else:
        razorpay_client = None
        logger.warning("Razorpay credentials not configured or empty. Payment gateway will not work.")
except Exception as e:
    razorpay_client = None
    logger.error(f"Failed to initialize Razorpay client: {e}", exc_info=True)


class RazorpayService:
    """Razorpay payment gateway service"""
    
    @staticmethod
    def create_order(amount, currency='INR', receipt=None, notes=None):
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in paise (e.g., 10000 for ₹100.00)
            currency: Currency code (default: INR)
            receipt: Receipt ID (optional)
            notes: Additional notes (optional)
        
        Returns:
            dict: Order details with order_id
        """
        if not razorpay_client:
            error_msg = "Razorpay client not initialized. Please configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your .env file."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            # Convert to paise (Razorpay expects amount in smallest currency unit)
            amount_in_paise = int(round(amount * 100))
            
            # Minimum amount check (1 rupee = 100 paise)
            if amount_in_paise < 100:
                raise ValueError("Amount must be at least ₹1.00")
            
            order_data = {
                'amount': amount_in_paise,
                'currency': currency,
            }
            
            if receipt:
                # Razorpay receipt must be max 40 characters, alphanumeric and hyphens only
                receipt_clean = ''.join(c for c in receipt if c.isalnum() or c in '-_')[:40]
                order_data['receipt'] = receipt_clean
            
            if notes:
                order_data['notes'] = notes
            
            logger.info(f"Creating Razorpay order with data: {order_data}")
            order = razorpay_client.order.create(data=order_data)
            
            logger.info(f"Razorpay order created successfully: {order.get('id')}")
            return {
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'status': order['status'],
            }
        except razorpay_errors.BadRequestError as e:
            logger.error(f"Razorpay BadRequestError: {e}")
            raise Exception(f"Invalid payment request: {str(e)}")
        except razorpay_errors.ServerError as e:
            logger.error(f"Razorpay ServerError: {e}")
            raise Exception(f"Payment gateway server error: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}", exc_info=True)
            raise Exception(f"Failed to create payment order: {str(e)}")
    
    @staticmethod
    def verify_payment_signature(order_id, payment_id, signature):
        """
        Verify Razorpay payment signature
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Payment signature from Razorpay
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not razorpay_client:
            raise Exception("Razorpay client not initialized.")
        
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            razorpay_client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay_errors.SignatureVerificationError:
            logger.error("Razorpay signature verification failed")
            return False
        except Exception as e:
            logger.error(f"Error verifying Razorpay signature: {e}")
            return False
    
    @staticmethod
    def fetch_payment(payment_id):
        """
        Fetch payment details from Razorpay
        
        Args:
            payment_id: Razorpay payment ID
        
        Returns:
            dict: Payment details
        """
        if not razorpay_client:
            raise Exception("Razorpay client not initialized.")
        
        try:
            payment = razorpay_client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to fetch payment from Razorpay: {e}")
            raise Exception(f"Failed to fetch payment: {str(e)}")
    
    @staticmethod
    def refund_payment(payment_id, amount=None, notes=None):
        """
        Create a refund for a payment
        
        Args:
            payment_id: Razorpay payment ID
            amount: Refund amount in paise (if None, full refund)
            notes: Refund notes (optional)
        
        Returns:
            dict: Refund details
        """
        if not razorpay_client:
            raise Exception("Razorpay client not initialized.")
        
        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to paise
            if notes:
                refund_data['notes'] = notes
            
            refund = razorpay_client.payment.refund(payment_id, refund_data)
            return refund
        except Exception as e:
            logger.error(f"Failed to create refund: {e}")
            raise Exception(f"Failed to create refund: {str(e)}")

