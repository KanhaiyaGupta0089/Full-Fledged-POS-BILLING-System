"""
Social Media Integration Service
Supports: Facebook, Instagram, Twitter, LinkedIn
"""
import requests
import logging
from typing import Dict, Optional
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SocialMediaService:
    """Service for managing social media posts"""
    
    def __init__(self):
        self.facebook_api_version = "v18.0"
        self.instagram_api_version = "v18.0"
    
    def post_to_facebook(self, account, content, caption: str = "", scheduled_time: Optional[datetime] = None) -> Dict:
        """Post to Facebook"""
        try:
            if not account.access_token:
                return {'success': False, 'error': 'Access token not available'}
            
            url = f"https://graph.facebook.com/{self.facebook_api_version}/{account.page_id}/photos"
            
            # Prepare data
            data = {
                'access_token': account.access_token,
                'message': caption or content.title or '',
            }
            
            # Handle image upload
            if content.image:
                files = {'source': content.image.file}
                response = requests.post(url, data=data, files=files, timeout=30)
            else:
                # Text-only post
                url = f"https://graph.facebook.com/{self.facebook_api_version}/{account.page_id}/feed"
                response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'post_id': result.get('id', ''),
                    'message': 'Post published successfully'
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('error', {}).get('message', 'Unknown error'),
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Facebook post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_instagram(self, account, content, caption: str = "") -> Dict:
        """Post to Instagram"""
        try:
            if not account.access_token:
                return {'success': False, 'error': 'Access token not available'}
            
            # Instagram requires two-step process
            # Step 1: Create media container
            url = f"https://graph.facebook.com/{self.instagram_api_version}/{account.page_id}/media"
            
            data = {
                'access_token': account.access_token,
                'caption': caption or content.title or '',
                'image_url': content.image.url if content.image else '',
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                container_id = response.json().get('id')
                
                # Step 2: Publish
                publish_url = f"https://graph.facebook.com/{self.instagram_api_version}/{account.page_id}/media_publish"
                publish_data = {
                    'access_token': account.access_token,
                    'creation_id': container_id
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                
                if publish_response.status_code == 200:
                    result = publish_response.json()
                    return {
                        'success': True,
                        'post_id': result.get('id', ''),
                        'message': 'Post published successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to publish to Instagram',
                        'status_code': publish_response.status_code
                    }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create Instagram media container',
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Instagram post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_twitter(self, account, content, caption: str = "") -> Dict:
        """Post to Twitter/X"""
        try:
            if not account.access_token:
                return {'success': False, 'error': 'Access token not available'}
            
            # Twitter API v2
            url = "https://api.twitter.com/2/tweets"
            
            headers = {
                'Authorization': f'Bearer {account.access_token}',
                'Content-Type': 'application/json'
            }
            
            text = caption or content.title or content.description or ''
            # Twitter character limit
            if len(text) > 280:
                text = text[:277] + '...'
            
            data = {
                'text': text
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'post_id': result.get('data', {}).get('id', ''),
                    'message': 'Tweet published successfully'
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': error_data.get('detail', 'Unknown error'),
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Twitter post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_facebook_auth_url(self, redirect_uri: str) -> str:
        """Get Facebook OAuth URL"""
        app_id = getattr(settings, 'FACEBOOK_APP_ID', '')
        scopes = 'pages_manage_posts,pages_read_engagement,business_management'
        return f"https://www.facebook.com/v{self.facebook_api_version}/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={scopes}&response_type=code"
    
    def get_instagram_auth_url(self, redirect_uri: str) -> str:
        """Get Instagram OAuth URL (uses Facebook OAuth)"""
        return self.get_facebook_auth_url(redirect_uri)
    
    def get_twitter_auth_url(self, redirect_uri: str) -> str:
        """Get Twitter OAuth URL"""
        # Twitter OAuth 2.0 flow
        client_id = getattr(settings, 'TWITTER_CLIENT_ID', '')
        scopes = 'tweet.read tweet.write users.read offline.access'
        return f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state=random_state&code_challenge=challenge&code_challenge_method=plain"
    
    def refresh_token(self, account) -> bool:
        """Refresh OAuth token"""
        try:
            if account.platform == 'facebook' or account.platform == 'instagram':
                # Facebook token refresh
                url = f"https://graph.facebook.com/{self.facebook_api_version}/oauth/access_token"
                params = {
                    'grant_type': 'fb_exchange_token',
                    'client_id': getattr(settings, 'FACEBOOK_APP_ID', ''),
                    'client_secret': getattr(settings, 'FACEBOOK_APP_SECRET', ''),
                    'fb_exchange_token': account.access_token
                }
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    account.access_token = data.get('access_token', '')
                    expires_in = data.get('expires_in', 5184000)  # Default 60 days
                    account.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
                    account.save()
                    return True
            return False
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    def get_post_analytics(self, account, post_id: str) -> Dict:
        """Get analytics for a post"""
        try:
            if account.platform == 'facebook':
                url = f"https://graph.facebook.com/{self.facebook_api_version}/{post_id}/insights"
                params = {
                    'access_token': account.access_token,
                    'metric': 'post_impressions,post_engaged_users,post_clicks'
                }
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    return {'success': True, 'data': response.json()}
            
            return {'success': False, 'error': 'Analytics not available for this platform'}
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {'success': False, 'error': str(e)}


# Singleton instance
social_media_service = SocialMediaService()


