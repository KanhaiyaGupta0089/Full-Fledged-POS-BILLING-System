import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../services/api';
import {
  DollarSign,
  ShoppingCart,
  Package,
  TrendingUp,
  Users,
  AlertCircle,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

function AdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_sales: 0,
    total_orders: 0,
    total_products: 0,
    low_stock: 0,
    growth: 0,
  });
  const [salesData, setSalesData] = useState([]);
  const [topProducts, setTopProducts] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/admin/');
      setStats(response.data);
      
      // Use real sales data from API
      if (response.data.sales_data && response.data.sales_data.length > 0) {
        setSalesData(response.data.sales_data);
      } else {
        // Fallback: generate empty data structure
        const last7Days = [];
        for (let i = 6; i >= 0; i--) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
          last7Days.push({
            name: dayName,
            sales: 0,
            orders: 0,
          });
        }
        setSalesData(last7Days);
      }
      
      // Use real top products from API
      if (response.data.top_products && response.data.top_products.length > 0) {
        setTopProducts(response.data.top_products.map(p => ({
          name: p.product__name || 'Unknown',
          sales: parseFloat(p.total_revenue || 0),
          quantity: p.total_quantity || 0,
        })));
      } else {
        // Fallback: fetch from products endpoint
        try {
          const productsResponse = await api.get('/products/products/?ordering=-selling_price&limit=5');
          setTopProducts((productsResponse.data.results || productsResponse.data).slice(0, 5).map(p => ({
            name: p.name,
            sales: parseFloat(p.selling_price || 0) * (p.current_stock || 0),
            quantity: p.current_stock || 0,
          })));
        } catch (err) {
          setTopProducts([]);
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Sales (This Month)',
      value: `₹${stats.total_sales?.toLocaleString() || 0}`,
      change: `+${stats.growth || 0}%`,
      icon: DollarSign,
      gradient: 'from-green-500 to-emerald-600',
      bgGradient: 'from-green-500/10 to-emerald-600/10',
      subtitle: 'Paid & Partial invoices only',
    },
    {
      title: 'Total Orders',
      value: stats.total_orders || 0,
      change: '+12%',
      icon: ShoppingCart,
      gradient: 'from-blue-500 to-cyan-600',
      bgGradient: 'from-blue-500/10 to-cyan-600/10',
    },
    {
      title: 'Total Products',
      value: stats.total_products || 0,
      change: '+5',
      icon: Package,
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-500/10 to-pink-600/10',
    },
    {
      title: 'Low Stock Alerts',
      value: stats.low_stock || 0,
      change: 'Action needed',
      icon: AlertCircle,
      gradient: 'from-orange-500 to-red-600',
      bgGradient: 'from-orange-500/10 to-red-600/10',
    },
  ];

  return (
    <DashboardLayout title="Admin Dashboard">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {statCards.map((card, index) => {
              const Icon = card.icon;
              return (
                <motion.div
                  key={card.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`card bg-white dark:bg-gradient-to-br dark:from-slate-800 dark:to-slate-900 border-gray-100 dark:border-slate-700 hover:border-gray-200 dark:hover:border-slate-600 transition-all duration-300 hover:scale-105 hover:shadow-xl dark:hover:shadow-2xl`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-slate-400 mb-2">{card.title}</p>
                      {card.subtitle && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{card.subtitle}</p>
                      )}
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{card.value}</p>
                      <p className="text-xs text-green-600 dark:text-green-400 font-medium">{card.change}</p>
                    </div>
                    <div className={`bg-gradient-to-br ${card.gradient} p-4 rounded-xl shadow-lg`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sales Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card bg-white dark:bg-gradient-to-br dark:from-slate-800 dark:to-slate-900 border-gray-100 dark:border-slate-700"
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Sales Overview</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #475569',
                      borderRadius: '8px',
                      color: '#f1f5f9'
                    }} 
                  />
                  <Bar dataKey="sales" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Orders Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card"
            >
              <h2 className="text-xl font-bold text-white mb-6">Orders Trend</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #475569',
                      borderRadius: '8px',
                      color: '#f1f5f9'
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="orders" 
                    stroke="#8b5cf6" 
                    strokeWidth={3}
                    dot={{ fill: '#8b5cf6', r: 5 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </motion.div>
          </div>

          {/* Top Products */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <h2 className="text-xl font-bold text-white mb-6">Top Selling Products</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-slate-700">
                    <th className="text-left py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Product</th>
                    <th className="text-right py-4 px-4 text-sm font-semibold text-slate-300">Sales</th>
                    <th className="text-right py-4 px-4 text-sm font-semibold text-slate-300">Quantity</th>
                  </tr>
                </thead>
                <tbody>
                  {topProducts.length === 0 ? (
                    <tr>
                      <td colSpan="3" className="text-center py-4 text-gray-500 dark:text-gray-400">
                        No products found
                      </td>
                    </tr>
                  ) : (
                    topProducts.map((product, index) => (
                    <tr key={index} className="border-b border-gray-200 dark:border-slate-700/50 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="py-4 px-4 text-sm text-gray-900 dark:text-white font-medium">{product.name}</td>
                      <td className="py-4 px-4 text-sm text-gray-900 dark:text-white text-right font-semibold">
                        ₹{product.sales.toLocaleString()}
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-900 dark:text-white text-right">{product.quantity}</td>
                    </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default AdminDashboard;

