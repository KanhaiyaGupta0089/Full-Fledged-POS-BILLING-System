"""
Daybook admin
"""
from django.contrib import admin
from .models import DayBookEntry


@admin.register(DayBookEntry)
class DayBookEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'entry_type', 'description', 'debit', 'credit', 'balance', 'created_at']
    list_filter = ['entry_type', 'date', 'created_at']
    search_fields = ['description', 'invoice__invoice_number']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at']







