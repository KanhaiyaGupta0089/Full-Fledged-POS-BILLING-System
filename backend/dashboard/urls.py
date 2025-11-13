from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.AdminDashboardView.as_view(), name='admin'),
    path('owner/', views.OwnerDashboardView.as_view(), name='owner'),
    path('manager/', views.ManagerDashboardView.as_view(), name='manager'),
    path('employee/', views.EmployeeDashboardView.as_view(), name='employee'),
]

