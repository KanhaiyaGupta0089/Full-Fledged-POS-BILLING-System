"""
Management command to add 10 working coupons to the database
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from discounts.models import Coupon


class Command(BaseCommand):
    help = 'Add 10 working coupons to the database'

    def handle(self, *args, **options):
        # Get current time
        now = timezone.now()
        valid_until = now + timedelta(days=365)  # Valid for 1 year
        
        coupons_data = [
            {
                'code': 'WELCOME10',
                'name': 'Welcome Discount',
                'description': '10% off on your first purchase',
                'discount_type': 'percentage',
                'discount_value': Decimal('10.00'),
                'max_discount': Decimal('500.00'),
                'min_purchase_amount': Decimal('100.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 1000,
                'max_uses_per_user': 1,
            },
            {
                'code': 'SAVE20',
                'name': 'Save 20%',
                'description': 'Get 20% discount on orders above Rs. 500',
                'discount_type': 'percentage',
                'discount_value': Decimal('20.00'),
                'max_discount': Decimal('1000.00'),
                'min_purchase_amount': Decimal('500.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 500,
                'max_uses_per_user': 2,
            },
            {
                'code': 'FLAT50',
                'name': 'Flat Rs. 50 Off',
                'description': 'Get flat Rs. 50 discount on minimum purchase of Rs. 200',
                'discount_type': 'fixed',
                'discount_value': Decimal('50.00'),
                'max_discount': None,
                'min_purchase_amount': Decimal('200.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 2000,
                'max_uses_per_user': 3,
            },
            {
                'code': 'MEGA25',
                'name': 'Mega Sale 25%',
                'description': '25% discount on orders above Rs. 1000',
                'discount_type': 'percentage',
                'discount_value': Decimal('25.00'),
                'max_discount': Decimal('2000.00'),
                'min_purchase_amount': Decimal('1000.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 300,
                'max_uses_per_user': 1,
            },
            {
                'code': 'FLAT100',
                'name': 'Flat Rs. 100 Off',
                'description': 'Get flat Rs. 100 discount on minimum purchase of Rs. 500',
                'discount_type': 'fixed',
                'discount_value': Decimal('100.00'),
                'max_discount': None,
                'min_purchase_amount': Decimal('500.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 1000,
                'max_uses_per_user': 2,
            },
            {
                'code': 'SUPER15',
                'name': 'Super 15% Off',
                'description': '15% discount on all orders',
                'discount_type': 'percentage',
                'discount_value': Decimal('15.00'),
                'max_discount': Decimal('750.00'),
                'min_purchase_amount': Decimal('50.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': None,  # Unlimited
                'max_uses_per_user': 5,
            },
            {
                'code': 'FLAT200',
                'name': 'Flat Rs. 200 Off',
                'description': 'Get flat Rs. 200 discount on minimum purchase of Rs. 1000',
                'discount_type': 'fixed',
                'discount_value': Decimal('200.00'),
                'max_discount': None,
                'min_purchase_amount': Decimal('1000.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 500,
                'max_uses_per_user': 1,
            },
            {
                'code': 'BIG30',
                'name': 'Big 30% Off',
                'description': '30% discount on orders above Rs. 2000',
                'discount_type': 'percentage',
                'discount_value': Decimal('30.00'),
                'max_discount': Decimal('3000.00'),
                'min_purchase_amount': Decimal('2000.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 200,
                'max_uses_per_user': 1,
            },
            {
                'code': 'FLAT500',
                'name': 'Flat Rs. 500 Off',
                'description': 'Get flat Rs. 500 discount on minimum purchase of Rs. 2500',
                'discount_type': 'fixed',
                'discount_value': Decimal('500.00'),
                'max_discount': None,
                'min_purchase_amount': Decimal('2500.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 100,
                'max_uses_per_user': 1,
            },
            {
                'code': 'VIP40',
                'name': 'VIP 40% Off',
                'description': 'Exclusive 40% discount on orders above Rs. 5000',
                'discount_type': 'percentage',
                'discount_value': Decimal('40.00'),
                'max_discount': Decimal('5000.00'),
                'min_purchase_amount': Decimal('5000.00'),
                'valid_from': now,
                'valid_until': valid_until,
                'is_active': True,
                'max_uses': 50,
                'max_uses_per_user': 1,
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for coupon_data in coupons_data:
            code = coupon_data['code']
            # Check if coupon already exists
            if Coupon.objects.filter(code=code).exists():
                self.stdout.write(
                    self.style.WARNING(f'Coupon {code} already exists. Skipping...')
                )
                skipped_count += 1
                continue
            
            try:
                coupon = Coupon.objects.create(**coupon_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created coupon: {code} - {coupon.name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to create coupon {code}: {str(e)}')
                )
                skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {created_count} coupons!'
            )
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ Skipped {skipped_count} coupons (already exist or error)')
            )
        
        # Display summary
        self.stdout.write('\n📋 Coupon Summary:')
        self.stdout.write('=' * 60)
        for coupon in Coupon.objects.filter(is_active=True).order_by('code'):
            discount_info = f"{coupon.discount_value}%"
            if coupon.discount_type == 'fixed':
                discount_info = f"Rs. {coupon.discount_value}"
            self.stdout.write(
                f"  {coupon.code:12} - {coupon.name:25} ({discount_info})"
            )








