# 🚀 Quick Guide: Create Dummy Users on Railway

## Option 1: Use Railway CLI (Interactive - You Need to Do This)

Since Railway login requires a browser, follow these steps:

### Step 1: Login to Railway

Open your terminal and run:
```bash
railway login
```

This will open your browser for authentication.

### Step 2: Link Your Project

```bash
railway link
```

Select your Railway project when prompted.

### Step 3: Run Create Dummy Data Command

```bash
railway run --service backend python manage.py create_dummy_data
```

This creates:
- ✅ Admin: `admin` / `admin123`
- ✅ Owner: `owner` / `owner123`
- ✅ Plus categories, products, customers, invoices, etc.

### Step 4: Or Just Create Users

If you only want users (faster):
```bash
railway run --service backend python manage.py shell
```

Then paste this code:
```python
from accounts.models import User, Role

Role.objects.get_or_create(name='admin')
Role.objects.get_or_create(name='owner')

admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@pos.com', 'first_name': 'Admin', 'last_name': 'User', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
)
admin.set_password('admin123')
admin.save()
print("✅ Admin created: admin / admin123")

owner, _ = User.objects.get_or_create(
    username='owner',
    defaults={'email': 'owner@pos.com', 'first_name': 'Owner', 'last_name': 'User', 'role': 'owner'}
)
owner.set_password('owner123')
owner.save()
print("✅ Owner created: owner / owner123")
```

## Option 2: Use Railway Web Console (If Available)

Some Railway plans allow running commands via web console:
1. Go to Railway Dashboard → Backend Service
2. Look for "Console" or "Shell" option
3. Run: `python manage.py create_dummy_data`

## Option 3: Add to Build Script (Temporary)

You can temporarily add user creation to your build process, but this is not recommended for production.

## Login Credentials

After creating users, use these to login:

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Owner User:**
- Username: `owner`
- Password: `owner123`

## Test Login

1. **Via Frontend**: Go to your Vercel frontend URL and login
2. **Via API**: 
   ```bash
   curl -X POST https://web-production-12808.up.railway.app/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

## Quick Commands Summary

```bash
# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login (opens browser)
railway login

# Link project
railway link

# Create all dummy data
railway run --service backend python manage.py create_dummy_data

# Or just create users
railway run --service backend python manage.py shell
# Then paste the Python code above
```

## What Gets Created

**With `create_dummy_data`:**
- 2 users (admin, owner)
- 5 categories
- 5 brands  
- 20 products
- 10 customers
- 30 invoices
- Credit accounts
- Stock entries

**With manual user creation:**
- Just the users (admin, owner)

Choose based on what you need! 🚀

