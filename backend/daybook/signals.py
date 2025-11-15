"""
Signals for daybook app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from billing.models import Invoice
from .models import DayBookEntry
from decimal import Decimal


@receiver(post_save, sender=Invoice)
def create_daybook_entry(sender, instance, created, **kwargs):
    """Auto-create daybook entry when invoice is created or updated"""
    # Skip if invoice is cancelled or has no total amount
    if instance.status == 'cancelled' or instance.total_amount == 0:
        return
    
    # Calculate previous day's balance
    invoice_date = instance.created_at.date() if instance.created_at else timezone.now().date()
    # Get the last entry before this invoice's date (or same date but earlier time)
    previous_entries = DayBookEntry.objects.filter(
        date__lt=invoice_date
    ).order_by('-date', '-created_at')
    
    # If no entries before this date, check same date entries created before this invoice
    if not previous_entries.exists() and instance.created_at:
        previous_entries = DayBookEntry.objects.filter(
            date=invoice_date,
            created_at__lt=instance.created_at
        ).order_by('-created_at')
    
    previous_balance = previous_entries.first().balance if previous_entries.exists() else Decimal('0.00')
    
    # Check if it's a cash/UPI/card invoice with immediate full payment
    is_immediate_payment = instance.payment_method in ['cash', 'upi', 'card'] and instance.paid_amount == instance.total_amount
    
    if is_immediate_payment:
        # For cash/UPI/card with immediate payment, create a single combined entry
        # Only create if it doesn't exist
        DayBookEntry.objects.get_or_create(
            invoice=instance,
            entry_type='sale',
            defaults={
                'date': invoice_date,
                'description': f"Sale & Payment - Invoice {instance.invoice_number} ({instance.payment_method.upper()})",
                'debit': instance.total_amount,
                'credit': instance.paid_amount,
                'balance': previous_balance  # Balance remains same as both debit and credit cancel out
            }
        )
    else:
        # For credit or partial payments, create separate entries
        # Create daybook entry for sale (only if it doesn't exist)
        sale_entry, sale_created = DayBookEntry.objects.get_or_create(
            invoice=instance,
            entry_type='sale',
            defaults={
                'date': invoice_date,
                'description': f"Sale - Invoice {instance.invoice_number}",
                'debit': instance.total_amount,
                'credit': Decimal('0.00'),
                'balance': previous_balance + instance.total_amount
            }
        )
        
        # Update balance if entry already existed
        if not sale_created:
            sale_entry.debit = instance.total_amount
            sale_entry.balance = previous_balance + instance.total_amount
            sale_entry.save()
        
        # Create entry for payment if paid (for partial payments or later payments)
        if instance.paid_amount > 0:
            # Get the balance after the sale entry
            sale_balance = previous_balance + instance.total_amount
            # Check if payment entry already exists
            payment_entry, payment_created = DayBookEntry.objects.get_or_create(
                invoice=instance,
                entry_type='payment',
                defaults={
                    'date': invoice_date,
                    'description': f"Payment - Invoice {instance.invoice_number}",
                    'debit': Decimal('0.00'),
                    'credit': instance.paid_amount,
                    'balance': sale_balance - instance.paid_amount
                }
            )
            
            # Update if entry already existed
            if not payment_created:
                payment_entry.credit = instance.paid_amount
                payment_entry.balance = sale_balance - instance.paid_amount
                payment_entry.save()

