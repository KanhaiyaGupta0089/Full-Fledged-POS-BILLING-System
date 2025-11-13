"""
URL configuration for pos_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/credit/', include('credit_ledger.urls')),
    path('api/daybook/', include('daybook.urls')),
    path('api/returns/', include('returns.urls')),
    path('api/discounts/', include('discounts.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/notifications/', include('notifications.urls')),
    # New high-priority features
    path('api/customers/', include('customers.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/expenses/', include('expenses.urls')),
    path('api/currencies/', include('currencies.urls')),
    path('api/ocr/', include('ocr.urls')),
    path('api/forecasting/', include('forecasting.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/marketing/', include('marketing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

