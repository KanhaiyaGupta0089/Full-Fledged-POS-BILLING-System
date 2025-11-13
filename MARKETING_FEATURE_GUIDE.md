# AI-Powered Marketing & Advertisement Feature - Complete Guide

## Overview
This feature provides AI-powered content generation for advertisements, social media management, and automated posting capabilities. It integrates with free AI services and major social media platforms.

## Features

### 1. **AI Content Generation**
- **Text Generation**: AI generates headlines, descriptions, and ad copy
- **Image Generation**: AI creates custom posters and images (when API keys configured)
- **Hashtag Generation**: Automatically generates relevant hashtags
- **CTA Generation**: Creates effective call-to-action text
- **Multiple Styles & Tones**: Professional, casual, creative, modern styles with friendly, formal, humorous, persuasive tones

### 2. **Campaign Management**
- Create and manage ad campaigns
- Set budgets and track spending
- Define target audience
- Schedule campaigns with start/end dates
- Multiple campaign types: Product Promotion, Brand Awareness, Seasonal Sale, New Product Launch, Event Promotion, Custom

### 3. **Content Management**
- Create posters, videos, text posts, carousels, stories
- AI-generated or manual content
- Customize colors, fonts, text overlays
- Link content to products
- Approve/reject workflow

### 4. **Social Media Integration**
- Connect Facebook, Instagram, Twitter/X, LinkedIn, YouTube, Pinterest, TikTok
- OAuth authentication
- Automatic token refresh
- Post scheduling
- Engagement tracking

### 5. **Post Management**
- Schedule posts for future publishing
- Publish immediately
- Track engagement (likes, comments, shares, views, clicks)
- View analytics per post
- Error handling and retry

## Setup Instructions

### Backend Setup

1. **Install Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Run Migrations**:
```bash
python manage.py makemigrations marketing
python manage.py migrate marketing
```

3. **Configure AI API Keys (Optional - for enhanced features)**:
Add to your `.env` file or `settings.py`:
```python
# Optional - for AI image generation
HUGGINGFACE_API_KEY = 'your_huggingface_api_key'  # Free tier available at huggingface.co

# Optional - for better text generation
OPENAI_API_KEY = 'your_openai_api_key'  # Free tier available

# Social Media API Keys (Required for posting)
FACEBOOK_APP_ID = 'your_facebook_app_id'
FACEBOOK_APP_SECRET = 'your_facebook_app_secret'
TWITTER_CLIENT_ID = 'your_twitter_client_id'
TWITTER_CLIENT_SECRET = 'your_twitter_client_secret'
```

**Note**: The system works without API keys using template-based generation, but AI features are enhanced with API keys.

4. **Create Media Directories**:
```bash
mkdir -p media/advertisements/images
mkdir -p media/advertisements/videos
mkdir -p media/advertisements/thumbnails
```

### Frontend Setup

The frontend is already integrated. Just ensure the backend is running and accessible.

## Usage Guide

### Creating a Campaign

1. Navigate to **Marketing & AI Ads** in the sidebar
2. Click **Create Campaign**
3. Fill in:
   - Campaign Name
   - Campaign Type
   - Budget (optional)
   - Start/End Dates (optional)
   - AI Style & Tone preferences
4. Click **Create Campaign**

### Generating AI Content

1. Click **AI Generate** button or select a campaign and click the sparkles icon
2. Select:
   - Campaign (required)
   - Product (optional - for product-specific ads)
   - Content Type (Poster, Video, Text, etc.)
   - Enter a prompt (optional - AI will generate if empty)
   - Choose Style & Tone
   - Check "Generate AI Image" if you want AI-generated images
3. Click **Generate Content**
4. AI will create:
   - Headline
   - Description
   - Call-to-Action
   - Hashtags
   - Image (if requested and API configured)

### Creating Manual Content

1. Go to **Ad Contents** tab
2. Click **Create Content**
3. Fill in all fields manually
4. Upload your own image/video
5. Customize colors, fonts, text overlays
6. Save

### Connecting Social Media Accounts

1. Go to **Social Media** tab
2. Click **Connect Account**
3. Select platform
4. Click **Connect** - you'll be redirected to platform OAuth
5. Authorize the app
6. Account will be connected automatically

### Publishing Posts

1. Go to **Posts** tab
2. Click **Create Post**
3. Select:
   - Content (must be approved)
   - Social Account (must be connected)
   - Caption (optional)
   - Schedule time (optional - leave empty for immediate publish)
4. Click **Publish Post**

### Viewing Analytics

- Campaign Analytics: Click on a campaign to see total posts, engagement, budget spent
- Post Analytics: Click on a post to see likes, comments, shares, views, clicks

## API Endpoints

### Campaigns
- `GET /api/marketing/campaigns/` - List campaigns
- `POST /api/marketing/campaigns/` - Create campaign
- `GET /api/marketing/campaigns/{id}/` - Get campaign details
- `PATCH /api/marketing/campaigns/{id}/` - Update campaign
- `POST /api/marketing/campaigns/{id}/generate_content/` - Generate AI content
- `GET /api/marketing/campaigns/{id}/analytics/` - Get campaign analytics

### Contents
- `GET /api/marketing/contents/` - List contents
- `POST /api/marketing/contents/` - Create content
- `PATCH /api/marketing/contents/{id}/` - Update content
- `POST /api/marketing/contents/{id}/regenerate/` - Regenerate with AI
- `POST /api/marketing/contents/{id}/approve/` - Approve content

### Social Media
- `GET /api/marketing/social-accounts/` - List accounts
- `POST /api/marketing/social-accounts/` - Add account
- `GET /api/marketing/social-accounts/auth_url/` - Get OAuth URL
- `POST /api/marketing/social-accounts/{id}/refresh_token/` - Refresh token

### Posts
- `GET /api/marketing/posts/` - List posts
- `POST /api/marketing/posts/publish/` - Publish post
- `POST /api/marketing/posts/{id}/publish_now/` - Publish scheduled post now
- `GET /api/marketing/posts/{id}/analytics/` - Get post analytics

## AI Service Details

### Free AI Options

1. **Template-Based (Default)**: Works without any API keys
   - Generates content using templates
   - Fast and reliable
   - No costs

2. **Hugging Face (Free Tier)**:
   - Sign up at huggingface.co
   - Get free API key
   - Supports text and image generation
   - Limited requests per day (free tier)

3. **OpenAI (Free Tier)**:
   - Sign up at openai.com
   - Get free API credits
   - Better text generation quality
   - Limited credits per month

### How AI Generation Works

1. **Text Generation**:
   - Uses prompt + style + tone
   - Generates headline, description, CTA
   - Creates relevant hashtags
   - All content is saved with metadata

2. **Image Generation**:
   - Creates image based on prompt
   - Customizable dimensions
   - Saves to media/advertisements/images/
   - Falls back to manual upload if API unavailable

3. **Hashtag Generation**:
   - Analyzes content
   - Generates relevant hashtags
   - Includes trending and campaign-specific tags

## Social Media Integration

### Supported Platforms

1. **Facebook**:
   - Requires Facebook App
   - OAuth 2.0 authentication
   - Posts to Pages
   - Analytics available

2. **Instagram**:
   - Uses Facebook OAuth
   - Posts images/videos
   - Stories support (coming soon)

3. **Twitter/X**:
   - OAuth 2.0
   - Text posts with media
   - Character limit handling

4. **LinkedIn** (Coming Soon)
5. **YouTube** (Coming Soon)
6. **Pinterest** (Coming Soon)
7. **TikTok** (Coming Soon)

### OAuth Setup

1. **Facebook/Instagram**:
   - Create app at developers.facebook.com
   - Add redirect URI: `http://localhost:3000/auth/callback`
   - Get App ID and App Secret
   - Add to settings

2. **Twitter**:
   - Create app at developer.twitter.com
   - Enable OAuth 2.0
   - Add redirect URI
   - Get Client ID and Secret

## Best Practices

1. **Campaign Planning**:
   - Set clear objectives
   - Define target audience
   - Set realistic budgets
   - Plan content calendar

2. **Content Creation**:
   - Use AI for initial drafts
   - Customize AI-generated content
   - Test different styles and tones
   - Always review before publishing

3. **Social Media**:
   - Connect accounts securely
   - Schedule posts for optimal times
   - Monitor engagement
   - Respond to comments

4. **Analytics**:
   - Track campaign performance
   - Adjust based on engagement
   - Optimize content based on data

## Troubleshooting

### AI Generation Not Working
- Check API keys in settings
- Verify internet connection
- Check API quota/limits
- System falls back to templates if APIs fail

### Social Media Post Failed
- Verify account is connected
- Check token expiration
- Ensure content is approved
- Verify platform permissions

### Image Upload Issues
- Check file size (max 10MB recommended)
- Verify file format (JPG, PNG, GIF)
- Check media directory permissions
- Ensure sufficient disk space

## Security Notes

- OAuth tokens are stored encrypted in production
- API keys should be in environment variables
- Never commit API keys to version control
- Use HTTPS in production
- Regularly refresh social media tokens

## Future Enhancements

- Video generation
- A/B testing
- Advanced analytics
- Multi-platform scheduling
- Content templates library
- Brand guidelines enforcement
- Automated posting based on triggers

---

For support or questions, refer to the API documentation or contact your system administrator.


