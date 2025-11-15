# Fix Email Sending Issues

## Common Problems

### 1. "Network is unreachable" Error
This error occurs when:
- Email credentials are not set in Railway environment variables
- Railway network restrictions block SMTP connections
- Firewall blocking SMTP ports (587, 465)

### 2. "Username and Password not accepted" Error
This means Gmail authentication failed:
- App Password not generated correctly
- App Password not set in environment variables
- 2-Step Verification not enabled

## Solutions

### Solution 1: Set Up Gmail App Password (Recommended for Development)

1. **Enable 2-Step Verification**
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter name: "POS System"
   - Copy the 16-character password (remove spaces)

3. **Add to Railway Environment Variables**
   - Go to Railway Dashboard → Your Service → Variables
   - Add these variables:
     ```
     EMAIL_HOST_USER=your-email@gmail.com
     EMAIL_HOST_PASSWORD=abcdefghijklmnop  (16 chars, no spaces, no quotes)
     EMAIL_HOST=smtp.gmail.com
     EMAIL_PORT=587
     EMAIL_USE_TLS=True
     DEFAULT_FROM_EMAIL=your-email@gmail.com
     ```

4. **Redeploy** your Railway service

### Solution 2: Use Email Service Provider (Recommended for Production)

Railway may block SMTP connections. Use a dedicated email service:

#### Option A: SendGrid (Free tier: 100 emails/day)

1. **Sign up**: https://sendgrid.com
2. **Create API Key**: Settings → API Keys → Create API Key
3. **Add to Railway**:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key
   DEFAULT_FROM_EMAIL=your-verified-email@domain.com
   ```

#### Option B: Mailgun (Free tier: 5,000 emails/month)

1. **Sign up**: https://www.mailgun.com
2. **Get SMTP credentials**: Sending → Domain Settings → SMTP credentials
3. **Add to Railway**:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.mailgun.org
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-mailgun-username
   EMAIL_HOST_PASSWORD=your-mailgun-password
   DEFAULT_FROM_EMAIL=your-verified-email@domain.com
   ```

#### Option C: AWS SES (Pay as you go)

1. **Set up AWS SES**: https://aws.amazon.com/ses/
2. **Verify email/domain**
3. **Add to Railway**:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=email-smtp.us-east-1.amazonaws.com  (use your region)
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-aws-access-key
   EMAIL_HOST_PASSWORD=your-aws-secret-key
   DEFAULT_FROM_EMAIL=your-verified-email@domain.com
   ```

### Solution 3: Use Console Backend (Development Only)

If you just want to test without sending real emails:

1. **Add to Railway**:
   ```
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

2. Emails will be printed to Railway logs instead of being sent

## Quick Fix Checklist

- [ ] Check Railway environment variables are set
- [ ] Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
- [ ] For Gmail: Ensure App Password is 16 characters, no spaces
- [ ] Check Railway logs for specific error messages
- [ ] Consider using SendGrid/Mailgun if Railway blocks SMTP
- [ ] Redeploy after changing environment variables

## Testing Email Configuration

After setting up, test by:

1. **Create an invoice** with a customer email
2. **Check Railway logs** for email sending attempts
3. **Check customer email** for the invoice PDF

## Troubleshooting

### Error: "Network is unreachable"
- **Cause**: Railway blocking SMTP connections
- **Fix**: Use SendGrid, Mailgun, or AWS SES instead

### Error: "535 Authentication failed"
- **Cause**: Wrong App Password or credentials
- **Fix**: Regenerate App Password and update EMAIL_HOST_PASSWORD

### Error: "Connection timed out"
- **Cause**: SMTP server unreachable or firewall blocking
- **Fix**: Check EMAIL_HOST and EMAIL_PORT, try different email service

### Emails not sending but no errors
- **Cause**: Console backend active or credentials missing
- **Fix**: Check EMAIL_BACKEND setting and ensure credentials are set

## Current Configuration

The application is configured to:
- Use SMTP backend by default
- Fall back to console backend only in DEBUG mode without credentials
- Log detailed error messages for troubleshooting
- Create notification records for sent/failed emails

Check `backend/billing/emailer.py` for email sending logic and error handling.

