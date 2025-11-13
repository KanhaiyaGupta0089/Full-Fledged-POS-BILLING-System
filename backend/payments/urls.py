"""
Payments URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentMethodViewSet, PaymentViewSet, razorpay_webhook

router = DefaultRouter()
router.register(r'methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'transactions', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('razorpay/webhook/', razorpay_webhook, name='razorpay-webhook'),
]
