"""
Signals for Purchase Order automation
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PurchaseOrder, GRNItem, GoodsReceiptNote
from .automation import auto_receive_grn, recalculate_po_totals
from inventory.models import InventoryTransaction, Stock
from inventory.advanced_models import Batch


@receiver(post_save, sender=PurchaseOrder)
def auto_approve_po(sender, instance, created, **kwargs):
    """Auto-approve PO if auto_approve is enabled"""
    if instance.auto_approve and instance.status == 'draft':
        instance.status = 'approved'
        instance.approved_at = timezone.now()
        PurchaseOrder.objects.filter(pk=instance.pk).update(
            status='approved',
            approved_at=timezone.now()
        )


@receiver(post_save, sender=GRNItem)
def update_po_item_on_grn(sender, instance, created, **kwargs):
    """Update PO item received quantity when GRN item is created"""
    if created and instance.po_item:
        # Update received quantity
        po_item = instance.po_item
        po_item.received_quantity += instance.quantity_received
        po_item.save()
        
        # Check if PO is fully received
        po = po_item.purchase_order
        all_received = all(item.is_fully_received for item in po.items.all())
        if all_received and po.status != 'received':
            po.status = 'received'
            po.actual_delivery_date = timezone.now().date()
            po.save()


@receiver(post_save, sender=GoodsReceiptNote)
def process_grn_automatically(sender, instance, created, **kwargs):
    """Automatically process GRN and update inventory when verified"""
    if instance.is_verified and not created:
        # Process GRN items
        for grn_item in instance.items.all():
            product = grn_item.product
            warehouse = instance.warehouse
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
                batch, batch_created = Batch.objects.get_or_create(
                    batch_number=grn_item.batch_number,
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': quantity,
                        'expiry_date': grn_item.expiry_date,
                        'unit_cost': grn_item.unit_price
                    }
                )
                if not batch_created:
                    batch.quantity += quantity
                    batch.save()
            
            # Create inventory transaction
            InventoryTransaction.objects.create(
                transaction_type='purchase',
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                reference_number=instance.grn_number,
                notes=f"Received from GRN {instance.grn_number}",
                created_by=instance.received_by
            )




