from rest_framework import serializers
from django.conf import settings
from .models import Product, Category, Brand


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 
            'is_active', 'product_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        return obj.products.count()


class BrandSerializer(serializers.ModelSerializer):
    """Brand serializer"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'description', 'logo',
            'is_active', 'product_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        return obj.products.count()


class ProductListSerializer(serializers.ModelSerializer):
    """Product list serializer (lightweight)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'qr_code', 'image',
            'category', 'category_name', 'brand', 'brand_name',
            'cost_price', 'selling_price', 'current_stock',
            'min_stock_level', 'stock_status', 'is_low_stock',
            'is_active', 'created_at'
        ]
    
    def get_image(self, obj):
        """Return full image URL"""
        if obj.image:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return f"{settings.MEDIA_URL}{obj.image.url}" if obj.image.url else None
            except Exception:
                return None
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Product detail serializer (full data)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'qr_code', 'description',
            'category', 'category_name', 'brand', 'brand_name',
            'cost_price', 'selling_price', 'profit_margin',
            'current_stock', 'min_stock_level', 'max_stock_level',
            'unit', 'weight', 'dimensions',
            'image', 'additional_images',
            'tax_rate', 'is_active', 'is_trackable',
            'stock_status', 'is_low_stock',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'sku', 'barcode', 'qr_code']
    
    def get_image(self, obj):
        """Return full image URL"""
        if obj.image:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return f"{settings.MEDIA_URL}{obj.image.url}" if obj.image.url else None
            except Exception:
                return None
        return None


class ProductSearchSerializer(serializers.ModelSerializer):
    """Product search serializer (for quick search)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'qr_code', 'image',
            'category_name', 'selling_price', 'current_stock',
            'is_active'
        ]
    
    def get_image(self, obj):
        """Return full image URL"""
        if obj.image:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return f"{settings.MEDIA_URL}{obj.image.url}" if obj.image.url else None
            except Exception:
                return None
        return None