"""
Purchase Orders URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseOrderViewSet, GoodsReceiptNoteViewSet, SupplierPaymentViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'grns', GoodsReceiptNoteViewSet, basename='grn')
router.register(r'goods-receipt-notes', GoodsReceiptNoteViewSet, basename='goods-receipt-note')  # Alias
router.register(r'payments', SupplierPaymentViewSet, basename='supplier-payment')

urlpatterns = [
    path('', include(router.urls)),
]

