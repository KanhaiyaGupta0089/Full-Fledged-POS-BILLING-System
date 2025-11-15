"""
Billing email templates and functions
"""
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .invoice_generator import generate_invoice_pdf
from notifications.models import Notification


def send_invoice_email(invoice):
    """Send invoice PDF to customer via email
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if not invoice.customer_email and not (invoice.customer and invoice.customer.email):
        return False, 'Customer email address is required'
    
    recipient_email = invoice.customer_email or (invoice.customer.email if invoice.customer else None)
    if not recipient_email or recipient_email.strip() == '':
        return False, 'Customer email address is required'
    
    # Validate email format
    try:
        validate_email(recipient_email)
    except ValidationError:
        return False, f'Invalid email address format: {recipient_email}'
    
    try:
        # Generate PDF
        pdf_buffer = generate_invoice_pdf(invoice)
        
        # Prepare email
        subject = f"Invoice {invoice.invoice_number} - POS Billing System"
        customer_name = invoice.customer.name if invoice.customer else invoice.customer_name or 'Customer'
        
        message = f"""
Dear {customer_name},

Thank you for your purchase!

Please find your invoice attached.

Invoice Details:
- Invoice Number: {invoice.invoice_number}
- Date: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}
- Total Amount: ₹{invoice.total_amount}
- Payment Status: {invoice.get_status_display()}
- Payment Method: {invoice.get_payment_method_display()}

Items Purchased:
{chr(10).join([f"  • {item.product.name} x {item.quantity} = ₹{item.total}" for item in invoice.items.all()])}

Payment Summary:
- Subtotal: ₹{invoice.subtotal}
- Discount: ₹{invoice.discount_amount}
- Tax: ₹{invoice.tax_amount}
- Total: ₹{invoice.total_amount}
- Paid: ₹{invoice.paid_amount}
- Balance: ₹{invoice.balance_amount}

Thank you for your business!

Best regards,
POS Billing System
"""
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        
        # Attach PDF
        email.attach(
            f'invoice_{invoice.invoice_number}.pdf',
            pdf_buffer.getvalue(),
            'application/pdf'
        )
        
        # Send email
        email.send()
        
        # Create notification record
        Notification.objects.create(
            notification_type='email',
            subject=subject,
            message=message,
            recipient_email=recipient_email,
            status='sent',
            metadata={'invoice_id': invoice.id, 'invoice_number': invoice.invoice_number}
        )
        
        return True, None
    except Exception as e:
        error_message = str(e)
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to send invoice email: {error_message}', exc_info=True)
        
        # Provide user-friendly error messages for common email errors
        if '535' in error_message or 'BadCredentials' in error_message or 'Username and Password not accepted' in error_message:
            error_message = (
                'Gmail authentication failed. Please check:\n'
                '1. 2-Step Verification is enabled on your Google account\n'
                '2. App Password is generated correctly (16 characters, no spaces)\n'
                '3. App Password is correctly set in environment variables (EMAIL_HOST_PASSWORD)\n'
                '4. No quotes around the password in environment variables\n'
                '5. On Railway: Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in Railway environment variables\n'
                'See backend/GMAIL_SETUP.md for detailed instructions.'
            )
        elif '534' in error_message or 'Application-specific password required' in error_message:
            error_message = (
                'Gmail requires an App Password. Please:\n'
                '1. Enable 2-Step Verification\n'
                '2. Generate an App Password from Google Account settings\n'
                '3. Update EMAIL_HOST_PASSWORD in environment variables\n'
                '4. On Railway: Add EMAIL_HOST_PASSWORD in Railway environment variables\n'
                'See backend/GMAIL_SETUP.md for detailed instructions.'
            )
        elif 'Network is unreachable' in error_message or 'Connection refused' in error_message or 'timeout' in error_message.lower():
            error_message = (
                'Email server connection failed. This might be due to:\n'
                '1. Network restrictions on Railway (SMTP ports may be blocked)\n'
                '2. Email credentials not set in Railway environment variables\n'
                '3. Firewall blocking SMTP connections\n'
                'Solutions:\n'
                '- Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in Railway environment variables\n'
                '- Consider using a service like SendGrid, Mailgun, or AWS SES instead of Gmail\n'
                '- Check Railway logs for more details\n'
                'For now, emails will be logged but not sent.'
            )
        elif 'Connection timed out' in error_message or 'timed out' in error_message.lower():
            error_message = (
                'Email server connection timed out. This might be due to:\n'
                '1. Network restrictions on Railway\n'
                '2. SMTP server is down or unreachable\n'
                '3. Firewall blocking connections\n'
                'Please check your email configuration and network settings.'
            )
        
        # Create failed notification record
        try:
            Notification.objects.create(
                notification_type='email',
                subject=f"Invoice {invoice.invoice_number}",
                message=message if 'message' in locals() else '',
                recipient_email=recipient_email if 'recipient_email' in locals() else None,
                status='failed',
                error_message=error_message,
                metadata={'invoice_id': invoice.id, 'invoice_number': invoice.invoice_number}
            )
        except Exception:
            # If notification creation fails, just log the error
            pass
        return False, error_message

