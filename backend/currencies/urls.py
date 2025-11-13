"""
Currency URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurrencyViewSet, ExchangeRateHistoryViewSet

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'exchange-rates', ExchangeRateHistoryViewSet, basename='exchange-rate')

urlpatterns = [
    path('', include(router.urls)),
]




