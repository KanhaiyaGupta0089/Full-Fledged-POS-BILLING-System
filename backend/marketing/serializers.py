"""
Serializers for Marketing & Advertisement
"""
from rest_framework import serializers
from .models import AdCampaign, AdContent, SocialMediaAccount, SocialMediaPost, AIGenerationLog
from products.serializers import ProductDetailSerializer


class AdCampaignSerializer(serializers.ModelSerializer):
    """Ad Campaign Serializer"""
    created_by_name = serializers.SerializerMethodField()
    contents_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AdCampaign
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username or str(obj.created_by)
        return None
    
    def get_contents_count(self, obj):
        return obj.contents.count()
    
    def get_posts_count(self, obj):
        return obj.posts.count()


class AdContentSerializer(serializers.ModelSerializer):
    """Ad Content Serializer"""
    campaign_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AdContent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'ai_generated', 'generation_time']
    
    def get_campaign_name(self, obj):
        return obj.campaign.name if obj.campaign else None
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
    
    def get_product_details(self, obj):
        if obj.product:
            return ProductDetailSerializer(obj.product, context=self.context).data
        return None


class SocialMediaAccountSerializer(serializers.ModelSerializer):
    """Social Media Account Serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialMediaAccount
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_sync']
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
        }
    
    def get_posts_count(self, obj):
        return obj.posts.count()


class SocialMediaPostSerializer(serializers.ModelSerializer):
    """Social Media Post Serializer"""
    campaign_name = serializers.SerializerMethodField()
    content_title = serializers.SerializerMethodField()
    platform_name = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialMediaPost
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'published_time', 'platform_post_id']
    
    def get_campaign_name(self, obj):
        return obj.campaign.name if obj.campaign else None
    
    def get_content_title(self, obj):
        return obj.content.title if obj.content else None
    
    def get_platform_name(self, obj):
        return obj.social_account.platform if obj.social_account else None
    
    def get_account_name(self, obj):
        return obj.social_account.account_name if obj.social_account else None


class AIGenerationLogSerializer(serializers.ModelSerializer):
    """AI Generation Log Serializer"""
    class Meta:
        model = AIGenerationLog
        fields = '__all__'
        read_only_fields = ['created_at']


class GenerateContentSerializer(serializers.Serializer):
    """Serializer for AI content generation request"""
    campaign_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)
    content_type = serializers.ChoiceField(choices=AdContent.CONTENT_TYPES, default='poster')
    prompt = serializers.CharField(required=False, allow_blank=True)
    style = serializers.CharField(required=False, default='professional')
    tone = serializers.CharField(required=False, default='friendly')
    campaign_type = serializers.CharField(required=False, default='product_promotion')
    generate_image = serializers.BooleanField(default=False)
    generate_video = serializers.BooleanField(default=False)
    generate_multiple_posters = serializers.BooleanField(default=False)
    poster_count = serializers.IntegerField(default=3, min_value=1, max_value=10, required=False)
    image_width = serializers.IntegerField(default=1024, required=False)
    image_height = serializers.IntegerField(default=1024, required=False)
    video_duration = serializers.IntegerField(default=15, min_value=5, max_value=60, required=False)


class PostToSocialMediaSerializer(serializers.Serializer):
    """Serializer for posting to social media"""
    content_id = serializers.IntegerField(required=True)
    social_account_id = serializers.IntegerField(required=True)
    caption = serializers.CharField(required=False, allow_blank=True)
    scheduled_time = serializers.DateTimeField(required=False, allow_null=True)

