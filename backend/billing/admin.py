"""
Billing admin
"""
from django.contrib import admin
from .models import Customer, Invoice, InvoiceItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone', 'gstin']
    ordering = ['-created_at']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'total_amount', 'paid_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'customer_phone', 'customer_email']
    ordering = ['-created_at']
    readonly_fields = ['invoice_number', 'balance_amount', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'product', 'quantity', 'unit_price', 'total']
    list_filter = ['invoice__created_at']
    search_fields = ['invoice__invoice_number', 'product__name', 'product__sku']
    ordering = ['-invoice__created_at']







