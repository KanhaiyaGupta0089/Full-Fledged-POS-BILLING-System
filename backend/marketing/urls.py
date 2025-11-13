"""
Marketing URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdCampaignViewSet, AdContentViewSet, SocialMediaAccountViewSet,
    SocialMediaPostViewSet, AIGenerationLogViewSet
)

router = DefaultRouter()
router.register(r'campaigns', AdCampaignViewSet, basename='campaign')
router.register(r'contents', AdContentViewSet, basename='content')
router.register(r'social-accounts', SocialMediaAccountViewSet, basename='social-account')
router.register(r'posts', SocialMediaPostViewSet, basename='post')
router.register(r'ai-logs', AIGenerationLogViewSet, basename='ai-log')

urlpatterns = [
    path('', include(router.urls)),
]


