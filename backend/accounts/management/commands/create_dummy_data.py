"""
Management command to create dummy data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from accounts.models import Role
from products.models import Category, Brand, Product
from billing.models import Customer, Invoice, InvoiceItem
from inventory.models import Warehouse, Stock
from credit_ledger.models import CustomerCredit, CreditTransaction
from daybook.models import DayBookEntry

User = get_user_model()


class Command(BaseCommand):
    help = 'Create dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data...')
        
        # Create roles if not exist
        roles = ['admin', 'owner', 'manager', 'employee']
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)
        
        # Create users
        self.stdout.write('Creating users...')
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pos.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        owner_user, _ = User.objects.get_or_create(
            username='owner',
            defaults={
                'email': 'owner@pos.com',
                'first_name': 'Owner',
                'last_name': 'User',
                'role': 'owner',
            }
        )
        owner_user.set_password('owner123')
        owner_user.save()
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home & Garden']
        category_objs = []
        for cat_name in categories:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'{cat_name} category', 'is_active': True}
            )
            category_objs.append(cat)
        
        # Create brands
        self.stdout.write('Creating brands...')
        brands = ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E']
        brand_objs = []
        for brand_name in brands:
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'description': f'{brand_name} brand', 'is_active': True}
            )
            brand_objs.append(brand)
        
        # Create warehouse
        self.stdout.write('Creating warehouse...')
        warehouse, _ = Warehouse.objects.get_or_create(
            name='Main Warehouse',
            defaults={
                'address': '123 Main St',
                'is_active': True
            }
        )
        
        # Create products
        self.stdout.write('Creating products...')
        products = []
        for i in range(20):
            try:
                # Generate unique SKU to avoid conflicts
                sku = f'PROD-DUMMY-{i+1:04d}'
                
                # Use filter().first() instead of get_or_create to handle duplicates
                product = Product.objects.filter(sku=sku).first()
                
                if not product:
                    # Create new product with unique SKU
                    product = Product.objects.create(
                        name=f'Product {i+1}',
                        sku=sku,
                        description=f'Description for Product {i+1}',
                        category=random.choice(category_objs),
                        brand=random.choice(brand_objs),
                        cost_price=Decimal(random.randint(100, 1000)),
                        selling_price=Decimal(random.randint(150, 1500)),
                        current_stock=random.randint(0, 100),
                        min_stock_level=10,
                        max_stock_level=200,
                        unit='pcs',
                        tax_rate=Decimal('18.00'),
                        is_active=True,
                        is_trackable=True,
                        created_by=admin_user
                    )
                products.append(product)
                
                # Create stock entry if it doesn't exist
                Stock.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': product.current_stock,
                        'min_quantity': product.min_stock_level,
                        'max_quantity': product.max_stock_level
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to create product {i+1}: {e}'))
                # Try to get existing product by SKU
                try:
                    sku = f'PROD-DUMMY-{i+1:04d}'
                    product = Product.objects.filter(sku=sku).first()
                    if product:
                        products.append(product)
                except:
                    pass
        
        # If we don't have enough products, get some existing ones
        if len(products) < 10:
            existing_products = list(Product.objects.filter(is_active=True)[:20])
            products.extend(existing_products)
            products = list(set(products))  # Remove duplicates
        
        # Create customers
        self.stdout.write('Creating customers...')
        customers = []
        for i in range(10):
            try:
                # Generate unique phone number to avoid conflicts
                phone = f'987654321{i}'
                customer, created = Customer.objects.get_or_create(
                    phone=phone,
                    defaults={
                        'name': f'Customer {i+1}',
                        'email': f'customer{i+1}@example.com',
                        'address': f'Address {i+1}',
                        'is_active': True
                    }
                )
                customers.append(customer)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to create customer {i+1}: {e}'))
                # Try to get existing customer by phone
                try:
                    customer = Customer.objects.filter(phone=phone).first()
                    if customer:
                        customers.append(customer)
                except:
                    pass
        
        # If we don't have enough customers, get some existing ones
        if len(customers) < 5:
            existing_customers = list(Customer.objects.all()[:10])
            customers.extend(existing_customers)
            customers = list(set(customers))  # Remove duplicates
        
        # Create invoices
        self.stdout.write('Creating invoices...')
        payment_methods = ['cash', 'card', 'upi', 'credit']
        from datetime import date as date_obj
        today = date_obj.today()
        
        # Ensure we have customers and products
        if not customers:
            customers = list(Customer.objects.all()[:10])
        if not products:
            products = list(Product.objects.filter(is_active=True)[:20])
        
        if not customers or not products:
            self.stdout.write(self.style.WARNING('Skipping invoice creation: need at least 1 customer and 1 product'))
        else:
            # Track invoice counts per date
            invoice_counts = {}
            
            for i in range(30):
                try:
                    customer = random.choice(customers) if random.choice([True, False]) else None
                    payment_method = random.choice(payment_methods)
                    
                    # Generate unique invoice number
                    invoice_date = timezone.now() - timedelta(days=random.randint(0, 30))
                    invoice_date_obj = invoice_date.date()
                    date_key = invoice_date_obj.strftime('%Y%m%d')
                    
                    # Get or increment count for this date
                    if date_key not in invoice_counts:
                        # Get max count for this date from existing invoices
                        existing_invoices = Invoice.objects.filter(invoice_number__startswith=f"INV-{date_key}-")
                        if existing_invoices.exists():
                            max_num = 0
                            for inv in existing_invoices:
                                try:
                                    num_part = inv.invoice_number.split('-')[-1]
                                    num = int(num_part)
                                    max_num = max(max_num, num)
                                except:
                                    pass
                            invoice_counts[date_key] = max_num
                        else:
                            invoice_counts[date_key] = 0
                    invoice_counts[date_key] += 1
                    count = invoice_counts[date_key]
                    
                    invoice_number = f"INV-{date_key}-{count:04d}"
                    
                    # Check if invoice already exists
                    invoice, invoice_created = Invoice.objects.get_or_create(
                        invoice_number=invoice_number,
                        defaults={
                            'customer': customer,
                            'customer_name': customer.name if customer else f'Walk-in Customer {i+1}',
                            'customer_phone': customer.phone if customer else f'987654321{i}',
                            'customer_email': customer.email if customer else f'walkin{i+1}@example.com',
                            'subtotal': Decimal('0.00'),
                            'discount_amount': Decimal('0.00'),
                            'tax_amount': Decimal('0.00'),
                            'total_amount': Decimal('0.00'),
                            'paid_amount': Decimal('0.00') if payment_method == 'credit' else Decimal('0.00'),
                            'payment_method': payment_method,
                            'status': 'pending' if payment_method == 'credit' else 'paid',
                            'created_by': admin_user,
                            'created_at': invoice_date
                        }
                    )
                    
                    # Skip if invoice already exists (items already created)
                    if not invoice_created:
                        continue
                    
                    # Create invoice items
                    num_items = random.randint(1, 5)
                    subtotal = Decimal('0.00')
                    for j in range(num_items):
                        product = random.choice(products)
                        quantity = random.randint(1, 5)
                        unit_price = product.selling_price
                        discount = Decimal('0.00')
                        tax_rate = product.tax_rate
                        
                        item_subtotal = unit_price * quantity
                        after_discount = item_subtotal - discount
                        tax_amount = (after_discount * tax_rate) / 100
                        total = after_discount + tax_amount
                        
                        InvoiceItem.objects.create(
                            invoice=invoice,
                            product=product,
                            quantity=quantity,
                            unit_price=unit_price,
                            discount=discount,
                            tax_rate=tax_rate,
                            tax_amount=tax_amount,
                            total=total
                        )
                        
                        subtotal += total
                    
                    # Update invoice totals - use update() to avoid triggering signal again
                    # But we need to save to trigger daybook signal, so save once with all data
                    invoice.subtotal = subtotal
                    invoice.tax_amount = subtotal * Decimal('0.18')
                    invoice.total_amount = subtotal + invoice.tax_amount
                    invoice.paid_amount = invoice.total_amount if payment_method != 'credit' else Decimal('0.00')
                    invoice.balance_amount = invoice.total_amount - invoice.paid_amount
                    invoice.save()  # This will trigger the daybook signal
                    
                    # Create credit entry if credit payment
                    if payment_method == 'credit' and customer:
                        credit_account, _ = CustomerCredit.objects.get_or_create(
                            customer=customer,
                            defaults={
                                'total_credit': Decimal('0.00'),
                                'total_paid': Decimal('0.00'),
                                'balance': Decimal('0.00')
                            }
                        )
                        
                        CreditTransaction.objects.create(
                            customer_credit=credit_account,
                            invoice=invoice,
                            transaction_type='credit',
                            amount=invoice.total_amount,
                            description=f'Credit sale - Invoice {invoice.invoice_number}',
                            created_by=admin_user
                        )
                        
                        credit_account.total_credit += invoice.total_amount
                        credit_account.balance = credit_account.total_credit - credit_account.total_paid
                        credit_account.last_transaction_date = timezone.now()
                        credit_account.save()
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to create invoice {i+1}: {e}'))
                    continue
        
        # Ensure daybook entries exist for all invoices
        self.stdout.write('Creating daybook entries for existing invoices...')
        from daybook.models import DayBookEntry
        invoices_without_entries = Invoice.objects.exclude(
            daybook_entries__isnull=False
        ).exclude(status='cancelled').exclude(total_amount=0)
        
        for invoice in invoices_without_entries:
            try:
                # Trigger the signal by saving the invoice
                invoice.save()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to create daybook entry for invoice {invoice.invoice_number}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Dummy data created successfully!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'  - {User.objects.count()} users')
        self.stdout.write(f'  - {Category.objects.count()} categories')
        self.stdout.write(f'  - {Brand.objects.count()} brands')
        self.stdout.write(f'  - {Product.objects.count()} products')
        self.stdout.write(f'  - {Customer.objects.count()} customers')
        self.stdout.write(f'  - {Invoice.objects.count()} invoices')
        self.stdout.write(f'  - {DayBookEntry.objects.count()} daybook entries')
        self.stdout.write(f'  - {CustomerCredit.objects.count()} credit accounts')

