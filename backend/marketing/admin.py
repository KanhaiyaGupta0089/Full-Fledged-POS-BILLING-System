"""
Admin configuration for Marketing app
"""
from django.contrib import admin
from .models import AdCampaign, AdContent, SocialMediaAccount, SocialMediaPost, AIGenerationLog


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'status', 'budget', 'spent', 'created_by', 'created_at']
    list_filter = ['status', 'campaign_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdContent)
class AdContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'campaign', 'content_type', 'ai_generated', 'is_active', 'is_approved', 'created_at']
    list_filter = ['content_type', 'ai_generated', 'is_active', 'is_approved']
    search_fields = ['title', 'description', 'headline']
    readonly_fields = ['created_at', 'updated_at', 'generation_time']


@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ['platform', 'account_name', 'user', 'is_connected', 'is_active', 'follower_count', 'created_at']
    list_filter = ['platform', 'is_connected', 'is_active']
    search_fields = ['account_name', 'platform']
    readonly_fields = ['created_at', 'updated_at', 'last_sync']


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ['social_account', 'content', 'status', 'scheduled_time', 'published_time', 'created_at']
    list_filter = ['status', 'social_account__platform', 'created_at']
    search_fields = ['caption', 'content__title']
    readonly_fields = ['created_at', 'updated_at', 'published_time']


@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display = ['generation_type', 'ai_model', 'success', 'tokens_used', 'cost', 'created_at']
    list_filter = ['generation_type', 'success', 'ai_model']
    readonly_fields = ['created_at']


