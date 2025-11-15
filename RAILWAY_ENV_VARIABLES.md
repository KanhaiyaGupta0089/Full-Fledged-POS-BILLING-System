# 🔐 Railway Environment Variables Guide

## Required Environment Variables

You **MUST** add these in Railway Dashboard for your app to work:

### 1. Django Core Settings

```bash
SECRET_KEY=your-secret-key-here-generate-a-random-one
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,*.railway.app
```

**How to generate SECRET_KEY:**
```python
# Run this in Python:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. Database (PostgreSQL)

Railway automatically provides `DATABASE_URL` when you add a PostgreSQL service. If not, add:

```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
```

**To add PostgreSQL in Railway:**
1. Go to your Railway project
2. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically set `DATABASE_URL` environment variable

### 3. Redis (Optional but Recommended)

If you're using Celery or caching, add Redis:

```bash
REDIS_URL=redis://default:password@host:port/0
CELERY_BROKER_URL=redis://default:password@host:port/0
CELERY_RESULT_BACKEND=redis://default:password@host:port/0
```

**To add Redis in Railway:**
1. Go to your Railway project
2. Click **"+ New"** → **"Database"** → **"Add Redis"**
3. Railway will automatically set `REDIS_URL` environment variable

## Optional Environment Variables

### AI Features (Marketing Module)

These are optional - the app will work without them, but AI features won't work:

```bash
# OpenAI (for text generation)
OPENAI_API_KEY=sk-...

# Hugging Face (free tier available)
HUGGINGFACE_API_KEY=hf_...

# Stability AI (for high-quality image generation)
STABILITY_API_KEY=sk-...

# Replicate (for image/video generation)
REPLICATE_API_KEY=r8_...

# Use local AI models (if you want to avoid API calls)
USE_LOCAL_AI=False
```

### Payment Gateway (Razorpay)

```bash
RAZORPAY_KEY_ID=rzp_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

### Email Settings

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Security Settings (Production)

```bash
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## How to Add Environment Variables in Railway

### Method 1: Via Railway Dashboard (Recommended)

1. Go to your Railway project: https://railway.app
2. Click on your **service** (backend)
3. Click on the **"Variables"** tab
4. Click **"+ New Variable"**
5. Add each variable:
   - **Name**: `SECRET_KEY`
   - **Value**: `your-secret-key-here`
6. Click **"Add"**
7. Repeat for all required variables

### Method 2: Via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link your project
railway link

# Add variables
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="your-app.railway.app"
```

## Quick Setup Checklist

### Minimum Required (App will start):
- [ ] `SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` (your Railway domain)
- [ ] `DATABASE_URL` (from PostgreSQL service)

### Recommended (For full functionality):
- [ ] `REDIS_URL` (if using Celery/caching)
- [ ] `OPENAI_API_KEY` (for AI text generation)
- [ ] `STABILITY_API_KEY` or `REPLICATE_API_KEY` (for AI image generation)
- [ ] `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` (for payments)
- [ ] Email settings (for notifications)

## Testing Your Environment Variables

After deployment, check your Railway logs to see if there are any missing variable errors:

1. Go to Railway Dashboard → Your Service
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. Check **"Logs"** tab

Common errors:
- `SECRET_KEY not set` → Add `SECRET_KEY`
- `Database connection failed` → Check `DATABASE_URL`
- `ALLOWED_HOSTS` error → Add your Railway domain to `ALLOWED_HOSTS`

## Getting Your Railway Domain

1. Go to Railway Dashboard → Your Service
2. Click **"Settings"** tab
3. Scroll to **"Domains"** section
4. Your domain will be something like: `your-app-production.up.railway.app`
5. Add this to `ALLOWED_HOSTS`: `your-app-production.up.railway.app`

## Example Complete .env for Railway

```bash
# Django Core
SECRET_KEY=django-insecure-your-actual-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-production.up.railway.app,*.railway.app

# Database (Railway provides this automatically)
# DATABASE_URL=postgresql://postgres:password@host:port/railway

# Redis (if using)
# REDIS_URL=redis://default:password@host:port/0

# AI Features (Optional)
# OPENAI_API_KEY=sk-...
# HUGGINGFACE_API_KEY=hf_...
# STABILITY_API_KEY=sk-...
# REPLICATE_API_KEY=r8_...

# Payments (Optional)
# RAZORPAY_KEY_ID=rzp_...
# RAZORPAY_KEY_SECRET=...
```

## Important Notes

1. **Never commit `.env` files** to Git - Railway uses environment variables from the dashboard
2. **SECRET_KEY** must be unique and secret - never share it
3. **DEBUG=False** in production for security
4. **ALLOWED_HOSTS** must include your Railway domain
5. Railway automatically provides `DATABASE_URL` and `REDIS_URL` when you add those services
6. The `PORT` variable is automatically set by Railway - don't override it

## Troubleshooting

### "SECRET_KEY not set" error
→ Add `SECRET_KEY` in Railway Variables

### "Invalid HTTP_HOST" error
→ Add your Railway domain to `ALLOWED_HOSTS`

### "Database connection failed"
→ Check that PostgreSQL service is added and `DATABASE_URL` is set

### "Module not found" errors
→ Check Railway build logs - dependencies might not be installing correctly

