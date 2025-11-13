import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Download, Filter, Calendar } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function Daybook() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    entryType: '',
  });

  useEffect(() => {
    fetchEntries();
  }, [filters]);

  const fetchEntries = async () => {
    try {
      let url = '/daybook/entries/';
      const params = new URLSearchParams();
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      if (filters.entryType) params.append('entry_type', filters.entryType);
      if (params.toString()) url += `?${params.toString()}`;
      
      const response = await api.get(url);
      setEntries(response.data.results || response.data);
      setLoading(false);
    } catch (error) {
      toast.error('Failed to fetch daybook entries');
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text('Daybook Report', 14, 22);
    doc.setFontSize(11);
    
    const tableData = entries.map(entry => [
      entry.date,
      entry.entry_type,
      entry.description || 'N/A',
      `₹${entry.debit || 0}`,
      `₹${entry.credit || 0}`,
      `₹${entry.balance || 0}`,
    ]);
    
    autoTable(doc, {
      head: [['Date', 'Type', 'Description', 'Debit', 'Credit', 'Balance']],
      body: tableData,
      startY: 30,
    });
    
    doc.save('daybook_report.pdf');
    toast.success('PDF exported successfully');
  };

  const exportToExcel = () => {
    const csvContent = [
      ['Date', 'Type', 'Description', 'Debit', 'Credit', 'Balance'].join(','),
      ...entries.map(entry => [
        entry.date,
        entry.entry_type,
        entry.description || 'N/A',
        entry.debit || 0,
        entry.credit || 0,
        entry.balance || 0,
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'daybook_report.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Excel file exported successfully');
  };

  const totalDebit = entries.reduce((sum, entry) => sum + (parseFloat(entry.debit) || 0), 0);
  const totalCredit = entries.reduce((sum, entry) => sum + (parseFloat(entry.credit) || 0), 0);

  return (
    <DashboardLayout title="Daybook">
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center flex-wrap gap-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Daybook</h1>
          <div className="flex gap-2">
            <button
              onClick={exportToPDF}
              className="btn-secondary flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
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

        {/* Filters */}
        <div className="card p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Entry Type</label>
              <select
                value={filters.entryType}
                onChange={(e) => setFilters({ ...filters, entryType: e.target.value })}
                className="input-field w-full"
              >
                <option value="">All Types</option>
                <option value="sale">Sale</option>
                <option value="payment">Payment</option>
                <option value="return">Return</option>
                <option value="credit">Credit</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ startDate: '', endDate: '', entryType: '' })}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Debit</h3>
            <p className="text-2xl font-bold text-red-600">₹{totalDebit.toFixed(2)}</p>
          </div>
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Total Credit</h3>
            <p className="text-2xl font-bold text-green-600">₹{totalCredit.toFixed(2)}</p>
          </div>
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Balance</h3>
            <p className="text-2xl font-bold text-blue-600">₹{(totalCredit - totalDebit).toFixed(2)}</p>
          </div>
        </div>

        {/* Entries Table */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="card p-6 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Date</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Type</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">Description</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-900 dark:text-white">Debit</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-900 dark:text-white">Credit</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-900 dark:text-white">Balance</th>
                </tr>
              </thead>
              <tbody>
                {entries.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center py-8 text-gray-500 dark:text-gray-400">
                      No entries found
                    </td>
                  </tr>
                ) : (
                  entries.map((entry) => (
                    <motion.tr
                      key={entry.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{entry.date}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          entry.entry_type === 'sale' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          entry.entry_type === 'payment' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                          entry.entry_type === 'return' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                          'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        }`}>
                          {entry.entry_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{entry.description || 'N/A'}</td>
                      <td className="py-3 px-4 text-right text-red-600">{entry.debit ? `₹${parseFloat(entry.debit).toFixed(2)}` : '-'}</td>
                      <td className="py-3 px-4 text-right text-green-600">{entry.credit ? `₹${parseFloat(entry.credit).toFixed(2)}` : '-'}</td>
                      <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">{entry.balance ? `₹${parseFloat(entry.balance).toFixed(2)}` : '-'}</td>
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

export default Daybook;

