"""
Celery tasks for Inventory automation
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Q, F
import logging
from .models import Stock, Warehouse
from .advanced_models import AutoReorderRule, Batch, StockValuation

logger = logging.getLogger(__name__)


@shared_task
def check_reorder_points_task():
    """
    Scheduled task to check reorder points and trigger auto PO creation
    Runs every 4 hours
    """
    try:
        logger.info("Checking reorder points...")
        reorder_rules = AutoReorderRule.objects.filter(is_active=True, auto_create_po=True)
        
        triggered_count = 0
        for rule in reorder_rules:
            try:
                result = rule.check_and_reorder()
                if result:
                    triggered_count += 1
                    logger.info(f"Triggered reorder for {rule.product.name}")
            except Exception as e:
                logger.error(f"Error checking reorder rule for {rule.product.name}: {e}")
        
        logger.info(f"Checked {reorder_rules.count()} reorder rules, triggered {triggered_count} reorders")
        return {
            'success': True,
            'rules_checked': reorder_rules.count(),
            'reorders_triggered': triggered_count
        }
    except Exception as e:
        logger.error(f"Error in reorder points check task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def calculate_stock_valuations_task():
    """
    Scheduled task to calculate stock valuations using different methods
    Runs daily at midnight
    """
    try:
        logger.info("Calculating stock valuations...")
        products = Stock.objects.values_list('product', 'warehouse').distinct()
        
        calculated_count = 0
        for product_id, warehouse_id in products:
            try:
                for method in ['fifo', 'lifo', 'average']:
                    valuation, created = StockValuation.objects.get_or_create(
                        product_id=product_id,
                        warehouse_id=warehouse_id,
                        valuation_method=method,
                        defaults={
                            'total_quantity': 0,
                            'total_value': 0,
                            'average_cost': 0
                        }
                    )
                    valuation.calculate_valuation()
                    calculated_count += 1
            except Exception as e:
                logger.error(f"Error calculating valuation for product {product_id}: {e}")
        
        logger.info(f"Calculated {calculated_count} stock valuations")
        return {
            'success': True,
            'valuations_calculated': calculated_count
        }
    except Exception as e:
        logger.error(f"Error in stock valuations task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def check_low_stock_alerts_task():
    """
    Scheduled task to check for low stock and send alerts
    Runs every 2 hours
    """
    try:
        logger.info("Checking for low stock items...")
        low_stock_items = Stock.objects.filter(
            Q(quantity__lte=F('min_quantity')) | 
            Q(product__current_stock__lte=F('product__min_stock_level'))
        ).exclude(min_quantity=0)
        
        alert_count = 0
        from notifications.emailer import send_low_stock_alert
        
        for stock in low_stock_items:
            try:
                if stock.is_low_stock:
                    send_low_stock_alert(stock)
                    alert_count += 1
            except Exception as e:
                logger.error(f"Error sending low stock alert for {stock.product.name}: {e}")
        
        logger.info(f"Found {low_stock_items.count()} low stock items, sent {alert_count} alerts")
        return {
            'success': True,
            'low_stock_items': low_stock_items.count(),
            'alerts_sent': alert_count
        }
    except Exception as e:
        logger.error(f"Error in low stock alerts task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_expired_batches_task():
    """
    Scheduled task to mark expired batches and update stock
    Runs daily
    """
    try:
        logger.info("Cleaning up expired batches...")
        from django.utils import timezone
        today = timezone.now().date()
        
        expired_batches = Batch.objects.filter(
            expiry_date__lt=today,
            is_active=True,
            quantity__gt=0
        )
        
        updated_count = 0
        for batch in expired_batches:
            try:
                # Mark as inactive
                batch.is_active = False
                batch.save()
                
                # Create inventory transaction for expiry
                from .models import InventoryTransaction
                InventoryTransaction.objects.create(
                    transaction_type='expired',
                    product=batch.product,
                    warehouse=batch.warehouse,
                    quantity=-batch.quantity,
                    reference_number=f'EXP-{batch.batch_number}',
                    notes=f'Batch {batch.batch_number} expired on {batch.expiry_date}',
                    created_by=None
                )
                
                # Update stock
                try:
                    stock = Stock.objects.get(
                        product=batch.product,
                        warehouse=batch.warehouse
                    )
                    stock.quantity = max(0, stock.quantity - batch.quantity)
                    stock.save()
                except Stock.DoesNotExist:
                    pass
                
                updated_count += 1
            except Exception as e:
                logger.error(f"Error processing expired batch {batch.batch_number}: {e}")
        
        logger.info(f"Processed {updated_count} expired batches")
        return {
            'success': True,
            'expired_batches': updated_count
        }
    except Exception as e:
        logger.error(f"Error in expired batches cleanup task: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

