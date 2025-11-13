# POS Billing and Inventory System - Backend

## Architecture Overview

This Django backend follows a modular architecture with separate apps for different functionalities.

## Folder Structure

```
backend/
├── pos_system/              # Main Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration (for async support)
│   └── celery.py            # Celery configuration for async tasks
│
├── accounts/                # User authentication and management
│   ├── models.py            # User, Role models
│   ├── views.py             # Authentication views
│   ├── serializers.py       # DRF serializers
│   ├── permissions.py       # Role-based permissions
│   └── emailer.py           # Email templates for accounts
│
├── products/                # Product management
│   ├── models.py            # Product, Category, Brand models
│   ├── views.py             # Product CRUD operations
│   ├── serializers.py       # Product serializers
│   └── emailer.py           # Email templates for products
│
├── inventory/               # Inventory management
│   ├── models.py            # Stock, Warehouse, InventoryTransaction models
│   ├── views.py             # Inventory operations
│   ├── serializers.py       # Inventory serializers
│   └── emailer.py           # Email templates for inventory alerts
│
├── billing/                 # Billing and invoicing
│   ├── models.py            # Invoice, InvoiceItem, Payment models
│   ├── views.py             # Billing operations
│   ├── serializers.py       # Billing serializers
│   ├── invoice_generator.py # PDF invoice generation
│   └── emailer.py           # Invoice email templates
│
├── payments/                # Payment processing
│   ├── models.py            # Payment, PaymentMethod models
│   ├── views.py             # Payment processing
│   ├── serializers.py       # Payment serializers
│   ├── upi_handler.py       # UPI payment integration
│   └── emailer.py           # Payment confirmation emails
│
├── credit_ledger/           # Udhar Khata (Credit Ledger)
│   ├── models.py            # CreditTransaction, CustomerCredit models
│   ├── views.py             # Credit operations
│   ├── serializers.py       # Credit serializers
│   └── emailer.py           # Credit reminder emails
│
├── daybook/                 # Day Book (Daily transactions)
│   ├── models.py            # DayBookEntry model
│   ├── views.py             # Day book operations
│   ├── serializers.py       # Day book serializers
│   └── signals.py           # Auto-generate entries on invoice creation
│
├── returns/                 # Product returns
│   ├── models.py            # Return, ReturnItem models
│   ├── views.py             # Return operations
│   ├── serializers.py       # Return serializers
│   └── emailer.py           # Return confirmation emails
│
├── discounts/               # Coupons and discounts
│   ├── models.py            # Coupon, Discount models
│   ├── views.py             # Discount operations
│   ├── serializers.py       # Discount serializers
│   └── emailer.py           # Coupon notification emails
│
├── analytics/               # Business insights and analytics
│   ├── models.py            # Analytics cache models
│   ├── views.py             # Analytics endpoints
│   ├── serializers.py       # Analytics serializers
│   ├── ai_insights.py       # AI-powered insights (trending products, low stock, etc.)
│   └── reports.py            # Report generation
│
├── dashboard/               # Dashboard data
│   ├── views.py             # Dashboard endpoints
│   ├── serializers.py       # Dashboard serializers
│   └── aggregators.py       # Data aggregation logic
│
├── notifications/           # Email and notification system
│   ├── models.py            # Notification, EmailQueue models
│   ├── views.py             # Notification endpoints
│   ├── serializers.py       # Notification serializers
│   ├── email_service.py     # Email sending service
│   ├── redis_pubsub.py      # Redis pub/sub for async emails
│   └── tasks.py             # Celery tasks for scheduled emails
│
├── common/                  # Shared utilities
│   ├── utils.py             # Common utility functions
│   ├── permissions.py       # Shared permissions
│   ├── pagination.py        # Custom pagination
│   └── exceptions.py        # Custom exceptions
│
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
└── .env.example             # Environment variables template
```

## Key Technologies

- **Django REST Framework**: API development
- **PostgreSQL**: Primary database (recommended for production)
- **Redis**: Caching and pub/sub for email system
- **Celery**: Async task processing (scheduled emails, reports)
- **Django Channels**: WebSocket support (optional for real-time updates)
- **ReportLab/WeasyPrint**: PDF invoice generation
- **Django Q**: Alternative to Celery (lighter weight)

## Setup Instructions

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy .env.example to .env)

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `EMAIL_HOST`: SMTP host
- `EMAIL_PORT`: SMTP port
- `EMAIL_USER`: Email username
- `EMAIL_PASSWORD`: Email password
- `UPI_MERCHANT_ID`: UPI merchant ID
- `UPI_API_KEY`: UPI API key

## Role-Based Access Control

- **Admin/Owner**: Full access to all features
- **Manager**: Access to reports, inventory, billing (no user management)
- **Cash Counter Employee**: Access to billing, product search, basic operations

## Scheduled Tasks

- Daily business summary email at 9 AM (previous day)
- Low stock alerts
- Credit payment reminders
- Weekly/monthly reports

