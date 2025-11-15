"""
Serializers for Expense Management
"""
from rest_framework import serializers
from .models import ExpenseCategory, Expense


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Expense Category serializer"""
    class Meta:
        model = ExpenseCategory
        fields = '__all__'
        read_only_fields = ['created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    """Expense serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    created_by_name = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    receipt_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['expense_number', 'created_at', 'updated_at']
    
    def get_receipt_image_url(self, obj):
        """Get receipt image URL"""
        if obj.receipt_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_image.url)
        return None
    
    def get_created_by_name(self, obj):
        """Get created by name safely"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
    
    def create(self, validated_data):
        """Handle category ID"""
        category_id = validated_data.pop('category_id', None)
        if category_id:
            validated_data['category'] = ExpenseCategory.objects.get(pk=category_id)
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

