"""
Automation logic for Purchase Orders and Inventory
"""
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import logging

from purchases.models import PurchaseOrder, PurchaseOrderItem, Supplier
from inventory.models import Stock, Warehouse
from inventory.advanced_models import AutoReorderRule, Batch
from products.models import Product

logger = logging.getLogger(__name__)


def check_low_stock_and_create_po():
    """
    Automatically check for low stock and create purchase orders
    This should be run periodically (via Celery beat)
    """
    created_pos = []
    
    # Get all active reorder rules
    reorder_rules = AutoReorderRule.objects.filter(is_active=True, auto_create_po=True)
    
    for rule in reorder_rules:
        try:
            stock = Stock.objects.get(product=rule.product, warehouse=rule.warehouse)
            
            # Check if stock is at or below reorder point
            if stock.quantity <= rule.reorder_point:
                # Check if there's already a pending PO for this product
                existing_po = PurchaseOrder.objects.filter(
                    status__in=['draft', 'pending', 'approved', 'sent'],
                    items__product=rule.product,
                    warehouse=rule.warehouse
                ).first()
                
                if not existing_po:
                    # Create new PO
                    po = create_auto_po(rule)
                    if po:
                        created_pos.append(po)
                        logger.info(f"Auto-created PO {po.po_number} for {rule.product.name}")
        except Stock.DoesNotExist:
            # Stock doesn't exist, create it
            stock = Stock.objects.create(
                product=rule.product,
                warehouse=rule.warehouse,
                quantity=0,
                min_quantity=rule.reorder_point,
                max_quantity=rule.max_stock_level
            )
            # Create PO
            po = create_auto_po(rule)
            if po:
                created_pos.append(po)
        except Exception as e:
            logger.error(f"Error creating auto PO for {rule.product.name}: {e}")
    
    return created_pos


def create_auto_po(reorder_rule):
    """Create purchase order automatically based on reorder rule"""
    try:
        supplier = reorder_rule.preferred_supplier
        
        # If no preferred supplier, find best supplier for this product
        if not supplier:
            supplier = find_best_supplier_for_product(reorder_rule.product)
        
        if not supplier:
            logger.warning(f"No supplier found for product {reorder_rule.product.name}")
            return None
        
        # Create PO
        po = PurchaseOrder.objects.create(
            supplier=supplier,
            warehouse=reorder_rule.warehouse,
            status='draft',
            auto_create_on_low_stock=True,
            auto_approve=reorder_rule.auto_create_po,
            notes=f"Auto-created due to low stock. Reorder point: {reorder_rule.reorder_point}, Current stock: {get_current_stock(reorder_rule.product, reorder_rule.warehouse)}"
        )
        
        # Get product cost price or last purchase price
        unit_price = get_product_purchase_price(reorder_rule.product, supplier)
        
        # Create PO item
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=reorder_rule.product,
            quantity=reorder_rule.reorder_quantity,
            unit_price=unit_price,
            tax_rate=reorder_rule.product.tax_rate or Decimal('0.00')
        )
        
        # Recalculate PO totals
        recalculate_po_totals(po)
        
        return po
    except Exception as e:
        logger.error(f"Error creating auto PO: {e}")
        return None


def find_best_supplier_for_product(product):
    """Find best supplier for a product based on past performance"""
    # Get suppliers who have supplied this product before
    suppliers = Supplier.objects.filter(
        purchase_orders__items__product=product,
        is_active=True
    ).distinct()
    
    if not suppliers.exists():
        # Return first active supplier if no history
        return Supplier.objects.filter(is_active=True).first()
    
    # Find supplier with best rating and delivery time
    best_supplier = None
    best_score = 0
    
    for supplier in suppliers:
        # Calculate score: rating * 0.6 + (1/delivery_time) * 0.4
        rating_score = float(supplier.rating) * 0.6
        delivery_score = 0.4
        if supplier.average_delivery_time > 0:
            delivery_score = (1.0 / supplier.average_delivery_time) * 0.4
        
        score = rating_score + delivery_score
        
        if score > best_score:
            best_score = score
            best_supplier = supplier
    
    return best_supplier or suppliers.first()


def get_product_purchase_price(product, supplier):
    """Get product purchase price from last purchase or cost price"""
    # Try to get last purchase price from this supplier
    last_po_item = PurchaseOrderItem.objects.filter(
        purchase_order__supplier=supplier,
        product=product,
        purchase_order__status='received'
    ).order_by('-purchase_order__order_date').first()
    
    if last_po_item:
        return last_po_item.unit_price
    
    # Fallback to product cost price
    return product.cost_price or Decimal('0.00')


def get_current_stock(product, warehouse):
    """Get current stock quantity"""
    try:
        stock = Stock.objects.get(product=product, warehouse=warehouse)
        return stock.quantity
    except Stock.DoesNotExist:
        return 0


def recalculate_po_totals(po):
    """Recalculate purchase order totals"""
    items = po.items.all()
    
    subtotal = Decimal('0.00')
    tax_total = Decimal('0.00')
    discount_total = Decimal('0.00')
    
    for item in items:
        item_subtotal = item.unit_price * Decimal(item.quantity)
        discount_total += item.discount
        after_discount = item_subtotal - item.discount
        tax_amount = (after_discount * item.tax_rate) / Decimal('100')
        tax_total += tax_amount
        subtotal += item_subtotal
    
    po.subtotal = subtotal
    po.tax_amount = tax_total
    po.discount_amount = discount_total
    po.total_amount = subtotal - discount_total + tax_total
    po.save(update_fields=['subtotal', 'tax_amount', 'discount_amount', 'total_amount'])


def auto_receive_grn(grn):
    """
    Automatically process GRN and update inventory
    This is called when GRN is created/verified
    """
    from purchases.models import GRNItem
    
    for grn_item in grn.items.all():
        product = grn_item.product
        warehouse = grn.warehouse
        quantity = grn_item.quantity_received
        
        # Update or create stock
        stock, created = Stock.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={'quantity': 0}
        )
        
        # Add to stock
        stock.quantity += quantity
        stock.save()
        
        # Update product current_stock
        product.current_stock += quantity
        product.save(update_fields=['current_stock'])
        
        # Create or update batch if batch number provided
        if grn_item.batch_number:
            batch, created = Batch.objects.get_or_create(
                batch_number=grn_item.batch_number,
                product=product,
                warehouse=warehouse,
                defaults={
                    'quantity': quantity,
                    'expiry_date': grn_item.expiry_date,
                    'unit_cost': grn_item.unit_price
                }
            )
            if not created:
                batch.quantity += quantity
                batch.save()
        
        # Update PO item received quantity
        if grn_item.po_item:
            grn_item.po_item.received_quantity += quantity
            grn_item.po_item.save()
            
            # Check if PO is fully received
            po = grn_item.po_item.purchase_order
            all_received = all(item.is_fully_received for item in po.items.all())
            if all_received:
                po.status = 'received'
                po.actual_delivery_date = timezone.now().date()
                po.save()
        
        # Create inventory transaction
        from inventory.models import InventoryTransaction
        InventoryTransaction.objects.create(
            transaction_type='purchase',
            product=product,
            warehouse=warehouse,
            quantity=quantity,
            reference_number=grn.grn_number,
            notes=f"Auto-received from GRN {grn.grn_number}",
            created_by=grn.received_by
        )


def check_expiring_products(days_ahead=30):
    """Check for products expiring soon"""
    from django.utils import timezone
    expiry_date = timezone.now().date() + timedelta(days=days_ahead)
    
    expiring_batches = Batch.objects.filter(
        expiry_date__lte=expiry_date,
        expiry_date__gte=timezone.now().date(),
        quantity__gt=0,
        is_active=True
    ).select_related('product', 'warehouse')
    
    return expiring_batches


def auto_update_supplier_performance(supplier):
    """Automatically update supplier performance metrics"""
    from django.db.models import Avg, Count
    from datetime import timedelta
    
    # Get completed POs
    completed_pos = supplier.purchase_orders.filter(status='received')
    
    # Calculate total purchases
    total_purchases = completed_pos.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    supplier.total_purchases = total_purchases
    supplier.total_orders = completed_pos.count()
    
    # Calculate average delivery time
    delivery_times = []
    for po in completed_pos:
        if po.expected_delivery_date and po.actual_delivery_date:
            delta = po.actual_delivery_date - po.expected_delivery_date
            delivery_times.append(delta.days)
    
    if delivery_times:
        supplier.average_delivery_time = sum(delivery_times) / len(delivery_times)
    
    supplier.save(update_fields=['total_purchases', 'total_orders', 'average_delivery_time'])

