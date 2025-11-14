# 🔧 Railway Deployment Fix

## Problem
Railway is trying to use a Dockerfile that references `pip` but Python isn't installed in the Docker context.

## ✅ Solution

I've created `nixpacks.toml` which tells Railway to use Python build instead of Docker.

## Steps to Fix

### 1. Commit and Push Changes

```bash
git add .
git commit -m "Add nixpacks.toml for Railway Python build"
git push
```

### 2. In Railway Dashboard

1. Go to your Railway project
2. Click on your service
3. Go to **Settings** tab
4. Under **Build**, make sure:
   - **Builder**: `Nixpacks` (not Docker)
   - Railway will automatically use `nixpacks.toml` if present

### 3. Clear Build Cache (If Needed)

If Railway still tries to use Docker:

1. In Railway Dashboard → Your Service
2. Go to **Settings** → **Deploy**
3. Click **"Clear Build Cache"**
4. Redeploy

### 4. Manual Override (If Still Issues)

If Railway still doesn't detect Python:

1. Go to **Settings** → **Variables**
2. Add environment variable:
   - Key: `NIXPACKS_PYTHON_VERSION`
   - Value: `3.12`

3. Or in **Settings** → **Build**:
   - Set **Build Command** manually:
     ```
     pip install --upgrade pip && pip install -r backend/requirements.txt && cd backend && python manage.py collectstatic --noinput
     ```
   - Set **Start Command**:
     ```
     cd backend && gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT
     ```

## What Changed

1. ✅ Created `nixpacks.toml` - Railway's preferred config file
2. ✅ Updated `railway.json` - Removed Docker references
3. ✅ Configured Python 3.12 build
4. ✅ Set correct build and start commands

## Verify

After deployment, check build logs:
- ✅ Should see: "Installing Python packages..."
- ✅ Should see: "Collecting static files..."
- ✅ Should NOT see: "Dockerfile" or "docker" errors
- ✅ Should see: "Starting gunicorn..."

## Alternative: Delete railway.json

If Railway keeps using Docker, you can delete `railway.json` and Railway will auto-detect from `nixpacks.toml`:

```bash
git rm railway.json
git commit -m "Remove railway.json, use nixpacks.toml only"
git push
```

