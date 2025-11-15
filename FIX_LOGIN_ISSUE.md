# 🔐 Fix: Cannot Login - Database Tables Missing

## The Problem

Error: `relation "users" does not exist`

This means database migrations haven't run yet. The `users` table (and other tables) don't exist in the database.

## ✅ Solution Applied

I've updated `nixpacks.toml` to run migrations **directly in the start command** instead of using a separate script. This ensures migrations run every time the service starts.

## Next Steps

### 1. Commit and Push the Fix

```bash
git add nixpacks.toml
git commit -m "Fix: Run migrations at startup to create database tables"
git push
```

### 2. Wait for Railway to Deploy

Railway will automatically:
1. Build your application
2. Start the service
3. **Run migrations** (creates all tables including `users`)
4. **Create dummy data** (creates `admin` and `owner` users)
5. Start Gunicorn server

### 3. Verify Migrations Ran

After deployment, check Railway logs:

1. Go to **Railway Dashboard** → **Backend Service** → **Deployments** → **Latest**
2. Click **"View Logs"**
3. Look for:
   ```
   Running migrations:
     Applying accounts.0001_initial... OK
     Applying products.0001_initial... OK
     ...
   Creating dummy data...
   Users created successfully
   ```

### 4. Test Login

After migrations complete, try logging in with:

- **Username**: `admin`
- **Password**: `admin123`

OR

- **Username**: `owner`
- **Password**: `owner123`

## What Changed

**Before:**
- Migrations were in a separate script that might not execute
- Tables weren't being created

**After:**
- Migrations run directly in start command
- Tables are created automatically on every startup
- Dummy data is created automatically

## Expected Result

After pushing, you should be able to:
1. ✅ Login with `admin` / `admin123`
2. ✅ Access all API endpoints
3. ✅ See data in the database

## Troubleshooting

### If migrations still don't run:

1. **Check Railway logs** for errors during startup
2. **Verify DATABASE_URL** is set in Railway variables
3. **Check PostgreSQL service** is running (green status)

### If login still fails:

1. **Check if migrations actually ran** (look for "Applying..." in logs)
2. **Verify dummy data was created** (look for "Users created" in logs)
3. **Try creating a user manually**:

```bash
railway run --service web python3 manage.py createsuperuser
```

## Summary

**The issue**: Database tables don't exist because migrations didn't run  
**The fix**: Run migrations directly in start command  
**Result**: Tables created automatically → Login works! 🎉

