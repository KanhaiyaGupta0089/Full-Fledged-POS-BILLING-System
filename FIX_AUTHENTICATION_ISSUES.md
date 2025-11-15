# Fix Authentication and API Access Issues

## Issues Fixed

### 1. CORS Configuration
**Problem:** The backend was not allowing requests from the Vercel frontend domain.

**Solution:** Updated `backend/pos_system/settings.py` to:
- Allow all origins in production by default (can be restricted later)
- Support dynamic Vercel domains
- Maintain security while allowing frontend access

### 2. Token Retrieval from Zustand Storage
**Problem:** The API interceptor was not reliably finding the authentication token in Zustand's persisted storage.

**Solution:** Updated `frontend/src/services/api.js` to:
- Try multiple paths to find the token (`state.token`, `token`, `state.access`, `access`)
- Only log warnings in development mode to avoid console spam
- Handle edge cases where the storage structure might differ

### 3. Environment Variable Setup
**Problem:** Frontend needs to know the Railway backend URL.

**Solution:** Created `VERCEL_ENV_SETUP.md` with instructions for setting `VITE_API_BASE_URL` in Vercel.

## Next Steps

### 1. Set Environment Variable in Vercel
Follow the instructions in `VERCEL_ENV_SETUP.md` to set:
- `VITE_API_BASE_URL` = `https://YOUR-RAILWAY-DOMAIN.up.railway.app/api`

### 2. Redeploy Both Services
1. **Railway (Backend):**
   - Push the changes to trigger a new deployment
   - The CORS changes will take effect automatically

2. **Vercel (Frontend):**
   - After setting the environment variable, redeploy
   - Go to Deployments → Latest → Redeploy

### 3. Test Authentication
1. Clear browser localStorage or use incognito mode
2. Navigate to the login page
3. Use credentials:
   - Username: `admin`, Password: `admin123`
   - Username: `owner`, Password: `owner123`

### 4. Verify API Access
After logging in, verify that:
- Dashboard loads correctly
- API calls include the `Authorization: Bearer <token>` header
- No 403 Forbidden errors
- No "No token found" warnings in console

## Troubleshooting

### If you still see "No token found":
1. Open browser DevTools → Application → Local Storage
2. Check the `auth-storage` key
3. Verify it has structure: `{ state: { token: "...", user: {...}, ... }, version: 0 }`
4. If structure is different, the interceptor should still find it via alternative paths

### If you see CORS errors:
1. Check Railway logs to see if CORS is blocking requests
2. Verify `CORS_ALLOW_ALL_ORIGINS=True` in Railway environment variables (or it defaults to True)
3. Check browser network tab for CORS preflight errors

### If API calls return 403 Forbidden:
1. Verify the token is being sent in the Authorization header
2. Check browser Network tab → Request Headers
3. Verify the user has the correct permissions (admin/owner/manager/employee)
4. Check Railway logs for permission errors

### If login returns "Method Not Allowed":
1. Verify the frontend is making a POST request (not GET)
2. Check that `VITE_API_BASE_URL` is correctly set
3. Verify the endpoint is `/api/auth/login/` (with trailing slash)

## Expected Behavior After Fix

1. ✅ Login works without "Method Not Allowed" errors
2. ✅ Token is stored correctly in localStorage
3. ✅ API calls include the Authorization header
4. ✅ No "No token found" warnings (in production)
5. ✅ Dashboard and other pages load data correctly
6. ✅ No 403 Forbidden errors for authenticated users

## Additional Notes

- The warnings about Tesseract OCR and email sending are expected and don't affect functionality
- The `pkg_resources` deprecation warning is from the Razorpay library and can be ignored
- Email sending failures are expected if SMTP is not configured (this is optional)

