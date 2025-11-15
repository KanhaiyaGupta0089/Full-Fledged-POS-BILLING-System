# 🚀 Frontend Deployment Guide

## Current Situation

- ✅ **Backend**: Deployed on Railway at `web-production-12808.up.railway.app`
- ❌ **Frontend**: Not deployed yet (React app)

## Option 1: Deploy Frontend to Railway (Recommended)

### Step 1: Create a New Service in Railway

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"GitHub Repo"** (or **"Empty Service"**)
3. Select the same repository
4. Railway will auto-detect it's a Node.js app

### Step 2: Configure the Service

1. **Root Directory**: Set to `frontend`
2. **Build Command**: `npm install && npm run build`
3. **Start Command**: `npm run preview` (or use a static file server)
4. **Output Directory**: `dist` (Vite's default build output)

### Step 3: Add Environment Variable

Add this environment variable in Railway:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://web-production-12808.up.railway.app/api`

### Step 4: Deploy

Railway will automatically:
- Install dependencies
- Build the React app
- Deploy it

## Option 2: Deploy to Vercel (Easier for React Apps)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Deploy

```bash
cd frontend
vercel
```

### Step 3: Configure Environment Variable

In Vercel Dashboard → Your Project → Settings → Environment Variables:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://web-production-12808.up.railway.app/api`

### Step 4: Redeploy

Vercel will automatically redeploy with the new environment variable.

## Option 3: Deploy to Netlify

### Step 1: Install Netlify CLI

```bash
npm install -g netlify-cli
```

### Step 2: Deploy

```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

### Step 3: Configure Environment Variable

In Netlify Dashboard → Site Settings → Environment Variables:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://web-production-12808.up.railway.app/api`

## Option 4: Serve Frontend from Backend (Not Recommended)

You can serve the built frontend from Django, but it's not ideal for React apps.

## Quick Setup for Railway

### Create `railway.json` in `frontend/` directory:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm install && npm run build"
  },
  "deploy": {
    "startCommand": "npx serve -s dist -l $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Or use `package.json` scripts:

Add to `frontend/package.json`:
```json
{
  "scripts": {
    "start": "npx serve -s dist -l $PORT"
  }
}
```

## Environment Variables Needed

**In Railway/Vercel/Netlify Dashboard:**

```
VITE_API_BASE_URL=https://web-production-12808.up.railway.app/api
```

## Testing Locally

To test the frontend locally with the Railway backend:

1. Create `frontend/.env.local`:
   ```
   VITE_API_BASE_URL=https://web-production-12808.up.railway.app/api
   ```

2. Run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open `http://localhost:5173` (or the port Vite shows)

## CORS Configuration

Make sure your backend allows requests from your frontend domain. The backend already has `CORS_ALLOW_ALL_ORIGINS = True` in development, but for production you might want to restrict it.

## Recommended: Railway for Both

Since your backend is on Railway, deploying the frontend to Railway too keeps everything in one place:

1. **Backend Service**: `web-production-12808.up.railway.app`
2. **Frontend Service**: Will get its own Railway URL (e.g., `frontend-production-xxxxx.up.railway.app`)

Both services in the same Railway project can share environment variables and are easier to manage.

## Next Steps

1. Choose a deployment platform (Railway recommended)
2. Deploy the frontend
3. Set `VITE_API_BASE_URL` environment variable
4. Test the frontend URL
5. Update CORS settings if needed

