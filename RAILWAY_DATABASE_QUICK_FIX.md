# 🚨 Quick Fix: Add PostgreSQL Database to Railway

## The Problem

Your backend is trying to connect to PostgreSQL at `localhost:5432`, but there's no database server running. You need to add a PostgreSQL database service to Railway.

## ✅ Solution (5 Minutes)

### Step 1: Add PostgreSQL Service

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your project** (the one with your backend)
3. **Click "+ New"** button (top right)
4. **Select "Database"** → **"Add PostgreSQL"**
5. Railway will automatically:
   - Create a PostgreSQL database
   - Set `DATABASE_URL` environment variable for your backend
   - Link the database to your backend service

### Step 2: Verify DATABASE_URL is Set

1. Go to your **Backend Service** (not the database service)
2. Click **"Variables"** tab
3. Look for `DATABASE_URL` - Railway should have automatically added it
4. It should look like:
   ```
   postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
   ```

### Step 3: Run Migrations

After the database is added, you need to run migrations to create tables:

**Option A: Using Railway CLI (Recommended)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project (select your project when prompted)
railway link

# Run migrations
railway run --service backend python manage.py migrate
```

**Option B: Add Migration to Build (Temporary)**

Update `nixpacks.toml` to run migrations during build:

```toml
[phases.build]
cmds = [
  "cd backend && python3 manage.py migrate --noinput || true",
  "cd backend && python3 manage.py collectstatic --noinput || true"
]
```

Then commit and push:
```bash
git add nixpacks.toml
git commit -m "Add migrations to build process"
git push
```

**After first deployment, remove the migrate command** from `nixpacks.toml` to avoid running migrations on every build.

### Step 4: Create Superuser (Optional)

To access Django admin at `/admin/`:

```bash
railway run --service backend python manage.py createsuperuser
```

Follow the prompts to create an admin user.

## What Happens After Setup

1. ✅ PostgreSQL database is running
2. ✅ `DATABASE_URL` is automatically set
3. ✅ Backend connects to database
4. ✅ Migrations create all tables
5. ✅ Your API will work!

## Verify It's Working

1. Go to Railway Dashboard → Backend Service → Deployments
2. Check the latest deployment logs
3. You should see successful database connection
4. Try accessing: `https://web-production-12808.up.railway.app/api/docs/`
5. Try logging in via API

## Troubleshooting

### Still Getting "Connection Refused"

1. **Check Variables**: Go to Backend Service → Variables → Make sure `DATABASE_URL` exists
2. **Check Database Service**: Make sure PostgreSQL service is running (green status)
3. **Redeploy**: After adding database, redeploy your backend service

### DATABASE_URL Not Set Automatically

1. Go to PostgreSQL service → **"Variables"** tab
2. Copy the `DATABASE_URL` value
3. Go to Backend service → **"Variables"** tab
4. Click **"+ New Variable"**
5. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: (paste the value from PostgreSQL service)
6. Save and redeploy

## Quick Checklist

- [ ] PostgreSQL service added to Railway
- [ ] `DATABASE_URL` environment variable exists in Backend service
- [ ] Migrations run successfully
- [ ] Backend can connect to database (check logs)
- [ ] API endpoints work (test `/api/docs/`)

## Summary

**The issue**: No PostgreSQL database in Railway  
**The fix**: Add PostgreSQL service → Railway auto-sets `DATABASE_URL` → Run migrations → Done!

After adding PostgreSQL and running migrations, your backend will work! 🚀

