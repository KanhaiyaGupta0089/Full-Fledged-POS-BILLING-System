# 🚀 Quick Deploy Guide - 5 Minutes

## Prerequisites
- ✅ Code pushed to GitHub
- ✅ Account on Render.com (free)

## Step-by-Step Deployment

### 1. Deploy Backend (2 minutes)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo
4. Settings:
   - **Name**: `pos-backend`
   - **Build Command**: `cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `cd backend && gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT`
5. Add Environment Variables:
   ```
   SECRET_KEY=<click-generate>
   DEBUG=False
   ALLOWED_HOSTS=pos-backend.onrender.com,*.onrender.com
   ```
6. Click **"Create Web Service"**

### 2. Add Database (1 minute)

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `pos-database`
3. Click **"Create Database"**
4. Copy **Internal Database URL**
5. Go to backend → Environment → Add:
   ```
   DATABASE_URL=<paste-url>
   ```

### 3. Deploy Frontend (1 minute)

1. Click **"New +"** → **"Static Site"**
2. Connect GitHub repo
3. Settings:
   - **Name**: `pos-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add Environment Variable:
   ```
   VITE_API_BASE_URL=https://pos-backend.onrender.com/api
   ```
5. Click **"Create Static Site"**

### 4. Run Migrations (1 minute)

1. Go to backend service
2. Click **"Shell"** tab
3. Run:
   ```bash
   cd backend
   python manage.py migrate
   python manage.py createsuperuser
   ```

### 5. Update CORS

1. Backend → Environment → Add:
   ```
   CORS_ALLOWED_ORIGINS=https://pos-frontend.onrender.com
   ```

## ✅ Done!

- Frontend: `https://pos-frontend.onrender.com`
- Backend: `https://pos-backend.onrender.com/api`
- Admin: `https://pos-backend.onrender.com/admin`

## 📝 Notes

- Free tier services spin down after 15 min inactivity
- First request may take 30-60 seconds to wake up
- See `DEPLOYMENT_GUIDE.md` for detailed instructions

