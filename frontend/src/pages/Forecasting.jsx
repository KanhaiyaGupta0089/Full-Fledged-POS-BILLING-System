import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, BarChart3, Download, FileText, RefreshCw, Calculator } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Forecasting() {
  const [forecasts, setForecasts] = useState([]);
  const [demandPatterns, setDemandPatterns] = useState([]);
  const [optimalStockLevels, setOptimalStockLevels] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('forecasts'); // 'forecasts', 'demand', 'optimal'
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generateForm, setGenerateForm] = useState({
    product_id: '',
    warehouse_id: '',
    method: 'moving_average',
    period_days: 30,
    window_size: 7,
    alpha: 0.3,
    period_type: 'monthly'
  });

  useEffect(() => {
    fetchForecasts();
    fetchDemandPatterns();
    fetchOptimalStockLevels();
    fetchProducts();
    fetchWarehouses();
  }, []);

  const fetchForecasts = async () => {
    try {
      const response = await api.get('/forecasting/forecasts/');
      setForecasts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch forecasts:', error);
    }
  };

  const fetchDemandPatterns = async () => {
    try {
      const response = await api.get('/forecasting/demand-patterns/');
      setDemandPatterns(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch demand patterns:', error);
    }
  };

  const fetchOptimalStockLevels = async () => {
    try {
      const response = await api.get('/forecasting/optimal-stock-levels/');
      setOptimalStockLevels(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch optimal stock levels:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/products/');
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const fetchWarehouses = async () => {
    try {
      const response = await api.get('/inventory/warehouses/');
      setWarehouses(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch warehouses:', error);
    }
  };

  const handleGenerateForecast = async (e) => {
    e.preventDefault();
    try {
      toast.loading('Generating forecast...', { id: 'generate-forecast' });
      const response = await api.post('/forecasting/forecasts/generate_forecast/', generateForm);
      toast.success('Forecast generated successfully!', { id: 'generate-forecast' });
      setShowGenerateModal(false);
      fetchForecasts();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate forecast', { id: 'generate-forecast' });
    }
  };

  const handleAnalyzeDemand = async (productId, warehouseId = null) => {
    try {
      toast.loading('Analyzing demand pattern...', { id: 'analyze-demand' });
      await api.post('/forecasting/demand-patterns/analyze_demand/', {
        product_id: productId,
        warehouse_id: warehouseId,
        period_days: 90
      });
      toast.success('Demand pattern analyzed!', { id: 'analyze-demand' });
      fetchDemandPatterns();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze demand', { id: 'analyze-demand' });
    }
  };

  const handleCalculateOptimal = async (productId, warehouseId) => {
    try {
      toast.loading('Calculating optimal stock levels...', { id: 'calculate-optimal' });
      await api.post('/forecasting/optimal-stock-levels/calculate_optimal/', {
        product_id: productId,
        warehouse_id: warehouseId
      });
      toast.success('Optimal stock levels calculated!', { id: 'calculate-optimal' });
      fetchOptimalStockLevels();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to calculate optimal levels', { id: 'calculate-optimal' });
    }
  };

  const exportToPDF = () => {
    try {
      toast.loading('Generating PDF...', { id: 'pdf-export' });
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text('Sales Forecasting Report', 14, 15);
      doc.setFontSize(11);
      doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 22);
      
      const tableData = forecasts.map(f => [
        f.product_name || '',
        f.warehouse_name || 'All',
        f.forecast_method || '',
        f.predicted_quantity || 0,
        `₹${parseFloat(f.predicted_revenue || 0).toFixed(2)}`,
        `${f.confidence_level || 0}%`,
        f.forecast_date ? new Date(f.forecast_date).toLocaleDateString() : '-'
      ]);

      autoTable(doc, {
        head: [['Product', 'Warehouse', 'Method', 'Predicted Qty', 'Predicted Revenue', 'Confidence', 'Date']],
        body: tableData,
        startY: 28,
        styles: { fontSize: 9 },
        headStyles: { fillColor: [66, 139, 202] },
      });

      doc.save(`forecasting_${new Date().toISOString().split('T')[0]}.pdf`);
      toast.success('PDF exported successfully!', { id: 'pdf-export' });
    } catch (error) {
      console.error('PDF export error:', error);
      toast.error('Failed to export PDF', { id: 'pdf-export' });
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Forecasting">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Sales Forecasting & Demand Planning">
      <div className="p-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setSelectedTab('forecasts')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'forecasts'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Sales Forecasts
          </button>
          <button
            onClick={() => setSelectedTab('demand')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'demand'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            Demand Patterns
          </button>
          <button
            onClick={() => setSelectedTab('optimal')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'optimal'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Calculator className="w-4 h-4 inline mr-2" />
            Optimal Stock Levels
          </button>
        </div>

        {/* Sales Forecasts Tab */}
        {selectedTab === 'forecasts' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Sales Forecasts</h2>
              <div className="flex gap-2">
                <button onClick={exportToPDF} className="btn-secondary">
                  <FileText className="w-4 h-4 mr-2" />
                  Export PDF
                </button>
                <button onClick={() => setShowGenerateModal(true)} className="btn-primary">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Generate Forecast
                </button>
              </div>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Product</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Method</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Predicted Qty</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Predicted Revenue</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Confidence</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {forecasts.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                          No forecasts found. Generate a forecast to get started.
                        </td>
                      </tr>
                    ) : (
                      forecasts.map((forecast) => (
                        <tr key={forecast.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {forecast.product_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {forecast.warehouse_name || 'All Warehouses'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {forecast.forecast_method || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {forecast.predicted_quantity || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            ₹{parseFloat(forecast.predicted_revenue || 0).toLocaleString('en-IN')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              forecast.confidence_level >= 80 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              forecast.confidence_level >= 60 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                              'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            }`}>
                              {forecast.confidence_level || 0}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {forecast.forecast_date ? new Date(forecast.forecast_date).toLocaleDateString() : '-'}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Demand Patterns Tab */}
        {selectedTab === 'demand' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Demand Patterns</h2>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Product</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Trend</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Avg Daily</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Avg Weekly</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Avg Monthly</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Reorder Point</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {demandPatterns.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                          No demand patterns found. Analyze demand for products to get started.
                        </td>
                      </tr>
                    ) : (
                      demandPatterns.map((pattern) => (
                        <tr key={pattern.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {pattern.product_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              {pattern.trend === 'increasing' && <TrendingUp className="w-4 h-4 text-green-500" />}
                              {pattern.trend === 'decreasing' && <TrendingDown className="w-4 h-4 text-red-500" />}
                              {pattern.trend === 'stable' && <Minus className="w-4 h-4 text-gray-500" />}
                              <span className="text-sm text-gray-900 dark:text-white capitalize">{pattern.trend || '-'}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {parseFloat(pattern.average_daily_sales || 0).toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {parseFloat(pattern.average_weekly_sales || 0).toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {parseFloat(pattern.average_monthly_sales || 0).toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {pattern.recommended_reorder_point || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => handleAnalyzeDemand(pattern.product, pattern.warehouse)}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                              title="Re-analyze"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Optimal Stock Levels Tab */}
        {selectedTab === 'optimal' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Optimal Stock Levels</h2>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Product</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Current Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Min Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Max Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Reorder Point</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {optimalStockLevels.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                          No optimal stock levels found. Calculate optimal levels for products to get started.
                        </td>
                      </tr>
                    ) : (
                      optimalStockLevels.map((level) => (
                        <tr key={level.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {level.product_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {level.warehouse_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {level.current_stock || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {level.optimal_min_stock || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {level.optimal_max_stock || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {level.optimal_reorder_point || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              level.stock_status === 'optimal' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              level.stock_status === 'low' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                              level.stock_status === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                              'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                            }`}>
                              {level.stock_status || 'optimal'}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Generate Forecast Modal */}
        {showGenerateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Generate Sales Forecast</h2>
                <form onSubmit={handleGenerateForecast} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Product *</label>
                      <select
                        required
                        value={generateForm.product_id}
                        onChange={(e) => setGenerateForm({ ...generateForm, product_id: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">Select Product</option>
                        {products.map(p => (
                          <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Warehouse</label>
                      <select
                        value={generateForm.warehouse_id}
                        onChange={(e) => setGenerateForm({ ...generateForm, warehouse_id: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">All Warehouses</option>
                        {warehouses.map(w => (
                          <option key={w.id} value={w.id}>{w.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Forecast Method *</label>
                      <select
                        required
                        value={generateForm.method}
                        onChange={(e) => setGenerateForm({ ...generateForm, method: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="moving_average">Moving Average</option>
                        <option value="exponential_smoothing">Exponential Smoothing</option>
                        <option value="seasonal_decomposition">Seasonal Decomposition</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Period Type</label>
                      <select
                        value={generateForm.period_type}
                        onChange={(e) => setGenerateForm({ ...generateForm, period_type: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Period Days</label>
                      <input
                        type="number"
                        min="7"
                        max="365"
                        value={generateForm.period_days}
                        onChange={(e) => setGenerateForm({ ...generateForm, period_days: parseInt(e.target.value) })}
                        className="input-field w-full"
                      />
                    </div>
                    {generateForm.method === 'moving_average' && (
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Window Size</label>
                        <input
                          type="number"
                          min="3"
                          max="30"
                          value={generateForm.window_size}
                          onChange={(e) => setGenerateForm({ ...generateForm, window_size: parseInt(e.target.value) })}
                          className="input-field w-full"
                        />
                      </div>
                    )}
                    {generateForm.method === 'exponential_smoothing' && (
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Alpha (0-1)</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="1"
                          value={generateForm.alpha}
                          onChange={(e) => setGenerateForm({ ...generateForm, alpha: parseFloat(e.target.value) })}
                          className="input-field w-full"
                        />
                      </div>
                    )}
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowGenerateModal(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      Generate Forecast
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Forecasting;




