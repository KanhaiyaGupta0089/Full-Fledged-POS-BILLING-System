from rest_framework import permissions


class IsAdminOrManager(permissions.BasePermission):
    """Allow access to admin and manager only"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager']
        )


class IsAdminOrManagerOrEmployee(permissions.BasePermission):
    """Allow access to admin, manager, and employee"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager', 'employee']
        )


class IsAdminOrOwner(permissions.BasePermission):
    """Allow access to admin and owner only"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'owner']
        )





