"""
Management command to add 10,000 real products with complete information
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

from products.models import Category, Brand, Product
from products.utils import (
    generate_unique_sku,
    generate_unique_barcode,
    generate_unique_qr_code,
    get_existing_product_codes
)
from inventory.models import Warehouse, Stock

User = get_user_model()

# Real product categories with descriptions
CATEGORIES = [
    {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
    {'name': 'Clothing', 'description': 'Apparel and fashion items'},
    {'name': 'Food & Beverages', 'description': 'Food items and drinks'},
    {'name': 'Home & Kitchen', 'description': 'Home appliances and kitchenware'},
    {'name': 'Beauty & Personal Care', 'description': 'Cosmetics and personal care products'},
    {'name': 'Sports & Outdoors', 'description': 'Sports equipment and outdoor gear'},
    {'name': 'Books & Media', 'description': 'Books, movies, and music'},
    {'name': 'Toys & Games', 'description': 'Toys and gaming products'},
    {'name': 'Health & Wellness', 'description': 'Health supplements and wellness products'},
    {'name': 'Automotive', 'description': 'Car accessories and parts'},
    {'name': 'Office Supplies', 'description': 'Stationery and office equipment'},
    {'name': 'Pet Supplies', 'description': 'Pet food and accessories'},
    {'name': 'Baby Products', 'description': 'Baby care and essentials'},
    {'name': 'Furniture', 'description': 'Home and office furniture'},
    {'name': 'Jewelry', 'description': 'Jewelry and accessories'},
]

# Real brand names
BRANDS = [
    'Samsung', 'Apple', 'Sony', 'LG', 'Nike', 'Adidas', 'Puma', 'Reebok',
    'Coca-Cola', 'Pepsi', 'Nestle', 'Unilever', 'Procter & Gamble',
    'Philips', 'Whirlpool', 'Bosch', 'Panasonic', 'Canon', 'Nikon',
    'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'Microsoft', 'Google',
    'Amazon', 'Flipkart', 'Myntra', 'Zara', 'H&M', 'Levi\'s', 'Calvin Klein',
    'L\'Oreal', 'Maybelline', 'Revlon', 'MAC', 'Estee Lauder',
    'Tata', 'Reliance', 'Mahindra', 'Maruti', 'Hyundai', 'Honda',
    'Toyota', 'Ford', 'BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen',
    'PepsiCo', 'Britannia', 'Amul', 'Parle', 'ITC', 'HUL',
    'Godrej', 'Asian Paints', 'Berger', 'Dulux', 'Nippon',
    'IKEA', 'Pepperfry', 'Urban Ladder', 'HomeTown', 'Fabindia',
    'Tanishq', 'Kalyan Jewellers', 'Malabar Gold', 'PC Jeweller',
    'Raymond', 'Van Heusen', 'Allen Solly', 'Peter England', 'Arrow',
]

# Real product names by category
PRODUCTS_BY_CATEGORY = {
    'Electronics': [
        'Smartphone', 'Laptop', 'Tablet', 'Smart TV', 'Headphones', 'Speaker',
        'Camera', 'Smartwatch', 'Power Bank', 'Charger', 'USB Cable', 'Mouse',
        'Keyboard', 'Monitor', 'Printer', 'Router', 'Modem', 'Hard Drive',
        'SSD', 'RAM', 'Graphics Card', 'Processor', 'Motherboard', 'Cooling Fan',
        'Webcam', 'Microphone', 'Bluetooth Earbuds', 'Smart Home Hub', 'Smart Bulb',
        'Drone', 'Action Camera', 'Gaming Console', 'Controller', 'VR Headset',
    ],
    'Clothing': [
        'T-Shirt', 'Jeans', 'Shirt', 'Dress', 'Sweater', 'Jacket', 'Coat',
        'Shoes', 'Sneakers', 'Sandals', 'Boots', 'Socks', 'Underwear',
        'Shorts', 'Pants', 'Skirt', 'Blouse', 'Suit', 'Tie', 'Belt',
        'Hat', 'Cap', 'Scarf', 'Gloves', 'Sunglasses', 'Watch', 'Wallet',
        'Handbag', 'Backpack', 'Purse', 'Jewelry Set', 'Bracelet', 'Necklace',
    ],
    'Food & Beverages': [
        'Rice', 'Wheat Flour', 'Sugar', 'Salt', 'Oil', 'Ghee', 'Butter',
        'Milk', 'Yogurt', 'Cheese', 'Bread', 'Biscuits', 'Cookies', 'Chips',
        'Chocolate', 'Candy', 'Juice', 'Soft Drink', 'Tea', 'Coffee',
        'Spices', 'Masala', 'Pickle', 'Jam', 'Honey', 'Cereal', 'Oats',
        'Noodles', 'Pasta', 'Sauce', 'Ketchup', 'Mayonnaise', 'Vinegar',
    ],
    'Home & Kitchen': [
        'Cookware Set', 'Pressure Cooker', 'Frying Pan', 'Saucepan', 'Knife Set',
        'Cutting Board', 'Mixer', 'Blender', 'Food Processor', 'Microwave',
        'Refrigerator', 'Washing Machine', 'Dishwasher', 'Vacuum Cleaner',
        'Iron', 'Toaster', 'Coffee Maker', 'Kettle', 'Mixer Grinder',
        'Dinner Set', 'Glass Set', 'Spoon Set', 'Fork Set', 'Plate', 'Bowl',
        'Towel', 'Bed Sheet', 'Pillow', 'Blanket', 'Curtain', 'Carpet',
    ],
    'Beauty & Personal Care': [
        'Shampoo', 'Conditioner', 'Soap', 'Body Wash', 'Face Wash', 'Moisturizer',
        'Sunscreen', 'Lip Balm', 'Perfume', 'Deodorant', 'Toothpaste', 'Toothbrush',
        'Razor', 'Shaving Cream', 'Hair Oil', 'Face Cream', 'Serum', 'Toner',
        'Makeup Kit', 'Lipstick', 'Mascara', 'Foundation', 'Concealer', 'Blush',
        'Nail Polish', 'Hair Dryer', 'Straightener', 'Trimmer', 'Tweezers',
    ],
    'Sports & Outdoors': [
        'Cricket Bat', 'Cricket Ball', 'Football', 'Basketball', 'Tennis Racket',
        'Badminton Racket', 'Shuttlecock', 'Yoga Mat', 'Dumbbells', 'Resistance Bands',
        'Running Shoes', 'Sports Bra', 'Gym Bag', 'Water Bottle', 'Fitness Tracker',
        'Tent', 'Sleeping Bag', 'Backpack', 'Hiking Boots', 'Camping Stove',
        'Flashlight', 'Compass', 'Binoculars', 'Fishing Rod', 'Cycling Helmet',
    ],
    'Books & Media': [
        'Novel', 'Textbook', 'Dictionary', 'Encyclopedia', 'Biography',
        'Comic Book', 'Magazine', 'Newspaper', 'DVD', 'Blu-ray', 'CD',
        'USB Drive', 'Memory Card', 'External Hard Drive', 'E-book Reader',
    ],
    'Toys & Games': [
        'Action Figure', 'Doll', 'Puzzle', 'Board Game', 'Card Game',
        'Building Blocks', 'Remote Control Car', 'Drone Toy', 'Educational Toy',
        'Musical Toy', 'Art Supplies', 'Craft Kit', 'Science Kit', 'Robot Toy',
    ],
    'Health & Wellness': [
        'Vitamins', 'Protein Powder', 'Supplements', 'Multivitamin', 'Omega-3',
        'Probiotics', 'Herbal Tea', 'Green Tea', 'Yoga Mat', 'Meditation Cushion',
        'Massage Oil', 'Essential Oil', 'Aromatherapy Diffuser', 'Weight Scale',
        'Blood Pressure Monitor', 'Thermometer', 'First Aid Kit', 'Bandage',
    ],
    'Automotive': [
        'Car Battery', 'Tire', 'Engine Oil', 'Brake Pad', 'Air Filter',
        'Spark Plug', 'Car Cover', 'Car Mat', 'Seat Cover', 'Steering Cover',
        'Car Charger', 'Dash Cam', 'GPS Navigator', 'Car Freshener', 'Wiper Blade',
    ],
    'Office Supplies': [
        'Pen', 'Pencil', 'Notebook', 'Stapler', 'Paper Clips', 'Binder',
        'Folder', 'File', 'Envelope', 'Stamp', 'Marker', 'Highlighter',
        'Eraser', 'Ruler', 'Calculator', 'Desk Organizer', 'Whiteboard',
        'Projector', 'Printer Paper', 'Ink Cartridge', 'USB Drive',
    ],
    'Pet Supplies': [
        'Dog Food', 'Cat Food', 'Pet Bowl', 'Pet Leash', 'Pet Collar',
        'Pet Bed', 'Pet Toy', 'Pet Shampoo', 'Pet Grooming Kit', 'Pet Carrier',
        'Litter Box', 'Cat Litter', 'Bird Cage', 'Fish Tank', 'Pet Treats',
    ],
    'Baby Products': [
        'Diapers', 'Baby Wipes', 'Baby Formula', 'Baby Food', 'Baby Bottle',
        'Pacifier', 'Baby Clothes', 'Baby Shoes', 'Stroller', 'Car Seat',
        'Baby Carrier', 'High Chair', 'Baby Crib', 'Baby Monitor', 'Baby Toys',
    ],
    'Furniture': [
        'Sofa', 'Chair', 'Table', 'Desk', 'Bed', 'Wardrobe', 'Dresser',
        'Bookshelf', 'TV Stand', 'Coffee Table', 'Dining Table', 'Dining Chair',
        'Office Chair', 'Recliner', 'Bean Bag', 'Shoe Rack', 'Study Table',
    ],
    'Jewelry': [
        'Gold Ring', 'Silver Ring', 'Diamond Ring', 'Necklace', 'Earrings',
        'Bracelet', 'Anklet', 'Pendant', 'Chain', 'Bangle', 'Nose Pin',
        'Toe Ring', 'Hairpin', 'Brooch', 'Cufflinks', 'Tie Pin',
    ],
}

# Real product descriptions
DESCRIPTIONS = [
    'High quality product with excellent durability and performance.',
    'Premium quality item designed for long-lasting use.',
    'Eco-friendly product made from sustainable materials.',
    'Innovative design with modern features and functionality.',
    'Best-selling product with excellent customer reviews.',
    'Professional grade product suitable for commercial use.',
    'Compact and lightweight design for easy portability.',
    'Energy-efficient product that helps save on utility bills.',
    'Multi-purpose product that serves various needs.',
    'Stylish design that complements any decor or style.',
    'Easy to use product with intuitive controls and features.',
    'Durable construction ensures years of reliable performance.',
    'Premium materials used for superior quality and finish.',
    'Versatile product suitable for multiple applications.',
    'Ergonomic design for comfortable and safe use.',
]

# Units by category
UNITS_BY_CATEGORY = {
    'Electronics': 'pcs',
    'Clothing': 'pcs',
    'Food & Beverages': ['kg', 'liter', 'pcs', 'pack'],
    'Home & Kitchen': ['pcs', 'set', 'kg'],
    'Beauty & Personal Care': ['pcs', 'ml', 'gm', 'pack'],
    'Sports & Outdoors': 'pcs',
    'Books & Media': 'pcs',
    'Toys & Games': 'pcs',
    'Health & Wellness': ['pcs', 'bottle', 'pack', 'tablets'],
    'Automotive': 'pcs',
    'Office Supplies': ['pcs', 'pack', 'set'],
    'Pet Supplies': ['pcs', 'kg', 'pack'],
    'Baby Products': ['pcs', 'pack', 'set'],
    'Furniture': 'pcs',
    'Jewelry': 'pcs',
}


class Command(BaseCommand):
    help = 'Add 10,000 real products with complete information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10000,
            help='Number of products to create (default: 10000)',
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} real products...')
        
        # Get or create admin user
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
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories_dict = {}
        for cat_data in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            categories_dict[cat_data['name']] = category
        
        # Create brands
        self.stdout.write('Creating brands...')
        brands_list = []
        for brand_name in BRANDS:
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'is_active': True}
            )
            brands_list.append(brand)
        
        # Get or create default warehouse
        warehouse, _ = Warehouse.objects.get_or_create(
            name='Main Warehouse',
            defaults={
                'address': 'Default warehouse location',
                'is_active': True
            }
        )
        
        # Create products
        self.stdout.write(f'Creating {count} products...')
        products_created = 0
        batch_size = 100
        
        # Get existing SKUs, barcodes, and QR codes from database
        existing_skus, existing_barcodes, existing_qr_codes = get_existing_product_codes()
        
        # Track generated SKUs, barcodes, and QR codes to ensure uniqueness within batch
        generated_skus = set(existing_skus)
        generated_barcodes = set(existing_barcodes)
        generated_qr_codes = set(existing_qr_codes)
        
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            products_batch = []
            
            for i in range(batch_start, batch_end):
                # Select random category
                category_name = random.choice(list(PRODUCTS_BY_CATEGORY.keys()))
                category = categories_dict[category_name]
                
                # Select random product name from category
                product_names = PRODUCTS_BY_CATEGORY[category_name]
                base_name = random.choice(product_names)
                
                # Add brand name to product name
                brand = random.choice(brands_list)
                
                # Make product name unique by adding sequential number
                product_name = f"{brand.name} {base_name} - #{i+1:06d}"
                
                # Generate pricing (realistic ranges)
                if category_name == 'Electronics':
                    cost_price = Decimal(random.randint(500, 50000))
                    selling_price = cost_price * Decimal('1.3')  # 30% margin
                elif category_name == 'Clothing':
                    cost_price = Decimal(random.randint(200, 5000))
                    selling_price = cost_price * Decimal('1.5')  # 50% margin
                elif category_name == 'Food & Beverages':
                    cost_price = Decimal(random.randint(50, 500))
                    selling_price = cost_price * Decimal('1.4')  # 40% margin
                elif category_name == 'Jewelry':
                    cost_price = Decimal(random.randint(1000, 100000))
                    selling_price = cost_price * Decimal('1.6')  # 60% margin
                else:
                    cost_price = Decimal(random.randint(100, 10000))
                    selling_price = cost_price * Decimal('1.35')  # 35% margin
                
                # Generate stock levels
                current_stock = random.randint(0, 1000)
                min_stock_level = random.randint(10, 100)
                max_stock_level = random.randint(500, 2000)
                
                # Select unit
                units = UNITS_BY_CATEGORY.get(category_name, 'pcs')
                if isinstance(units, list):
                    unit = random.choice(units)
                else:
                    unit = units
                
                # Generate description
                description = random.choice(DESCRIPTIONS)
                description += f" Perfect for {category_name.lower()} needs."
                
                # Generate weight and dimensions
                weight = Decimal(random.randint(100, 5000)) / 100  # 1g to 50kg
                dimensions = f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)} cm"
                
                # Tax rate (GST in India: 0%, 5%, 12%, 18%, 28%)
                tax_rates = [Decimal('0.00'), Decimal('5.00'), Decimal('12.00'), Decimal('18.00'), Decimal('28.00')]
                tax_rate = random.choice(tax_rates)
                
                # Generate unique SKU, barcode, and QR code using utility functions
                sku = generate_unique_sku(existing_skus=generated_skus)
                barcode = generate_unique_barcode(existing_barcodes=generated_barcodes)
                qr_code = generate_unique_qr_code(existing_qr_codes=generated_qr_codes)
                
                # Create product
                product = Product(
                    name=product_name,
                    sku=sku,
                    barcode=barcode,
                    qr_code=qr_code,
                    description=description,
                    category=category,
                    brand=brand,
                    cost_price=cost_price,
                    selling_price=selling_price,
                    current_stock=current_stock,
                    min_stock_level=min_stock_level,
                    max_stock_level=max_stock_level,
                    unit=unit,
                    weight=weight,
                    dimensions=dimensions,
                    tax_rate=tax_rate,
                    is_active=True,
                    is_trackable=True,
                    created_by=admin_user,
                )
                products_batch.append(product)
            
            # Bulk create products
            try:
                created = Product.objects.bulk_create(products_batch, ignore_conflicts=False)
                products_created += len(created)
            except Exception as e:
                # If bulk_create fails, try creating one by one to identify the issue
                self.stdout.write(self.style.WARNING(f'Bulk create failed: {e}'))
                self.stdout.write('Creating products individually...')
                for product in products_batch:
                    try:
                        product.save()
                        products_created += 1
                    except Exception as e2:
                        self.stdout.write(self.style.ERROR(f'Failed to create product {product.name}: {e2}'))
            
            # Create stock entries for trackable products
            created_products = Product.objects.filter(
                name__in=[p.name for p in products_batch],
                is_trackable=True
            )
            
            stock_entries = []
            for product in created_products:
                stock_entry = Stock(
                    product=product,
                    warehouse=warehouse,
                    quantity=product.current_stock,
                    min_quantity=product.min_stock_level,
                    max_quantity=product.max_stock_level,
                )
                stock_entries.append(stock_entry)
            
            if stock_entries:
                Stock.objects.bulk_create(stock_entries, ignore_conflicts=True)
            
            # Progress update
            self.stdout.write(f'Created {products_created}/{count} products...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {products_created} real products with complete information!'
            )
        )

