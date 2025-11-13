"""
Payments admin
"""
from django.contrib import admin
from .models import PaymentMethod, Payment


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'requires_verification', 'created_at']
    list_filter = ['is_active', 'requires_verification']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['invoice__invoice_number', 'transaction_id', 'payment_reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

