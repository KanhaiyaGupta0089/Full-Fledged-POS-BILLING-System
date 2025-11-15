# Razorpay Payment Gateway Integration Setup

## Backend Setup

1. **Install Razorpay SDK:**
   ```bash
   cd backend
   pip install razorpay==1.4.1
   ```

2. **Add Razorpay Credentials to `.env` file:**
   ```env
   RAZORPAY_KEY_ID=your_razorpay_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_key_secret
   RAZORPAY_WEBHOOK_SECRET=your_webhook_secret  # Optional, for webhook verification
   ```

3. **Get Razorpay Credentials:**
   - Sign up at https://razorpay.com
   - Go to Dashboard → Settings → API Keys
   - Copy your Key ID and Key Secret
   - For production, use Live keys
   - For testing, use Test keys

## Frontend Setup

1. **Add Razorpay Key ID to `.env` file (in frontend directory):**
   ```env
   VITE_RAZORPAY_KEY_ID=your_razorpay_key_id
   ```

2. **The Razorpay checkout script is already added to `index.html`**

## How It Works

1. **Create Invoice:** When user selects "Online Payment (Razorpay)" and creates invoice
2. **Create Order:** Backend creates a Razorpay order with invoice details
3. **Checkout:** Frontend opens Razorpay checkout modal
4. **Payment:** Customer completes payment via UPI/Card/Net Banking/Wallets
5. **Verification:** Backend verifies payment signature and updates invoice
6. **Webhook (Optional):** Razorpay sends webhook to `/api/payments/razorpay/webhook/` for additional verification

## API Endpoints

- `POST /api/payments/transactions/create_order/` - Create Razorpay order
- `POST /api/payments/transactions/verify_payment/` - Verify payment and update invoice
- `POST /api/payments/razorpay/webhook/` - Razorpay webhook handler

## Testing

1. Use Razorpay Test Mode credentials
2. Test cards: https://razorpay.com/docs/payments/test-cards/
3. Test UPI: Use any UPI ID in test mode

## Production

1. Switch to Live Mode in Razorpay Dashboard
2. Update credentials in `.env` files
3. Configure webhook URL in Razorpay Dashboard:
   - Webhook URL: `https://yourdomain.com/api/payments/razorpay/webhook/`
   - Events: `payment.captured`

## Features

- ✅ UPI Payments
- ✅ Card Payments (Credit/Debit)
- ✅ Net Banking
- ✅ Wallets (Paytm, PhonePe, etc.)
- ✅ Payment verification
- ✅ Automatic invoice status update
- ✅ Payment transaction records
- ✅ Webhook support








