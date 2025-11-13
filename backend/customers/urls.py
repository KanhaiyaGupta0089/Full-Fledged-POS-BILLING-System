"""
Customer Management URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerCommunicationViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'communications', CustomerCommunicationViewSet, basename='customer-communication')

urlpatterns = [
    path('', include(router.urls)),
]




