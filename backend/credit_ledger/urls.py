"""
Credit Ledger URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerCreditViewSet, CreditTransactionViewSet

router = DefaultRouter()
router.register(r'accounts', CustomerCreditViewSet, basename='customer-credit')
router.register(r'transactions', CreditTransactionViewSet, basename='credit-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
