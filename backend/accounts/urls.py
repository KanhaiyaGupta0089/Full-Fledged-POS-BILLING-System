"""
URLs for accounts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user/', views.UserView.as_view(), name='user'),
    path('refresh/', views.RefreshTokenView.as_view(), name='refresh'),
    path('', include(router.urls)),
]

