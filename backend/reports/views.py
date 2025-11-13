"""
Views for Advanced Reporting
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from .gst_reports import GSTReports
from .tax_reports import TaxReports
from .pl_reports import PLReports
from common.permissions import IsAdminOrManager


class ReportsViewSet(viewsets.ViewSet):
    """Advanced Reports API endpoints"""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    @action(detail=False, methods=['post'], url_path='gst/gstr1')
    def gstr1(self, request):
        """Generate GSTR-1 (Outward Supplies) report"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            gstin = request.data.get('gstin')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = GSTReports.gstr1_outward_supplies(date_from, date_to, gstin)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='gst/gstr2')
    def gstr2(self, request):
        """Generate GSTR-2 (Inward Supplies) report"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            supplier_gstin = request.data.get('supplier_gstin')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = GSTReports.gstr2_inward_supplies(date_from, date_to, supplier_gstin)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='gst/summary')
    def gst_summary(self, request):
        """Generate GST Summary report"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = GSTReports.gst_summary(date_from, date_to)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='tax/by-category')
    def tax_by_category(self, request):
        """Generate tax report by category"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = TaxReports.tax_by_category(date_from, date_to)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='tax/by-product')
    def tax_by_product(self, request):
        """Generate tax report by product"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            product_id = request.data.get('product_id')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = TaxReports.tax_by_product(date_from, date_to, product_id)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='tax/summary')
    def tax_summary(self, request):
        """Generate tax summary report"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = TaxReports.tax_summary(date_from, date_to)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='pl/statement')
    def pl_statement(self, request):
        """Generate Profit & Loss statement"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = PLReports.profit_loss_statement(date_from, date_to)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='pl/revenue-breakdown')
    def revenue_breakdown(self, request):
        """Generate revenue breakdown"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = PLReports.revenue_breakdown(date_from, date_to)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='pl/expense-breakdown')
    def expense_breakdown(self, request):
        """Generate expense breakdown"""
        try:
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            
            if not date_from or not date_to:
                return Response(
                    {'error': 'date_from and date_to are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            report = PLReports.expense_breakdown(date_from, date_to)
            return Response(report)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
