"""
Celery tasks for Purchase Orders automation
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from .automation import check_low_stock_and_create_po, auto_update_supplier_performance, check_expiring_products
from .models import Supplier, PurchaseOrder

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock_and_create_pos_task():
    """
    Scheduled task to check for low stock and automatically create purchase orders
    Runs daily at 9 AM
    """
    try:
        logger.info("Starting automated low stock check and PO creation...")
        created_pos = check_low_stock_and_create_po()
        logger.info(f"Created {len(created_pos)} purchase orders automatically")
        return {
            'success': True,
            'pos_created': len(created_pos),
            'po_numbers': [po.po_number for po in created_pos]
        }
    except Exception as e:
        logger.error(f"Error in low stock check task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def update_supplier_performance_task():
    """
    Scheduled task to update supplier performance metrics
    Runs weekly on Monday
    """
    try:
        logger.info("Updating supplier performance metrics...")
        suppliers = Supplier.objects.filter(is_active=True)
        updated_count = 0
        
        for supplier in suppliers:
            try:
                auto_update_supplier_performance(supplier)
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating supplier {supplier.name}: {e}")
        
        logger.info(f"Updated performance metrics for {updated_count} suppliers")
        return {
            'success': True,
            'suppliers_updated': updated_count
        }
    except Exception as e:
        logger.error(f"Error in supplier performance update task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def check_expiring_products_task(days_ahead=30):
    """
    Scheduled task to check for products expiring soon
    Runs daily
    """
    try:
        logger.info(f"Checking for products expiring in next {days_ahead} days...")
        expiring_batches = check_expiring_products(days_ahead)
        
        # Send alerts for expiring products
        from notifications.emailer import send_expiry_alert
        alert_count = 0
        
        for batch in expiring_batches:
            try:
                days_to_expiry = batch.days_to_expiry
                if days_to_expiry and days_to_expiry <= days_ahead:
                    # Send alert
                    send_expiry_alert(batch)
                    alert_count += 1
            except Exception as e:
                logger.error(f"Error sending expiry alert for batch {batch.batch_number}: {e}")
        
        logger.info(f"Found {expiring_batches.count()} expiring batches, sent {alert_count} alerts")
        return {
            'success': True,
            'expiring_batches': expiring_batches.count(),
            'alerts_sent': alert_count
        }
    except Exception as e:
        logger.error(f"Error in expiring products check task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def auto_approve_pending_pos_task():
    """
    Scheduled task to auto-approve pending POs that meet criteria
    Runs hourly
    """
    try:
        logger.info("Checking for POs to auto-approve...")
        pending_pos = PurchaseOrder.objects.filter(
            status='draft',
            auto_approve=True
        )
        
        approved_count = 0
        for po in pending_pos:
            try:
                po.status = 'approved'
                po.approved_at = timezone.now()
                po.save()
                approved_count += 1
                logger.info(f"Auto-approved PO {po.po_number}")
            except Exception as e:
                logger.error(f"Error auto-approving PO {po.po_number}: {e}")
        
        logger.info(f"Auto-approved {approved_count} purchase orders")
        return {
            'success': True,
            'pos_approved': approved_count
        }
    except Exception as e:
        logger.error(f"Error in auto-approve POs task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }




