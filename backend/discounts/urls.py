"""
Discounts URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, DiscountViewSet

router = DefaultRouter()
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'discounts', DiscountViewSet, basename='discount')

urlpatterns = [
    path('', include(router.urls)),
]
