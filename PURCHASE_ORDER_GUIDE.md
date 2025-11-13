# Purchase Order Feature - Usage Guide

## Overview
The Purchase Order (PO) system helps you manage procurement from suppliers, track deliveries, receive goods, and handle payments. The system supports automation features like auto-approval and low-stock reordering.

## Key Components

### 1. **Suppliers**
- Manage supplier/vendor information
- Track payment terms, credit limits, and performance
- Mark preferred suppliers for auto-reordering

### 2. **Purchase Orders (PO)**
- Create purchase orders with multiple items
- Track order status through the procurement lifecycle
- Auto-generate PO numbers
- Support for discounts, taxes, and multiple warehouses

### 3. **Goods Receipt Notes (GRN)**
- Automatically created when receiving items from a PO
- Track batch numbers and expiry dates
- Quality check and verification workflow

### 4. **Supplier Payments**
- Record payments made to suppliers
- Support multiple payment methods (cash, bank transfer, cheque, UPI, credit)
- Link payments to specific purchase orders

## Purchase Order Workflow

### Step 1: Create a Purchase Order

1. **Navigate to Purchase Orders** in the menu
2. **Click "Create New Purchase Order"**
3. **Fill in the details:**
   - Select Supplier
   - Select Warehouse (where goods will be received)
   - Set Expected Delivery Date
   - Add Notes (optional)

4. **Add Items:**
   - Select Product
   - Enter Quantity
   - Enter Unit Price (defaults to product cost price)
   - Set Tax Rate (defaults to product tax rate)
   - Add Discount (optional)
   - Click "Add Item"

5. **Review Totals:**
   - Subtotal (sum of all items)
   - Discount Amount
   - Tax Amount
   - Total Amount

6. **Save as Draft** or **Submit for Approval**

### Step 2: PO Status Lifecycle

**Status Flow:**
```
Draft → Pending Approval → Approved → Sent to Supplier → 
Partially Received → Received → (Payment)
```

- **Draft**: Initial creation, can be edited
- **Pending Approval**: Submitted for manager/admin approval
- **Approved**: Approved and ready to send to supplier
- **Sent to Supplier**: PO has been sent to supplier
- **Partially Received**: Some items received, waiting for rest
- **Received**: All items received
- **Cancelled**: Order cancelled (can happen at any stage)

### Step 3: Approve Purchase Order

1. Navigate to the PO details
2. Click **"Approve"** button (if you have permission)
3. PO status changes to "Approved"
4. You can now send it to the supplier

### Step 4: Receive Goods (Create GRN)

When goods arrive from the supplier:

1. **Navigate to the Purchase Order**
2. **Click "Receive Goods" or "Create GRN"**
3. **For each item:**
   - Enter Quantity Received (may be less than ordered)
   - Enter Batch Number (if tracking batches)
   - Set Expiry Date (if applicable)
   - Mark Quality Check status
   - Add Quality Notes (if any issues)

4. **Save GRN:**
   - GRN number is auto-generated
   - Inventory is automatically updated
   - PO status updates to "Partially Received" or "Received"

### Step 5: Verify GRN (Optional)

1. Navigate to GRN details
2. Review received items
3. Click **"Verify"** to mark as verified
4. This updates inventory and completes the receiving process

### Step 6: Record Supplier Payment

1. **Navigate to Supplier Payments**
2. **Click "Create Payment"**
3. **Fill in details:**
   - Select Supplier
   - Link to Purchase Order (optional)
   - Enter Payment Amount
   - Select Payment Method
   - Enter Payment Date
   - Add Reference Number (transaction ID, cheque number, etc.)
   - Add Notes

4. **Save Payment**

## Automation Features

### Auto-Approval
- Enable `auto_approve` flag on a PO
- PO automatically moves to "Approved" status when saved
- Useful for routine purchases

### Low Stock Auto-Reordering
- Set up Auto Reorder Rules for products
- System automatically creates POs when stock falls below reorder point
- Uses preferred supplier if configured

### Auto PO Creation
- Navigate to Purchase Orders
- Click **"Auto Create from Low Stock"**
- System checks all products with low stock
- Creates POs based on reorder rules

## Best Practices

1. **Always set Expected Delivery Date** - Helps with planning and tracking
2. **Use Notes field** - Document special requirements or instructions
3. **Verify GRNs promptly** - Ensures inventory accuracy
4. **Link payments to POs** - Better financial tracking
5. **Use preferred suppliers** - For consistent quality and pricing
6. **Track batch numbers** - Important for expiry management and recalls

## Common Tasks

### View All Purchase Orders
- Filter by Status, Supplier, Warehouse
- Search by PO Number or Supplier Name
- Sort by Date, Amount, etc.

### Track Pending Orders
- Filter by status: "Pending Approval", "Approved", "Sent to Supplier"
- Monitor expected delivery dates

### Check Receiving Status
- View "Partially Received" POs
- See which items are still pending
- Track delivery delays

### Supplier Performance
- View supplier statistics
- Check average delivery times
- Review payment history

## Tips

- **Draft Status**: Use for planning before finalizing
- **Partial Receiving**: Common in real scenarios - receive what's available
- **Quality Checks**: Always verify quality before marking GRN as verified
- **Payment Terms**: Set payment terms on suppliers for better cash flow management
- **Multiple Warehouses**: Create separate POs for different warehouses

## Sample Data

To populate the system with sample purchase orders, suppliers, GRNs, and payments, run:

```bash
python manage.py shell
>>> exec(open('scripts/create_dummy_data.py').read())
```

This creates:
- 5 Suppliers with complete information
- 20 Purchase Orders with various statuses
- 10 GRNs for received orders
- Multiple Supplier Payments

## API Endpoints

### Purchase Orders
- `GET /api/purchases/purchase-orders/` - List all POs
- `POST /api/purchases/purchase-orders/` - Create new PO
- `GET /api/purchases/purchase-orders/{id}/` - Get PO details
- `PUT /api/purchases/purchase-orders/{id}/` - Update PO
- `POST /api/purchases/purchase-orders/{id}/approve/` - Approve PO
- `POST /api/purchases/purchase-orders/auto_create_from_low_stock/` - Auto-create POs

### GRNs
- `GET /api/purchases/grns/` - List all GRNs
- `POST /api/purchases/grns/` - Create new GRN
- `POST /api/purchases/grns/{id}/verify/` - Verify GRN

### Suppliers
- `GET /api/purchases/suppliers/` - List suppliers
- `POST /api/purchases/suppliers/` - Create supplier
- `GET /api/purchases/suppliers/top_suppliers/` - Get top suppliers

### Payments
- `GET /api/purchases/payments/` - List payments
- `POST /api/purchases/payments/` - Create payment

## Troubleshooting

**PO not updating totals?**
- Ensure all items are saved
- Check that item totals are calculated correctly
- Recalculate PO totals if needed

**GRN not updating inventory?**
- Verify the GRN is marked as "Verified"
- Check warehouse assignment
- Ensure products exist in inventory

**Auto-reorder not working?**
- Check Auto Reorder Rules are active
- Verify reorder points are set correctly
- Ensure preferred supplier is assigned

---

For more details, refer to the API documentation or contact your system administrator.


