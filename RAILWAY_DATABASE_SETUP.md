# 🗄️ Railway Database Setup Guide

## The Problem

Your backend is trying to connect to PostgreSQL at `localhost:5432`, but there's no database server. You need to add a PostgreSQL database service to Railway.

## Error You're Seeing

```
connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

This means `DATABASE_URL` is either:
- Not set in Railway
- Using the default localhost value
- PostgreSQL service not added

## ✅ Solution: Add PostgreSQL to Railway

### Step 1: Add PostgreSQL Service

1. Go to your Railway project dashboard
2. Click **"+ New"** button
3. Select **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL database
   - Set the `DATABASE_URL` environment variable
   - Link it to your backend service

### Step 2: Verify DATABASE_URL is Set

1. Go to your **Backend Service** (not the database)
2. Click **"Variables"** tab
3. Look for `DATABASE_URL` - it should be automatically set by Railway
4. It should look like:
   ```
   postgresql://postgres:password@hostname:port/railway
   ```

### Step 3: Run Migrations

After the database is added, you need to run migrations:

**Option A: Via Railway CLI (Recommended)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run --service backend python manage.py migrate
```

**Option B: Via Railway Dashboard**

1. Go to Railway Dashboard → Backend Service
2. Click **"Deployments"** tab
3. Click **"..."** on latest deployment
4. Click **"View Logs"**
5. You can't run commands directly, but you can add a one-time migration command

**Option C: Add Migration to Build (Temporary)**

Add this to your `nixpacks.toml` temporarily:

```toml
[phases.build]
cmds = [
  "cd backend && python3 manage.py collectstatic --noinput || true",
  "cd backend && python3 manage.py migrate --noinput || true"
]
```

Then remove the migrate command after first deployment.

### Step 4: Create Superuser (Optional)

To access Django admin, create a superuser:

```bash
railway run --service backend python manage.py createsuperuser
```

Or add it to a one-time script.

## Quick Checklist

- [ ] PostgreSQL service added to Railway
- [ ] `DATABASE_URL` environment variable is set (check in Variables tab)
- [ ] Backend service is linked to PostgreSQL service
- [ ] Migrations run successfully
- [ ] Superuser created (optional)

## Verify Database Connection

After setup, check Railway logs:
1. Go to Backend Service → Deployments → Latest → Logs
2. Look for database connection errors
3. If you see "connection refused", the `DATABASE_URL` is not set correctly

## Troubleshooting

### Issue: DATABASE_URL Not Set

**Solution**: 
1. Make sure PostgreSQL service is added
2. Make sure backend service is in the same Railway project
3. Railway should auto-link them, but check Variables tab

### Issue: Still Connecting to Localhost

**Solution**: 
1. Check `DATABASE_URL` in Railway Variables
2. Make sure it's not set to localhost
3. Delete and recreate if needed
4. Redeploy backend service

### Issue: Migration Errors

**Solution**:
1. Check database logs in Railway
2. Make sure database is running
3. Try running migrations manually via CLI

## Database URL Format

Railway's `DATABASE_URL` should look like:
```
postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
```

NOT:
```
postgresql://localhost:5432/dbname
```

## Next Steps After Database Setup

1. ✅ Database added
2. ✅ Migrations run
3. ✅ Create superuser (for admin access)
4. ✅ Test API endpoints
5. ✅ Deploy frontend to Vercel

## Summary

The issue is that you don't have a PostgreSQL database service in Railway. Add one, and Railway will automatically set `DATABASE_URL` for your backend service.

