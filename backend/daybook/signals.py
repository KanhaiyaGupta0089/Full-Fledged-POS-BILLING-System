"""
Signals for daybook app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import Invoice
from .models import DayBookEntry
from decimal import Decimal


@receiver(post_save, sender=Invoice)
def create_daybook_entry(sender, instance, created, **kwargs):
    """Auto-create daybook entry when invoice is created"""
    if created and instance.status != 'cancelled':
        # Calculate previous day's balance
        previous_entries = DayBookEntry.objects.filter(
            date__lt=instance.created_at.date()
        ).order_by('-date', '-created_at')
        previous_balance = previous_entries.first().balance if previous_entries.exists() else Decimal('0.00')
        
        # Check if it's a cash/UPI/card invoice with immediate full payment
        is_immediate_payment = instance.payment_method in ['cash', 'upi', 'card'] and instance.paid_amount == instance.total_amount
        
        if is_immediate_payment:
            # For cash/UPI/card with immediate payment, create a single combined entry
            DayBookEntry.objects.create(
                date=instance.created_at.date(),
                entry_type='sale',
                invoice=instance,
                description=f"Sale & Payment - Invoice {instance.invoice_number} ({instance.payment_method.upper()})",
                debit=instance.total_amount,
                credit=instance.paid_amount,
                balance=previous_balance  # Balance remains same as both debit and credit cancel out
            )
        else:
            # For credit or partial payments, create separate entries
            # Create daybook entry for sale
            DayBookEntry.objects.create(
                date=instance.created_at.date(),
                entry_type='sale',
                invoice=instance,
                description=f"Sale - Invoice {instance.invoice_number}",
                debit=instance.total_amount,
                credit=Decimal('0.00'),
                balance=previous_balance + instance.total_amount
            )
            
            # Create entry for payment if paid (for partial payments or later payments)
            if instance.paid_amount > 0:
                # Get the balance after the sale entry
                sale_balance = previous_balance + instance.total_amount
                DayBookEntry.objects.create(
                    date=instance.created_at.date(),
                    entry_type='payment',
                    invoice=instance,
                    description=f"Payment - Invoice {instance.invoice_number}",
                    debit=Decimal('0.00'),
                    credit=instance.paid_amount,
                    balance=sale_balance - instance.paid_amount
                )

