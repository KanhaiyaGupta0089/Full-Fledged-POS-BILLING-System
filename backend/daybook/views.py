"""
Daybook views
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DayBookEntry
from .serializers import DayBookEntrySerializer
from common.permissions import IsAdminOrManager, IsAdminOrOwner


class DayBookEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Daybook entry viewset (read-only, auto-generated)"""
    queryset = DayBookEntry.objects.select_related('invoice').all()
    serializer_class = DayBookEntrySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['entry_type', 'date']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date', '-created_at']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get daybook summary for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date().isoformat())
        
        if not start_date:
            start_date = timezone.now().date().isoformat()
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=400
            )
        
        entries = self.queryset.filter(date__range=[start, end])
        
        summary = {
            'start_date': start_date,
            'end_date': end_date,
            'total_debit': entries.aggregate(Sum('debit'))['debit__sum'] or 0,
            'total_credit': entries.aggregate(Sum('credit'))['credit__sum'] or 0,
            'entries': DayBookEntrySerializer(entries, many=True).data
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's daybook entries"""
        today = timezone.now().date()
        entries = self.queryset.filter(date=today)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)







