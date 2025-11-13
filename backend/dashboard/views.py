from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .aggregators import (
    get_admin_dashboard_stats,
    get_owner_dashboard_stats,
    get_manager_dashboard_stats,
    get_employee_dashboard_stats
)

class AdminDashboardView(APIView):
    """Admin dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response(
                {'detail': 'Permission denied'},
                status=403
            )
        
        stats = get_admin_dashboard_stats()
        return Response(stats)

class OwnerDashboardView(APIView):
    """Owner dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'owner':
            return Response(
                {'detail': 'Permission denied'},
                status=403
            )
        
        stats = get_owner_dashboard_stats()
        return Response(stats)

class ManagerDashboardView(APIView):
    """Manager dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'manager':
            return Response(
                {'detail': 'Permission denied'},
                status=403
            )
        
        stats = get_manager_dashboard_stats()
        return Response(stats)

class EmployeeDashboardView(APIView):
    """Employee dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'employee':
            return Response(
                {'detail': 'Permission denied'},
                status=403
            )
        
        stats = get_employee_dashboard_stats(user=request.user)
        return Response(stats)