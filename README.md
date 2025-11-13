# POS Billing and Inventory System

A comprehensive Point of Sale (POS) billing and inventory management system built with React.js and Django.

## 🚀 Features

### Core Features
- ✅ **Role-Based Authentication** - Admin, Owner, Manager, Cash Counter Employee
- ✅ **Login System** - Secure JWT-based authentication
- 🔄 **Product Management** - Add, edit, delete products
- 🔄 **Inventory Management** - Real-time stock tracking
- 🔄 **Billing System** - Generate invoices and bills
- 🔄 **Payment Integration** - UPI and other payment methods
- 🔄 **Credit Ledger (Udhar Khata)** - Track customer credits
- 🔄 **Day Book** - Automatic daily transaction records
- 🔄 **Product Returns** - Handle return transactions
- 🔄 **Coupons & Discounts** - Apply discounts and coupons
- 🔄 **Email System** - Automated email notifications
- 🔄 **Analytics & Insights** - AI-powered business insights
- 🔄 **Dashboard** - Role-specific dashboards
- 🔄 **Reports** - Graphical and textual reports
- 🔄 **PWA Support** - Progressive Web App for mobile use

### Product Search Methods
- QR Code scanning
- Barcode scanning
- Product name search
- Product ID search

### Email Notifications
- Daily business summary (9 AM)
- Low stock alerts
- Invoice emails to customers
- Credit reminders
- Order confirmations

## 🛠️ Tech Stack

### Frontend
- **React.js** - UI framework
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **React Router** - Routing
- **Zustand** - State management
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Recharts** - Data visualization
- **html5-qrcode** - QR/Barcode scanning
- **jsPDF** - PDF generation

### Backend
- **Django** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database (recommended)
- **Redis** - Caching & pub/sub
- **Celery** - Async task processing
- **JWT** - Authentication
- **ReportLab/WeasyPrint** - PDF generation

## 📁 Project Structure

```
bill2/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── services/    # API services
│   │   └── store/       # State management
│   └── package.json
│
├── backend/              # Django backend
│   ├── pos_system/      # Main project
│   ├── accounts/        # Authentication
│   ├── products/        # Products
│   ├── inventory/      # Inventory
│   ├── billing/         # Billing
│   ├── payments/        # Payments
│   ├── credit_ledger/   # Credit ledger
│   ├── daybook/         # Day book
│   ├── returns/         # Returns
│   ├── discounts/       # Discounts
│   ├── analytics/       # Analytics
│   ├── dashboard/       # Dashboard
│   ├── notifications/   # Email system
│   └── common/          # Utilities
│
└── README.md
```

## 🚦 Quick Start

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL (optional)
- Redis (optional, for async tasks)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env with your settings

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Running Celery (for async tasks)

```bash
cd backend
source venv/bin/activate
celery -A pos_system worker -l info
celery -A pos_system beat -l info  # For scheduled tasks
```

## 📝 Environment Variables

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### Backend (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🔐 User Roles

1. **Admin** - Full system access
2. **Owner** - Business owner access
3. **Manager** - Management access (no user management)
4. **Cash Counter Employee** - Billing and basic operations

## 📊 Current Status

### ✅ Completed
- [x] Project structure setup
- [x] Frontend dependencies
- [x] Tailwind CSS configuration
- [x] Login page (frontend)
- [x] Authentication backend
- [x] Role-based access control
- [x] Django project structure

### 🔄 In Progress
- [ ] Dashboard implementation
- [ ] Product management
- [ ] Inventory management
- [ ] Billing system
- [ ] Payment integration
- [ ] Email system
- [ ] Analytics & reports
- [ ] PWA setup

## 📚 Documentation

- [Setup Guide](./SETUP.md)
- [Backend Architecture](./backend/README.md)
- [API Documentation](http://localhost:8000/api/docs/) (when running)

## 🤝 Contributing

This is a step-by-step implementation. We'll build features incrementally.

## 📄 License

This project is for educational/practice purposes.

## 🆘 Support

For issues or questions, refer to the documentation files in respective directories.

---

**Note**: This is an active development project. Features are being implemented step by step.

