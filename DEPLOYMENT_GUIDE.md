# Deployment Guide - Free Platform Deployment

This guide will help you deploy your POS Billing and Inventory System to free hosting platforms like **Render**, **Railway**, or **Fly.io**.

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended - Easiest)

Render offers free tiers for:
- Web Services (Django backend)
- Static Sites (React frontend)
- PostgreSQL Database
- Redis (optional)

**Free Tier Limits:**
- 750 hours/month (enough for 24/7 operation)
- Services spin down after 15 minutes of inactivity (free tier)
- PostgreSQL: 1GB storage, 90 days retention
- Redis: 25MB storage

### Option 2: Railway

Railway offers:
- $5 free credit monthly
- PostgreSQL included
- Auto-deploy from GitHub

### Option 3: Fly.io

Fly.io offers:
- 3 shared-cpu VMs free
- PostgreSQL addon available
- Global edge deployment

---

## 📋 Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Render/Railway/Fly.io Account** - Sign up at:
   - Render: https://render.com
   - Railway: https://railway.app
   - Fly.io: https://fly.io

---

## 🎯 Deployment Steps for Render

### Step 1: Prepare Your Repository

1. Make sure all your code is committed and pushed to GitHub:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

2. Verify these files exist in your repo:
   - `render.yaml` (at root)
   - `backend/requirements.txt`
   - `frontend/package.json`
   - `Procfile` (optional, for Heroku compatibility)

### Step 2: Deploy on Render

#### A. Deploy Backend (Django)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `pos-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `cd backend && gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT`
   - **Plan**: Free

5. Add Environment Variables:
   ```
   SECRET_KEY=<generate-a-random-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=pos-backend.onrender.com,*.onrender.com
   PYTHON_VERSION=3.12.0
   DJANGO_SETTINGS_MODULE=pos_system.settings
   ```

6. Click **"Create Web Service"**

#### B. Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `pos-database`
   - **Database**: `pos_system`
   - **User**: `pos_user`
   - **Plan**: Free
3. Click **"Create Database"**
4. Copy the **Internal Database URL**
5. Go back to your backend service → **Environment** tab
6. Add:
   ```
   DATABASE_URL=<paste-internal-database-url>
   ```

#### C. Create Redis (Optional)

1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name**: `pos-redis`
   - **Plan**: Free
3. Click **"Create Redis"**
4. Copy the **Internal Redis URL**
5. Add to backend environment:
   ```
   REDIS_URL=<paste-internal-redis-url>
   CELERY_BROKER_URL=<paste-internal-redis-url>
   CELERY_RESULT_BACKEND=<paste-internal-redis-url>
   ```

#### D. Deploy Frontend (React)

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `pos-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Plan**: Free

4. Add Environment Variable:
   ```
   VITE_API_BASE_URL=https://pos-backend.onrender.com/api
   ```

5. Click **"Create Static Site"**

### Step 3: Run Database Migrations

1. Go to your backend service on Render
2. Click **"Shell"** tab
3. Run:
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### Step 4: Update CORS Settings

1. In backend service → **Environment** tab
2. Add:
   ```
   CORS_ALLOWED_ORIGINS=https://pos-frontend.onrender.com
   ```

### Step 5: Access Your Application

- Frontend: `https://pos-frontend.onrender.com`
- Backend API: `https://pos-backend.onrender.com/api`
- Admin Panel: `https://pos-backend.onrender.com/admin`

---

## 🚂 Deployment Steps for Railway

### Step 1: Connect Repository

1. Go to https://railway.app
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository

### Step 2: Add Services

Railway will auto-detect your services. You can also add manually:

1. **Backend Service**:
   - Add PostgreSQL database (Railway will auto-create)
   - Set start command: `cd backend && gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT`
   - Add environment variables (same as Render)

2. **Frontend Service**:
   - Add as static site or Node.js service
   - Build command: `cd frontend && npm install && npm run build`
   - Set `VITE_API_BASE_URL` to your backend URL

### Step 3: Deploy

Railway will automatically deploy on every push to your main branch.

---

## ✈️ Deployment Steps for Fly.io

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login

```bash
fly auth login
```

### Step 3: Initialize Backend

```bash
cd backend
fly launch
```

Follow the prompts. Fly.io will create:
- `fly.toml` configuration
- Dockerfile (if needed)

### Step 4: Deploy

```bash
fly deploy
```

---

## 🔧 Environment Variables Reference

### Backend (Django)

```env
# Required
SECRET_KEY=<generate-random-key>
DEBUG=False
ALLOWED_HOSTS=your-backend-url.onrender.com,*.onrender.com
DATABASE_URL=<provided-by-platform>
DJANGO_SETTINGS_MODULE=pos_system.settings

# Optional but Recommended
REDIS_URL=<provided-by-platform>
CELERY_BROKER_URL=<provided-by-platform>
CELERY_RESULT_BACKEND=<provided-by-platform>
CORS_ALLOWED_ORIGINS=https://your-frontend-url.onrender.com

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway (Optional)
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret

# AI Services (Optional)
STABILITY_API_KEY=your-key
REPLICATE_API_KEY=your-key
HUGGINGFACE_API_KEY=your-key
OPENAI_API_KEY=your-key
```

### Frontend (React)

```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
```

---

## 📝 Post-Deployment Checklist

- [ ] Database migrations run successfully
- [ ] Superuser created
- [ ] Frontend can connect to backend API
- [ ] CORS configured correctly
- [ ] Static files served correctly
- [ ] Media files accessible (may need cloud storage for production)
- [ ] Environment variables set correctly
- [ ] SSL/HTTPS enabled (automatic on Render/Railway)

---

## 🗄️ Media Files Storage

**Important**: Free tier platforms have limited storage. For production, use cloud storage:

### Option 1: AWS S3 (Recommended)
1. Create S3 bucket
2. Install: `pip install django-storages boto3`
3. Update settings:
```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
```

### Option 2: Cloudinary (Free tier available)
1. Sign up at https://cloudinary.com
2. Install: `pip install django-cloudinary-storage`
3. Configure in settings

---

## 🐛 Troubleshooting

### Backend Issues

**Issue**: "Application failed to respond"
- Check logs in Render dashboard
- Verify `startCommand` is correct
- Ensure `gunicorn` is in `requirements.txt`

**Issue**: "Database connection failed"
- Verify `DATABASE_URL` is set correctly
- Check database is running
- Ensure database credentials are correct

**Issue**: "Static files not loading"
- Run `python manage.py collectstatic --noinput` in build command
- Verify `STATIC_ROOT` is set
- Check WhiteNoise is installed

### Frontend Issues

**Issue**: "Cannot connect to API"
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS settings in backend
- Ensure backend URL is accessible

**Issue**: "Build fails"
- Check Node.js version compatibility
- Verify all dependencies in `package.json`
- Check build logs for specific errors

---

## 🔄 Continuous Deployment

All platforms support auto-deploy from GitHub:

1. **Render**: Automatic on push to main branch
2. **Railway**: Automatic on push to main branch
3. **Fly.io**: Use `fly deploy` or GitHub Actions

---

## 💰 Cost Estimation

### Render (Free Tier)
- ✅ Backend: Free (spins down after inactivity)
- ✅ Frontend: Free
- ✅ PostgreSQL: Free (1GB)
- ✅ Redis: Free (25MB)
- **Total: $0/month** (with limitations)

### Railway
- $5 free credit/month
- PostgreSQL: ~$5/month (after free credit)
- **Total: ~$0-5/month**

### Fly.io
- 3 free VMs
- PostgreSQL: ~$2-5/month
- **Total: ~$0-5/month**

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Fly.io Documentation](https://fly.io/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

## 🆘 Need Help?

If you encounter issues:
1. Check platform logs
2. Verify environment variables
3. Test locally with production settings
4. Check platform status pages
5. Review platform documentation

---

**Happy Deploying! 🚀**

