"""
Serializers for Purchase Orders & Supplier Management
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem, SupplierPayment


class SupplierSerializer(serializers.ModelSerializer):
    """Supplier serializer"""
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'total_purchases', 'total_orders']
    
    def validate_credit_limit(self, value):
        """Convert empty string to 0"""
        if value == '' or value is None:
            return Decimal('0.00')
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return Decimal('0.00')


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Purchase Order Item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Purchase Order serializer"""
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    items_data = PurchaseOrderItemSerializer(many=True, write_only=True, required=False)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    supplier_id = serializers.IntegerField(write_only=True, required=False)
    warehouse_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['po_number', 'created_at', 'updated_at', 'approved_at']
    
    def create(self, validated_data):
        """Handle supplier, warehouse IDs and items"""
        supplier_id = validated_data.pop('supplier_id', None)
        warehouse_id = validated_data.pop('warehouse_id', None)
        items_data = validated_data.pop('items_data', [])
        
        if supplier_id:
            from .models import Supplier
            validated_data['supplier'] = Supplier.objects.get(pk=supplier_id)
        if warehouse_id:
            from inventory.models import Warehouse
            validated_data['warehouse'] = Warehouse.objects.get(pk=warehouse_id)
        
        # Create PO
        po = super().create(validated_data)
        
        # Create items
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
        
        # Recalculate totals
        from .automation import recalculate_po_totals
        recalculate_po_totals(po)
        
        return po
    
    def update(self, instance, validated_data):
        """Handle items update"""
        items_data = validated_data.pop('items_data', None)
        
        po = super().update(instance, validated_data)
        
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            # Create new items
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
            
            # Recalculate totals
            from .automation import recalculate_po_totals
            recalculate_po_totals(po)
        
        return po


class GRNItemSerializer(serializers.ModelSerializer):
    """GRN Item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = GRNItem
        fields = '__all__'


class GoodsReceiptNoteSerializer(serializers.ModelSerializer):
    """GRN serializer"""
    items = GRNItemSerializer(many=True, read_only=True)
    items_data = GRNItemSerializer(many=True, write_only=True, required=False)
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)
    purchase_order_id = serializers.IntegerField(write_only=True, required=False)
    warehouse_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = GoodsReceiptNote
        fields = '__all__'
        read_only_fields = ['grn_number', 'created_at', 'received_at']
    
    def create(self, validated_data):
        """Handle purchase_order, warehouse IDs and items"""
        purchase_order_id = validated_data.pop('purchase_order_id', None)
        warehouse_id = validated_data.pop('warehouse_id', None)
        items_data = validated_data.pop('items_data', [])
        
        if purchase_order_id:
            validated_data['purchase_order'] = PurchaseOrder.objects.get(pk=purchase_order_id)
        if warehouse_id:
            from inventory.models import Warehouse
            validated_data['warehouse'] = Warehouse.objects.get(pk=warehouse_id)
        
        # Create GRN
        grn = super().create(validated_data)
        
        # Create items
        for item_data in items_data:
            GRNItem.objects.create(grn=grn, **item_data)
        
        # Update total amount
        total = sum(item.unit_price * item.quantity_received for item in grn.items.all())
        grn.total_amount = total
        grn.save(update_fields=['total_amount'])
        
        return grn


class SupplierPaymentSerializer(serializers.ModelSerializer):
    """Supplier Payment serializer"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierPayment
        fields = '__all__'
        read_only_fields = ['created_at']

