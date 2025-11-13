"""
Views for Expense Management
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ExpenseCategory, Expense
from .serializers import ExpenseCategorySerializer, ExpenseSerializer
from common.permissions import IsAdminOrManager


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """Expense Category CRUD"""
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    search_fields = ['name']


class ExpenseViewSet(viewsets.ModelViewSet):
    """Expense CRUD operations"""
    queryset = Expense.objects.select_related('category', 'created_by', 'approved_by')
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'payment_method', 'is_recurring', 'is_approved']
    search_fields = ['description', 'vendor_name', 'expense_number', 'bill_number']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']
    
    def get_serializer_context(self):
        """Add request to serializer context for image URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        """Set created_by on create"""
        serializer.save(created_by=self.request.user)

