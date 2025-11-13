from django.contrib import admin
from .models import Product, Category, Brand


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'brand',
        'selling_price', 'current_stock', 'is_low_stock',
        'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'brand', 'is_active', 'is_trackable',
        'created_at'
    ]
    search_fields = ['name', 'sku', 'barcode', 'qr_code']
    readonly_fields = ['created_at', 'updated_at', 'profit_margin', 'stock_status']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'barcode', 'qr_code', 'description')
        }),
        ('Relationships', {
            'fields': ('category', 'brand')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price', 'tax_rate', 'profit_margin')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'min_stock_level', 'max_stock_level', 'unit', 'stock_status')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions', 'image', 'additional_images')
        }),
        ('Status', {
            'fields': ('is_active', 'is_trackable')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
