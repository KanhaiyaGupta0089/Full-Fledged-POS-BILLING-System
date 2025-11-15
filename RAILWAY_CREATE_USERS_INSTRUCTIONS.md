# 🎯 Create Dummy Users on Railway - Step by Step

## The Issue

`railway run` command runs locally, not on Railway servers. Here are the solutions:

## ✅ Solution 1: Add to Build Process (Temporary - Easiest)

I've updated `nixpacks.toml` to automatically create dummy data during build. 

**Just commit and push:**

```bash
git add nixpacks.toml
git commit -m "Add dummy data creation to build process"
git push
```

Railway will automatically:
1. Run migrations
2. **Create dummy users and data**
3. Collect static files
4. Deploy

**After first successful deployment, remove the `create_dummy_data` line** from `nixpacks.toml` to avoid recreating data on every build.

## ✅ Solution 2: Use Railway Web Console (If Available)

1. Go to Railway Dashboard → Your Backend Service
2. Look for **"Console"** or **"Shell"** tab
3. Run:
   ```bash
   cd backend
   python3 manage.py create_dummy_data
   ```

## ✅ Solution 3: Railway CLI with Correct Syntax

Try this command (make sure you're logged in and linked):

```bash
railway run --service web sh -c "cd backend && python3 manage.py create_dummy_data"
```

Or if Railway runs from `/app` directory:

```bash
railway run --service web python3 /app/backend/manage.py create_dummy_data
```

## ✅ Solution 4: Create Users via Django Shell

Run this command:

```bash
railway run --service web python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()
from accounts.models import User, Role
Role.objects.get_or_create(name='admin')
Role.objects.get_or_create(name='owner')
admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@pos.com', 'first_name': 'Admin', 'last_name': 'User', 'role': 'admin', 'is_staff': True, 'is_superuser': True})
admin.set_password('admin123')
admin.save()
owner, _ = User.objects.get_or_create(username='owner', defaults={'email': 'owner@pos.com', 'first_name': 'Owner', 'last_name': 'User', 'role': 'owner'})
owner.set_password('owner123')
owner.save()
print('✅ Users created: admin/admin123 and owner/owner123')
"
```

## Recommended: Use Solution 1

**Just push the updated `nixpacks.toml`** - it's the easiest way. The dummy data will be created automatically on the next deployment.

## Login Credentials

After dummy data is created:

- **Admin**: `admin` / `admin123`
- **Owner**: `owner` / `owner123`

## After First Deployment

Remember to remove the `create_dummy_data` line from `nixpacks.toml` after the first successful deployment to avoid recreating data on every build.

