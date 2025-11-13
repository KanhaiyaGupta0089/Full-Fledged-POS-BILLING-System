"""
Marketing & Advertisement Models with AI Integration
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from accounts.models import User
from products.models import Product


class AdCampaign(models.Model):
    """Advertisement Campaign Model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CAMPAIGN_TYPES = [
        ('product_promotion', 'Product Promotion'),
        ('brand_awareness', 'Brand Awareness'),
        ('seasonal_sale', 'Seasonal Sale'),
        ('new_product', 'New Product Launch'),
        ('event', 'Event Promotion'),
        ('custom', 'Custom Campaign'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=50, choices=CAMPAIGN_TYPES, default='product_promotion')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Target Audience
    target_audience = models.TextField(blank=True, help_text="AI-generated or manual target audience description")
    target_age_min = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(13), MaxValueValidator(100)])
    target_age_max = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(13), MaxValueValidator(100)])
    target_gender = models.CharField(max_length=20, blank=True, choices=[('all', 'All'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    target_locations = models.TextField(blank=True, help_text="Comma-separated locations")
    
    # Budget & Dates
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # AI Settings
    use_ai_content = models.BooleanField(default=True, help_text="Use AI to generate content")
    ai_style = models.CharField(max_length=100, blank=True, help_text="AI style preference (e.g., professional, casual, creative)")
    ai_tone = models.CharField(max_length=100, blank=True, help_text="AI tone preference (e.g., friendly, formal, humorous)")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ad_campaigns'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AdContent(models.Model):
    """Advertisement Content Model - AI Generated"""
    CONTENT_TYPES = [
        ('poster', 'Poster/Image'),
        ('video', 'Video'),
        ('text', 'Text Post'),
        ('carousel', 'Carousel'),
        ('story', 'Story'),
    ]
    
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='contents')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='poster')
    
    # AI Generated Content
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    headline = models.CharField(max_length=200, blank=True)
    call_to_action = models.CharField(max_length=100, blank=True)
    hashtags = models.TextField(blank=True, help_text="AI-generated hashtags")
    
    # Media Files
    image = models.ImageField(upload_to='advertisements/images/', blank=True, null=True)
    video = models.FileField(upload_to='advertisements/videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='advertisements/thumbnails/', blank=True, null=True)
    
    # AI Generation Metadata
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True, help_text="Prompt used for AI generation")
    ai_model = models.CharField(max_length=100, blank=True, help_text="AI model used")
    generation_time = models.DateTimeField(null=True, blank=True)
    
    # Customization
    custom_text = models.TextField(blank=True, help_text="Custom text overlay")
    text_color = models.CharField(max_length=7, default='#000000', help_text="Hex color code")
    background_color = models.CharField(max_length=7, default='#FFFFFF', help_text="Hex color code")
    font_style = models.CharField(max_length=50, default='Arial', blank=True)
    font_size = models.IntegerField(default=24, validators=[MinValueValidator(8), MaxValueValidator(200)])
    
    # Product Link (if applicable)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='ad_contents')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ad_contents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.campaign.name} - {self.content_type}"


class SocialMediaAccount(models.Model):
    """Social Media Account Integration"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest'),
        ('tiktok', 'TikTok'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=200)
    account_id = models.CharField(max_length=200, blank=True, help_text="Platform account ID")
    page_id = models.CharField(max_length=200, blank=True, help_text="Page/Profile ID")
    
    # OAuth Tokens (encrypted in production)
    access_token = models.TextField(blank=True, help_text="OAuth access token")
    refresh_token = models.TextField(blank=True, help_text="OAuth refresh token")
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account Info
    profile_picture = models.URLField(blank=True)
    follower_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_connected = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_media_accounts'
        unique_together = ['platform', 'account_id', 'user']
        ordering = ['platform', 'account_name']
    
    def __str__(self):
        return f"{self.platform} - {self.account_name}"


class SocialMediaPost(models.Model):
    """Social Media Post Model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    content = models.ForeignKey(AdContent, on_delete=models.CASCADE, related_name='social_posts')
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='posts')
    
    # Post Details
    platform_post_id = models.CharField(max_length=200, blank=True, help_text="Post ID from platform")
    caption = models.TextField(blank=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    published_time = models.DateTimeField(null=True, blank=True)
    
    # Engagement Metrics
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    error_message = models.TextField(blank=True, help_text="Error if post failed")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_media_posts'
        ordering = ['-scheduled_time', '-created_at']
    
    def __str__(self):
        return f"{self.social_account.platform} - {self.content.title or 'Untitled'}"


class AIGenerationLog(models.Model):
    """Log of AI Content Generations"""
    content = models.ForeignKey(AdContent, on_delete=models.CASCADE, related_name='ai_logs', null=True, blank=True)
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='ai_logs', null=True, blank=True)
    
    generation_type = models.CharField(max_length=50, choices=[
        ('text', 'Text Generation'),
        ('image', 'Image Generation'),
        ('video', 'Video Generation'),
        ('hashtags', 'Hashtag Generation'),
        ('cta', 'CTA Generation'),
    ])
    
    prompt = models.TextField()
    response = models.TextField(blank=True)
    ai_model = models.CharField(max_length=100)
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'))
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_generation_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.generation_type} - {self.created_at}"


