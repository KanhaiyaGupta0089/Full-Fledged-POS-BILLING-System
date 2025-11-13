# POS Billing and Inventory System - Setup Guide

## Project Overview

A full-fledged POS (Point of Sale) billing and inventory management system built with:
- **Frontend**: React.js + Tailwind CSS + Framer Motion
- **Backend**: Django REST Framework
- **Database**: PostgreSQL (recommended) or SQLite (development)
- **Cache/Queue**: Redis
- **Task Queue**: Celery

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.10 or higher)
- PostgreSQL (optional, SQLite works for development)
- Redis (for caching and async tasks)

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Update `.env` with your API URL:
```
VITE_API_BASE_URL=http://localhost:8000/api
```

5. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
# Copy the example and update with your values
cp .env.example .env
```

5. Update `.env` file with your settings:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # For development
# Or use PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/pos_system
REDIS_URL=redis://localhost:6379/0
```

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Start development server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

## Running Celery (for async tasks)

In a separate terminal:

```bash
cd backend
source venv/bin/activate
celery -A pos_system worker -l info
```

For scheduled tasks (Celery Beat):
```bash
celery -A pos_system beat -l info
```

## Initial Setup Steps

1. **Create Roles**: After creating superuser, login to Django admin (`http://localhost:8000/admin`) and create roles:
   - Admin
   - Owner
   - Manager
   - Cash Counter Employee

2. **Create Users**: Create users with appropriate roles

3. **Test Login**: Use the frontend login page to test authentication

## Development Workflow

1. Start Redis (if using):
```bash
redis-server
```

2. Start Backend:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

3. Start Frontend (in another terminal):
```bash
cd frontend
npm run dev
```

4. Start Celery (in another terminal, if needed):
```bash
cd backend
source venv/bin/activate
celery -A pos_system worker -l info
```

## Project Structure

```
bill2/
├── frontend/          # React frontend
│   ├── src/
│   │   ├── pages/     # Page components
│   │   ├── components/ # Reusable components
│   │   ├── services/  # API services
│   │   └── store/     # State management (Zustand)
│   └── package.json
│
└── backend/           # Django backend
    ├── pos_system/    # Main project settings
    ├── accounts/      # Authentication
    ├── products/      # Product management
    ├── inventory/     # Inventory management
    ├── billing/       # Billing & invoicing
    ├── payments/      # Payment processing
    ├── credit_ledger/ # Udhar Khata
    ├── daybook/       # Day book
    ├── returns/       # Product returns
    ├── discounts/     # Coupons & discounts
    ├── analytics/     # Business insights
    ├── dashboard/     # Dashboard data
    ├── notifications/ # Email system
    └── common/        # Shared utilities
```

## Next Steps

1. ✅ Login page (COMPLETED)
2. ⏭️ Dashboard implementation
3. ⏭️ Product management
4. ⏭️ Inventory management
5. ⏭️ Billing system
6. ⏭️ Payment integration
7. ⏭️ Email system
8. ⏭️ Analytics & reports
9. ⏭️ PWA setup

## Troubleshooting

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 5173 is available

### Backend Issues
- Check if port 8000 is available
- Verify database connection in `.env`
- Check Redis connection if using async tasks

### Database Issues
- Reset database: `python manage.py flush`
- Recreate migrations: `rm -rf */migrations/0*.py && python manage.py makemigrations`

## Support

For issues or questions, refer to the README files in respective directories.

