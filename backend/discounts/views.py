"""
Discounts views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coupon, Discount
from .serializers import CouponSerializer, DiscountSerializer
from common.permissions import IsAdminOrManager, IsAdminOrManagerOrEmployee


class CouponViewSet(viewsets.ModelViewSet):
    """Coupon CRUD operations"""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['is_active', 'discount_type']
    search_fields = ['code', 'name']
    ordering_fields = ['created_at', 'valid_until']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Allow employees to list and validate coupons, but only admins/managers can modify"""
        if self.action in ['list', 'validate', 'available']:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filter queryset based on action"""
        queryset = super().get_queryset()
        if self.action in ['list', 'available']:
            # For listing, show only active and valid coupons
            from django.utils import timezone
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            )
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available/valid coupons"""
        from django.utils import timezone
        from decimal import Decimal
        
        now = timezone.now()
        amount = request.query_params.get('amount', 0)
        
        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            amount = Decimal('0.00')
        
        # Get all active and valid coupons
        coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )
        
        # Filter by minimum purchase amount and usage limits
        available_coupons = []
        for coupon in coupons:
            # Check usage limits
            if coupon.max_uses and coupon.used_count >= coupon.max_uses:
                continue
            
            # Check minimum purchase amount
            if amount < coupon.min_purchase_amount:
                continue
            
            # Calculate discount for this amount
            discount_amount = coupon.calculate_discount(amount)
            
            coupon_data = CouponSerializer(coupon).data
            coupon_data['calculated_discount'] = float(discount_amount)
            available_coupons.append(coupon_data)
        
        return Response(available_coupons)
    
    @action(detail=False, methods=['get'])
    def validate(self, request):
        """Validate coupon code"""
        code = request.query_params.get('code', '').strip()
        amount = request.query_params.get('amount', 0)
        
        if not code:
            return Response(
                {'error': 'Coupon code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code=code)
            is_valid = coupon.is_valid()
            discount_amount = 0
            
            if is_valid:
                try:
                    discount_amount = float(coupon.calculate_discount(float(amount)))
                except (ValueError, TypeError):
                    discount_amount = 0
            
            return Response({
                'valid': is_valid,
                'coupon': CouponSerializer(coupon).data if is_valid else None,
                'discount_amount': discount_amount
            })
        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Coupon not found'
            })


class DiscountViewSet(viewsets.ModelViewSet):
    """Discount CRUD operations"""
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'discount_percentage']
    ordering = ['-created_at']

