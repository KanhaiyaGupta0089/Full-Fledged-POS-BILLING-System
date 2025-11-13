"""
Reports URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportsViewSet

router = DefaultRouter()
router.register(r'reports', ReportsViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]




