"""
Views for Customer Management
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from billing.models import Customer
from billing.customer_extras import CustomerPurchaseHistory, CustomerCommunication
from .serializers import CustomerSerializer, CustomerPurchaseHistorySerializer, CustomerCommunicationSerializer
from common.permissions import IsAdminOrManagerOrEmployee
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class CustomerViewSet(viewsets.ModelViewSet):
    """Customer CRUD operations"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'gstin', 'pan']
    filterset_fields = ['customer_type', 'is_active', 'is_blacklisted']
    ordering_fields = ['name', 'created_at', 'total_purchases']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set created_by on create"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update customer"""
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def purchase_history(self, request, pk=None):
        """Get customer purchase history"""
        customer = self.get_object()
        history = CustomerPurchaseHistory.objects.filter(customer=customer).order_by('-created_at')
        serializer = CustomerPurchaseHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_loyalty_points(self, request, pk=None):
        """Add loyalty points to customer"""
        customer = self.get_object()
        points = request.data.get('points', 0)
        customer.add_loyalty_points(points)
        return Response({'message': f'Added {points} loyalty points'})


class CustomerCommunicationViewSet(viewsets.ModelViewSet):
    """Customer Communication operations"""
    queryset = CustomerCommunication.objects.select_related('customer', 'sent_by')
    serializer_class = CustomerCommunicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'communication_type']
    
    def perform_create(self, serializer):
        serializer.save(sent_by=self.request.user)

