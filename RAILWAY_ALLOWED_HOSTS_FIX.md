# 🔧 Fix ALLOWED_HOSTS Error on Railway

## The Problem

You're seeing:
```
Invalid HTTP_HOST header: 'web-production-12808.up.railway.app'. 
You may need to add 'web-production-12808.up.railway.app' to ALLOWED_HOSTS.
```

## The Issue

Your `ALLOWED_HOSTS` environment variable in Railway is set incorrectly. Looking at your error, it shows:
```
ALLOWED_HOSTS: ['https://web-production-12808.up.railway.app/']
```

**This is wrong!** `ALLOWED_HOSTS` should contain **only the domain name**, not:
- ❌ `https://` prefix
- ❌ Trailing `/` slash
- ❌ Full URL

## ✅ The Fix

### Option 1: Update in Railway Dashboard (Recommended)

1. Go to Railway Dashboard → Your Service
2. Click **"Variables"** tab
3. Find `ALLOWED_HOSTS` variable
4. **Delete the current value** and set it to:
   ```
   web-production-12808.up.railway.app,*.railway.app
   ```
   Or just:
   ```
   *.railway.app
   ```
   (The `*.railway.app` wildcard will match all Railway subdomains)

5. Click **"Save"**
6. Railway will automatically redeploy

### Option 2: Use Railway CLI

```bash
railway variables set ALLOWED_HOSTS="web-production-12808.up.railway.app,*.railway.app"
```

## Correct Format

✅ **Correct:**
- `web-production-12808.up.railway.app`
- `*.railway.app`
- `web-production-12808.up.railway.app,*.railway.app`

❌ **Wrong:**
- `https://web-production-12808.up.railway.app/`
- `https://web-production-12808.up.railway.app`
- `web-production-12808.up.railway.app/`

## Why This Happens

Django's `ALLOWED_HOSTS` is a security feature that validates the `Host` header. It expects:
- Just the domain name (e.g., `example.com`)
- No protocol (`http://` or `https://`)
- No path (`/` or `/path`)
- No port (unless explicitly needed)

## Additional Settings

I've also updated `settings.py` to include `*.railway.app` as a default fallback, so Railway domains will work even if the environment variable isn't set correctly.

## After Fixing

1. Save the environment variable in Railway
2. Wait for automatic redeploy (or manually redeploy)
3. Your app should now work! 🚀

## Quick Checklist

- [ ] Go to Railway Dashboard → Variables
- [ ] Find `ALLOWED_HOSTS`
- [ ] Change to: `web-production-12808.up.railway.app,*.railway.app`
- [ ] Save
- [ ] Wait for redeploy
- [ ] Test your app

