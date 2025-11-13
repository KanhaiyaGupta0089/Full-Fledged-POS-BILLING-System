import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../../components/DashboardLayout';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  PieChart,
  BarChart3,
} from 'lucide-react';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const mockData = {
  stats: {
    totalRevenue: 450000,
    profit: 125000,
    profitMargin: 27.8,
    growth: 18.5,
  },
  categoryData: [
    { name: 'Electronics', value: 35, color: '#0ea5e9' },
    { name: 'Clothing', value: 25, color: '#8b5cf6' },
    { name: 'Food', value: 20, color: '#10b981' },
    { name: 'Other', value: 20, color: '#f59e0b' },
  ],
  monthlyRevenue: [
    { month: 'Jan', revenue: 120000 },
    { month: 'Feb', revenue: 135000 },
    { month: 'Mar', revenue: 145000 },
    { month: 'Apr', revenue: 150000 },
    { month: 'May', revenue: 165000 },
    { month: 'Jun', revenue: 180000 },
  ],
};

function OwnerDashboard() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setLoading(false), 500);
  }, []);

  return (
    <DashboardLayout title="Owner Dashboard">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ₹{mockData.stats.totalRevenue.toLocaleString()}
                  </p>
                  <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    +{mockData.stats.growth}% from last month
                  </p>
                </div>
                <div className="bg-green-500 p-3 rounded-lg">
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Profit</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ₹{mockData.stats.profit.toLocaleString()}
                  </p>
                  <p className="text-xs text-green-600 mt-1">This month</p>
                </div>
                <div className="bg-blue-500 p-3 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Profit Margin</p>
                  <p className="text-2xl font-bold text-gray-900">{mockData.stats.profitMargin}%</p>
                  <p className="text-xs text-green-600 mt-1">Healthy</p>
                </div>
                <div className="bg-purple-500 p-3 rounded-lg">
                  <PieChart className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Growth Rate</p>
                  <p className="text-2xl font-bold text-gray-900">+{mockData.stats.growth}%</p>
                  <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    Positive trend
                  </p>
                </div>
                <div className="bg-orange-500 p-3 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue by Category */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card"
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Category</h2>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={mockData.categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {mockData.categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Monthly Revenue Trend */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card"
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Monthly Revenue Trend</h2>
              <div className="space-y-3">
                {mockData.monthlyRevenue.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{item.month}</span>
                    <div className="flex-1 mx-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full"
                          style={{
                            width: `${(item.revenue / mockData.monthlyRevenue[mockData.monthlyRevenue.length - 1].revenue) * 100}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      ₹{item.revenue.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Business Insights */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Business Insights</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Strong Growth</p>
                  <p className="text-sm text-gray-600">
                    Revenue has increased by 18.5% compared to last month
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <PieChart className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Category Performance</p>
                  <p className="text-sm text-gray-600">
                    Electronics category is leading with 35% of total revenue
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
                <BarChart3 className="w-5 h-5 text-orange-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Profitability</p>
                  <p className="text-sm text-gray-600">
                    Profit margin of 27.8% indicates healthy business operations
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default OwnerDashboard;

