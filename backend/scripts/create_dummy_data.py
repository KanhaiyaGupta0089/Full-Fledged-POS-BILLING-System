"""
Script to create dummy data for testing
Run with: python manage.py shell < scripts/create_dummy_data.py
Or: python manage.py shell
>>> exec(open('scripts/create_dummy_data.py').read())
"""
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()

from django.utils import timezone
from accounts.models import User
from products.models import Product, Category, Brand
from inventory.models import Warehouse, Stock
from billing.models import Customer, Invoice, InvoiceItem
from purchases.models import Supplier, PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem, SupplierPayment
from expenses.models import ExpenseCategory, Expense
from forecasting.models import SalesForecast, DemandPattern, OptimalStockLevel
from inventory.advanced_models import Batch, StockValuation, AutoReorderRule

def create_dummy_data():
    """Create dummy data for testing"""
    print("Creating dummy data...")
    
    # Get or create admin user
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✓ Created admin user: {admin_user.username}")
    
    # Create Categories
    categories = []
    category_names = ['Electronics', 'Clothing', 'Food & Beverages', 'Books', 'Toys']
    for name in category_names:
        cat, _ = Category.objects.get_or_create(name=name)
        categories.append(cat)
    print(f"✓ Created {len(categories)} categories")
    
    # Create Brands
    brands = []
    brand_names = ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E']
    for name in brand_names:
        brand, _ = Brand.objects.get_or_create(name=name)
        brands.append(brand)
    print(f"✓ Created {len(brands)} brands")
    
    # Create Products
    products = []
    for i in range(1, 11):
        product, _ = Product.objects.get_or_create(
            sku=f'PROD-{i:03d}',
            defaults={
                'name': f'Product {i}',
                'description': f'Description for Product {i}',
                'category': random.choice(categories),
                'brand': random.choice(brands),
                'cost_price': Decimal(str(random.uniform(50, 500))),
                'selling_price': Decimal(str(random.uniform(100, 1000))),
                'tax_rate': Decimal(str(random.choice([5, 12, 18, 28]))),
                'is_active': True
            }
        )
        products.append(product)
    print(f"✓ Created {len(products)} products")
    
    # Create Warehouses
    warehouses = []
    warehouse_names = ['Main Warehouse', 'Store A', 'Store B']
    for name in warehouse_names:
        warehouse, _ = Warehouse.objects.get_or_create(
            name=name,
            defaults={
                'address': f'Address for {name}'
            }
        )
        warehouses.append(warehouse)
    print(f"✓ Created {len(warehouses)} warehouses")
    
    # Create Stock entries
    for product in products:
        for warehouse in warehouses:
            stock, _ = Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={
                    'quantity': random.randint(0, 100),
                    'min_quantity': random.randint(10, 30)
                }
            )
    print(f"✓ Created stock entries")
    
    # Create Customers
    customers = []
    for i in range(1, 11):
        customer, _ = Customer.objects.get_or_create(
            phone=f'987654321{i}',
            defaults={
                'name': f'Customer {i}',
                'email': f'customer{i}@example.com',
                'address': f'Address {i}',
                'city': 'City',
                'state': 'State',
                'pincode': '123456',
                'customer_type': random.choice(['regular', 'vip', 'wholesale', 'retail']),
                'is_active': True
            }
        )
        customers.append(customer)
    print(f"✓ Created {len(customers)} customers")
    
    # Create Invoices
    invoices = []
    for i in range(1, 21):
        invoice_date = timezone.now() - timedelta(days=random.randint(0, 30))
        customer = random.choice(customers)
        invoice, _ = Invoice.objects.get_or_create(
            invoice_number=f'INV-{invoice_date.strftime("%Y%m%d")}-{i:04d}',
            defaults={
                'customer': customer,
                'customer_name': customer.name,
                'customer_email': customer.email,
                'customer_phone': customer.phone,
                'subtotal': Decimal('0.00'),
                'discount_amount': Decimal('0.00'),
                'tax_amount': Decimal('0.00'),
                'total_amount': Decimal('0.00'),
                'balance_amount': Decimal('0.00'),
                'status': random.choice(['paid', 'partial', 'pending']),
                'payment_method': random.choice(['cash', 'card', 'credit', 'online']),
                'created_by': admin_user,
                'created_at': invoice_date
            }
        )
        
        # Add invoice items
        num_items = random.randint(1, 5)
        subtotal = Decimal('0.00')
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            unit_price = product.selling_price
            discount = Decimal(str(random.uniform(0, 10)))
            tax_rate = product.tax_rate
            tax_amount = ((unit_price * Decimal(quantity) - discount) * tax_rate) / Decimal('100')
            total = (unit_price * Decimal(quantity) - discount) + tax_amount
            
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
            subtotal += unit_price * Decimal(quantity) - discount
        
        invoice.subtotal = subtotal
        invoice.discount_amount = Decimal(str(random.uniform(0, float(subtotal) * 0.1)))
        invoice.tax_amount = (subtotal - invoice.discount_amount) * Decimal('0.18')  # Simplified
        invoice.total_amount = subtotal - invoice.discount_amount + invoice.tax_amount
        invoice.balance_amount = invoice.total_amount if invoice.status != 'paid' else Decimal('0.00')
        invoice.save()
        
        invoices.append(invoice)
    print(f"✓ Created {len(invoices)} invoices")
    
    # Create Suppliers
    suppliers = []
    for i in range(1, 6):
        supplier, _ = Supplier.objects.get_or_create(
            name=f'Supplier {i}',
            defaults={
                'email': f'supplier{i}@example.com',
                'phone': f'987654321{i}',
                'address': f'Supplier Address {i}',
                'city': 'City',
                'state': 'State',
                'pincode': '123456',
                'gstin': f'GSTIN{i:012d}',
                'is_active': True
            }
        )
        suppliers.append(supplier)
    print(f"✓ Created {len(suppliers)} suppliers")
    
    # Create Purchase Orders with realistic data
    purchase_orders = []
    statuses = ['draft', 'pending', 'approved', 'sent', 'partially_received', 'received', 'cancelled']
    status_weights = [1, 2, 3, 2, 1, 4, 1]  # More received, fewer cancelled
    
    for i in range(1, 21):  # Create 20 purchase orders
        po_date = timezone.now() - timedelta(days=random.randint(0, 60))
        supplier = random.choice(suppliers)
        warehouse = random.choice(warehouses)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Calculate expected delivery date (7-30 days from order date)
        expected_delivery = po_date.date() + timedelta(days=random.randint(7, 30))
        
        # For received/partially_received, set actual delivery date
        actual_delivery = None
        if status in ['received', 'partially_received']:
            actual_delivery = expected_delivery + timedelta(days=random.randint(-5, 5))
        
        po, created = PurchaseOrder.objects.get_or_create(
            po_number=f'PO-{po_date.strftime("%Y%m%d")}-{i:04d}',
            defaults={
                'supplier': supplier,
                'warehouse': warehouse,
                'status': status,
                'order_date': po_date.date(),
                'expected_delivery_date': expected_delivery,
                'actual_delivery_date': actual_delivery,
                'subtotal': Decimal('0.00'),
                'tax_amount': Decimal('0.00'),
                'discount_amount': Decimal('0.00'),
                'total_amount': Decimal('0.00'),
                'notes': f'Purchase order for {supplier.name}',
                'auto_approve': False,
                'created_by': admin_user,
                'created_at': po_date
            }
        )
        
        # Add PO items with proper calculations
        num_items = random.randint(2, 6)
        subtotal = Decimal('0.00')
        tax_total = Decimal('0.00')
        discount_total = Decimal('0.00')
        
        for j in range(num_items):
            product = random.choice(products)
            quantity = random.randint(10, 100)
            unit_price = product.cost_price * Decimal(str(random.uniform(0.9, 1.1)))  # Slight variation
            tax_rate = product.tax_rate
            discount = Decimal(str(random.uniform(0, 50))) if random.random() > 0.7 else Decimal('0.00')
            
            # Calculate item totals
            item_subtotal = unit_price * Decimal(quantity)
            after_discount = item_subtotal - discount
            tax_amount = (after_discount * tax_rate) / Decimal('100')
            item_total = after_discount + tax_amount
            
            po_item = PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=tax_rate,
                discount=discount,
                total=item_total,
                received_quantity=random.randint(0, quantity) if status in ['partially_received', 'received'] else 0
            )
            
            subtotal += item_subtotal
            tax_total += tax_amount
            discount_total += discount
        
        # Update PO totals
        po.subtotal = subtotal
        po.tax_amount = tax_total
        po.discount_amount = discount_total
        po.total_amount = subtotal - discount_total + tax_total
        po.save()
        purchase_orders.append(po)
    print(f"✓ Created {len(purchase_orders)} purchase orders")
    
    # Create GRNs (Goods Receipt Notes) for received/partially received POs
    grns = []
    received_pos = [po for po in purchase_orders if po.status in ['received', 'partially_received']]
    
    for po in received_pos[:10]:  # Create GRNs for up to 10 received POs
        grn_date = po.actual_delivery_date or po.expected_delivery_date
        if grn_date:
            grn_datetime = timezone.make_aware(datetime.combine(grn_date, datetime.min.time()))
            
            # Check if GRN already exists for this PO
            grn = GoodsReceiptNote.objects.filter(purchase_order=po).first()
            if not grn:
                grn = GoodsReceiptNote.objects.create(
                    purchase_order=po,
                    warehouse=po.warehouse,
                    total_amount=Decimal('0.00'),  # Will be calculated
                    is_verified=random.choice([True, False]),
                    notes=f'GRN for {po.po_number}',
                    quality_check_notes='Quality check passed' if random.random() > 0.2 else '',
                    received_by=admin_user,
                    received_at=grn_datetime,
                    created_at=grn_datetime
                )
                
                # Create GRN items
                grn_total = Decimal('0.00')
                for po_item in po.items.all():
                    if po_item.received_quantity > 0:
                        batch_num = f'BATCH-{po_item.product.sku}-{grn_date.strftime("%Y%m%d")}'
                        expiry_date = grn_date + timedelta(days=random.randint(180, 730))
                        
                        GRNItem.objects.create(
                            grn=grn,
                            po_item=po_item,
                            product=po_item.product,
                            quantity_received=po_item.received_quantity,
                            unit_price=po_item.unit_price,
                            batch_number=batch_num,
                            expiry_date=expiry_date,
                            is_quality_approved=random.choice([True, False]),
                            quality_notes='Approved' if random.random() > 0.3 else 'Minor defects noted'
                        )
                        grn_total += po_item.unit_price * Decimal(po_item.received_quantity)
                
                grn.total_amount = grn_total
                grn.save()
                grns.append(grn)
            else:
                grns.append(grn)
            
    
    print(f"✓ Created {len(grns)} GRNs (Goods Receipt Notes)")
    
    # Create Supplier Payments
    supplier_payments = []
    payment_methods = ['cash', 'bank_transfer', 'cheque', 'upi', 'credit']
    
    for po in purchase_orders[:15]:  # Create payments for first 15 POs
        if po.status in ['received', 'partially_received'] and random.random() > 0.3:
            payment_date = (po.actual_delivery_date or po.expected_delivery_date) + timedelta(days=random.randint(0, 30))
            payment_method = random.choice(payment_methods)
            
            # Partial or full payment
            if random.random() > 0.7:
                amount = po.total_amount * Decimal(str(random.uniform(0.5, 1.0)))  # Partial payment
            else:
                amount = po.total_amount  # Full payment
            
            payment, created = SupplierPayment.objects.get_or_create(
                purchase_order=po,
                defaults={
                    'supplier': po.supplier,
                    'amount': amount,
                    'payment_method': payment_method,
                    'payment_date': payment_date,
                    'reference_number': f'REF-{payment_date.strftime("%Y%m%d")}-{random.randint(1000, 9999)}' if payment_method != 'cash' else '',
                    'notes': f'Payment for {po.po_number}',
                    'created_by': admin_user
                }
            )
            if created:
                supplier_payments.append(payment)
    
    print(f"✓ Created {len(supplier_payments)} supplier payments")
    
    # Create Expense Categories
    expense_categories = []
    category_names = ['Rent', 'Utilities', 'Salaries', 'Marketing', 'Office Supplies']
    for name in category_names:
        cat, _ = ExpenseCategory.objects.get_or_create(name=name)
        expense_categories.append(cat)
    print(f"✓ Created {len(expense_categories)} expense categories")
    
    # Create Expenses
    for i in range(1, 11):
        expense_date = timezone.now() - timedelta(days=random.randint(0, 30))
        Expense.objects.get_or_create(
            expense_number=f'EXP-{expense_date.strftime("%Y%m%d")}-{i:04d}',
            defaults={
                'category': random.choice(expense_categories),
                'description': f'Expense {i}',
                'amount': Decimal(str(random.uniform(100, 5000))),
                'tax_amount': Decimal('0.00'),
                'total_amount': Decimal(str(random.uniform(100, 5000))),
                'expense_date': expense_date.date(),
                'payment_method': random.choice(['cash', 'card', 'bank_transfer']),
                'is_approved': random.choice([True, False]),
                'created_by': admin_user
            }
        )
    print(f"✓ Created expenses")
    
    # Create Batches
    for product in products[:5]:  # First 5 products
        for warehouse in warehouses:
            batch, _ = Batch.objects.get_or_create(
                batch_number=f'BATCH-{product.sku}-{warehouse.id}',
                product=product,
                warehouse=warehouse,
                defaults={
                    'quantity': random.randint(10, 100),
                    'unit_cost': product.cost_price,
                    'manufacturing_date': timezone.now().date() - timedelta(days=random.randint(30, 365)),
                    'expiry_date': timezone.now().date() + timedelta(days=random.randint(30, 365)),
                    'is_active': True
                }
            )
    print(f"✓ Created batches")
    
    # Create Auto Reorder Rules
    for product in products[:5]:  # First 5 products
        for warehouse in warehouses:
            AutoReorderRule.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={
                    'min_stock': random.randint(10, 30),
                    'max_stock': random.randint(50, 100),
                    'reorder_point': random.randint(20, 40),
                    'preferred_supplier': random.choice(suppliers) if suppliers else None,
                    'is_active': True
                }
            )
    print(f"✓ Created auto reorder rules")
    
    print("\n✅ Dummy data creation completed!")
    print(f"   - {len(products)} Products")
    print(f"   - {len(customers)} Customers")
    print(f"   - {len(invoices)} Invoices")
    print(f"   - {len(suppliers)} Suppliers")
    print(f"   - {len(warehouses)} Warehouses")
    print(f"   - {len(purchase_orders)} Purchase Orders")
    print(f"   - {len(grns)} GRNs (Goods Receipt Notes)")
    print(f"   - {len(supplier_payments)} Supplier Payments")
    print(f"   - Expenses, Batches, and Reorder Rules created")

if __name__ == '__main__':
    create_dummy_data()

