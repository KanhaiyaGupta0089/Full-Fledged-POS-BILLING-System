"""
Views for Marketing & Advertisement
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO
import base64
import logging

from .models import AdCampaign, AdContent, SocialMediaAccount, SocialMediaPost, AIGenerationLog

logger = logging.getLogger(__name__)
from .serializers import (
    AdCampaignSerializer, AdContentSerializer, SocialMediaAccountSerializer,
    SocialMediaPostSerializer, AIGenerationLogSerializer,
    GenerateContentSerializer, PostToSocialMediaSerializer
)
from .ai_service import ai_generator
from .social_media_service import social_media_service
from products.models import Product


class AdCampaignViewSet(viewsets.ModelViewSet):
    """Ad Campaign CRUD operations"""
    queryset = AdCampaign.objects.select_related('created_by').prefetch_related('contents', 'posts')
    serializer_class = AdCampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'campaign_type']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'budget']
    ordering = ['-created_at']
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_content(self, request, pk=None):
        """Generate AI content for campaign"""
        campaign = self.get_object()
        serializer = GenerateContentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        content_type = data.get('content_type', 'poster')
        style = data.get('style', 'professional')
        tone = data.get('tone', 'friendly')
        product_id = data.get('product_id')
        
        # Get product if specified
        product = None
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                pass
        
        # Generate content using AI
        prompt = data.get('prompt', '')
        if not prompt and product:
            prompt = f"Create advertisement for {product.name}: {product.description or ''}"
        elif not prompt:
            prompt = f"Create {campaign.campaign_type} advertisement for {campaign.name}"
        
        # Generate text content
        text_result = ai_generator.generate_text(prompt, max_length=200, style=style, tone=tone)
        generated_text = text_result.get('text', '')
        
        # Generate headline
        headline = ai_generator.generate_headline(
            product_name=product.name if product else '',
            campaign_type=campaign.campaign_type
        )
        
        # Generate CTA
        cta = ai_generator.generate_cta(campaign.campaign_type)
        
        # Generate hashtags
        hashtags = ai_generator.generate_hashtags(generated_text, count=10)
        hashtags_str = ' '.join(hashtags)
        
        # Create content object
        content = AdContent.objects.create(
            campaign=campaign,
            content_type=content_type,
            title=headline,
            description=generated_text,
            headline=headline,
            call_to_action=cta,
            hashtags=hashtags_str,
            product=product,
            ai_generated=True,
            ai_prompt=prompt,
            ai_model=text_result.get('model', 'template-based'),
            generation_time=timezone.now(),
            is_active=True
        )
        
        # Generate multiple posters if requested
        if data.get('generate_multiple_posters', False):
            poster_count = data.get('poster_count', 3)
            base_prompt = ai_generator.generate_image_prompt(
                product_name=product.name if product else '',
                campaign_type=campaign.campaign_type,
                style=style
            )
            
            poster_variations = ai_generator.generate_multiple_posters(
                base_prompt,
                count=poster_count,
                width=data.get('image_width', 1024),
                height=data.get('image_height', 1024),
                style=style
            )
            
            created_contents = [content]  # Start with the main content
            
            # Create additional content objects for each poster variation
            for i, variation in enumerate(poster_variations):
                if variation.get('success') and variation.get('image_data'):
                    try:
                        variation_content = AdContent.objects.create(
                            campaign=campaign,
                            content_type='poster',
                            title=f"{headline} - Variation {variation['index']}",
                            description=generated_text,
                            headline=headline,
                            call_to_action=cta,
                            hashtags=hashtags_str,
                            product=product,
                            ai_generated=True,
                            ai_prompt=variation['prompt'],
                            ai_model='pillow-generated',
                            generation_time=timezone.now(),
                            is_active=True
                        )
                        
                        # Save the image
                        variation_content.image.save(
                            f"{campaign.name}_poster_{variation_content.id}_v{variation['index']}.png",
                            ContentFile(variation['image_data']),
                            save=True
                        )
                        created_contents.append(variation_content)
                    except Exception as e:
                        logger.error(f"Error creating poster variation {variation['index']}: {e}")
            
            # Return all created contents
            serializer = AdContentSerializer(created_contents, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Generate image if requested
        if data.get('generate_image', False):
            image_prompt = ai_generator.generate_image_prompt(
                product_name=product.name if product else '',
                campaign_type=campaign.campaign_type,
                style=style
            )
            image_result = ai_generator.generate_image(
                image_prompt,
                width=data.get('image_width', 1024),
                height=data.get('image_height', 1024)
            )
            
            if image_result.get('success') and image_result.get('image_data'):
                try:
                    content.image.save(
                        f"{campaign.name}_{content.id}.png",
                        ContentFile(image_result['image_data']),
                        save=True
                    )
                except Exception as e:
                    logger.error(f"Error saving AI-generated image: {e}")
                    # Continue without image - user can upload manually
        
        # Generate video if requested (for any content type, but typically for video type)
        if data.get('generate_video', False):
            video_prompt = ai_generator.generate_image_prompt(
                product_name=product.name if product else '',
                campaign_type=campaign.campaign_type,
                style=style
            )
            video_result = ai_generator.generate_video(
                video_prompt,
                duration=data.get('video_duration', 15),
                width=1280,
                height=720
            )
            
            if video_result.get('success') and video_result.get('video_data'):
                try:
                    content.video.save(
                        f"{campaign.name}_{content.id}.mp4",
                        ContentFile(video_result['video_data']),
                        save=True
                    )
                    
                    # Generate thumbnail image for video
                    thumbnail_prompt = ai_generator.generate_image_prompt(
                        product_name=product.name if product else '',
                        campaign_type=campaign.campaign_type,
                        style=style
                    )
                    thumbnail_result = ai_generator.generate_image(thumbnail_prompt, width=640, height=360)
                    if thumbnail_result.get('success') and thumbnail_result.get('image_data'):
                        content.thumbnail.save(
                            f"{campaign.name}_{content.id}_thumb.png",
                            ContentFile(thumbnail_result['image_data']),
                            save=True
                        )
                except Exception as e:
                    logger.error(f"Error saving AI-generated video: {e}")
                    # Continue without video - user can upload manually
        
        # Log generation
        AIGenerationLog.objects.create(
            content=content,
            campaign=campaign,
            generation_type='text',
            prompt=prompt,
            response=generated_text,
            ai_model=text_result.get('model', 'template-based'),
            tokens_used=text_result.get('tokens_used', 0),
            success=text_result.get('success', True)
        )
        
        return Response(AdContentSerializer(content, context={'request': request}).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get campaign analytics"""
        campaign = self.get_object()
        
        total_posts = campaign.posts.count()
        published_posts = campaign.posts.filter(status='published').count()
        total_engagement = sum(
            post.likes + post.comments + post.shares + post.views
            for post in campaign.posts.all()
        )
        
        return Response({
            'total_posts': total_posts,
            'published_posts': published_posts,
            'total_engagement': total_engagement,
            'budget_spent': float(campaign.spent),
            'budget_remaining': float(campaign.budget - campaign.spent),
        })


class AdContentViewSet(viewsets.ModelViewSet):
    """Ad Content CRUD operations"""
    queryset = AdContent.objects.select_related('campaign', 'product')
    serializer_class = AdContentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'campaign', 'is_active', 'is_approved']
    search_fields = ['title', 'description', 'headline']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate content using AI"""
        content = self.get_object()
        campaign = content.campaign
        
        # Regenerate text
        prompt = request.data.get('prompt', content.ai_prompt or f"Create advertisement for {campaign.name}")
        style = request.data.get('style', 'professional')
        tone = request.data.get('tone', 'friendly')
        
        text_result = ai_generator.generate_text(prompt, max_length=200, style=style, tone=tone)
        
        # Update content
        content.description = text_result.get('text', content.description)
        content.headline = ai_generator.generate_headline(
            product_name=content.product.name if content.product else '',
            campaign_type=campaign.campaign_type
        )
        content.call_to_action = ai_generator.generate_cta(campaign.campaign_type)
        content.hashtags = ' '.join(ai_generator.generate_hashtags(content.description, count=10))
        content.ai_prompt = prompt
        content.ai_model = text_result.get('model', 'template-based')
        content.generation_time = timezone.now()
        content.save()
        
        return Response(AdContentSerializer(content).data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve content"""
        content = self.get_object()
        content.is_approved = True
        content.save()
        return Response({'message': 'Content approved'})


class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    """Social Media Account CRUD operations"""
    queryset = SocialMediaAccount.objects.select_related('user').prefetch_related('posts')
    serializer_class = SocialMediaAccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform', 'is_active', 'is_connected']
    search_fields = ['account_name', 'platform']
    ordering = ['platform', 'account_name']
    
    def get_queryset(self):
        """Filter by current user"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def auth_url(self, request):
        """Get OAuth URL for platform"""
        platform = request.query_params.get('platform')
        redirect_uri = request.query_params.get('redirect_uri', 'http://localhost:3000/auth/callback')
        
        if platform == 'facebook':
            url = social_media_service.get_facebook_auth_url(redirect_uri)
        elif platform == 'instagram':
            url = social_media_service.get_instagram_auth_url(redirect_uri)
        elif platform == 'twitter':
            url = social_media_service.get_twitter_auth_url(redirect_uri)
        else:
            return Response({'error': 'Invalid platform'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'auth_url': url})
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh OAuth token"""
        account = self.get_object()
        success = social_media_service.refresh_token(account)
        if success:
            return Response({'message': 'Token refreshed successfully'})
        return Response({'error': 'Failed to refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class SocialMediaPostViewSet(viewsets.ModelViewSet):
    """Social Media Post CRUD operations"""
    queryset = SocialMediaPost.objects.select_related('campaign', 'content', 'social_account', 'created_by')
    serializer_class = SocialMediaPostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'campaign', 'social_account']
    search_fields = ['caption']
    ordering_fields = ['scheduled_time', 'published_time', 'created_at']
    ordering = ['-scheduled_time', '-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def publish(self, request):
        """Publish post to social media"""
        serializer = PostToSocialMediaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        content_id = data['content_id']
        account_id = data['social_account_id']
        caption = data.get('caption', '')
        scheduled_time = data.get('scheduled_time')
        
        try:
            content = AdContent.objects.get(pk=content_id)
            account = SocialMediaAccount.objects.get(pk=account_id, user=request.user)
        except (AdContent.DoesNotExist, SocialMediaAccount.DoesNotExist):
            return Response({'error': 'Content or account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create post record
        post = SocialMediaPost.objects.create(
            campaign=content.campaign,
            content=content,
            social_account=account,
            caption=caption or content.description or content.title,
            scheduled_time=scheduled_time,
            status='scheduled' if scheduled_time else 'draft',
            created_by=request.user
        )
        
        # Publish immediately if not scheduled
        if not scheduled_time:
            result = self._publish_to_platform(account, content, caption)
            if result.get('success'):
                post.status = 'published'
                post.platform_post_id = result.get('post_id', '')
                post.published_time = timezone.now()
                post.save()
                return Response(SocialMediaPostSerializer(post).data)
            else:
                post.status = 'failed'
                post.error_message = result.get('error', 'Unknown error')
                post.save()
                return Response({'error': result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(SocialMediaPostSerializer(post).data)
    
    def _publish_to_platform(self, account, content, caption):
        """Publish to specific platform"""
        if account.platform == 'facebook':
            return social_media_service.post_to_facebook(account, content, caption)
        elif account.platform == 'instagram':
            return social_media_service.post_to_instagram(account, content, caption)
        elif account.platform == 'twitter':
            return social_media_service.post_to_twitter(account, content, caption)
        else:
            return {'success': False, 'error': f'Platform {account.platform} not supported'}
    
    @action(detail=True, methods=['post'])
    def publish_now(self, request, pk=None):
        """Publish scheduled post now"""
        post = self.get_object()
        
        if post.status == 'published':
            return Response({'error': 'Post already published'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = self._publish_to_platform(post.social_account, post.content, post.caption)
        
        if result.get('success'):
            post.status = 'published'
            post.platform_post_id = result.get('post_id', '')
            post.published_time = timezone.now()
            post.save()
            return Response(SocialMediaPostSerializer(post).data)
        else:
            post.status = 'failed'
            post.error_message = result.get('error', 'Unknown error')
            post.save()
            return Response({'error': result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get post analytics"""
        post = self.get_object()
        
        if post.status != 'published' or not post.platform_post_id:
            return Response({'error': 'Post not published'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = social_media_service.get_post_analytics(post.social_account, post.platform_post_id)
        return Response(result)


class AIGenerationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """AI Generation Log ViewSet (Read-only)"""
    queryset = AIGenerationLog.objects.select_related('content', 'campaign')
    serializer_class = AIGenerationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['generation_type', 'success']
    ordering = ['-created_at']

