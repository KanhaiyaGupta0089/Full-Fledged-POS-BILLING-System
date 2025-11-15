"""
Celery tasks for products
"""
from celery import shared_task
from celery.result import AsyncResult
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
import logging
from .models import Product
from .label_generator import generate_labels_pdf

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_labels_pdf_task(self, product_ids=None, labels_per_page=6):
    """Generate labels PDF asynchronously
    
    Args:
        product_ids: List of product IDs (optional, if None, all active products)
        labels_per_page: Number of labels per page (default: 6)
    
    Returns:
        dict with 'status', 'file_path', 'filename', 'product_count'
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Fetching products...'})
        
        # Get products
        if product_ids:
            products = Product.objects.filter(id__in=product_ids, is_active=True).order_by('name')
        else:
            products = Product.objects.filter(is_active=True).order_by('name')
        
        product_count = products.count()
        if product_count == 0:
            return {
                'status': 'error',
                'error': 'No products found to generate labels'
            }
        
        self.update_state(state='PROGRESS', meta={
            'progress': 10,
            'status': f'Generating labels for {product_count} products...'
        })
        
        # Generate PDF
        pdf_buffer = generate_labels_pdf(products, labels_per_page=labels_per_page)
        
        self.update_state(state='PROGRESS', meta={
            'progress': 90,
            'status': 'Finalizing PDF...'
        })
        
        # Save to temporary storage
        filename = f'product_labels_{product_count}_products.pdf'
        file_path = f'temp_labels/{filename}'
        
        # Save PDF to storage
        pdf_content = pdf_buffer.getvalue()
        default_storage.save(file_path, ContentFile(pdf_content))
        
        return {
            'status': 'success',
            'file_path': file_path,
            'filename': filename,
            'product_count': product_count,
            'file_size': len(pdf_content)
        }
    except Exception as e:
        logger.error(f"Error generating labels PDF: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }







