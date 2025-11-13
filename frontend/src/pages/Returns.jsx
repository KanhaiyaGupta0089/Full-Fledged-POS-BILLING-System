import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Plus, Search, Check, X, Package, AlertCircle, Zap, FileText, Filter, Download } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function Returns() {
  const [returns, setReturns] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    invoice: '',
    invoice_number: '',
    reason: 'defective',
    reason_description: '',
    notes: '',
    items: [],
  });
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [invoiceSearchInput, setInvoiceSearchInput] = useState('');
  const [searchingInvoice, setSearchingInvoice] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(20);

  useEffect(() => {
    fetchReturns();
    fetchInvoices();
  }, [currentPage, statusFilter, searchQuery]);

  const fetchReturns = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      if (searchQuery) params.append('search', searchQuery);
      params.append('page', currentPage);
      params.append('page_size', pageSize);
      params.append('ordering', '-created_at');
      
      const response = await api.get(`/returns/orders/?${params.toString()}`);
      
      if (response.data.results) {
        setReturns(response.data.results);
        setTotalPages(Math.ceil(response.data.count / pageSize));
        setTotalCount(response.data.count);
      } else {
        setReturns(response.data);
        setTotalPages(1);
        setTotalCount(response.data.length);
      }
    } catch (error) {
      toast.error('Failed to fetch returns');
      setReturns([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchInvoices = async () => {
    try {
      const response = await api.get('/billing/invoices/?page_size=100&ordering=-created_at');
      setInvoices(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch invoices');
    }
  };

  const searchInvoiceByNumber = async () => {
    if (!invoiceSearchInput.trim()) {
      toast.error('Please enter an invoice number');
      return;
    }
    
    setSearchingInvoice(true);
    try {
      const response = await api.get(`/returns/orders/search_invoice/?invoice_number=${invoiceSearchInput.trim()}`);
      setSelectedInvoice(response.data);
      setFormData({
        ...formData,
        invoice: response.data.id,
        invoice_number: response.data.invoice_number,
        items: response.data.items.map(item => ({
          invoice_item_id: item.id,
          product_id: item.product?.id || item.product_id,
          quantity: 0,
          max_quantity: item.quantity,
        })),
      });
      toast.success('Invoice found!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Invoice not found');
      setSelectedInvoice(null);
    } finally {
      setSearchingInvoice(false);
    }
  };

  const fetchInvoiceDetails = async (invoiceId) => {
    try {
      const response = await api.get(`/billing/invoices/${invoiceId}/`);
      setSelectedInvoice(response.data);
      setFormData({
        ...formData,
        invoice: invoiceId,
        invoice_number: response.data.invoice_number,
        items: response.data.items.map(item => ({
          invoice_item_id: item.id,
          product_id: item.product?.id || item.product_id,
          quantity: 0,
          max_quantity: item.quantity,
        })),
      });
    } catch (error) {
      toast.error('Failed to fetch invoice details');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate that at least one item has quantity > 0
    const hasItems = formData.items.some(item => item.quantity > 0);
    if (!hasItems) {
      toast.error('Please select at least one item to return');
      return;
    }
    
    // Filter out items with quantity 0
    const itemsToReturn = formData.items.filter(item => item.quantity > 0);
    
    try {
      const response = await api.post('/returns/orders/', {
        ...formData,
        items: itemsToReturn,
      });
      const returnNumber = response.data.return_number;
      toast.success(`Return request ${returnNumber} created successfully!`, {
        duration: 5000,
      });
      setShowModal(false);
      resetForm();
      fetchReturns();
    } catch (error) {
      toast.error(error.response?.data?.detail || error.response?.data?.error || 'Failed to create return');
    }
  };

  const resetForm = () => {
    setFormData({
      invoice: '',
      invoice_number: '',
      reason: 'defective',
      reason_description: '',
      notes: '',
      items: [],
    });
    setSelectedInvoice(null);
    setInvoiceSearchInput('');
  };

  const handleQuickComplete = async (returnId) => {
    try {
      await api.post(`/returns/orders/${returnId}/quick_complete/`);
      toast.success('Return processed successfully');
      fetchReturns();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to process return');
    }
  };

  const handleApprove = async (returnId) => {
    try {
      await api.post(`/returns/orders/${returnId}/approve/`);
      toast.success('Return approved successfully');
      fetchReturns();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to approve return');
    }
  };

  const handleComplete = async (returnId) => {
    try {
      await api.post(`/returns/orders/${returnId}/complete/`);
      toast.success('Return completed successfully');
      fetchReturns();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to complete return');
    }
  };

  const updateItemQuantity = (index, quantity) => {
    const newItems = [...formData.items];
    const qty = parseInt(quantity) || 0;
    const maxQty = newItems[index].max_quantity || 0;
    newItems[index].quantity = Math.min(Math.max(0, qty), maxQty);
    setFormData({ ...formData, items: newItems });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
      case 'approved':
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
      case 'completed':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20';
      case 'rejected':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-900/20';
    }
  };

  const calculateTotalRefund = () => {
    if (!selectedInvoice) return 0;
    return formData.items.reduce((total, item) => {
      const invoiceItem = selectedInvoice.items?.find(i => i.id === item.invoice_item_id);
      if (invoiceItem && item.quantity > 0) {
        return total + (parseFloat(invoiceItem.unit_price || 0) * item.quantity);
      }
      return total;
    }, 0);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const exportToPDF = async () => {
    try {
      const response = await api.get('/returns/orders/?page_size=10000');
      const allReturns = response.data.results || response.data;
      
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text('Returns Report', 14, 22);
      doc.setFontSize(11);
      
      const tableData = allReturns.map(r => [
        r.return_number || 'N/A',
        r.invoice?.invoice_number || 'N/A',
        r.created_at ? format(new Date(r.created_at), 'dd/MM/yyyy') : 'N/A',
        r.status || 'N/A',
        `₹${parseFloat(r.refund_amount || 0).toFixed(2)}`,
        r.reason || 'N/A',
      ]);
      
      autoTable(doc, {
        head: [['Return #', 'Invoice #', 'Date', 'Status', 'Refund Amount', 'Reason']],
        body: tableData,
        startY: 30,
      });
      
      doc.save('returns_report.pdf');
      toast.success('PDF exported successfully');
    } catch (error) {
      toast.error('Failed to export PDF');
    }
  };

  const exportToExcel = async () => {
    try {
      const response = await api.get('/returns/orders/?page_size=10000');
      const allReturns = response.data.results || response.data;
      
      let csvContent = [];
      csvContent.push('Return #,Invoice #,Date,Status,Refund Amount,Reason');
      allReturns.forEach(r => {
        csvContent.push([
          r.return_number || 'N/A',
          r.invoice?.invoice_number || 'N/A',
          r.created_at ? format(new Date(r.created_at), 'dd/MM/yyyy') : 'N/A',
          r.status || 'N/A',
          parseFloat(r.refund_amount || 0).toFixed(2),
          r.reason || 'N/A',
        ].join(','));
      });
      
      const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'returns_report.csv';
      link.click();
      toast.success('Excel exported successfully');
    } catch (error) {
      toast.error('Failed to export Excel');
    }
  };

  return (
    <DashboardLayout title="Returns">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Product Returns</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage product returns and refunds</p>
          </div>
          <div className="flex gap-2">
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
                setShowModal(true);
                resetForm();
              }}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              New Return
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="card p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Return number, invoice number..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="input-field pl-10 w-full"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="input-field w-full"
              >
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="completed">Completed</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div className="flex items-end">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {returns.length} of {totalCount} returns
              </p>
            </div>
          </div>
        </div>

        {/* Returns List */}
        {loading ? (
          <div className="card p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading returns...</p>
          </div>
        ) : returns.length === 0 ? (
          <div className="card p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg">No returns found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {returns.map((returnOrder) => (
              <motion.div
                key={returnOrder.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Return #{returnOrder.return_number}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(returnOrder.status)}`}>
                        {returnOrder.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">Invoice</p>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {returnOrder.invoice?.invoice_number || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">Date</p>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {format(new Date(returnOrder.created_at), 'MMM dd, yyyy')}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">Total Amount</p>
                        <p className="text-gray-900 dark:text-white font-medium">
                          ₹{parseFloat(returnOrder.total_amount || 0).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500 dark:text-gray-400">Refund Amount</p>
                        <p className="text-green-600 dark:text-green-400 font-medium">
                          ₹{parseFloat(returnOrder.refund_amount || 0).toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <strong>Reason:</strong> {returnOrder.reason.replace('_', ' ').toUpperCase()}
                      </p>
                      {returnOrder.reason_description && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                          {returnOrder.reason_description}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {returnOrder.items && returnOrder.items.length > 0 && (
                  <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Items:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {returnOrder.items.map((item, index) => (
                        <div key={index} className="text-sm">
                          <p className="text-gray-900 dark:text-white">
                            {item.product?.name || 'N/A'} × {item.quantity}
                          </p>
                          <p className="text-gray-500 dark:text-gray-400">
                            ₹{parseFloat(item.unit_price || 0).toFixed(2)} each
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  {returnOrder.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleApprove(returnOrder.id)}
                        className="btn-secondary text-sm px-4 py-2 flex items-center gap-2"
                      >
                        <Check className="w-4 h-4" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleQuickComplete(returnOrder.id)}
                        className="btn-primary text-sm px-4 py-2 flex items-center gap-2"
                      >
                        <Zap className="w-4 h-4" />
                        Quick Complete
                      </button>
                    </>
                  )}
                  {returnOrder.status === 'approved' && (
                    <button
                      onClick={() => handleComplete(returnOrder.id)}
                      className="btn-primary text-sm px-4 py-2 flex items-center gap-2"
                    >
                      <Check className="w-4 h-4" />
                      Complete
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="card p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(1)}
                  disabled={currentPage === 1}
                  className="btn-secondary px-3 py-1 disabled:opacity-50"
                >
                  First
                </button>
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="btn-secondary px-3 py-1 disabled:opacity-50"
                >
                  Previous
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page {currentPage} of {totalPages}
                </span>
                <input
                  type="number"
                  min="1"
                  max={totalPages}
                  value={currentPage}
                  onChange={(e) => {
                    const page = parseInt(e.target.value);
                    if (page >= 1 && page <= totalPages) {
                      handlePageChange(page);
                    }
                  }}
                  className="w-16 px-2 py-1 text-center border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Go to page</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="btn-secondary px-3 py-1 disabled:opacity-50"
                >
                  Next
                </button>
                <button
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                  className="btn-secondary px-3 py-1 disabled:opacity-50"
                >
                  Last
                </button>
              </div>
            </div>
          </div>
        )}

        {/* New Return Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">New Return Request</h2>
                <button
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Quick Invoice Search */}
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                    Quick Search by Invoice Number
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Enter invoice number (e.g., INV-20251109-0001)"
                      value={invoiceSearchInput}
                      onChange={(e) => setInvoiceSearchInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          searchInvoiceByNumber();
                        }
                      }}
                      className="input-field flex-1"
                    />
                    <button
                      type="button"
                      onClick={searchInvoiceByNumber}
                      disabled={searchingInvoice}
                      className="btn-primary px-4 disabled:opacity-50"
                    >
                      {searchingInvoice ? 'Searching...' : 'Search'}
                    </button>
                  </div>
                </div>

                {/* Or Select from Dropdown */}
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Or Select Invoice from List
                  </label>
                  <select
                    value={formData.invoice}
                    onChange={(e) => {
                      setFormData({ ...formData, invoice: e.target.value });
                      if (e.target.value) {
                        fetchInvoiceDetails(e.target.value);
                      } else {
                        setSelectedInvoice(null);
                      }
                    }}
                    className="input-field w-full"
                  >
                    <option value="">Select Invoice</option>
                    {invoices.slice(0, 50).map((invoice) => (
                      <option key={invoice.id} value={invoice.id}>
                        {invoice.invoice_number} - ₹{parseFloat(invoice.total_amount || 0).toFixed(2)} - {format(new Date(invoice.created_at), 'MMM dd, yyyy')}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedInvoice && (
                  <>
                    <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <h4 className="font-semibold mb-3 text-gray-900 dark:text-white">Invoice Details:</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">Invoice Number</p>
                          <p className="text-gray-900 dark:text-white font-medium">{selectedInvoice.invoice_number}</p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">Customer</p>
                          <p className="text-gray-900 dark:text-white font-medium">
                            {selectedInvoice.customer_name || (selectedInvoice.customer && selectedInvoice.customer.name) || 'Walk-in'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">Date</p>
                          <p className="text-gray-900 dark:text-white font-medium">
                            {format(new Date(selectedInvoice.created_at), 'MMM dd, yyyy')}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400">Total Amount</p>
                          <p className="text-gray-900 dark:text-white font-medium">
                            ₹{parseFloat(selectedInvoice.total_amount || 0).toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <h4 className="font-semibold mb-3 text-gray-900 dark:text-white">Select Items to Return:</h4>
                      <div className="space-y-3">
                        {formData.items.map((item, index) => {
                          const invoiceItem = selectedInvoice.items?.find(i => i.id === item.invoice_item_id);
                          if (!invoiceItem) return null;
                          
                          return (
                            <div key={item.invoice_item_id} className="p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <p className="font-semibold text-gray-900 dark:text-white">{invoiceItem.product?.name || 'N/A'}</p>
                                  <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Available: {item.max_quantity} | Price: ₹{parseFloat(invoiceItem.unit_price || 0).toFixed(2)} each
                                  </p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <button
                                    type="button"
                                    onClick={() => updateItemQuantity(index, item.quantity - 1)}
                                    disabled={item.quantity <= 0}
                                    className="p-1 w-8 h-8 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                                  >
                                    -
                                  </button>
                                  <input
                                    type="number"
                                    min="0"
                                    max={item.max_quantity}
                                    value={item.quantity}
                                    onChange={(e) => updateItemQuantity(index, e.target.value)}
                                    className="w-20 text-center input-field"
                                  />
                                  <button
                                    type="button"
                                    onClick={() => updateItemQuantity(index, item.quantity + 1)}
                                    disabled={item.quantity >= item.max_quantity}
                                    className="p-1 w-8 h-8 rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                                  >
                                    +
                                  </button>
                                </div>
                              </div>
                              {item.quantity > 0 && (
                                <p className="text-sm text-green-600 dark:text-green-400 mt-2">
                                  Refund: ₹{(parseFloat(invoiceItem.unit_price || 0) * item.quantity).toFixed(2)}
                                </p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                      {calculateTotalRefund() > 0 && (
                        <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                          <p className="text-lg font-bold text-green-600 dark:text-green-400">
                            Total Refund: ₹{calculateTotalRefund().toFixed(2)}
                          </p>
                        </div>
                      )}
                    </div>
                  </>
                )}

                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Reason *
                  </label>
                  <select
                    required
                    value={formData.reason}
                    onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                    className="input-field w-full"
                  >
                    <option value="defective">Defective Product</option>
                    <option value="wrong_item">Wrong Item</option>
                    <option value="damaged">Damaged in Transit</option>
                    <option value="not_satisfied">Not Satisfied</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Reason Description
                  </label>
                  <textarea
                    value={formData.reason_description}
                    onChange={(e) => setFormData({ ...formData, reason_description: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                    placeholder="Describe the reason for return..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Notes
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="input-field w-full"
                    rows="2"
                    placeholder="Additional notes..."
                  />
                </div>

                <div className="flex gap-4 pt-4">
                  <button 
                    type="submit" 
                    className="btn-primary flex-1" 
                    disabled={!selectedInvoice || formData.items.every(item => item.quantity === 0)}
                  >
                    Create Return Request
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
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

export default Returns;
