"""
Django settings for pos_system project.
"""
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

# ALLOWED_HOSTS: List of allowed host/domain names
# For Railway: use 'web-production-12808.up.railway.app' or '*.railway.app' (without https:// or trailing slash)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '*.railway.app'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    
    # Local apps
    'accounts',
    'products',
    'inventory',
    'billing',
    'payments',
    'credit_ledger',
    'daybook',
    'returns',
    'discounts',
    'analytics',
    'dashboard',
    'notifications',
    'common',
    # New high-priority features
    'customers',
    'purchases',
    'expenses',
    'currencies',
    'ocr',
    'forecasting',
    'reports',
    'marketing',  # AI-powered Marketing & Advertisement
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pos_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pos_system.wsgi.application'

# Database
# For PostgreSQL, use: postgresql://user:password@localhost:port/dbname
# For SQLite (development only), use: sqlite:///db.sqlite3
# Docker default (if using separate docker-compose): postgresql://pos_user:12345678@localhost:5433/pos_system
# Using existing Docker: postgresql://ez_user:12345678@localhost:5432/ez_delivery
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgresql://ez_user:12345678@localhost:5432/ez_delivery')
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS settings
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[
        'http://localhost:5173',
        'http://localhost:5176',
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5176',
        'http://127.0.0.1:3000',
    ]
)

CORS_ALLOW_CREDENTIALS = True

# Allow all origins in development (remove in production)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Email settings
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='gkanha1500@gmail.com')
EMAIL_TIMEOUT = 10

# Use console backend only if explicitly set or in DEBUG mode without email credentials
if EMAIL_BACKEND == 'console' or (DEBUG and not EMAIL_HOST_USER):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Redis settings
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

# Celery settings
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat settings
from celery.schedules import crontab
from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    'send-daily-summary': {
        'task': 'notifications.tasks.send_daily_business_summary',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    # Purchase Orders Automation
    'check-low-stock-and-create-pos': {
        'task': 'purchases.tasks.check_low_stock_and_create_pos_task',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'auto-approve-pending-pos': {
        'task': 'purchases.tasks.auto_approve_pending_pos_task',
        'schedule': crontab(minute=0),  # Every hour
    },
    'update-supplier-performance': {
        'task': 'purchases.tasks.update_supplier_performance_task',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),  # Every Monday at midnight
    },
    'check-expiring-products': {
        'task': 'purchases.tasks.check_expiring_products_task',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    # Inventory Automation
    'check-reorder-points': {
        'task': 'inventory.tasks.check_reorder_points_task',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    'check-low-stock-alerts': {
        'task': 'inventory.tasks.check_low_stock_alerts_task',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
    },
    'calculate-stock-valuations': {
        'task': 'inventory.tasks.calculate_stock_valuations_task',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'cleanup-expired-batches': {
        'task': 'inventory.tasks.cleanup_expired_batches_task',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'POS Billing and Inventory System API',
    'DESCRIPTION': 'API documentation for POS System',
    'VERSION': '1.0.0',
}

# Razorpay Payment Gateway Settings
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='')
RAZORPAY_WEBHOOK_SECRET = env('RAZORPAY_WEBHOOK_SECRET', default='')

