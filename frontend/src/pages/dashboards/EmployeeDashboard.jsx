import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../services/api';
import {
  DollarSign,
  ShoppingCart,
  Package,
  Clock,
  LogIn,
  LogOut,
} from 'lucide-react';

function EmployeeDashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    bills: 0,
    revenue: 0,
    items: 0,
    attendance: null,
    recent_bills: [],
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/employee/');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Today\'s Bills',
      value: stats.bills || 0,
      change: '+12%',
      icon: ShoppingCart,
      gradient: 'from-blue-500 to-cyan-600',
      bgGradient: 'from-blue-500/10 to-cyan-600/10',
    },
    {
      title: 'Today\'s Revenue',
      value: `₹${(stats.revenue || 0).toLocaleString()}`,
      change: '+8%',
      icon: DollarSign,
      gradient: 'from-green-500 to-emerald-600',
      bgGradient: 'from-green-500/10 to-emerald-600/10',
    },
    {
      title: 'Items Sold',
      value: stats.items || 0,
      change: '+5',
      icon: Package,
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-500/10 to-pink-600/10',
    },
    {
      title: 'Login Duration',
      value: stats.attendance?.total_duration || '0h 0m',
      change: stats.attendance?.is_active ? 'Active' : 'Inactive',
      icon: Clock,
      gradient: 'from-orange-500 to-red-600',
      bgGradient: 'from-orange-500/10 to-red-600/10',
    },
  ];

  return (
    <DashboardLayout title="Employee Dashboard">
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

          {/* Attendance Info */}
          {stats.attendance && (
            <div className="card p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Today's Attendance</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Login Time</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <LogIn className="w-4 h-4 text-green-500" />
                    {stats.attendance.login_time || 'Not logged in'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Logout Time</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <LogOut className="w-4 h-4 text-red-500" />
                    {stats.attendance.logout_time || 'Active'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Duration</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Clock className="w-4 h-4 text-blue-500" />
                    {stats.attendance.total_duration}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                  <p className={`text-lg font-semibold flex items-center gap-2 ${
                    stats.attendance.is_active ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    <span className={`w-3 h-3 rounded-full ${
                      stats.attendance.is_active ? 'bg-green-500' : 'bg-gray-400'
                    }`}></span>
                    {stats.attendance.is_active ? 'Active' : 'Inactive'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Recent Bills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <h2 className="text-xl font-bold text-white mb-6">Recent Bills</h2>
            {stats.recent_bills && stats.recent_bills.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-slate-700">
                      <th className="text-left py-4 px-4 text-sm font-semibold text-slate-300">Customer</th>
                      <th className="text-right py-4 px-4 text-sm font-semibold text-slate-300">Amount</th>
                      <th className="text-right py-4 px-4 text-sm font-semibold text-slate-300">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_bills.map((bill) => (
                      <tr key={bill.id} className="border-b border-gray-200 dark:border-slate-700/50 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="py-4 px-4 text-sm text-white font-medium">{bill.customer}</td>
                        <td className="py-4 px-4 text-sm text-white text-right font-semibold">
                          ₹{bill.amount.toLocaleString()}
                        </td>
                        <td className="py-4 px-4 text-sm text-slate-300 text-right">{bill.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8">No bills today</p>
            )}
          </motion.div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default EmployeeDashboard;
