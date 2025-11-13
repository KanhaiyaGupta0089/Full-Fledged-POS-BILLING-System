import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Filter, TrendingUp, DollarSign, ShoppingCart, Package } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function Reports() {
  const [reportType, setReportType] = useState('sales');
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
  });
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState({});

  useEffect(() => {
    fetchReport();
  }, [reportType, filters]);

  const fetchReport = async () => {
    setLoading(true);
    try {
      let url = '';
      switch (reportType) {
        case 'sales':
          url = '/billing/invoices/';
          break;
        case 'products':
          url = '/products/products/';
          break;
        case 'customers':
          url = '/billing/customers/';
          break;
        default:
          url = '/billing/invoices/';
      }
      
      const params = new URLSearchParams();
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      // Don't filter by status in API - we'll filter on frontend for consistency
      if (params.toString()) url += `?${params.toString()}`;
      
      const response = await api.get(url);
      let allData = response.data.results || response.data;
      
      // For sales reports, filter by status on frontend for consistency
      if (reportType === 'sales') {
        allData = allData.filter(
          inv => inv.status === 'paid' || inv.status === 'partial'
        );
      }
      
      setData(allData);
      
      // Calculate summary - filter by status for sales
      if (reportType === 'sales') {
        setSummary({
          totalSales: allData.reduce((sum, inv) => sum + parseFloat(inv.total_amount || 0), 0),
          totalInvoices: allData.length,
          paidAmount: allData.reduce((sum, inv) => sum + parseFloat(inv.paid_amount || 0), 0),
          pendingAmount: allData.reduce((sum, inv) => sum + parseFloat(inv.balance_amount || 0), 0),
        });
      } else if (reportType === 'products') {
        const products = response.data.results || response.data;
        setSummary({
          totalProducts: products.length,
          lowStock: products.filter(p => p.is_low_stock).length,
          activeProducts: products.filter(p => p.is_active).length,
        });
      } else if (reportType === 'customers') {
        const customers = response.data.results || response.data;
        setSummary({
          totalCustomers: customers.length,
        });
      }
      
      setLoading(false);
    } catch (error) {
      toast.error('Failed to fetch report data');
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text(`${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`, 14, 22);
    doc.setFontSize(11);
    
    let tableData = [];
    let headers = [];
    
    if (reportType === 'sales') {
      headers = [['Invoice #', 'Date', 'Customer', 'Amount', 'Status', 'Payment']];
      tableData = data.map(item => [
        item.invoice_number || 'N/A',
        item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A',
        item.customer_name || item.customer?.name || 'Walk-in',
        `₹${parseFloat(item.total_amount || 0).toFixed(2)}`,
        item.status || 'N/A',
        item.payment_method || 'N/A',
      ]);
    } else if (reportType === 'products') {
      headers = [['Name', 'SKU', 'Stock', 'Price', 'Status']];
      tableData = data.map(item => [
        item.name || 'N/A',
        item.sku || 'N/A',
        item.current_stock || 0,
        `₹${parseFloat(item.selling_price || 0).toFixed(2)}`,
        item.is_active ? 'Active' : 'Inactive',
      ]);
    } else if (reportType === 'customers') {
      headers = [['Name', 'Phone', 'Email', 'Total Invoices']];
      tableData = data.map(item => [
        item.name || 'N/A',
        item.phone || 'N/A',
        item.email || 'N/A',
        item.total_invoices || 0,
      ]);
    }
    
    autoTable(doc, {
      head: headers,
      body: tableData,
      startY: 30,
    });
    
    doc.save(`${reportType}_report.pdf`);
    toast.success('PDF exported successfully');
  };

  const exportToExcel = () => {
    let csvContent = [];
    let headers = [];
    
    if (reportType === 'sales') {
      headers = ['Invoice #', 'Date', 'Customer', 'Amount', 'Status', 'Payment'];
      csvContent = [
        headers.join(','),
        ...data.map(item => [
          item.invoice_number || 'N/A',
          item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A',
          item.customer_name || item.customer?.name || 'Walk-in',
          parseFloat(item.total_amount || 0).toFixed(2),
          item.status || 'N/A',
          item.payment_method || 'N/A',
        ].join(','))
      ];
    } else if (reportType === 'products') {
      headers = ['Name', 'SKU', 'Stock', 'Price', 'Status'];
      csvContent = [
        headers.join(','),
        ...data.map(item => [
          item.name || 'N/A',
          item.sku || 'N/A',
          item.current_stock || 0,
          parseFloat(item.selling_price || 0).toFixed(2),
          item.is_active ? 'Active' : 'Inactive',
        ].join(','))
      ];
    } else if (reportType === 'customers') {
      headers = ['Name', 'Phone', 'Email', 'Total Invoices'];
      csvContent = [
        headers.join(','),
        ...data.map(item => [
          item.name || 'N/A',
          item.phone || 'N/A',
          item.email || 'N/A',
          item.total_invoices || 0,
        ].join(','))
      ];
    }
    
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${reportType}_report.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Excel file exported successfully');
  };

  return (
    <DashboardLayout title="Reports">
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center flex-wrap gap-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Reports</h1>
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
          </div>
        </div>

        {/* Report Type Selection */}
        <div className="card p-4">
          <div className="flex gap-4 flex-wrap">
            <button
              onClick={() => setReportType('sales')}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                reportType === 'sales'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              <ShoppingCart className="w-4 h-4 inline mr-2" />
              Sales Report
            </button>
            <button
              onClick={() => setReportType('products')}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                reportType === 'products'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              <Package className="w-4 h-4 inline mr-2" />
              Products Report
            </button>
            <button
              onClick={() => setReportType('customers')}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                reportType === 'customers'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              <TrendingUp className="w-4 h-4 inline mr-2" />
              Customers Report
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="card p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Start Date</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                className="input-field w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">End Date</label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                className="input-field w-full"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ startDate: '', endDate: '' })}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        {reportType === 'sales' && summary.totalSales !== undefined && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Sales</h3>
              <p className="text-2xl font-bold text-green-600">₹{summary.totalSales?.toFixed(2) || 0}</p>
            </div>
            <div className="card p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Invoices</h3>
              <p className="text-2xl font-bold text-blue-600">{summary.totalInvoices || 0}</p>
            </div>
            <div className="card p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Paid Amount</h3>
              <p className="text-2xl font-bold text-green-600">₹{summary.paidAmount?.toFixed(2) || 0}</p>
            </div>
            <div className="card p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Pending Amount</h3>
              <p className="text-2xl font-bold text-red-600">₹{summary.pendingAmount?.toFixed(2) || 0}</p>
            </div>
          </div>
        )}

        {/* Data Table */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="card p-6 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  {reportType === 'sales' && (
                    <>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Invoice #</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Date</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Customer</th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-900 dark:text-white">Amount</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Status</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Payment</th>
                    </>
                  )}
                  {reportType === 'products' && (
                    <>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Name</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">SKU</th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-900 dark:text-white">Stock</th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-900 dark:text-white">Price</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Status</th>
                    </>
                  )}
                  {reportType === 'customers' && (
                    <>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Name</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Phone</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Email</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {data.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center py-8 text-gray-500 dark:text-gray-400">
                      No data found
                    </td>
                  </tr>
                ) : (
                  data.map((item) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      {reportType === 'sales' && (
                        <>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{item.invoice_number || 'N/A'}</td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">
                            {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
                          </td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">
                            {item.customer_name || item.customer?.name || 'Walk-in'}
                          </td>
                          <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                            ₹{parseFloat(item.total_amount || 0).toFixed(2)}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              item.status === 'paid' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              item.status === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                              'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            }`}>
                              {item.status || 'N/A'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{item.payment_method || 'N/A'}</td>
                        </>
                      )}
                      {reportType === 'products' && (
                        <>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{item.name || 'N/A'}</td>
                          <td className="py-3 px-4 text-gray-500 dark:text-gray-400">{item.sku || 'N/A'}</td>
                          <td className="py-3 px-4 text-right text-gray-900 dark:text-white">{item.current_stock || 0}</td>
                          <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                            ₹{parseFloat(item.selling_price || 0).toFixed(2)}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              item.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            }`}>
                              {item.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                        </>
                      )}
                      {reportType === 'customers' && (
                        <>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{item.name || 'N/A'}</td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{item.phone || 'N/A'}</td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white">{item.email || 'N/A'}</td>
                        </>
                      )}
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Reports;

