"""
Utility functions for product management
"""
import uuid
from datetime import datetime
from django.db.models import Q


def generate_unique_sku(existing_skus=None):
    """
    Generate a unique SKU for a product.
    
    Format: PROD-YYYYMMDD-XXXXXXXX
    
    Args:
        existing_skus: Set of existing SKUs to avoid duplicates (optional)
    
    Returns:
        str: A unique SKU string
    """
    from products.models import Product
    
    if existing_skus is None:
        existing_skus = set()
    
    date_prefix = datetime.now().strftime('%Y%m%d')
    max_attempts = 100
    
    for _ in range(max_attempts):
        unique_suffix = str(uuid.uuid4())[:8].upper()
        sku = f"PROD-{date_prefix}-{unique_suffix}"
        
        # Check against provided set and database
        if sku not in existing_skus and not Product.objects.filter(sku=sku).exists():
            existing_skus.add(sku)
            return sku
    
    # Fallback: use timestamp if UUID collisions occur
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[-12:]
    sku = f"PROD-{date_prefix}-{timestamp}"
    existing_skus.add(sku)
    return sku


def generate_unique_barcode(existing_barcodes=None):
    """
    Generate a unique barcode for a product.
    
    Format: BAR-XXXXXXXX
    
    Args:
        existing_barcodes: Set of existing barcodes to avoid duplicates (optional)
    
    Returns:
        str: A unique barcode string
    """
    from products.models import Product
    
    if existing_barcodes is None:
        existing_barcodes = set()
    
    max_attempts = 100
    
    for _ in range(max_attempts):
        barcode_suffix = str(uuid.uuid4())[:8].upper()
        barcode = f"BAR-{barcode_suffix}"
        
        # Check against provided set and database
        if barcode not in existing_barcodes and not Product.objects.filter(barcode=barcode).exists():
            existing_barcodes.add(barcode)
            return barcode
    
    # Fallback: use timestamp if UUID collisions occur
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[-12:]
    barcode = f"BAR-{timestamp}"
    existing_barcodes.add(barcode)
    return barcode


def generate_unique_qr_code(existing_qr_codes=None):
    """
    Generate a unique QR code for a product.
    
    Format: QR-XXXXXXXX
    
    Args:
        existing_qr_codes: Set of existing QR codes to avoid duplicates (optional)
    
    Returns:
        str: A unique QR code string
    """
    from products.models import Product
    
    if existing_qr_codes is None:
        existing_qr_codes = set()
    
    max_attempts = 100
    
    for _ in range(max_attempts):
        qr_suffix = str(uuid.uuid4())[:8].upper()
        qr_code = f"QR-{qr_suffix}"
        
        # Check against provided set and database
        if qr_code not in existing_qr_codes and not Product.objects.filter(qr_code=qr_code).exists():
            existing_qr_codes.add(qr_code)
            return qr_code
    
    # Fallback: use timestamp if UUID collisions occur
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[-12:]
    qr_code = f"QR-{timestamp}"
    existing_qr_codes.add(qr_code)
    return qr_code


def get_existing_product_codes():
    """
    Get all existing SKUs, barcodes, and QR codes from the database.
    
    Returns:
        tuple: (set of SKUs, set of barcodes, set of QR codes)
    """
    from products.models import Product
    
    existing_skus = set(
        Product.objects.exclude(sku='').values_list('sku', flat=True)
    )
    existing_barcodes = set(
        Product.objects.exclude(
            Q(barcode__isnull=True) | Q(barcode='')
        ).values_list('barcode', flat=True)
    )
    existing_qr_codes = set(
        Product.objects.exclude(
            Q(qr_code__isnull=True) | Q(qr_code='')
        ).values_list('qr_code', flat=True)
    )
    
    return existing_skus, existing_barcodes, existing_qr_codes








