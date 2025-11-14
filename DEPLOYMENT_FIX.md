# Deployment Fix - Docker Build Error

## Problem
Render is trying to use Docker but `pip` command is not found in the Docker build context.

## Solution Options

### Option 1: Use Python Build (Recommended - Simpler)

If Render is auto-detecting Docker, you can force it to use Python build:

1. In Render Dashboard → Your Service → Settings
2. Change **Environment** from "Docker" to **"Python 3"**
3. Set these manually:
   - **Build Command**: `pip install --upgrade pip && pip install -r backend/requirements.txt && cd backend && python manage.py collectstatic --noinput`
   - **Start Command**: `cd backend && gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT`
   - **Python Version**: `3.12.0`

### Option 2: Use Docker Build (Current Setup)

The Dockerfile has been created and should work. If you want to use Docker:

1. Make sure the Dockerfile is in the root directory (it is)
2. In Render Dashboard → Your Service → Settings
3. Set **Environment** to **"Docker"**
4. Set **Dockerfile Path**: `./Dockerfile`
5. Set **Docker Context**: `.` (root directory)

### Option 3: Remove Dockerfile (Force Python Build)

If you want to force Python build and avoid Docker:

1. Temporarily rename or delete `Dockerfile`:
   ```bash
   mv Dockerfile Dockerfile.backup
   ```

2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Remove Dockerfile to use Python build"
   git push
   ```

3. Render will now use Python build automatically

4. After deployment works, you can restore Dockerfile if needed

## Quick Fix Steps

1. **Go to Render Dashboard** → Your backend service
2. **Settings** tab
3. **Change Environment** to **"Python 3"** (not Docker)
4. **Set Build Command**:
   ```
   pip install --upgrade pip && pip install -r backend/requirements.txt && cd backend && python manage.py collectstatic --noinput
   ```
5. **Set Start Command**:
   ```
   cd backend && gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT
   ```
6. **Save Changes**
7. **Manual Deploy** → Deploy latest commit

## Verify

After deployment, check:
- Build logs show Python packages installing
- No Docker-related errors
- Service starts successfully
- API responds at your backend URL

