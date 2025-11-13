"""
Daybook URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DayBookEntryViewSet

router = DefaultRouter()
router.register(r'entries', DayBookEntryViewSet, basename='daybook-entry')

urlpatterns = [
    path('', include(router.urls)),
]
