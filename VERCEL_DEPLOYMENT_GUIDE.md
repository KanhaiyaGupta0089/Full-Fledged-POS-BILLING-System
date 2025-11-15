# 🚀 Deploy Frontend to Vercel - Step by Step Guide

## Prerequisites

- GitHub account (your code should be on GitHub)
- Vercel account (free tier available)
- Backend deployed on Railway: `https://web-production-12808.up.railway.app`

## Step 1: Create Vercel Account

1. Go to [https://vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Sign up with your GitHub account (recommended)

## Step 2: Import Your Project

1. After logging in, click **"Add New..."** → **"Project"**
2. Click **"Import Git Repository"**
3. Select your repository (`Billing-and-inventory/bill2` or your repo name)
4. Click **"Import"**

## Step 3: Configure Project Settings

Vercel will auto-detect it's a Vite project, but verify these settings:

### Framework Preset
- **Framework Preset**: `Vite` (should be auto-detected)

### Root Directory
- **Root Directory**: `frontend`
  - Click **"Edit"** next to Root Directory
  - Enter: `frontend`
  - Click **"Continue"**

### Build Settings
- **Build Command**: `npm run build` (auto-filled)
- **Output Directory**: `dist` (auto-filled)
- **Install Command**: `npm install` (auto-filled)

## Step 4: Add Environment Variable

**IMPORTANT**: Before deploying, add the environment variable:

1. In the project configuration page, scroll to **"Environment Variables"**
2. Click **"Add"** or **"Add New"**
3. Add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://web-production-12808.up.railway.app/api`
   - **Environment**: Select all (Production, Preview, Development)
4. Click **"Save"**

## Step 5: Deploy

1. Click **"Deploy"** button
2. Vercel will:
   - Install dependencies
   - Build your React app
   - Deploy it
3. Wait for deployment to complete (usually 1-2 minutes)

## Step 6: Get Your Frontend URL

After deployment:
1. You'll see a success message
2. Your frontend will be available at: `https://your-project-name.vercel.app`
3. Click the URL to open your app

## Step 7: Update CORS (If Needed)

If you get CORS errors, update your backend settings:

1. Go to Railway Dashboard → Backend Service → Variables
2. Check if `CORS_ALLOW_ALL_ORIGINS` is set to `True` (should work)
3. Or add your Vercel domain to `CORS_ALLOWED_ORIGINS`:
   ```
   https://your-project-name.vercel.app
   ```

## Troubleshooting

### Issue: Build Fails

**Solution**: Check build logs in Vercel dashboard:
1. Go to your project → **"Deployments"** tab
2. Click on the failed deployment
3. Check the build logs for errors
4. Common issues:
   - Missing dependencies → Add to `package.json`
   - Build errors → Fix in code
   - Environment variables → Make sure `VITE_API_BASE_URL` is set

### Issue: 404 on Routes

**Solution**: The `vercel.json` file I created includes rewrites to handle React Router. If you still get 404s:
1. Make sure `vercel.json` is in the `frontend/` directory
2. Redeploy

### Issue: API Calls Fail

**Solution**: 
1. Check that `VITE_API_BASE_URL` environment variable is set correctly
2. Check browser console for errors
3. Verify backend is accessible: `https://web-production-12808.up.railway.app/api/docs/`

### Issue: Environment Variable Not Working

**Solution**:
1. Make sure variable name starts with `VITE_` (required for Vite)
2. Redeploy after adding environment variables
3. Check in Vercel Dashboard → Settings → Environment Variables

## Updating Your Deployment

### Automatic Deployments

Vercel automatically deploys when you push to:
- **Production**: `main` or `master` branch
- **Preview**: Any other branch or pull request

### Manual Redeploy

1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click **"..."** on any deployment
4. Click **"Redeploy"**

### Update Environment Variables

1. Go to Vercel Dashboard → Your Project → Settings
2. Click **"Environment Variables"**
3. Edit or add variables
4. Redeploy (or wait for next auto-deploy)

## Custom Domain (Optional)

1. Go to Vercel Dashboard → Your Project → Settings
2. Click **"Domains"**
3. Add your custom domain
4. Follow DNS configuration instructions

## Project Structure

Your project structure should be:
```
bill2/
├── backend/          # Django backend (deployed on Railway)
├── frontend/         # React frontend (deployed on Vercel)
│   ├── vercel.json   # Vercel configuration
│   ├── package.json
│   └── ...
└── ...
```

## Quick Checklist

- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Root Directory set to `frontend`
- [ ] Environment variable `VITE_API_BASE_URL` added
- [ ] Deployed successfully
- [ ] Frontend URL working
- [ ] API calls working (check browser console)

## Next Steps After Deployment

1. **Test the frontend**: Visit your Vercel URL
2. **Test login**: Try logging in with your backend credentials
3. **Check API calls**: Open browser DevTools → Network tab
4. **Update backend CORS** (if needed): Add Vercel domain to allowed origins

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser console for errors
3. Verify environment variables are set
4. Test backend API directly: `https://web-production-12808.up.railway.app/api/docs/`

## Summary

✅ **Backend**: `https://web-production-12808.up.railway.app` (Railway)  
✅ **Frontend**: `https://your-project-name.vercel.app` (Vercel)  
✅ **Environment Variable**: `VITE_API_BASE_URL=https://web-production-12808.up.railway.app/api`

Your full-stack application is now deployed! 🎉

