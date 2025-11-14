import { useState } from 'react';
import { FileText, Download, TrendingUp, TrendingDown, DollarSign, Receipt, BarChart3, PieChart } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { LineChart, Line, BarChart, Bar, PieChart as RechartsPieChart, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function AdvancedReports() {
  const [selectedReport, setSelectedReport] = useState('gst'); // 'gst', 'tax', 'pl'
  const [dateFrom, setDateFrom] = useState(new Date(new Date().setDate(1)).toISOString().split('T')[0]); // First day of current month
  const [dateTo, setDateTo] = useState(new Date().toISOString().split('T')[0]); // Today
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateReport = async (reportType, endpoint) => {
    try {
      setLoading(true);
      toast.loading('Generating report...', { id: 'generate-report' });
      const response = await api.post(`/reports/reports/${endpoint}/`, {
        date_from: dateFrom,
        date_to: dateTo
      });
      setReportData({ type: reportType, data: response.data });
      toast.success('Report generated successfully!', { id: 'generate-report' });
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate report', { id: 'generate-report' });
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    if (!reportData) {
      toast.error('Please generate a report first');
      return;
    }

    try {
      toast.loading('Generating PDF...', { id: 'pdf-export' });
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text(reportData.data.report_type || 'Report', 14, 15);
      doc.setFontSize(11);
      doc.text(`Period: ${reportData.data.period || ''}`, 14, 22);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);

      if (reportData.type === 'gst') {
        if (reportData.data.summary) {
          const summaryData = [
            ['Total Invoices/GRNs', reportData.data.summary.total_invoices || reportData.data.summary.total_grns || 0],
            ['Total Taxable Value', `₹${(reportData.data.summary.total_taxable_value || 0).toLocaleString('en-IN')}`],
            ['Total CGST', `₹${(reportData.data.summary.total_cgst || 0).toLocaleString('en-IN')}`],
            ['Total SGST', `₹${(reportData.data.summary.total_sgst || 0).toLocaleString('en-IN')}`],
            ['Total IGST', `₹${(reportData.data.summary.total_igst || 0).toLocaleString('en-IN')}`],
            ['Total Tax', `₹${(reportData.data.summary.total_tax || 0).toLocaleString('en-IN')}`],
          ];

          autoTable(doc, {
            head: [['Item', 'Value']],
            body: summaryData,
            startY: 35,
            styles: { fontSize: 10 },
            headStyles: { fillColor: [66, 139, 202] },
          });
        }
      } else if (reportData.type === 'tax') {
        if (reportData.data.summary) {
          const summaryData = [
            ['Total Taxable Value', `₹${(reportData.data.summary.total_taxable_value || 0).toLocaleString('en-IN')}`],
            ['Total Tax', `₹${(reportData.data.summary.total_tax || 0).toLocaleString('en-IN')}`],
            ['Categories/Products', reportData.data.summary.categories_count || reportData.data.summary.products_count || 0],
          ];

          autoTable(doc, {
            head: [['Item', 'Value']],
            body: summaryData,
            startY: 35,
            styles: { fontSize: 10 },
            headStyles: { fillColor: [66, 139, 202] },
          });
        }
      } else if (reportData.type === 'pl') {
        if (reportData.data.summary) {
          const summaryData = [
            ['Total Revenue', `₹${(reportData.data.summary.total_revenue || 0).toLocaleString('en-IN')}`],
            ['Total COGS', `₹${(reportData.data.summary.total_cogs || 0).toLocaleString('en-IN')}`],
            ['Gross Profit', `₹${(reportData.data.summary.gross_profit || 0).toLocaleString('en-IN')}`],
            ['Total Expenses', `₹${(reportData.data.summary.total_expenses || 0).toLocaleString('en-IN')}`],
            ['Net Profit', `₹${(reportData.data.summary.net_profit || 0).toLocaleString('en-IN')}`],
          ];

          autoTable(doc, {
            head: [['Item', 'Value']],
            body: summaryData,
            startY: 35,
            styles: { fontSize: 10 },
            headStyles: { fillColor: [66, 139, 202] },
          });
        }
      }

      doc.save(`${reportData.data.report_type || 'report'}_${new Date().toISOString().split('T')[0]}.pdf`);
      toast.success('PDF exported successfully!', { id: 'pdf-export' });
    } catch (error) {
      console.error('PDF export error:', error);
      toast.error('Failed to export PDF', { id: 'pdf-export' });
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  return (
    <DashboardLayout title="Advanced Reports">
      <div className="p-6 space-y-6">
        {/* Date Range Selector */}
        <div className="card p-4">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">From Date</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="input-field w-full"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">To Date</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="input-field w-full"
              />
            </div>
            <div>
              <button
                onClick={() => {
                  const today = new Date();
                  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
                  setDateFrom(firstDay.toISOString().split('T')[0]);
                  setDateTo(today.toISOString().split('T')[0]);
                }}
                className="btn-secondary"
              >
                This Month
              </button>
            </div>
          </div>
        </div>

        {/* Report Type Tabs */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => { setSelectedReport('gst'); setReportData(null); }}
            className={`px-4 py-2 font-medium ${
              selectedReport === 'gst'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Receipt className="w-4 h-4 inline mr-2" />
            GST Reports
          </button>
          <button
            onClick={() => { setSelectedReport('tax'); setReportData(null); }}
            className={`px-4 py-2 font-medium ${
              selectedReport === 'tax'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Tax Reports
          </button>
          <button
            onClick={() => { setSelectedReport('pl'); setReportData(null); }}
            className={`px-4 py-2 font-medium ${
              selectedReport === 'pl'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            P&L Reports
          </button>
        </div>

        {/* GST Reports */}
        {selectedReport === 'gst' && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <button
                onClick={() => generateReport('gst', 'gst/gstr1')}
                disabled={loading}
                className="btn-primary"
              >
                Generate GSTR-1 (Outward)
              </button>
              <button
                onClick={() => generateReport('gst', 'gst/gstr2')}
                disabled={loading}
                className="btn-primary"
              >
                Generate GSTR-2 (Inward)
              </button>
              <button
                onClick={() => generateReport('gst', 'gst/summary')}
                disabled={loading}
                className="btn-primary"
              >
                GST Summary
              </button>
              {reportData && (
                <button onClick={exportToPDF} className="btn-secondary">
                  <Download className="w-4 h-4 mr-2" />
                  Export PDF
                </button>
              )}
            </div>

            {reportData && reportData.type === 'gst' && (
              <div className="card p-6 space-y-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{reportData.data.report_type}</h3>
                
                {reportData.data.summary && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Invoices/GRNs</div>
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {reportData.data.summary.total_invoices || reportData.data.summary.total_grns || 0}
                      </div>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Taxable Value</div>
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        ₹{(reportData.data.summary.total_taxable_value || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Tax</div>
                      <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        ₹{(reportData.data.summary.total_tax || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                  </div>
                )}

                {reportData.data.details && reportData.data.details.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">GSTIN</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Taxable Value</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">CGST</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">SGST</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">IGST</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                        {reportData.data.details.map((detail, idx) => (
                          <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{detail.gstin}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              {detail.customer_name || detail.supplier_name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              ₹{(detail.total_taxable_value || 0).toLocaleString('en-IN')}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              ₹{(detail.total_cgst || 0).toLocaleString('en-IN')}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              ₹{(detail.total_sgst || 0).toLocaleString('en-IN')}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              ₹{(detail.total_igst || 0).toLocaleString('en-IN')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {reportData.data.net_gst_payable !== undefined && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Net GST Payable</div>
                    <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                      ₹{(reportData.data.net_gst_payable || 0).toLocaleString('en-IN')}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tax Reports */}
        {selectedReport === 'tax' && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <button
                onClick={() => generateReport('tax', 'tax/by-category')}
                disabled={loading}
                className="btn-primary"
              >
                Tax by Category
              </button>
              <button
                onClick={() => generateReport('tax', 'tax/by-product')}
                disabled={loading}
                className="btn-primary"
              >
                Tax by Product
              </button>
              <button
                onClick={() => generateReport('tax', 'tax/summary')}
                disabled={loading}
                className="btn-primary"
              >
                Tax Summary
              </button>
              {reportData && (
                <button onClick={exportToPDF} className="btn-secondary">
                  <Download className="w-4 h-4 mr-2" />
                  Export PDF
                </button>
              )}
            </div>

            {reportData && reportData.type === 'tax' && (
              <div className="card p-6 space-y-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{reportData.data.report_type}</h3>
                
                {reportData.data.summary && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Taxable Value</div>
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        ₹{(reportData.data.summary.total_taxable_value || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Tax</div>
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        ₹{(reportData.data.summary.total_tax || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Items Count</div>
                      <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {reportData.data.summary.categories_count || reportData.data.summary.products_count || 0}
                      </div>
                    </div>
                  </div>
                )}

                {reportData.data.details && reportData.data.details.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                            {reportData.data.report_type.includes('Category') ? 'Category' : 'Product'}
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Quantity</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Taxable Value</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Tax Rate</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Tax Amount</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                        {reportData.data.details.map((detail, idx) => (
                          <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                              {detail.category || detail.product_name || '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              {detail.total_quantity || 0}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              ₹{(detail.total_taxable_value || 0).toLocaleString('en-IN')}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              {detail.tax_rate || 0}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                              ₹{(detail.total_tax || 0).toLocaleString('en-IN')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {reportData.data.tax_by_rate && (
                  <div>
                    <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Tax by Rate</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {reportData.data.tax_by_rate.map((rate, idx) => (
                        <div key={idx} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                          <div className="text-sm text-gray-600 dark:text-gray-400">Tax Rate: {rate.rate}%</div>
                          <div className="text-lg font-semibold text-gray-900 dark:text-white">
                            ₹{(rate.tax_amount || 0).toLocaleString('en-IN')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* P&L Reports */}
        {selectedReport === 'pl' && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <button
                onClick={() => generateReport('pl', 'pl/statement')}
                disabled={loading}
                className="btn-primary"
              >
                P&L Statement
              </button>
              <button
                onClick={() => generateReport('pl', 'pl/revenue-breakdown')}
                disabled={loading}
                className="btn-primary"
              >
                Revenue Breakdown
              </button>
              <button
                onClick={() => generateReport('pl', 'pl/expense-breakdown')}
                disabled={loading}
                className="btn-primary"
              >
                Expense Breakdown
              </button>
              {reportData && (
                <button onClick={exportToPDF} className="btn-secondary">
                  <Download className="w-4 h-4 mr-2" />
                  Export PDF
                </button>
              )}
            </div>

            {reportData && reportData.type === 'pl' && (
              <div className="card p-6 space-y-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{reportData.data.report_type}</h3>
                
                {reportData.data.summary && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Revenue</div>
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                        ₹{(reportData.data.summary.total_revenue || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total COGS</div>
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                        ₹{(reportData.data.summary.total_cogs || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Gross Profit</div>
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        ₹{(reportData.data.summary.gross_profit || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Expenses</div>
                      <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                        ₹{(reportData.data.summary.total_expenses || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className={`p-4 rounded-lg ${(reportData.data.summary.net_profit || 0) >= 0 ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}`}>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Net Profit</div>
                      <div className={`text-2xl font-bold ${(reportData.data.summary.net_profit || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                        ₹{Math.abs(reportData.data.summary.net_profit || 0).toLocaleString('en-IN')}
                      </div>
                    </div>
                  </div>
                )}

                {reportData.data.revenue && (
                  <div>
                    <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Revenue Details</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Total Sales</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          ₹{(reportData.data.revenue.total_sales || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Tax Collected</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          ₹{(reportData.data.revenue.tax_collected || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Discount Given</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          ₹{(reportData.data.revenue.discount_given || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Net Revenue</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          ₹{(reportData.data.revenue.net_revenue || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {reportData.data.cost_of_goods_sold && (
                  <div>
                    <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Cost of Goods Sold</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Total COGS</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          ₹{(reportData.data.cost_of_goods_sold.total_cogs || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Gross Profit</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          ₹{(reportData.data.cost_of_goods_sold.gross_profit || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Gross Profit Margin</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          {(reportData.data.cost_of_goods_sold.gross_profit_margin || 0).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {reportData.data.expenses && reportData.data.expenses.by_category && (
                  <div>
                    <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Expenses by Category</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(reportData.data.expenses.by_category).map(([category, amount]) => (
                        <div key={category} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                          <div className="text-sm text-gray-600 dark:text-gray-400">{category}</div>
                          <div className="text-lg font-semibold text-gray-900 dark:text-white">
                            ₹{amount.toLocaleString('en-IN')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {reportData.data.net_profit && (
                  <div>
                    <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Net Profit</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className={`p-4 rounded-lg ${(reportData.data.net_profit.net_profit || 0) >= 0 ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}`}>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Net Profit</div>
                        <div className={`text-2xl font-bold ${(reportData.data.net_profit.net_profit || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                          ₹{Math.abs(reportData.data.net_profit.net_profit || 0).toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Net Profit Margin</div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {(reportData.data.net_profit.net_profit_margin || 0).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {loading && (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default AdvancedReports;





