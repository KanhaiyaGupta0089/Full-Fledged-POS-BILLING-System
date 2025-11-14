"""
Free OCR Service Integration
Using Tesseract OCR (free and open-source)
"""
import os
import logging
from PIL import Image
import pytesseract
from django.core.files.uploadedfile import UploadedFile
from io import BytesIO
import json

logger = logging.getLogger(__name__)


class OCRService:
    """OCR Service using Tesseract"""
    
    def __init__(self):
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            self.is_available = True
        except Exception as e:
            logger.warning(f"Tesseract OCR not available: {e}")
            self.is_available = False
    
    def extract_text(self, image_file, language='eng'):
        """
        Extract text from image
        
        Args:
            image_file: File object or path to image
            language: Language code (default: 'eng')
        
        Returns:
            dict with 'text', 'confidence', 'words'
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'OCR service not available. Please install Tesseract OCR.'
            }
        
        try:
            # Open image
            if isinstance(image_file, UploadedFile):
                image = Image.open(BytesIO(image_file.read()))
            elif isinstance(image_file, str):
                image = Image.open(image_file)
            else:
                image = Image.open(image_file)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text with confidence
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract words with positions
            words = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:
                    words.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': avg_confidence,
                'words': words,
                'raw_data': data
            }
        
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_invoice_data(self, image_file):
        """
        Extract structured data from invoice image
        Tries to identify invoice number, date, amount, etc.
        """
        result = self.extract_text(image_file)
        
        if not result['success']:
            return result
        
        text = result['text']
        
        # Try to extract invoice number
        import re
        invoice_patterns = [
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'inv\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'bill\s*#?\s*:?\s*([A-Z0-9\-]+)',
        ]
        
        invoice_number = None
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_number = match.group(1)
                break
        
        # Try to extract date
        date_patterns = [
            r'date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        date = None
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = match.group(1)
                break
        
        # Try to extract total amount
        amount_patterns = [
            r'total\s*:?\s*[₹$]?\s*([\d,]+\.?\d*)',
            r'amount\s*:?\s*[₹$]?\s*([\d,]+\.?\d*)',
            r'grand\s*total\s*:?\s*[₹$]?\s*([\d,]+\.?\d*)',
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                except:
                    pass
                break
        
        return {
            'success': True,
            'text': text,
            'extracted_data': {
                'invoice_number': invoice_number,
                'date': date,
                'total_amount': amount,
            },
            'confidence': result['confidence']
        }
    
    def extract_expense_receipt_data(self, image_file):
        """Extract data from expense receipt"""
        result = self.extract_text(image_file)
        
        if not result['success']:
            return result
        
        text = result['text']
        
        # Extract vendor name (usually at top)
        lines = text.split('\n')
        vendor_name = lines[0] if lines else ''
        
        # Extract amount
        import re
        amount_patterns = [
            r'total\s*:?\s*[₹$]?\s*([\d,]+\.?\d*)',
            r'amount\s*:?\s*[₹$]?\s*([\d,]+\.?\d*)',
            r'[₹$]\s*([\d,]+\.?\d*)',
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                except:
                    pass
                if amount:
                    break
        
        # Extract date
        date_patterns = [
            r'date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        date = None
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = match.group(1)
                break
        
        return {
            'success': True,
            'text': text,
            'extracted_data': {
                'vendor_name': vendor_name,
                'amount': amount,
                'date': date,
            },
            'confidence': result['confidence']
        }


# Global OCR service instance
ocr_service = OCRService()





