import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Package, AlertCircle, DollarSign, ShoppingCart, Download, FileText } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

function Analytics() {
  const [salesInsights, setSalesInsights] = useState(null);
  const [profitAnalysis, setProfitAnalysis] = useState(null);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [inventoryHealth, setInventoryHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [partialLoading, setPartialLoading] = useState({
    sales: false,
    profit: false,
    trending: false,
    lowStock: false,
    health: false,
  });
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchAllData();
  }, [days]);

  const fetchAllData = async () => {
    setLoading(true);
    // Fetch critical data first (stats cards)
    try {
      // Fetch stats cards data first (fast queries)
      const [sales, profit] = await Promise.all([
        api.get(`/analytics/sales_insights/?days=${days}`),
        api.get(`/analytics/profit_analysis/?days=${days}`),
      ]);

      setSalesInsights(sales.data);
      setProfitAnalysis(profit.data);
      setPartialLoading(prev => ({ ...prev, sales: true, profit: true }));
      setLoading(false); // Show page with initial data

      // Fetch remaining data in background
      Promise.all([
        api.get(`/analytics/trending_products/?days=${days}&limit=10`),
        api.get('/analytics/low_stock_alerts/'),
        api.get('/analytics/inventory_health/'),
      ]).then(([trending, lowStock, health]) => {
        setTrendingProducts(trending.data);
        setLowStockAlerts(lowStock.data);
        setInventoryHealth(health.data);
        setPartialLoading(prev => ({
          ...prev,
          trending: true,
          lowStock: true,
          health: true,
        }));
      }).catch(error => {
        console.error('Failed to fetch some analytics data:', error);
        toast.error('Some analytics data failed to load');
      });
    } catch (error) {
      toast.error('Failed to fetch analytics data');
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text('Analytics Report', 14, 22);
    doc.setFontSize(11);
    
    let yPos = 30;
    
    // Summary Stats
    doc.setFontSize(14);
    doc.text('Summary Statistics', 14, yPos);
    yPos += 10;
    
    doc.setFontSize(11);
    doc.text(`Total Sales: ₹${salesInsights?.total_sales?.toLocaleString() || '0'}`, 14, yPos);
    yPos += 7;
    doc.text(`Total Profit: ₹${profitAnalysis?.total_profit?.toLocaleString() || '0'}`, 14, yPos);
    yPos += 7;
    doc.text(`Total Invoices: ${salesInsights?.total_invoices || '0'}`, 14, yPos);
    yPos += 7;
    doc.text(`Profit Margin: ${profitAnalysis?.profit_margin?.toFixed(2) || '0'}%`, 14, yPos);
    yPos += 10;
    
    // Trending Products
    if (trendingProducts.length > 0) {
      doc.setFontSize(14);
      doc.text('Trending Products', 14, yPos);
      yPos += 10;
      
      const tableData = trendingProducts.map(p => [
        p.product__name || 'N/A',
        p.product__sku || 'N/A',
        p.total_quantity || 0,
        `₹${parseFloat(p.total_revenue || 0).toFixed(2)}`,
        p.order_count || 0,
      ]);
      
      autoTable(doc, {
        head: [['Product', 'SKU', 'Quantity', 'Revenue', 'Orders']],
        body: tableData,
        startY: yPos,
      });
      yPos = doc.lastAutoTable.finalY + 10;
    }
    
    // Low Stock Alerts
    if (lowStockAlerts.length > 0) {
      doc.setFontSize(14);
      doc.text('Low Stock Alerts', 14, yPos);
      yPos += 10;
      
      const tableData = lowStockAlerts.slice(0, 20).map(p => [
        p.name || 'N/A',
        p.sku || 'N/A',
        p.current_stock || 0,
        p.min_stock_level || 0,
      ]);
      
      autoTable(doc, {
        head: [['Product', 'SKU', 'Current Stock', 'Min Stock']],
        body: tableData,
        startY: yPos,
      });
    }
    
    doc.save(`analytics_report_${days}_days.pdf`);
    toast.success('PDF exported successfully');
  };

  const exportToExcel = () => {
    let csvContent = [];
    
    // Summary
    csvContent.push('Analytics Report');
    csvContent.push(`Period: Last ${days} days`);
    csvContent.push('');
    csvContent.push('Summary Statistics');
    csvContent.push(`Total Sales,₹${salesInsights?.total_sales || '0'}`);
    csvContent.push(`Total Profit,₹${profitAnalysis?.total_profit || '0'}`);
    csvContent.push(`Total Invoices,${salesInsights?.total_invoices || '0'}`);
    csvContent.push(`Profit Margin,${profitAnalysis?.profit_margin?.toFixed(2) || '0'}%`);
    csvContent.push('');
    
    // Trending Products
    csvContent.push('Trending Products');
    csvContent.push('Product,SKU,Quantity Sold,Revenue,Orders');
    trendingProducts.forEach(p => {
      csvContent.push([
        p.product__name || 'N/A',
        p.product__sku || 'N/A',
        p.total_quantity || 0,
        parseFloat(p.total_revenue || 0).toFixed(2),
        p.order_count || 0,
      ].join(','));
    });
    csvContent.push('');
    
    // Low Stock
    csvContent.push('Low Stock Alerts');
    csvContent.push('Product,SKU,Current Stock,Min Stock');
    lowStockAlerts.forEach(p => {
      csvContent.push([
        p.name || 'N/A',
        p.sku || 'N/A',
        p.current_stock || 0,
        p.min_stock_level || 0,
      ].join(','));
    });
    
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `analytics_report_${days}_days.csv`;
    link.click();
    toast.success('Excel exported successfully');
  };

  if (loading) {
    return (
      <DashboardLayout title="Analytics">
        <div className="p-6">
          <div className="text-center py-12">Loading analytics...</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Analytics">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics & Insights</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Showing data for paid and partially paid invoices only
            </p>
          </div>
          <div className="flex gap-3 items-center">
            <select
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
              className="input-field"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
            <button
              onClick={exportToPDF}
              className="btn-secondary flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Export PDF
            </button>
            <button
              onClick={exportToExcel}
              className="btn-secondary flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export Excel
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Sales</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  ₹{salesInsights?.total_sales?.toLocaleString() || '0'}
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-green-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Profit</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  ₹{profitAnalysis?.total_profit?.toLocaleString() || '0'}
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-blue-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Invoices</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  {salesInsights?.total_invoices || '0'}
                </p>
              </div>
              <ShoppingCart className="w-12 h-12 text-purple-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Low Stock Items</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  {lowStockAlerts?.length || '0'}
                </p>
              </div>
              <AlertCircle className="w-12 h-12 text-yellow-500" />
            </div>
          </motion.div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Sales Chart */}
          <div className="card p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Daily Sales</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={salesInsights?.daily_sales || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="created_at__date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="total" stroke="#0088FE" name="Sales (₹)" />
                <Line type="monotone" dataKey="count" stroke="#00C49F" name="Invoices" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Category Sales Chart */}
          <div className="card p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Sales by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={salesInsights?.category_sales || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="product__category__name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="total" fill="#0088FE" name="Revenue (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Profit Margin */}
          <div className="card p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Profit Analysis</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Profit Margin:</span>
                <span className="text-2xl font-bold text-green-600">
                  {profitAnalysis?.profit_margin?.toFixed(2) || '0'}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Total Revenue:</span>
                <span className="text-xl font-semibold text-gray-900 dark:text-white">
                  ₹{profitAnalysis?.total_revenue?.toLocaleString() || '0'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Total Cost:</span>
                <span className="text-xl font-semibold text-gray-900 dark:text-white">
                  ₹{profitAnalysis?.total_cost?.toLocaleString() || '0'}
                </span>
              </div>
            </div>
          </div>

          {/* Inventory Health */}
          <div className="card p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Inventory Health</h3>
            {!partialLoading.health ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-gray-600 dark:text-gray-400">Loading inventory health...</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'In Stock', value: inventoryHealth?.in_stock || 0 },
                      { name: 'Low Stock', value: inventoryHealth?.low_stock || 0 },
                      { name: 'Out of Stock', value: inventoryHealth?.out_of_stock || 0 },
                      { name: 'Overstock', value: inventoryHealth?.overstock || 0 },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[0, 1, 2, 3].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Trending Products */}
        <div className="card p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Trending Products</h3>
          {!partialLoading.trending ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Loading trending products...</p>
            </div>
          ) : trendingProducts.length === 0 ? (
            <p className="text-center py-8 text-gray-600 dark:text-gray-400">No trending products found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Product</th>
                    <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">SKU</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Quantity Sold</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Revenue</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Orders</th>
                  </tr>
                </thead>
                <tbody>
                  {trendingProducts.map((product, index) => (
                    <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{product.product__name}</td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{product.product__sku}</td>
                      <td className="py-3 px-4 text-right text-gray-900 dark:text-white">{product.total_quantity}</td>
                      <td className="py-3 px-4 text-right text-green-600">₹{parseFloat(product.total_revenue || 0).toFixed(2)}</td>
                      <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">{product.order_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Low Stock Alerts */}
        {!partialLoading.lowStock ? (
          <div className="card p-6">
            <h3 className="text-xl font-bold mb-4 text-yellow-600 flex items-center gap-2">
              <AlertCircle className="w-6 h-6" />
              Low Stock Alerts
            </h3>
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Loading low stock alerts...</p>
            </div>
          </div>
        ) : lowStockAlerts.length > 0 ? (
          <div className="card p-6">
            <h3 className="text-xl font-bold mb-4 text-yellow-600 flex items-center gap-2">
              <AlertCircle className="w-6 h-6" />
              Low Stock Alerts
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {lowStockAlerts.slice(0, 6).map((product) => (
                <div
                  key={product.id}
                  className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800"
                >
                  <h4 className="font-semibold text-gray-900 dark:text-white">{product.name}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">SKU: {product.sku}</p>
                  <p className="text-sm mt-2">
                    <span className="text-yellow-600 font-semibold">Current: {product.current_stock}</span>
                    {' / '}
                    <span className="text-gray-600 dark:text-gray-400">Min: {product.min_stock_level}</span>
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </DashboardLayout>
  );
}

export default Analytics;

