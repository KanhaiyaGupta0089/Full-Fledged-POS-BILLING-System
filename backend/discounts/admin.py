"""
Discounts admin
"""
from django.contrib import admin
from .models import Coupon, Discount


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_type', 'discount_value', 'is_active', 'valid_until', 'used_count', 'max_uses']
    list_filter = ['is_active', 'discount_type', 'valid_until']
    search_fields = ['code', 'name']
    ordering = ['-created_at']
    readonly_fields = ['used_count', 'created_at', 'updated_at']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_percentage', 'min_quantity', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']








