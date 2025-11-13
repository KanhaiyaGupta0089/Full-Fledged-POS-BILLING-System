import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Package, AlertCircle, TrendingUp, TrendingDown, Plus, Edit, Filter, Download, FileText, FileSpreadsheet, Warehouse, Tag, Award, ChevronLeft, ChevronRight } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import AnimatedNumber from '../components/AnimatedNumber';

function Inventory() {
  const [stocks, setStocks] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedStock, setSelectedStock] = useState(null);
  const [adjustmentData, setAdjustmentData] = useState({
    product_id: '',
    warehouse_id: '',
    quantity: '',
    notes: '',
  });
  const [filterWarehouse, setFilterWarehouse] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [showBrandModal, setShowBrandModal] = useState(false);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [categoryForm, setCategoryForm] = useState({ name: '', description: '' });
  const [brandForm, setBrandForm] = useState({ name: '', description: '' });
  const [transactions, setTransactions] = useState([]);
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'grid'
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(20);
  const [summaryStats, setSummaryStats] = useState({
    totalProducts: 0,
    totalStockItems: 0,
    lowStockItems: 0,
    totalTransactions: 0,
  });

  useEffect(() => {
    fetchWarehouses();
    fetchProducts();
    fetchCategories();
    fetchBrands();
    fetchTransactions();
    fetchSummaryStats();
    ensureDefaultWarehouse();
  }, []);

  useEffect(() => {
    fetchStocks();
  }, [currentPage, filterWarehouse, lowStockOnly]);

  const fetchTransactions = async () => {
    try {
      const response = await api.get('/inventory/transactions/');
      setTransactions(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch transactions');
    }
  };

  const fetchSummaryStats = async () => {
    try {
      // Use optimized single endpoint for all stats
      const response = await api.get('/inventory/stocks/summary_stats/');
      setSummaryStats({
        totalProducts: response.data.total_products || 0,
        totalStockItems: response.data.total_stock_items || 0,
        lowStockItems: response.data.low_stock_items || 0,
        totalTransactions: response.data.total_transactions || 0,
      });
    } catch (error) {
      console.error('Failed to fetch summary stats:', error);
      // Fallback to counting from current data
      setSummaryStats({
        totalProducts: products.length,
        totalStockItems: stocks.length,
        lowStockItems: stocks.filter(s => s.is_low_stock).length,
        totalTransactions: transactions.length,
      });
    }
  };

  const ensureDefaultWarehouse = async () => {
    try {
      const response = await api.get('/inventory/warehouses/');
      const warehouses = response.data.results || response.data;
      if (warehouses.length === 0) {
        // Create default warehouse
        await api.post('/inventory/warehouses/', {
          name: 'Main Warehouse',
          address: 'Default Location',
          is_active: true,
        });
        toast.success('Default warehouse created');
        fetchWarehouses();
      }
    } catch (error) {
      console.error('Error ensuring default warehouse:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/products/categories/');
      setCategories(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch categories');
    }
  };

  const fetchBrands = async () => {
    try {
      const response = await api.get('/products/brands/');
      setBrands(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch brands');
    }
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/products/categories/', categoryForm);
      toast.success('Category created successfully');
      setShowCategoryModal(false);
      setCategoryForm({ name: '', description: '' });
      fetchCategories();
    } catch (error) {
      toast.error('Failed to create category');
    }
  };

  const handleBrandSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/products/brands/', brandForm);
      toast.success('Brand created successfully');
      setShowBrandModal(false);
      setBrandForm({ name: '', description: '' });
      fetchBrands();
    } catch (error) {
      toast.error('Failed to create brand');
    }
  };

  const exportToPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text('Inventory Report', 14, 22);
    doc.setFontSize(11);
    
    const tableData = filteredStocks.map(stock => [
      stock.product?.name || 'N/A',
      stock.warehouse?.name || 'N/A',
      stock.quantity.toString(),
      stock.min_quantity.toString(),
      stock.max_quantity.toString(),
      stock.is_low_stock ? 'Yes' : 'No',
    ]);
    
    doc.autoTable({
      head: [['Product', 'Warehouse', 'Quantity', 'Min', 'Max', 'Low Stock']],
      body: tableData,
      startY: 30,
    });
    
    doc.save('inventory_report.pdf');
    toast.success('PDF exported successfully');
  };

  const exportToExcel = () => {
    const csvContent = [
      ['Product', 'Warehouse', 'Quantity', 'Min Quantity', 'Max Quantity', 'Low Stock'].join(','),
      ...filteredStocks.map(stock => [
        stock.product?.name || 'N/A',
        stock.warehouse?.name || 'N/A',
        stock.quantity,
        stock.min_quantity,
        stock.max_quantity,
        stock.is_low_stock ? 'Yes' : 'No',
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'inventory_report.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Excel file exported successfully');
  };

  const fetchStocks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
      });
      
      // Add filters if applied
      if (filterWarehouse) {
        params.append('warehouse', filterWarehouse);
      }
      
      // Add low stock filter - send to backend for server-side filtering
      if (lowStockOnly) {
        params.append('low_stock_only', 'true');
      }
      
      const response = await api.get(`/inventory/stocks/?${params.toString()}`);
      
      // Debug: Log response to check for errors
      if (!response.data) {
        console.error('Invalid response from API:', response);
        throw new Error('Invalid response from API');
      }
      
      const stocksData = response.data.results || response.data;
      
      // Update is_low_stock based on product's current_stock if needed
      let updatedStocks = stocksData.map(stock => {
        // If stock doesn't have is_low_stock or it's false, check product level
        if (stock.product) {
          const productMinStock = stock.product.min_stock_level || 0;
          const productCurrentStock = stock.product.current_stock || 0;
          const stockQuantity = stock.quantity || 0;
          
          // Use product's current_stock if stock quantity is 0 or doesn't match
          const effectiveQuantity = stockQuantity > 0 ? stockQuantity : productCurrentStock;
          const effectiveMinStock = stock.min_quantity > 0 ? stock.min_quantity : productMinStock;
          
          // Mark as low stock if quantity is less than or equal to min
          if (effectiveMinStock > 0 && effectiveQuantity <= effectiveMinStock) {
            return { ...stock, is_low_stock: true };
          }
        }
        return stock;
      });
      
      setStocks(updatedStocks);
      
      // Handle paginated response
      if (response.data.results) {
        const total = response.data.count || 0;
        setTotalCount(total);
        setTotalPages(Math.ceil(total / pageSize));
      } else {
        // Non-paginated response (fallback)
        setTotalCount(updatedStocks.length);
        setTotalPages(1);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stocks:', error);
      console.error('Error details:', error.response?.data || error.message);
      toast.error(error.response?.data?.detail || error.message || 'Failed to fetch stocks');
      setLoading(false);
      // Set empty data to prevent infinite loading
      setStocks([]);
      setTotalCount(0);
      setTotalPages(1);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const fetchWarehouses = async () => {
    try {
      const response = await api.get('/inventory/warehouses/');
      setWarehouses(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch warehouses');
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/products/');
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch products');
    }
  };

  const handleAdjust = async (e) => {
    e.preventDefault();
    try {
      await api.post('/inventory/transactions/adjust/', adjustmentData);
      toast.success('Inventory adjusted successfully');
      setShowAdjustModal(false);
      setSelectedStock(null);
      setAdjustmentData({ product_id: '', warehouse_id: '', quantity: '', notes: '' });
      fetchStocks();
      fetchTransactions();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to adjust inventory');
    }
  };

  const openAdjustModal = (stock = null) => {
    if (stock) {
      setSelectedStock(stock);
      setAdjustmentData({
        product_id: stock.product.id,
        warehouse_id: stock.warehouse.id,
        quantity: '',
        notes: '',
      });
    }
    setShowAdjustModal(true);
  };

  // Filtering is now handled in fetchStocks, but keep this for client-side filtering if needed
  const filteredStocks = stocks;

  return (
    <DashboardLayout title="Inventory">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center flex-wrap gap-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Inventory Management</h1>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setShowCategoryModal(true)}
              className="btn-secondary flex items-center gap-2"
            >
              <Tag className="w-4 h-4" />
              Add Category
            </button>
            <button
              onClick={() => setShowBrandModal(true)}
              className="btn-secondary flex items-center gap-2"
            >
              <Award className="w-4 h-4" />
              Add Brand
            </button>
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
              <FileSpreadsheet className="w-4 h-4" />
              Export Excel
            </button>
            <button
              onClick={() => window.location.href = '/dashboard/admin/products'}
              className="btn-secondary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Product
            </button>
            <button
              onClick={() => openAdjustModal()}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Adjust Stock
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Products</h3>
            <p className="text-2xl font-bold text-blue-600">
              <AnimatedNumber value={summaryStats.totalProducts} />
            </p>
          </div>
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Stock Items</h3>
            <p className="text-2xl font-bold text-green-600">
              <AnimatedNumber value={summaryStats.totalStockItems} />
            </p>
          </div>
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Low Stock Items</h3>
            <p className="text-2xl font-bold text-red-600">
              <AnimatedNumber value={summaryStats.lowStockItems} />
            </p>
          </div>
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Transactions</h3>
            <p className="text-2xl font-bold text-purple-600">
              <AnimatedNumber value={summaryStats.totalTransactions} />
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="card p-4">
          <div className="flex gap-4 items-center flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Warehouse</label>
              <select
                value={filterWarehouse}
                onChange={(e) => {
                  setFilterWarehouse(e.target.value);
                  setCurrentPage(1); // Reset to first page on filter change
                }}
                className="input-field w-full"
              >
                <option value="">All Warehouses</option>
                {warehouses.map((wh) => (
                  <option key={wh.id} value={wh.id}>{wh.name}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                id="lowStock"
                checked={lowStockOnly}
                onChange={(e) => {
                  setLowStockOnly(e.target.checked);
                  setCurrentPage(1); // Reset to first page on filter change
                }}
                className="rounded"
              />
              <label htmlFor="lowStock" className="text-sm text-gray-700 dark:text-gray-300">
                Low Stock Only
              </label>
            </div>
            <div className="flex items-center gap-2 pt-6">
              <button
                onClick={() => setViewMode(viewMode === 'table' ? 'grid' : 'table')}
                className="btn-secondary text-sm"
              >
                {viewMode === 'table' ? 'Grid View' : 'Table View'}
              </button>
            </div>
          </div>
        </div>

        {/* Stock List - Table View */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : viewMode === 'table' ? (
          <div className="card p-6 overflow-x-auto">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Inventory Table</h2>
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Product</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">SKU</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Warehouse</th>
                  <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Quantity</th>
                  <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Min Level</th>
                  <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Max Level</th>
                  <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Status</th>
                  <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredStocks.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="text-center py-8 text-gray-500 dark:text-gray-400">
                      No stock items found
                    </td>
                  </tr>
                ) : (
                  filteredStocks.map((stock) => (
                    <motion.tr
                      key={stock.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className={`border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 ${
                        stock.is_low_stock ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''
                      }`}
                    >
                      <td className="py-3 px-4 text-gray-900 dark:text-white font-medium">
                        {stock.product?.name || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400 text-sm font-mono">
                        {stock.product?.sku || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {stock.warehouse?.name || 'N/A'}
                      </td>
                      <td className={`py-3 px-4 text-right font-semibold ${
                        stock.is_low_stock ? 'text-yellow-600' : 'text-gray-900 dark:text-white'
                      }`}>
                        {stock.quantity}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                        {stock.min_quantity}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                        {stock.max_quantity}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {stock.is_low_stock ? (
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                            Low Stock
                          </span>
                        ) : (
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            In Stock
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex gap-2 justify-center">
                          <button
                            onClick={() => window.location.href = `/dashboard/admin/products?edit=${stock.product?.id}`}
                            className="btn-secondary text-sm px-3 py-1"
                          >
                            <Edit className="w-4 h-4 inline mr-1" />
                            Edit
                          </button>
                          <button
                            onClick={() => openAdjustModal(stock)}
                            className="btn-secondary text-sm px-3 py-1"
                          >
                            Adjust
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredStocks.map((stock) => (
              <motion.div
                key={stock.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`card p-6 ${stock.is_low_stock ? 'border-yellow-500 border-2' : ''}`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                      {stock.product?.name || 'N/A'}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {stock.warehouse?.name || 'N/A'}
                    </p>
                  </div>
                  {stock.is_low_stock && (
                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                  )}
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Quantity:</span>
                    <span className={`font-semibold ${
                      stock.is_low_stock ? 'text-yellow-600' : 'text-gray-900 dark:text-white'
                    }`}>
                      {stock.quantity}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Available:</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {stock.available_quantity || stock.quantity}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Min Level:</span>
                    <span className="text-gray-900 dark:text-white">{stock.min_quantity}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Max Level:</span>
                    <span className="text-gray-900 dark:text-white">{stock.max_quantity}</span>
                  </div>
                </div>

                <button
                  onClick={() => openAdjustModal(stock)}
                  className="btn-secondary w-full text-sm py-2"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Adjust Stock
                </button>
              </motion.div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between mt-6 gap-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} stock items
              <span className="ml-2">(Page {currentPage} of {totalPages})</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1}
                className={`px-3 py-2 rounded transition-colors text-sm ${
                  currentPage === 1
                    ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 cursor-not-allowed'
                    : 'bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
                title="First Page"
              >
                First
              </button>
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`p-2 rounded transition-colors ${
                  currentPage === 1
                    ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 cursor-not-allowed'
                    : 'bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
                title="Previous Page"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              
              {/* Page Numbers */}
              <div className="flex gap-1 flex-wrap justify-center">
                {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 7) {
                    pageNum = i + 1;
                  } else if (currentPage <= 4) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 3) {
                    pageNum = totalPages - 6 + i;
                  } else {
                    pageNum = currentPage - 3 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`px-3 py-2 rounded transition-colors text-sm min-w-[40px] ${
                        currentPage === pageNum
                          ? 'bg-primary-600 text-white'
                          : 'bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              {/* Go to Page Input */}
              {totalPages > 10 && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Go to:</span>
                  <input
                    type="number"
                    min="1"
                    max={totalPages}
                    defaultValue={currentPage}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const page = parseInt(e.target.value);
                        if (page >= 1 && page <= totalPages) {
                          handlePageChange(page);
                        }
                      }
                    }}
                    className="w-16 px-2 py-1 text-sm border border-gray-300 dark:border-slate-700 rounded bg-white dark:bg-slate-800 text-gray-900 dark:text-white"
                  />
                </div>
              )}
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`p-2 rounded transition-colors ${
                  currentPage === totalPages
                    ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 cursor-not-allowed'
                    : 'bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
                title="Next Page"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
              <button
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage === totalPages}
                className={`px-3 py-2 rounded transition-colors text-sm ${
                  currentPage === totalPages
                    ? 'bg-gray-200 dark:bg-slate-700 text-gray-400 cursor-not-allowed'
                    : 'bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
                title="Last Page"
              >
                Last
              </button>
            </div>
          </div>
        )}

        {/* Adjust Stock Modal */}
        {showAdjustModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-md w-full"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                {selectedStock ? 'Adjust Stock' : 'Add Stock Adjustment'}
              </h2>
              <form onSubmit={handleAdjust} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Product *
                  </label>
                  <select
                    required
                    value={adjustmentData.product_id}
                    onChange={(e) => setAdjustmentData({ ...adjustmentData, product_id: e.target.value })}
                    className="input-field w-full"
                    disabled={!!selectedStock}
                  >
                    <option value="">Select Product</option>
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>{product.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Warehouse *
                  </label>
                  <select
                    required
                    value={adjustmentData.warehouse_id}
                    onChange={(e) => setAdjustmentData({ ...adjustmentData, warehouse_id: e.target.value })}
                    className="input-field w-full"
                    disabled={!!selectedStock}
                  >
                    <option value="">Select Warehouse</option>
                    {warehouses.map((wh) => (
                      <option key={wh.id} value={wh.id}>{wh.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Quantity Adjustment *
                  </label>
                  <input
                    type="number"
                    required
                    value={adjustmentData.quantity}
                    onChange={(e) => setAdjustmentData({ ...adjustmentData, quantity: e.target.value })}
                    className="input-field w-full"
                    placeholder="Positive to add, negative to subtract"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Use positive numbers to add stock, negative to subtract
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Notes
                  </label>
                  <textarea
                    value={adjustmentData.notes}
                    onChange={(e) => setAdjustmentData({ ...adjustmentData, notes: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                    placeholder="Reason for adjustment..."
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">
                    Adjust Stock
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAdjustModal(false);
                      setSelectedStock(null);
                      setAdjustmentData({ product_id: '', warehouse_id: '', quantity: '', notes: '' });
                    }}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* Category Modal */}
        {showCategoryModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-md w-full"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Add Category</h2>
              <form onSubmit={handleCategorySubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
                  <input
                    type="text"
                    required
                    value={categoryForm.name}
                    onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                  <textarea
                    value={categoryForm.description}
                    onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">Create</button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCategoryModal(false);
                      setCategoryForm({ name: '', description: '' });
                    }}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* Brand Modal */}
        {showBrandModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-md w-full"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Add Brand</h2>
              <form onSubmit={handleBrandSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
                  <input
                    type="text"
                    required
                    value={brandForm.name}
                    onChange={(e) => setBrandForm({ ...brandForm, name: e.target.value })}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                  <textarea
                    value={brandForm.description}
                    onChange={(e) => setBrandForm({ ...brandForm, description: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">Create</button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowBrandModal(false);
                      setBrandForm({ name: '', description: '' });
                    }}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Inventory;

