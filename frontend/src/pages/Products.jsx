import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Plus, Search, Edit, Trash2, Package, AlertCircle, Filter, Upload, X, Image as ImageIcon, Grid3x3, Table2, ChevronLeft, ChevronRight, Download, FileText, Printer } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(20);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    brand: '',
    cost_price: '',
    selling_price: '',
    current_stock: '',
    min_stock_level: '',
    max_stock_level: '',
    unit: 'pcs',
    tax_rate: '0',
    is_active: true,
    is_trackable: true,
  });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchProducts();
    fetchCategories();
    fetchBrands();
  }, [currentPage, searchQuery]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
      });
      
      // Add search query if provided
      if (searchQuery) {
        params.append('search', searchQuery);
      }
      
      const response = await api.get(`/products/products/?${params.toString()}`);
      
      // Handle paginated response
      if (response.data.results) {
        setProducts(response.data.results);
        const total = response.data.count || 0;
        setTotalCount(total);
        setTotalPages(Math.ceil(total / pageSize));
        
        // Debug: Log pagination info
        console.log('Pagination Info:', {
          currentPage,
          pageSize,
          total,
          totalPages: Math.ceil(total / pageSize),
          resultsCount: response.data.results.length,
          next: response.data.next,
          previous: response.data.previous
        });
      } else {
        // Non-paginated response (fallback)
        setProducts(response.data);
        setTotalCount(response.data.length);
        setTotalPages(1);
      }
      setLoading(false);
    } catch (error) {
      toast.error('Failed to fetch products');
      setLoading(false);
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

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast.error('Image size should be less than 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        toast.error('Please select a valid image file');
        return;
      }
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = new FormData();
      
      // Add all form fields
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== undefined && formData[key] !== '') {
          submitData.append(key, formData[key]);
        }
      });
      
      // Add image if selected
      if (imageFile) {
        submitData.append('image', imageFile);
      }
      
      if (editingProduct) {
        const response = await api.put(`/products/products/${editingProduct.id}/`, submitData);
        toast.success('Product updated successfully');
      } else {
        const response = await api.post('/products/products/', submitData);
        toast.success(`Product created successfully! SKU: ${response.data.sku}, Barcode: ${response.data.barcode}, QR: ${response.data.qr_code}`);
      }
      setShowModal(false);
      setEditingProduct(null);
      resetForm();
      removeImage();
      fetchProducts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      await api.delete(`/products/products/${id}/`);
      toast.success('Product deleted successfully');
      fetchProducts();
    } catch (error) {
      // Check if the error message contains information about why deletion failed
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to delete product';
      if (errorMessage.includes('deactivated')) {
        // Product was soft-deleted (deactivated) instead
        toast.success('Product has been deactivated (cannot be deleted due to existing invoices/returns)');
        fetchProducts();
      } else {
        toast.error(errorMessage);
      }
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name || '',
      description: product.description || '',
      category: product.category || '',
      brand: product.brand || '',
      cost_price: product.cost_price || '',
      selling_price: product.selling_price || '',
      current_stock: product.current_stock || '',
      min_stock_level: product.min_stock_level || '',
      max_stock_level: product.max_stock_level || '',
      unit: product.unit || 'pcs',
      tax_rate: product.tax_rate || '0',
      is_active: product.is_active ?? true,
      is_trackable: product.is_trackable ?? true,
    });
    // Set image preview if product has image
    if (product.image) {
      setImagePreview(product.image);
    } else {
      setImagePreview(null);
    }
    setImageFile(null);
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: '',
      brand: '',
      cost_price: '',
      selling_price: '',
      current_stock: '',
      min_stock_level: '',
      max_stock_level: '',
      unit: 'pcs',
      tax_rate: '0',
      is_active: true,
      is_trackable: true,
    });
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // No need for client-side filtering since we're using server-side search
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const exportToPDF = async () => {
    try {
      // Fetch all products for export
      const response = await api.get('/products/products/?page_size=10000');
      const allProducts = response.data.results || response.data;
      
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text('Products Report', 14, 22);
      doc.setFontSize(11);
      
      const tableData = allProducts.map(p => [
        p.name || 'N/A',
        p.sku || 'N/A',
        p.current_stock || 0,
        `₹${parseFloat(p.cost_price || 0).toFixed(2)}`,
        `₹${parseFloat(p.selling_price || 0).toFixed(2)}`,
        p.is_active ? 'Active' : 'Inactive',
      ]);
      
      autoTable(doc, {
        head: [['Name', 'SKU', 'Stock', 'Cost Price', 'Selling Price', 'Status']],
        body: tableData,
        startY: 30,
      });
      
      doc.save('products_report.pdf');
      toast.success('PDF exported successfully');
    } catch (error) {
      toast.error('Failed to export PDF');
    }
  };

  const exportToExcel = async () => {
    try {
      // Fetch all products for export
      const response = await api.get('/products/products/?page_size=10000');
      const allProducts = response.data.results || response.data;
      
      let csvContent = [];
      csvContent.push('Name,SKU,Stock,Cost Price,Selling Price,Status');
      allProducts.forEach(p => {
        csvContent.push([
          p.name || 'N/A',
          p.sku || 'N/A',
          p.current_stock || 0,
          parseFloat(p.cost_price || 0).toFixed(2),
          parseFloat(p.selling_price || 0).toFixed(2),
          p.is_active ? 'Active' : 'Inactive',
        ].join(','));
      });
      
      const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'products_report.csv';
      link.click();
      toast.success('Excel exported successfully');
    } catch (error) {
      toast.error('Failed to export Excel');
    }
  };

  const printLabels = async () => {
    try {
      toast.loading('Starting label generation...', { id: 'print-labels' });
      
      // Build URL - limit to 10 products for testing
      // Remove ?limit=10 to generate for all products
      const url = '/products/products/print_labels/?limit=10';
      
      // Start label generation (async for heavy operations)
      // Make request to check if it's async (202) or sync (200 with PDF)
      const response = await api.get(url);
      
      // Check if async task was started (status 202 with task_id)
      if (response.status === 202 && response.data && response.data.task_id) {
        // Async processing - poll for status
        const taskId = response.data.task_id;
        const productCount = response.data.product_count || 0;
        
        toast.loading(
          `Generating labels for ${productCount} products... This may take a moment.`,
          { id: 'print-labels' }
        );
        
        // Poll for task status
        const pollStatus = async () => {
          try {
            const statusResponse = await api.get('/products/products/print_labels/status/', {
              params: { task_id: taskId }
            });
            
            const status = statusResponse.data;
            
            if (status.status === 'processing' || status.status === 'pending') {
              // Update progress
              const progress = status.progress || 0;
              const message = status.message || 'Processing...';
              toast.loading(
                `${message} (${progress}%)`,
                { id: 'print-labels' }
              );
              
              // Poll again after 1 second
              setTimeout(pollStatus, 1000);
            } else if (status.status === 'success') {
              // Task completed - download PDF
              toast.loading('Downloading PDF...', { id: 'print-labels' });
              
              const downloadUrl = status.download_url || `/products/products/print_labels/download/?task_id=${taskId}`;
              const pdfResponse = await api.get(downloadUrl, {
                responseType: 'blob',
              });
              
              // Create blob URL and download
              const url_blob = window.URL.createObjectURL(new Blob([pdfResponse.data], { type: 'application/pdf' }));
              const link = document.createElement('a');
              link.href = url_blob;
              link.setAttribute('download', status.filename || 'product_labels.pdf');
              document.body.appendChild(link);
              link.click();
              link.remove();
              
              // Clean up blob URL
              window.URL.revokeObjectURL(url_blob);
              
              toast.success(
                `Labels PDF generated successfully! (${status.product_count} products)`,
                { id: 'print-labels' }
              );
            } else if (status.status === 'error') {
              // Task failed
              toast.error(
                status.error || 'Failed to generate labels PDF',
                { id: 'print-labels' }
              );
            }
          } catch (error) {
            console.error('Error polling task status:', error);
            toast.error(
              error.response?.data?.error || 'Failed to check generation status',
              { id: 'print-labels' }
            );
          }
        };
        
        // Start polling
        setTimeout(pollStatus, 1000);
      } else {
        // Synchronous response (small batch) - fetch PDF blob directly
        const pdfResponse = await api.get(url, {
          responseType: 'blob',
        });
        
        // Create blob URL and download
        const url_blob = window.URL.createObjectURL(new Blob([pdfResponse.data], { type: 'application/pdf' }));
        const link = document.createElement('a');
        link.href = url_blob;
        link.setAttribute('download', 'product_labels.pdf');
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        // Clean up blob URL
        window.URL.revokeObjectURL(url_blob);
        
        toast.success('Labels PDF generated successfully! Ready to print.', { id: 'print-labels' });
      }
    } catch (error) {
      console.error('Failed to generate labels:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Failed to generate labels PDF';
      toast.error(errorMessage, { id: 'print-labels' });
    }
  };

  return (
    <DashboardLayout title="Products">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Products</h1>
          <div className="flex gap-3 items-center">
            <button
              onClick={printLabels}
              className="btn-secondary flex items-center gap-2"
            >
              <Printer className="w-4 h-4" />
              Print Labels
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
              <Download className="w-4 h-4" />
              Export Excel
            </button>
            <button
              onClick={() => {
                setEditingProduct(null);
                resetForm();
                setShowModal(true);
              }}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Product
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search products by name, SKU, or barcode..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1); // Reset to first page on search
              }}
              className="input-field pl-10 w-full"
            />
          </div>
          
          {/* View Mode Toggle */}
          <div className="flex gap-2 border border-gray-300 dark:border-slate-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'grid'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
              title="Grid View"
            >
              <Grid3x3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'table'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
              title="Table View"
            >
              <Table2 className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Results Count */}
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Showing {products.length} of {totalCount} products
        </div>

        {/* Products Display */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : products.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            No products found
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-6 hover:shadow-lg transition-shadow"
              >
                {/* Product Image */}
                {product.image && (
                  <div className="mb-4">
                    <img 
                      src={product.image}
                      alt={product.name}
                      className="w-full h-40 object-cover rounded-lg"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                )}
                
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900 dark:text-white">{product.name}</h3>
                    <p className="text-sm font-mono text-blue-600 dark:text-blue-400 font-semibold">SKU: {product.sku}</p>
                    {product.barcode && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">Barcode: {product.barcode}</p>
                    )}
                    {product.qr_code && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">QR: {product.qr_code}</p>
                    )}
                  </div>
                  {product.is_low_stock && (
                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                  )}
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Stock:</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{product.current_stock} {product.unit}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Price:</span>
                    <span className="font-semibold text-green-600">₹{product.selling_price}</span>
                  </div>
                  {product.category && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Category:</span>
                      <span className="text-gray-900 dark:text-white">{product.category_name || 'N/A'}</span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleEdit(product)}
                    className="flex-1 btn-secondary text-sm py-2"
                  >
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="btn-secondary text-sm py-2 px-3 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          /* Table View */
          <div className="card overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-slate-700">
                  <th className="text-left py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Image</th>
                  <th className="text-left py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Name</th>
                  <th className="text-left py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">SKU</th>
                  <th className="text-left py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Category</th>
                  <th className="text-left py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Brand</th>
                  <th className="text-right py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Stock</th>
                  <th className="text-right py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Cost Price</th>
                  <th className="text-right py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Selling Price</th>
                  <th className="text-center py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Status</th>
                  <th className="text-center py-4 px-4 text-sm font-semibold text-gray-700 dark:text-slate-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr
                    key={product.id}
                    className="border-b border-gray-200 dark:border-slate-700/50 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors"
                  >
                    <td className="py-4 px-4">
                      {product.image ? (
                        <img
                          src={product.image}
                          alt={product.name}
                          className="w-12 h-12 object-cover rounded"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-12 h-12 bg-gray-200 dark:bg-slate-700 rounded flex items-center justify-center">
                          <Package className="w-6 h-6 text-gray-400" />
                        </div>
                      )}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex flex-col">
                        <span className="font-medium text-gray-900 dark:text-white">{product.name}</span>
                        {product.is_low_stock && (
                          <span className="text-xs text-yellow-600 dark:text-yellow-400 flex items-center gap-1 mt-1">
                            <AlertCircle className="w-3 h-3" />
                            Low Stock
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="font-mono text-sm text-blue-600 dark:text-blue-400">{product.sku}</span>
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-700 dark:text-gray-300">
                      {product.category_name || 'N/A'}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-700 dark:text-gray-300">
                      {product.brand_name || 'N/A'}
                    </td>
                    <td className="py-4 px-4 text-right">
                      <span className={`font-semibold ${
                        product.current_stock <= (product.min_stock_level || 0)
                          ? 'text-red-600 dark:text-red-400'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {product.current_stock} {product.unit}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right text-sm text-gray-700 dark:text-gray-300">
                      ₹{parseFloat(product.cost_price || 0).toFixed(2)}
                    </td>
                    <td className="py-4 px-4 text-right">
                      <span className="font-semibold text-green-600 dark:text-green-400">
                        ₹{parseFloat(product.selling_price || 0).toFixed(2)}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        product.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {product.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex gap-2 justify-center">
                        <button
                          onClick={() => handleEdit(product)}
                          className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex flex-col sm:flex-row items-center justify-between mt-6 gap-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} products
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
              
              {/* Page Numbers - Show more pages for better navigation */}
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

        {/* Add/Edit Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                {editingProduct ? 'Edit Product' : 'Add Product'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  {editingProduct && (
                    <div className="col-span-2 grid grid-cols-3 gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div>
                        <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">SKU</label>
                        <p className="text-sm font-mono text-blue-600 dark:text-blue-400 font-semibold">{editingProduct.sku}</p>
                      </div>
                      {editingProduct.barcode && (
                        <div>
                          <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">Barcode</label>
                          <p className="text-sm font-mono text-gray-900 dark:text-white">{editingProduct.barcode}</p>
                        </div>
                      )}
                      {editingProduct.qr_code && (
                        <div>
                          <label className="block text-xs font-medium mb-1 text-gray-600 dark:text-gray-400">QR Code</label>
                          <p className="text-sm font-mono text-gray-900 dark:text-white">{editingProduct.qr_code}</p>
                        </div>
                      )}
                      <p className="col-span-3 text-xs text-gray-500 dark:text-gray-400 mt-2">All IDs are auto-generated</p>
                    </div>
                  )}
                  
                  {/* Image Upload */}
                  <div className="col-span-2">
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Product Image</label>
                    <div className="mt-2">
                      {imagePreview ? (
                        <div className="relative">
                          <img
                            src={imagePreview}
                            alt="Preview"
                            className="w-full h-48 object-cover rounded-lg border-2 border-gray-300 dark:border-gray-600"
                          />
                          <button
                            type="button"
                            onClick={removeImage}
                            className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div
                          onClick={() => fileInputRef.current?.click()}
                          className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
                        >
                          <ImageIcon className="w-12 h-12 mx-auto text-gray-400 mb-2" />
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Click to upload image
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                            PNG, JPG up to 5MB
                          </p>
                        </div>
                      )}
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Category</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="input-field"
                    >
                      <option value="">Select Category</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Brand</label>
                    <select
                      value={formData.brand}
                      onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                      className="input-field"
                    >
                      <option value="">Select Brand</option>
                      {brands.map((brand) => (
                        <option key={brand.id} value={brand.id}>{brand.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Cost Price *</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.cost_price}
                      onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Selling Price *</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.selling_price}
                      onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Current Stock</label>
                    <input
                      type="number"
                      value={formData.current_stock}
                      onChange={(e) => setFormData({ ...formData, current_stock: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Min Stock Level</label>
                    <input
                      type="number"
                      value={formData.min_stock_level}
                      onChange={(e) => setFormData({ ...formData, min_stock_level: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Max Stock Level</label>
                    <input
                      type="number"
                      value={formData.max_stock_level}
                      onChange={(e) => setFormData({ ...formData, max_stock_level: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Unit</label>
                    <select
                      value={formData.unit}
                      onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                      className="input-field"
                    >
                      <option value="pcs">Pieces</option>
                      <option value="kg">Kilogram</option>
                      <option value="liter">Liter</option>
                      <option value="box">Box</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Tax Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.tax_rate}
                      onChange={(e) => setFormData({ ...formData, tax_rate: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input-field"
                    rows="3"
                  />
                </div>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Active</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.is_trackable}
                      onChange={(e) => setFormData({ ...formData, is_trackable: e.target.checked })}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Track Inventory</span>
                  </label>
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">
                    {editingProduct ? 'Update' : 'Create'} Product
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setEditingProduct(null);
                      resetForm();
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

export default Products;

