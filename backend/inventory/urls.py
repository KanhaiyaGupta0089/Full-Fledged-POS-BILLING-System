"""
Inventory URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, StockViewSet, InventoryTransactionViewSet
from .advanced_views import (
    BatchViewSet, StockValuationViewSet, StockAdjustmentViewSet,
    StockTransferViewSet, AutoReorderRuleViewSet
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')
# Advanced inventory features
router.register(r'batches', BatchViewSet, basename='batch')
router.register(r'valuations', StockValuationViewSet, basename='stock-valuation')
router.register(r'adjustments', StockAdjustmentViewSet, basename='stock-adjustment')
router.register(r'transfers', StockTransferViewSet, basename='stock-transfer')
router.register(r'reorder-rules', AutoReorderRuleViewSet, basename='auto-reorder-rule')

urlpatterns = [
    path('', include(router.urls)),
]
