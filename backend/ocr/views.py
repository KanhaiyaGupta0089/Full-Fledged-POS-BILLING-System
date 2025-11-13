"""
OCR API Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.uploadedfile import UploadedFile
from .service import ocr_service


class OCRViewSet(viewsets.ViewSet):
    """OCR API endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='extract-text')
    def extract_text(self, request):
        """Extract text from uploaded image"""
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'success': False, 'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            language = request.data.get('language', 'eng')
            
            result = ocr_service.extract_text(image_file, language)
            
            if not result.get('success', False):
                return Response(
                    result,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result)
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='extract-invoice')
    def extract_invoice(self, request):
        """Extract structured data from invoice image"""
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'success': False, 'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            result = ocr_service.extract_invoice_data(image_file)
            
            if not result.get('success', False):
                return Response(
                    result,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result)
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='extract-receipt')
    def extract_receipt(self, request):
        """Extract data from expense receipt image"""
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'success': False, 'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            result = ocr_service.extract_expense_receipt_data(image_file)
            
            if not result.get('success', False):
                return Response(
                    result,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result)
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

