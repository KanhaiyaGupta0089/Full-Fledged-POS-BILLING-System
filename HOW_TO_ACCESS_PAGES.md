# How to Access the New Pages

## 🎯 Quick Access Guide

After logging into the system, you can access the new pages in **two ways**:

### Method 1: Using the Sidebar Navigation (Recommended)

The new pages have been added to the sidebar menu. Simply click on the menu items:

#### For Admin Users:
1. **Customers** - Click "Customers" in the sidebar (UserCircle icon)
2. **Purchase Orders** - Click "Purchase Orders" in the sidebar (ShoppingBag icon)
3. **Expenses** - Click "Expenses" in the sidebar (DollarSign icon)
4. **OCR** - Click "OCR" in the sidebar (ScanLine icon)

#### For Manager Users:
Same menu items are available in the manager sidebar.

### Method 2: Direct URL Access

You can also access pages directly by typing the URL in your browser:

#### Customer Management:
- Admin: `http://localhost:5173/dashboard/admin/customers`
- Manager: `http://localhost:5173/dashboard/manager/customers`

#### Purchase Orders:
- Admin: `http://localhost:5173/dashboard/admin/purchase-orders`
- Manager: `http://localhost:5173/dashboard/manager/purchase-orders`

#### Expenses:
- Admin: `http://localhost:5173/dashboard/admin/expenses`
- Manager: `http://localhost:5173/dashboard/manager/expenses`

#### OCR:
- Admin: `http://localhost:5173/dashboard/admin/ocr`
- Manager: `http://localhost:5173/dashboard/manager/ocr`

## 📍 Navigation Menu Structure

The sidebar menu now includes these new items in the following order:

### Admin Menu:
1. Dashboard
2. Products
3. Inventory
4. Billing
5. Invoice Search
6. **Customers** ⭐ NEW
7. **Purchase Orders** ⭐ NEW
8. **Expenses** ⭐ NEW
9. Returns
10. Credit Ledger
11. Daybook
12. Categories
13. Brands
14. **OCR** ⭐ NEW
15. Users
16. Analytics
17. Reports
18. Tools
19. Settings

### Manager Menu:
Similar structure with the same new items.

## 🚀 Step-by-Step Access Instructions

1. **Start the Application:**
   ```bash
   # Frontend
   cd frontend
   npm run dev
   
   # Backend
   cd backend
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Login:**
   - Go to `http://localhost:5173/login`
   - Login with your admin or manager credentials

3. **Navigate to New Pages:**
   - Look at the left sidebar
   - Find the new menu items:
     - 👤 **Customers** (UserCircle icon)
     - 🛍️ **Purchase Orders** (ShoppingBag icon)
     - 💰 **Expenses** (DollarSign icon)
     - 📷 **OCR** (ScanLine icon)
   - Click on any of these to access the page

## 🎨 Visual Guide

The sidebar menu items will appear with:
- **Icon** on the left
- **Label** (page name) on the right
- **Active state** highlighting when you're on that page
- **Hover effects** when you move your mouse over them

## ⚠️ Important Notes

1. **Role-Based Access:**
   - Customers, Purchase Orders, Expenses, and OCR are available to **Admin** and **Manager** roles
   - Employees do NOT have access to these pages

2. **If Pages Don't Appear:**
   - Make sure you're logged in as Admin or Manager
   - Check that the frontend server is running
   - Clear browser cache and refresh
   - Check browser console for any errors

3. **First Time Setup:**
   - Make sure migrations are run: `python manage.py migrate`
   - Ensure backend server is running on port 8000
   - Ensure frontend server is running on port 5173

## 🔍 Troubleshooting

If you can't see the new pages:

1. **Check Browser Console:**
   - Press F12
   - Look for any errors in the Console tab

2. **Verify Routes:**
   - Check `frontend/src/App.jsx` - routes should be added
   - Check `frontend/src/components/DashboardLayout.jsx` - menu items should be added

3. **Restart Servers:**
   ```bash
   # Stop both servers (Ctrl+C)
   # Then restart them
   ```

4. **Check User Role:**
   - Make sure you're logged in as Admin or Manager
   - Employees don't have access to these pages

## 📱 Mobile Access

On mobile devices:
1. Click the **hamburger menu** (☰) icon in the top-left
2. The sidebar will slide in from the left
3. Find and click on the new menu items
4. The sidebar will automatically close after selection

## ✨ Quick Tips

- **Keyboard Shortcut:** You can bookmark the pages for quick access
- **Search:** Use browser search (Ctrl+F) to find menu items quickly
- **Active Indicator:** The current page will be highlighted in blue/purple gradient
- **Icons:** Each page has a unique icon for easy identification

Enjoy using the new features! 🎉






