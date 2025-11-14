# Gmail App Password Setup Guide

## Error: "Username and Password not accepted"

This error means Gmail is rejecting your credentials. Follow these steps to fix it:

## Step 1: Enable 2-Step Verification

1. Go to https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "Signing in to Google", find **2-Step Verification**
4. If it's **OFF**, click it and follow the steps to enable it
5. You'll need to verify your phone number

## Step 2: Generate App Password

1. Go back to **Security** page
2. Under "Signing in to Google", find **2-Step Verification** (should be ON now)
3. Click on **App passwords** (you may need to sign in again)
4. If you don't see "App passwords":
   - Make sure 2-Step Verification is enabled
   - You might need to use a Google Workspace account or personal account
5. Select **Mail** as the app
6. Select **Other (Custom name)** as the device
7. Enter a name like "POS System" or "Django App"
8. Click **Generate**
9. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
10. **Important**: Copy it immediately - you won't be able to see it again!

## Step 3: Update .env File

1. Open `backend/.env` file
2. Update the `EMAIL_HOST_PASSWORD` line:
   ```
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   ```
   **Important**: 
   - Remove all spaces from the password
   - The password should be exactly 16 characters
   - No quotes around the password
   - Example: If Gmail shows `abcd efgh ijkl mnop`, use `abcdefghijklmnop`

3. Save the file

## Step 4: Restart Django Server

After updating the `.env` file, restart your Django server:

```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

## Step 5: Test Email Configuration

Run this command to test:

```bash
cd backend
source venv/bin/activate
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

try:
    send_mail(
        subject='Test Email',
        message='This is a test email from POS System',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['gkanha1500@gmail.com'],
        fail_silently=False,
    )
    print('✅ Email sent successfully!')
except Exception as e:
    print(f'❌ Email failed: {str(e)}')
"
```

## Common Issues

### Issue 1: "App passwords" option not showing
- **Solution**: Make sure 2-Step Verification is enabled first

### Issue 2: Password still not working
- **Solution**: Generate a new app password and update `.env` file
- Make sure there are no spaces in the password
- Make sure there are no quotes around the password

### Issue 3: "Less secure app access" error
- **Solution**: Gmail no longer supports "Less secure app access"
- You **must** use App Passwords with 2-Step Verification enabled

### Issue 4: Workspace account issues
- **Solution**: If using Google Workspace, your admin may need to enable app passwords
- Contact your Google Workspace administrator

## Alternative: Use Console Backend for Development

If you just want to test without email, you can use the console backend:

In `backend/.env`:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

This will print emails to the console instead of sending them.







