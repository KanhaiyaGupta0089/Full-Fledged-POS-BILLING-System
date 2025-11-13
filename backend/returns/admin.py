"""
Returns admin
"""
from django.contrib import admin
from .models import Return, ReturnItem


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0
    readonly_fields = ['total']


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'invoice', 'reason', 'status', 'total_amount', 'refund_amount', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['return_number', 'invoice__invoice_number']
    ordering = ['-created_at']
    readonly_fields = ['return_number', 'created_at', 'updated_at']
    inlines = [ReturnItemInline]


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ['return_order', 'product', 'quantity', 'unit_price', 'total']
    list_filter = ['return_order__created_at']
    search_fields = ['return_order__return_number', 'product__name']
    ordering = ['-return_order__created_at']






