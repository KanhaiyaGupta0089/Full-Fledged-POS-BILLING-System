"""
Inventory admin
"""
from django.contrib import admin
from .models import Warehouse, Stock, InventoryTransaction


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address', 'phone']
    ordering = ['name']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'min_quantity', 'max_quantity', 'last_updated']
    list_filter = ['warehouse', 'last_updated']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    ordering = ['-last_updated']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'product', 'warehouse', 'quantity', 'reference_number', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name', 'reference_number', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at']






