"""
Signals for Customer Management
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import Invoice
from billing.models import Customer
from billing.customer_extras import CustomerPurchaseHistory


@receiver(post_save, sender=Invoice)
def update_customer_stats(sender, instance, created, **kwargs):
    """Update customer statistics when invoice is created/updated"""
    # Only update stats when invoice is first created and paid, or when status changes to paid
    if not instance.customer or instance.status != 'paid':
        return
    
    customer = instance.customer
    
    # Only update stats if this is a new invoice or if purchase history doesn't exist
    purchase_history_exists = CustomerPurchaseHistory.objects.filter(
        invoice=instance,
        customer=customer
    ).exists()
    
    if created or not purchase_history_exists:
        # Update customer stats only once per invoice
        customer.total_purchases += instance.total_amount
        customer.total_orders += 1
        customer.last_purchase_date = instance.created_at or instance.updated_at
        
        # Calculate loyalty points (1 point per ₹100)
        points_to_add = int(instance.total_amount / 100)
        if points_to_add > 0:
            customer.loyalty_points += points_to_add
        
        customer.save(update_fields=['total_purchases', 'total_orders', 'last_purchase_date', 'loyalty_points'])
        
        # Create purchase history entry if it doesn't exist
        if not purchase_history_exists:
            items_count = instance.items.count()
            CustomerPurchaseHistory.objects.get_or_create(
                customer=customer,
                invoice=instance,
                defaults={
                    'total_amount': instance.total_amount,
                    'items_count': items_count
                }
            )

