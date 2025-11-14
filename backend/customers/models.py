"""
Enhanced Customer Management System
NOTE: Customer model is now in billing.models
This file is kept for backward compatibility - re-exports models
"""
from billing.models import Customer
from billing.customer_extras import CustomerPurchaseHistory, CustomerCommunication

# Re-export for compatibility
__all__ = ['Customer', 'CustomerPurchaseHistory', 'CustomerCommunication']





