# Vercel Environment Variables Setup

## Required Environment Variables

To connect your Vercel frontend to your Railway backend, you need to set the following environment variable in Vercel:

### 1. API Base URL

**Variable Name:** `VITE_API_BASE_URL`

**Value:** Your Railway backend URL (e.g., `https://web-production-12808.up.railway.app/api`)

**How to Set:**
1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Click **Add New**
4. Enter:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://web-production-12808.up.railway.app/api` (replace with your actual Railway URL)
   - **Environment:** Select all (Production, Preview, Development)
5. Click **Save**
6. **Important:** Redeploy your application for the changes to take effect

### 2. Verify Your Railway Backend URL

1. Go to your Railway project dashboard
2. Click on your backend service
3. Go to **Settings** → **Domains**
4. Copy the production domain (e.g., `web-production-12808.up.railway.app`)
5. Use this as your API base URL: `https://YOUR-RAILWAY-DOMAIN.up.railway.app/api`

## After Setting Environment Variables

1. **Redeploy on Vercel:**
   - Go to **Deployments** tab
   - Click the three dots on the latest deployment
   - Select **Redeploy**

2. **Clear Browser Cache:**
   - Clear your browser's localStorage
   - Or use incognito/private browsing mode

3. **Test Login:**
   - Use credentials: `admin` / `admin123` or `owner` / `owner123`

## Troubleshooting

### If you still see "No token found" errors:
1. Check browser console for the actual structure of `auth-storage`
2. Verify the token is being saved after login
3. Check that `VITE_API_BASE_URL` is correctly set in Vercel

### If you see CORS errors:
1. The backend CORS settings have been updated to allow all origins in production
2. If you want to restrict CORS, set `CORS_ALLOW_ALL_ORIGINS=False` in Railway environment variables
3. Then add your Vercel domain to `CORS_ALLOWED_ORIGINS` in Railway

### If API calls fail:
1. Verify the Railway backend is running (check Railway logs)
2. Verify the `VITE_API_BASE_URL` includes `/api` at the end
3. Check browser network tab to see the actual request URL

