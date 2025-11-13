import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import useAuthStore from './store/authStore';
import AdminDashboard from './pages/dashboards/AdminDashboard';
import OwnerDashboard from './pages/dashboards/OwnerDashboard';
import ManagerDashboard from './pages/dashboards/ManagerDashboard';
import EmployeeDashboard from './pages/dashboards/EmployeeDashboard';
import Products from './pages/Products';
import Billing from './pages/Billing';
import Inventory from './pages/Inventory';
import Analytics from './pages/Analytics';
import CreditLedger from './pages/CreditLedger';
import Returns from './pages/Returns';
import Discounts from './pages/Discounts';
import Users from './pages/Users';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Daybook from './pages/Daybook';
import Categories from './pages/Categories';
import Brands from './pages/Brands';
import InvoiceSearch from './pages/InvoiceSearch';
import Tools from './pages/Tools';
import Customers from './pages/Customers';
import PurchaseOrders from './pages/PurchaseOrders';
import Expenses from './pages/Expenses';
import OCR from './pages/OCR';
import Forecasting from './pages/Forecasting';
import AdvancedReports from './pages/AdvancedReports';
import AdvancedInventory from './pages/AdvancedInventory';
import Marketing from './pages/Marketing';

function App() {
  const { isAuthenticated, role } = useAuthStore();

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to={`/dashboard/${role}`} replace /> : <Login />}
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner"
            element={
              <ProtectedRoute allowedRoles={['owner']}>
                <OwnerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager"
            element={
              <ProtectedRoute allowedRoles={['manager']}>
                <ManagerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/employee"
            element={
              <ProtectedRoute allowedRoles={['employee']}>
                <EmployeeDashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Products Routes */}
          <Route
            path="/dashboard/admin/products"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Products />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/products"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Products />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/employee/products"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <Products />
              </ProtectedRoute>
            }
          />
          
          {/* Billing Routes */}
          <Route
            path="/dashboard/admin/billing"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <Billing />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/billing"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <Billing />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/employee/billing"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <Billing />
              </ProtectedRoute>
            }
          />
          
          {/* Invoice Search Routes */}
          <Route
            path="/dashboard/admin/invoices"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <InvoiceSearch />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/invoices"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <InvoiceSearch />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/employee/invoices"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <InvoiceSearch />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/invoices"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <InvoiceSearch />
              </ProtectedRoute>
            }
          />
          
          {/* Inventory Routes */}
          <Route
            path="/dashboard/admin/inventory"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Inventory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/inventory"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Inventory />
              </ProtectedRoute>
            }
          />
          
          {/* Analytics Routes */}
          <Route
            path="/dashboard/admin/analytics"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner', 'manager']}>
                <Analytics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/analytics"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Analytics />
              </ProtectedRoute>
            }
          />
          
          {/* Credit Ledger Routes */}
          <Route
            path="/dashboard/admin/credit"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <CreditLedger />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/credit"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <CreditLedger />
              </ProtectedRoute>
            }
          />
          
          {/* Returns Routes */}
          <Route
            path="/dashboard/admin/returns"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Returns />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/returns"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Returns />
              </ProtectedRoute>
            }
          />
          
          {/* Discounts Routes */}
          <Route
            path="/dashboard/admin/discounts"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Discounts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/discounts"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Discounts />
              </ProtectedRoute>
            }
          />
          
          {/* Users Routes */}
          <Route
            path="/dashboard/admin/users"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <Users />
              </ProtectedRoute>
            }
          />
          
          {/* Categories Routes */}
          <Route
            path="/dashboard/admin/categories"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Categories />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/categories"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Categories />
              </ProtectedRoute>
            }
          />
          
          {/* Brands Routes */}
          <Route
            path="/dashboard/admin/brands"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Brands />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/brands"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Brands />
              </ProtectedRoute>
            }
          />
          
          {/* Reports Routes */}
          <Route
            path="/dashboard/admin/reports"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner', 'manager']}>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/reports"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/reports"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Reports />
              </ProtectedRoute>
            }
          />
          
          {/* Settings Routes */}
          <Route
            path="/dashboard/admin/settings"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/settings"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Settings />
              </ProtectedRoute>
            }
          />
          
          {/* Tools Routes */}
          <Route
            path="/dashboard/admin/tools"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'owner']}>
                <Tools />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/tools"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Tools />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/tools"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Tools />
              </ProtectedRoute>
            }
          />
          
          {/* Customers Routes */}
          <Route
            path="/dashboard/admin/customers"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <Customers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/customers"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <Customers />
              </ProtectedRoute>
            }
          />
          
          {/* Purchase Orders Routes */}
          <Route
            path="/dashboard/admin/purchase-orders"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <PurchaseOrders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/purchase-orders"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <PurchaseOrders />
              </ProtectedRoute>
            }
          />
          
          {/* Expenses Routes */}
          <Route
            path="/dashboard/admin/expenses"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Expenses />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/expenses"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Expenses />
              </ProtectedRoute>
            }
          />
          
          {/* OCR Routes */}
          <Route
            path="/dashboard/admin/ocr"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <OCR />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/ocr"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'employee']}>
                <OCR />
              </ProtectedRoute>
            }
          />
          
          {/* Forecasting Routes */}
          <Route
            path="/dashboard/admin/forecasting"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Forecasting />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/forecasting"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Forecasting />
              </ProtectedRoute>
            }
          />
          
          {/* Advanced Reports Routes */}
          <Route
            path="/dashboard/admin/advanced-reports"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner', 'manager']}>
                <AdvancedReports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/advanced-reports"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <AdvancedReports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/advanced-reports"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <AdvancedReports />
              </ProtectedRoute>
            }
          />
          
          {/* Marketing Routes */}
          <Route
            path="/dashboard/admin/marketing"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager', 'owner']}>
                <Marketing />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/marketing"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Marketing />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/marketing"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Marketing />
              </ProtectedRoute>
            }
          />
          
          {/* Advanced Inventory Routes */}
          <Route
            path="/dashboard/admin/advanced-inventory"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <AdvancedInventory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/advanced-inventory"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <AdvancedInventory />
              </ProtectedRoute>
            }
          />
          
          {/* Daybook Routes */}
          <Route
            path="/dashboard/admin/daybook"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner', 'manager']}>
                <Daybook />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/owner/daybook"
            element={
              <ProtectedRoute allowedRoles={['admin', 'owner']}>
                <Daybook />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manager/daybook"
            element={
              <ProtectedRoute allowedRoles={['admin', 'manager']}>
                <Daybook />
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate to={`/dashboard/${role}`} replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
