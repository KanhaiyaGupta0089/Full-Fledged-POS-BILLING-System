# 🎯 Quick Guide: Create Dummy Data on Railway

## Method 1: Using Railway CLI (Recommended)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login and Link

```bash
railway login
railway link
```

When prompted, select your Railway project.

### Step 3: Run Dummy Data Command

```bash
railway run --service backend python manage.py create_dummy_data
```

This will create:
- ✅ **Admin user**: `admin` / `admin123`
- ✅ **Owner user**: `owner` / `owner123`
- ✅ Categories, Brands, Products
- ✅ Customers, Invoices
- ✅ Sample data for testing

## Method 2: Using Railway Dashboard (Alternative)

If CLI doesn't work, you can create users manually via Django shell:

1. Go to Railway Dashboard → Backend Service
2. Click "Deployments" → Latest deployment
3. You can't run commands directly, but you can:
   - Use Railway CLI (Method 1)
   - Or create a one-time migration/script

## Method 3: Quick User Creation Script

Create a temporary management command or use Django shell:

```bash
railway run --service backend python manage.py shell
```

Then paste this:

```python
from accounts.models import User, Role

# Create roles
Role.objects.get_or_create(name='admin')
Role.objects.get_or_create(name='owner')

# Create admin user
admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@pos.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
admin.set_password('admin123')
admin.save()
print(f"✅ Admin user created: {admin.username}")

# Create owner user
owner, _ = User.objects.get_or_create(
    username='owner',
    defaults={
        'email': 'owner@pos.com',
        'first_name': 'Owner',
        'last_name': 'User',
        'role': 'owner',
    }
)
owner.set_password('owner123')
owner.save()
print(f"✅ Owner user created: {owner.username}")
```

## Login Credentials

After running the command, use these to login:

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Owner User:**
- Username: `owner`
- Password: `owner123`

## Test Login

1. Go to your frontend URL (Vercel)
2. Or test via API:
   ```
   POST https://web-production-12808.up.railway.app/api/auth/login/
   Body: {"username": "admin", "password": "admin123"}
   ```

## What Gets Created

The `create_dummy_data` command creates:
- 2 users (admin, owner)
- 5 categories
- 5 brands
- 20 products
- 10 customers
- 30 invoices
- Credit accounts
- Stock entries
- Daybook entries

Perfect for testing your application! 🚀

