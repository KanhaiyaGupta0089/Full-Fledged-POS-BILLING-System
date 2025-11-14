"""
Forecasting URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesForecastViewSet, DemandPatternViewSet, OptimalStockLevelViewSet

router = DefaultRouter()
router.register(r'forecasts', SalesForecastViewSet, basename='sales-forecast')
router.register(r'demand-patterns', DemandPatternViewSet, basename='demand-pattern')
router.register(r'optimal-stock-levels', OptimalStockLevelViewSet, basename='optimal-stock-level')

urlpatterns = [
    path('', include(router.urls)),
]





