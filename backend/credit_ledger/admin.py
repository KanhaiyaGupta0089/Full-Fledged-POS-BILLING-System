"""
Credit Ledger admin
"""
from django.contrib import admin
from .models import CustomerCredit, CreditTransaction


@admin.register(CustomerCredit)
class CustomerCreditAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_credit', 'total_paid', 'balance', 'last_transaction_date']
    list_filter = ['last_transaction_date']
    search_fields = ['customer__name', 'customer__phone']
    ordering = ['-balance']
    readonly_fields = ['balance', 'created_at', 'updated_at']


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer_credit', 'transaction_type', 'amount', 'invoice', 'created_by', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['customer_credit__customer__name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']







