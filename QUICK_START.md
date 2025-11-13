# Quick Start Guide

## 🎯 First Steps

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This will install:
- React, React Router
- Tailwind CSS
- Framer Motion (animations)
- React Hook Form
- Zustand (state management)
- Axios (API calls)
- React Hot Toast (notifications)
- And other UI libraries

### 2. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

**Frontend** (`frontend/.env`):
```
VITE_API_BASE_URL=http://localhost:8000/api
```

**Backend** (`backend/.env`):
```
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### 4. Setup Database

```bash
cd backend
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```
Backend: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend: http://localhost:5173

**Terminal 3 - Celery (Optional, for async tasks):**
```bash
cd backend
source venv/bin/activate
celery -A pos_system worker -l info
```

## 🧪 Test Login

1. Open http://localhost:5173
2. You'll see the login page
3. Select a role (Admin, Owner, Manager, or Employee)
4. Enter username and password (from superuser you created)
5. Click "Sign In"

## 📝 Next Steps

After login is working:
1. ✅ Login page - DONE
2. ⏭️ Dashboard implementation
3. ⏭️ Product management
4. ⏭️ Inventory management
5. ⏭️ Billing system

## 🔧 Troubleshooting

### Frontend won't start
- Check if port 5173 is available
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Backend won't start
- Check if port 8000 is available
- Verify database connection in `.env`
- Run migrations: `python manage.py migrate`

### Login fails
- Check backend is running
- Verify user exists in database
- Check browser console for errors
- Verify API URL in frontend `.env`

## 📚 Documentation

- Full setup: [SETUP.md](./SETUP.md)
- Backend architecture: [backend/README.md](./backend/README.md)
- Main README: [README.md](./README.md)

