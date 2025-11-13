import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, X, Download, Mail, Eye, Calendar, FileText } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function InvoiceSearch() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    invoice_number: '',
    date_from: '',
    date_to: '',
    status: '',
    payment_method: '',
    customer: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(20);

  useEffect(() => {
    fetchInvoices();
  }, [currentPage, filters]);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      // Add search query
      if (filters.search) {
        params.append('search', filters.search);
      }
      
      // Add specific filters
      if (filters.invoice_number) {
        params.append('search', filters.invoice_number);
      }
      if (filters.date_from) {
        params.append('date_from', filters.date_from);
      }
      if (filters.date_to) {
        params.append('date_to', filters.date_to);
      }
      if (filters.status) {
        params.append('status', filters.status);
      }
      if (filters.payment_method) {
        params.append('payment_method', filters.payment_method);
      }
      if (filters.customer) {
        params.append('customer', filters.customer);
      }
      
      // Pagination
      params.append('page', currentPage);
      params.append('page_size', pageSize);
      
      // Ordering
      params.append('ordering', '-created_at');
      
      const response = await api.get(`/billing/invoices/?${params.toString()}`);
      
      if (response.data.results) {
        // Paginated response
        setInvoices(response.data.results);
        setTotalPages(Math.ceil(response.data.count / pageSize));
        setTotalCount(response.data.count);
      } else {
        // Non-paginated response
        setInvoices(response.data);
        setTotalPages(1);
        setTotalCount(response.data.length);
      }
    } catch (error) {
      console.error('Failed to fetch invoices:', error);
      toast.error('Failed to load invoices');
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      invoice_number: '',
      date_from: '',
      date_to: '',
      status: '',
      payment_method: '',
      customer: '',
    });
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const downloadPDF = async (invoiceId) => {
    try {
      const response = await api.get(`/billing/invoices/${invoiceId}/pdf/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${selectedInvoice?.invoice_number || invoiceId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF downloaded successfully');
    } catch (error) {
      console.error('Failed to download PDF:', error);
      toast.error('Failed to download PDF');
    }
  };

  const sendEmail = async (invoiceId) => {
    try {
      await api.post(`/billing/invoices/${invoiceId}/send_email/`);
      toast.success('Invoice email sent successfully');
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Failed to send email';
      toast.error(errorMessage);
    }
  };

  const viewInvoice = async (invoiceId) => {
    try {
      const response = await api.get(`/billing/invoices/${invoiceId}/`);
      setSelectedInvoice(response.data);
      setShowInvoiceModal(true);
    } catch (error) {
      console.error('Failed to fetch invoice:', error);
      toast.error('Failed to load invoice details');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      paid: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      partial: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      pending: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      cancelled: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    };
    return colors[status] || colors.draft;
  };

  const getPaymentMethodColor = (method) => {
    const colors = {
      cash: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      card: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      upi: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      credit: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      mixed: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    };
    return colors[method] || colors.mixed;
  };

  const exportToPDF = async () => {
    try {
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      params.append('page_size', '10000');
      
      const response = await api.get(`/billing/invoices/?${params.toString()}`);
      const allInvoices = response.data.results || response.data;
      
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text('Invoice Search Report', 14, 22);
      doc.setFontSize(11);
      
      const tableData = allInvoices.map(inv => [
        inv.invoice_number || 'N/A',
        inv.created_at ? format(new Date(inv.created_at), 'dd/MM/yyyy') : 'N/A',
        inv.customer_name || inv.customer?.name || 'Walk-in',
        `₹${parseFloat(inv.total_amount || 0).toFixed(2)}`,
        inv.status || 'N/A',
        inv.payment_method || 'N/A',
      ]);
      
      autoTable(doc, {
        head: [['Invoice #', 'Date', 'Customer', 'Amount', 'Status', 'Payment']],
        body: tableData,
        startY: 30,
      });
      
      doc.save('invoice_search_report.pdf');
      toast.success('PDF exported successfully');
    } catch (error) {
      toast.error('Failed to export PDF');
    }
  };

  const exportToExcel = async () => {
    try {
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      params.append('page_size', '10000');
      
      const response = await api.get(`/billing/invoices/?${params.toString()}`);
      const allInvoices = response.data.results || response.data;
      
      let csvContent = [];
      csvContent.push('Invoice #,Date,Customer,Amount,Status,Payment Method');
      allInvoices.forEach(inv => {
        csvContent.push([
          inv.invoice_number || 'N/A',
          inv.created_at ? format(new Date(inv.created_at), 'dd/MM/yyyy') : 'N/A',
          inv.customer_name || inv.customer?.name || 'Walk-in',
          parseFloat(inv.total_amount || 0).toFixed(2),
          inv.status || 'N/A',
          inv.payment_method || 'N/A',
        ].join(','));
      });
      
      const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'invoice_search_report.csv';
      link.click();
      toast.success('Excel exported successfully');
    } catch (error) {
      toast.error('Failed to export Excel');
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Invoice Search</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Search and filter invoices by various criteria</p>
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
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary flex items-center gap-2"
            >
              <Filter className="w-5 h-5" />
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="card p-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Quick Search
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Invoice number, customer name, phone..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>

              {/* Invoice Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Invoice Number
                </label>
                <input
                  type="text"
                  placeholder="e.g., INV-20251109-0001"
                  value={filters.invoice_number}
                  onChange={(e) => handleFilterChange('invoice_number', e.target.value)}
                  className="input-field w-full"
                />
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date From
                </label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  className="input-field w-full"
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date To
                </label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  className="input-field w-full"
                />
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="input-field w-full"
                >
                  <option value="">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="pending">Pending</option>
                  <option value="paid">Paid</option>
                  <option value="partial">Partially Paid</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              {/* Payment Method */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Payment Method
                </label>
                <select
                  value={filters.payment_method}
                  onChange={(e) => handleFilterChange('payment_method', e.target.value)}
                  className="input-field w-full"
                >
                  <option value="">All Methods</option>
                  <option value="cash">Cash</option>
                  <option value="card">Card</option>
                  <option value="upi">UPI</option>
                  <option value="credit">Credit (Udhar)</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>
            </div>

            {/* Clear Filters Button */}
            <div className="mt-4 flex justify-end">
              <button
                onClick={clearFilters}
                className="btn-secondary flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Clear Filters
              </button>
            </div>
          </motion.div>
        )}

        {/* Results Summary */}
        <div className="card p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {invoices.length} of {totalCount} invoices
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {filters.date_from && filters.date_to
                  ? `${filters.date_from} to ${filters.date_to}`
                  : filters.date_from
                  ? `From ${filters.date_from}`
                  : filters.date_to
                  ? `Until ${filters.date_to}`
                  : 'All dates'}
              </span>
            </div>
          </div>
        </div>

        {/* Invoices Table */}
        {loading ? (
          <div className="card p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading invoices...</p>
          </div>
        ) : invoices.length === 0 ? (
          <div className="card p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg">No invoices found</p>
            <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
              Try adjusting your filters or search criteria
            </p>
          </div>
        ) : (
          <div className="card p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Invoice #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Total Amount
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Paid
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Balance
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Payment
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {invoices.map((invoice) => (
                    <motion.tr
                      key={invoice.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {invoice.invoice_number}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {invoice.customer_name || (invoice.customer && invoice.customer.name) || 'Walk-in Customer'}
                        </div>
                        {invoice.customer_phone && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {invoice.customer_phone}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {format(new Date(invoice.created_at), 'MMM dd, yyyy')}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {format(new Date(invoice.created_at), 'hh:mm a')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          ₹{parseFloat(invoice.total_amount).toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm text-gray-900 dark:text-white">
                          ₹{parseFloat(invoice.paid_amount).toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className={`text-sm font-medium ${
                          parseFloat(invoice.balance_amount) > 0
                            ? 'text-red-600 dark:text-red-400'
                            : 'text-green-600 dark:text-green-400'
                        }`}>
                          ₹{parseFloat(invoice.balance_amount).toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(invoice.status)}`}>
                          {invoice.status_display || invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getPaymentMethodColor(invoice.payment_method)}`}>
                          {invoice.payment_method_display || invoice.payment_method}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => viewInvoice(invoice.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                            title="View Invoice"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => downloadPDF(invoice.id)}
                            className="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded transition-colors"
                            title="Download PDF"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          {invoice.customer_email && (
                            <button
                              onClick={() => sendEmail(invoice.id)}
                              className="p-2 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded transition-colors"
                              title="Send Email"
                            >
                              <Mail className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
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
                  className="btn-secondary px-3 py-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  First
                </button>
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="btn-secondary px-3 py-1 disabled:opacity-50 disabled:cursor-not-allowed"
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
                  className="btn-secondary px-3 py-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
                <button
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                  className="btn-secondary px-3 py-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Last
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Invoice Detail Modal */}
        {showInvoiceModal && selectedInvoice && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Invoice {selectedInvoice.invoice_number}
                  </h2>
                  <button
                    onClick={() => setShowInvoiceModal(false)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Customer</h3>
                    <p className="text-gray-900 dark:text-white">
                      {selectedInvoice.customer_name || (selectedInvoice.customer && selectedInvoice.customer.name) || 'Walk-in Customer'}
                    </p>
                    {selectedInvoice.customer_phone && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">{selectedInvoice.customer_phone}</p>
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Date</h3>
                    <p className="text-gray-900 dark:text-white">
                      {format(new Date(selectedInvoice.created_at), 'MMM dd, yyyy hh:mm a')}
                    </p>
                  </div>
                </div>

                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Items</h3>
                  <div className="space-y-2">
                    {selectedInvoice.items && selectedInvoice.items.length > 0 ? (
                      selectedInvoice.items.map((item, idx) => (
                        <div key={idx} className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
                          <div>
                            <p className="text-gray-900 dark:text-white">
                              {item.product?.name || item.product_name || 'Unknown Product'}
                            </p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {item.quantity} x ₹{parseFloat(item.unit_price || 0).toFixed(2)}
                            </p>
                          </div>
                          <p className="text-gray-900 dark:text-white font-medium">
                            ₹{parseFloat(item.total || 0).toFixed(2)}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400 text-center py-4">No items found</p>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Subtotal:</span>
                      <span className="text-gray-900 dark:text-white">₹{parseFloat(selectedInvoice.subtotal || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Discount:</span>
                      <span className="text-gray-900 dark:text-white">₹{parseFloat(selectedInvoice.discount_amount || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Tax:</span>
                      <span className="text-gray-900 dark:text-white">₹{parseFloat(selectedInvoice.tax_amount || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-bold text-lg pt-2 border-t border-gray-200 dark:border-gray-700">
                      <span className="text-gray-900 dark:text-white">Total:</span>
                      <span className="text-gray-900 dark:text-white">₹{parseFloat(selectedInvoice.total_amount).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Paid:</span>
                      <span className="text-gray-900 dark:text-white">₹{parseFloat(selectedInvoice.paid_amount || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-semibold">
                      <span className="text-gray-900 dark:text-white">Balance:</span>
                      <span className={parseFloat(selectedInvoice.balance_amount || 0) > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}>
                        ₹{parseFloat(selectedInvoice.balance_amount || 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={() => downloadPDF(selectedInvoice.id)}
                    className="btn-primary flex items-center gap-2 flex-1"
                  >
                    <Download className="w-4 h-4" />
                    Download PDF
                  </button>
                  {selectedInvoice.customer_email && (
                    <button
                      onClick={() => sendEmail(selectedInvoice.id)}
                      className="btn-secondary flex items-center gap-2 flex-1"
                    >
                      <Mail className="w-4 h-4" />
                      Send Email
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default InvoiceSearch;

