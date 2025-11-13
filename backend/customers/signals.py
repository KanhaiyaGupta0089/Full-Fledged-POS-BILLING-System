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
    if instance.customer and instance.status == 'paid':
        customer = instance.customer
        
        # Update customer stats
        customer.total_purchases += instance.total_amount
        customer.total_orders += 1
        customer.last_purchase_date = instance.created_at
        
        # Calculate loyalty points (1 point per ₹100)
        points_to_add = int(instance.total_amount / 100)
        if points_to_add > 0:
            customer.loyalty_points += points_to_add
        
        customer.save(update_fields=['total_purchases', 'total_orders', 'last_purchase_date', 'loyalty_points'])
        
        # Create purchase history entry
        if created:
            items_count = instance.items.count()
            CustomerPurchaseHistory.objects.create(
                customer=customer,
                invoice=instance,
                total_amount=instance.total_amount,
                items_count=items_count
            )

