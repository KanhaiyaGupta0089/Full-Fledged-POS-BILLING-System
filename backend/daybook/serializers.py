"""
Daybook serializers
"""
from rest_framework import serializers
from .models import DayBookEntry


class DayBookEntrySerializer(serializers.ModelSerializer):
    """Daybook entry serializer"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = DayBookEntry
        fields = '__all__'
        read_only_fields = ['created_at']








