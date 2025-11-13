import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Users,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Receipt,
  CreditCard,
  FileText,
  TrendingUp,
  AlertCircle,
  Bell,
  Sun,
  Moon,
  BookOpen,
  Tag,
  Award,
  Search,
  RotateCcw,
  Calculator,
  UserCircle,
  ShoppingBag,
  DollarSign,
  ScanLine,
  Warehouse,
  PieChart,
  TrendingDown,
  Sparkles,
} from 'lucide-react';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

const menuItems = {
  admin: [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard/admin' },
    { icon: Package, label: 'Products', path: '/dashboard/admin/products' },
    { icon: ShoppingCart, label: 'Inventory', path: '/dashboard/admin/inventory' },
    { icon: Warehouse, label: 'Advanced Inventory', path: '/dashboard/admin/advanced-inventory' },
    { icon: Receipt, label: 'Billing', path: '/dashboard/admin/billing' },
    { icon: Search, label: 'Invoice Search', path: '/dashboard/admin/invoices' },
    { icon: UserCircle, label: 'Customers', path: '/dashboard/admin/customers' },
    { icon: ShoppingBag, label: 'Purchase Orders', path: '/dashboard/admin/purchase-orders' },
    { icon: DollarSign, label: 'Expenses', path: '/dashboard/admin/expenses' },
    { icon: RotateCcw, label: 'Returns', path: '/dashboard/admin/returns' },
    { icon: CreditCard, label: 'Credit Ledger', path: '/dashboard/admin/credit' },
    { icon: BookOpen, label: 'Daybook', path: '/dashboard/admin/daybook' },
    { icon: Tag, label: 'Categories', path: '/dashboard/admin/categories' },
    { icon: Award, label: 'Brands', path: '/dashboard/admin/brands' },
    { icon: ScanLine, label: 'OCR', path: '/dashboard/admin/ocr' },
    { icon: Users, label: 'Users', path: '/dashboard/admin/users' },
    { icon: BarChart3, label: 'Analytics', path: '/dashboard/admin/analytics' },
    { icon: FileText, label: 'Reports', path: '/dashboard/admin/reports' },
    { icon: TrendingUp, label: 'Forecasting', path: '/dashboard/admin/forecasting' },
    { icon: PieChart, label: 'Advanced Reports', path: '/dashboard/admin/advanced-reports' },
    { icon: Sparkles, label: 'Marketing & AI Ads', path: '/dashboard/admin/marketing' },
    { icon: Calculator, label: 'Tools', path: '/dashboard/admin/tools' },
    { icon: Settings, label: 'Settings', path: '/dashboard/admin/settings' },
  ],
  owner: [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard/owner' },
    { icon: Search, label: 'Invoice Search', path: '/dashboard/owner/invoices' },
    { icon: BarChart3, label: 'Analytics', path: '/dashboard/owner/analytics' },
    { icon: TrendingUp, label: 'Business Insights', path: '/dashboard/owner/insights' },
    { icon: BookOpen, label: 'Daybook', path: '/dashboard/owner/daybook' },
    { icon: FileText, label: 'Reports', path: '/dashboard/owner/reports' },
    { icon: PieChart, label: 'Advanced Reports', path: '/dashboard/owner/advanced-reports' },
    { icon: Sparkles, label: 'Marketing & AI Ads', path: '/dashboard/owner/marketing' },
    { icon: Calculator, label: 'Tools', path: '/dashboard/owner/tools' },
    { icon: Users, label: 'Users', path: '/dashboard/owner/users' },
    { icon: Settings, label: 'Settings', path: '/dashboard/owner/settings' },
  ],
  manager: [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard/manager' },
    { icon: Package, label: 'Products', path: '/dashboard/manager/products' },
    { icon: ShoppingCart, label: 'Inventory', path: '/dashboard/manager/inventory' },
    { icon: Warehouse, label: 'Advanced Inventory', path: '/dashboard/manager/advanced-inventory' },
    { icon: Receipt, label: 'Billing', path: '/dashboard/manager/billing' },
    { icon: Search, label: 'Invoice Search', path: '/dashboard/manager/invoices' },
    { icon: UserCircle, label: 'Customers', path: '/dashboard/manager/customers' },
    { icon: ShoppingBag, label: 'Purchase Orders', path: '/dashboard/manager/purchase-orders' },
    { icon: DollarSign, label: 'Expenses', path: '/dashboard/manager/expenses' },
    { icon: RotateCcw, label: 'Returns', path: '/dashboard/manager/returns' },
    { icon: CreditCard, label: 'Credit Ledger', path: '/dashboard/manager/credit' },
    { icon: BookOpen, label: 'Daybook', path: '/dashboard/manager/daybook' },
    { icon: Tag, label: 'Categories', path: '/dashboard/manager/categories' },
    { icon: Award, label: 'Brands', path: '/dashboard/manager/brands' },
    { icon: ScanLine, label: 'OCR', path: '/dashboard/manager/ocr' },
    { icon: BarChart3, label: 'Reports', path: '/dashboard/manager/reports' },
    { icon: TrendingUp, label: 'Forecasting', path: '/dashboard/manager/forecasting' },
    { icon: PieChart, label: 'Advanced Reports', path: '/dashboard/manager/advanced-reports' },
    { icon: Sparkles, label: 'Marketing & AI Ads', path: '/dashboard/manager/marketing' },
    { icon: Calculator, label: 'Tools', path: '/dashboard/manager/tools' },
    { icon: AlertCircle, label: 'Alerts', path: '/dashboard/manager/alerts' },
  ],
  employee: [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard/employee' },
    { icon: Receipt, label: 'Billing', path: '/dashboard/employee/billing' },
    { icon: Search, label: 'Invoice Search', path: '/dashboard/employee/invoices' },
    { icon: Package, label: 'Products', path: '/dashboard/employee/products' },
    { icon: CreditCard, label: 'Payments', path: '/dashboard/employee/payments' },
  ],
};

function DashboardLayout({ children, title = 'Dashboard' }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, role, logout } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Ensure theme is applied on mount
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  // Close sidebar when clicking outside on mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false); // Close mobile sidebar on desktop
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogout = async () => {
    try {
      await authService.logout();
      logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Error logging out');
      logout();
      navigate('/login');
    }
  };

  const menu = menuItems[role] || menuItems.employee;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gradient-to-br dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Always visible on desktop, animated on mobile */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white dark:bg-gradient-to-b dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 shadow-lg dark:shadow-2xl border-r border-gray-200 dark:border-slate-700 transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-5 border-b border-gray-200 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
                <ShoppingCart className="w-6 h-6 text-white" />
              </div>
              <span className="font-bold text-xl text-gray-900 dark:text-white">POS System</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* User Info */}
          <div className="p-5 border-b border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/50">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center shadow-lg ring-2 ring-primary-500/20">
                <span className="text-white font-bold text-lg">
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                  {user?.first_name && user?.last_name
                    ? `${user.first_name} ${user.last_name}`
                    : user?.username || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-slate-400 capitalize">{role}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-hide">
            {menu.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                    isActive
                      ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-500/30'
                      : 'text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500 dark:text-slate-400 group-hover:text-gray-700 dark:group-hover:text-white'}`} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-200 dark:border-slate-700">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 w-full px-4 py-3 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-700 dark:hover:text-red-300 rounded-xl transition-all duration-200 group"
            >
              <LogOut className="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <header className="bg-white dark:bg-slate-800/80 backdrop-blur-lg shadow-sm dark:shadow-lg sticky top-0 z-30 border-b border-gray-200 dark:border-slate-700 transition-colors duration-300">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-500 dark:text-slate-300 hover:text-gray-700 dark:hover:text-white transition-colors"
              >
                <Menu className="w-6 h-6" />
              </button>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h1>
            </div>
            <div className="flex items-center gap-3">
              {/* Theme Toggle Button */}
              <button
                onClick={toggleTheme}
                className="relative p-2.5 text-gray-500 dark:text-slate-300 hover:text-gray-700 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-all duration-200 group"
                aria-label="Toggle theme"
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: theme === 'dark' ? 0 : 180 }}
                  transition={{ duration: 0.3 }}
                >
                  {theme === 'dark' ? (
                    <Sun className="w-5 h-5" />
                  ) : (
                    <Moon className="w-5 h-5" />
                  )}
                </motion.div>
              </button>
              
              {/* Notifications */}
              <button className="relative p-2.5 text-gray-500 dark:text-slate-300 hover:text-gray-700 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-all duration-200">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white dark:ring-slate-800"></span>
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}

export default DashboardLayout;
