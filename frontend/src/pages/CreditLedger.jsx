import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Search, DollarSign, CreditCard, TrendingUp, TrendingDown, X, Download, FileText } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function CreditLedger() {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showTransactions, setShowTransactions] = useState(false);
  const [selectedAccountForTransactions, setSelectedAccountForTransactions] = useState(null);
  const [transactionType, setTransactionType] = useState('credit');
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [formData, setFormData] = useState({
    customer_id: '',
    amount: '',
    description: '',
    invoice_id: '',
  });

  useEffect(() => {
    fetchAccounts();
    fetchCustomers();
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const response = await api.get('/credit/transactions/');
      setTransactions(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch transactions');
    }
  };

  const fetchAccountTransactions = async (accountId) => {
    try {
      const response = await api.get(`/credit/transactions/?customer_credit=${accountId}`);
      return response.data.results || response.data;
    } catch (error) {
      console.error('Failed to fetch account transactions');
      return [];
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await api.get('/credit/accounts/');
      setAccounts(response.data.results || response.data);
      setLoading(false);
    } catch (error) {
      toast.error('Failed to fetch credit accounts');
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/billing/customers/');
      setCustomers(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch customers');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (transactionType === 'credit') {
        await api.post(`/credit/accounts/${selectedAccount || formData.customer_id}/add_credit/`, {
          amount: formData.amount,
          description: formData.description,
          invoice_id: formData.invoice_id || null,
        });
        toast.success('Credit added successfully');
      } else {
        await api.post(`/credit/accounts/${selectedAccount || formData.customer_id}/record_payment/`, {
          amount: formData.amount,
          description: formData.description,
        });
        toast.success('Payment recorded successfully');
      }
      setShowModal(false);
      setFormData({ customer_id: '', amount: '', description: '', invoice_id: '' });
      fetchAccounts();
      fetchTransactions();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to process transaction');
    }
  };

  const handleViewTransactions = async (account) => {
    setSelectedAccountForTransactions(account);
    const accountTransactions = await fetchAccountTransactions(account.id);
    setSelectedAccountForTransactions({ ...account, transactions: accountTransactions });
    setShowTransactions(true);
  };

  const openModal = (account = null, type = 'credit') => {
    setSelectedAccount(account?.id || null);
    setTransactionType(type);
    setFormData({
      customer_id: account?.customer?.id || '',
      amount: '',
      description: '',
      invoice_id: '',
    });
    setShowModal(true);
  };

  const outstandingAccounts = accounts.filter(acc => acc.balance > 0);

  const exportToPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text('Credit Ledger Report', 14, 22);
    doc.setFontSize(11);
    
    const tableData = accounts.map(acc => [
      acc.customer?.name || 'N/A',
      acc.customer?.phone || 'N/A',
      `₹${parseFloat(acc.total_credit || 0).toFixed(2)}`,
      `₹${parseFloat(acc.total_paid || 0).toFixed(2)}`,
      `₹${parseFloat(acc.balance || 0).toFixed(2)}`,
    ]);
    
    autoTable(doc, {
      head: [['Customer', 'Phone', 'Total Credit', 'Total Paid', 'Balance']],
      body: tableData,
      startY: 30,
    });
    
    doc.save('credit_ledger_report.pdf');
    toast.success('PDF exported successfully');
  };

  const exportToExcel = () => {
    let csvContent = [];
    csvContent.push('Customer,Phone,Total Credit,Total Paid,Balance');
    accounts.forEach(acc => {
      csvContent.push([
        acc.customer?.name || 'N/A',
        acc.customer?.phone || 'N/A',
        parseFloat(acc.total_credit || 0).toFixed(2),
        parseFloat(acc.total_paid || 0).toFixed(2),
        parseFloat(acc.balance || 0).toFixed(2),
      ].join(','));
    });
    
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'credit_ledger_report.csv';
    link.click();
    toast.success('Excel exported successfully');
  };

  return (
    <DashboardLayout title="Credit Ledger (Udhar Khata)">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Credit Ledger (Udhar Khata)</h1>
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
              onClick={() => openModal(null, 'credit')}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Credit
            </button>
            <button
              onClick={() => openModal(null, 'payment')}
              className="btn-secondary flex items-center gap-2"
            >
              <CreditCard className="w-5 h-5" />
              Record Payment
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Credit Given</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  ₹{accounts.reduce((sum, acc) => sum + parseFloat(acc.total_credit || 0), 0).toLocaleString()}
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
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Payments Received</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  ₹{accounts.reduce((sum, acc) => sum + parseFloat(acc.total_paid || 0), 0).toLocaleString()}
                </p>
              </div>
              <TrendingDown className="w-12 h-12 text-green-500" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Outstanding Balance</p>
                <p className="text-2xl font-bold text-red-600 mt-2">
                  ₹{accounts.reduce((sum, acc) => sum + parseFloat(acc.balance || 0), 0).toLocaleString()}
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-red-500" />
            </div>
          </motion.div>
        </div>

        {/* Outstanding Accounts */}
        {outstandingAccounts.length > 0 && (
          <div className="card p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Outstanding Accounts</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Customer</th>
                    <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Phone</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Total Credit</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Total Paid</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Balance</th>
                    <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {outstandingAccounts.map((account) => (
                    <tr key={account.id} className="border-b border-gray-100 dark:border-gray-800">
                      <td className="py-3 px-4 text-gray-900 dark:text-white">
                        {account.customer?.name || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {account.customer?.phone || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                        ₹{parseFloat(account.total_credit || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right text-green-600">
                        ₹{parseFloat(account.total_paid || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right text-red-600 font-semibold">
                        ₹{parseFloat(account.balance || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex gap-2 justify-center">
                          <button
                            onClick={() => openModal(account, 'credit')}
                            className="btn-secondary text-sm px-3 py-1"
                          >
                            Add Credit
                          </button>
                          <button
                            onClick={() => openModal(account, 'payment')}
                            className="btn-primary text-sm px-3 py-1"
                          >
                            Payment
                          </button>
                          <button
                            onClick={() => handleViewTransactions(account)}
                            className="btn-secondary text-sm px-3 py-1"
                          >
                            View Transactions
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* All Transactions */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">All Transactions</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Date</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Customer</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Type</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Invoice</th>
                  <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Amount</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Description</th>
                </tr>
              </thead>
              <tbody>
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center py-8 text-gray-500 dark:text-gray-400">
                      No transactions found
                    </td>
                  </tr>
                ) : (
                  transactions.map((transaction) => (
                    <tr key={transaction.id} className="border-b border-gray-100 dark:border-gray-800">
                      <td className="py-3 px-4 text-gray-900 dark:text-white">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-gray-900 dark:text-white">
                        {transaction.customer_credit?.customer?.name || 'N/A'}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          transaction.transaction_type === 'credit' 
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        }`}>
                          {transaction.transaction_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {transaction.invoice_number || 'N/A'}
                      </td>
                      <td className={`py-3 px-4 text-right font-semibold ${
                        transaction.transaction_type === 'credit' ? 'text-red-600' : 'text-green-600'
                      }`}>
                        ₹{parseFloat(transaction.amount || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {transaction.description || 'N/A'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* All Accounts */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">All Credit Accounts</h2>
          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Customer</th>
                    <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Phone</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Total Credit</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Total Paid</th>
                    <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Balance</th>
                    <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((account) => (
                    <tr key={account.id} className="border-b border-gray-100 dark:border-gray-800">
                      <td className="py-3 px-4 text-gray-900 dark:text-white">
                        {account.customer?.name || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {account.customer?.phone || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                        ₹{parseFloat(account.total_credit || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right text-green-600">
                        ₹{parseFloat(account.total_paid || 0).toFixed(2)}
                      </td>
                      <td className={`py-3 px-4 text-right font-semibold ${
                        account.balance > 0 ? 'text-red-600' : 'text-gray-900 dark:text-white'
                      }`}>
                        ₹{parseFloat(account.balance || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex gap-2 justify-center">
                          <button
                            onClick={() => openModal(account, 'credit')}
                            className="btn-secondary text-sm px-3 py-1"
                          >
                            Credit
                          </button>
                          <button
                            onClick={() => openModal(account, 'payment')}
                            className="btn-primary text-sm px-3 py-1"
                          >
                            Payment
                          </button>
                          <button
                            onClick={() => handleViewTransactions(account)}
                            className="btn-secondary text-sm px-3 py-1"
                          >
                            View Transactions
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Transactions Modal */}
        {showTransactions && selectedAccountForTransactions && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Transactions - {selectedAccountForTransactions.customer?.name || 'N/A'}
                </h2>
                <button
                  onClick={() => {
                    setShowTransactions(false);
                    setSelectedAccountForTransactions(null);
                  }}
                  className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Date</th>
                      <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Type</th>
                      <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Invoice</th>
                      <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Amount</th>
                      <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(selectedAccountForTransactions.transactions || []).length === 0 ? (
                      <tr>
                        <td colSpan="5" className="text-center py-8 text-gray-500 dark:text-gray-400">
                          No transactions found
                        </td>
                      </tr>
                    ) : (
                      (selectedAccountForTransactions.transactions || []).map((transaction) => (
                        <tr key={transaction.id} className="border-b border-gray-100 dark:border-gray-800">
                          <td className="py-3 px-4 text-gray-900 dark:text-white">
                            {new Date(transaction.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              transaction.transaction_type === 'credit' 
                                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            }`}>
                              {transaction.transaction_type}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                            {transaction.invoice_number || 'N/A'}
                          </td>
                          <td className={`py-3 px-4 text-right font-semibold ${
                            transaction.transaction_type === 'credit' ? 'text-red-600' : 'text-green-600'
                          }`}>
                            ₹{parseFloat(transaction.amount || 0).toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                            {transaction.description || 'N/A'}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>
        )}

        {/* Transaction Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-md w-full"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                {transactionType === 'credit' ? 'Add Credit' : 'Record Payment'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Customer *
                  </label>
                  <select
                    required
                    value={formData.customer_id}
                    onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                    className="input-field w-full"
                    disabled={!!selectedAccount}
                  >
                    <option value="">Select Customer</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>{customer.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Amount *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    className="input-field w-full"
                    placeholder="Enter amount"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                    placeholder="Transaction description..."
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">
                    {transactionType === 'credit' ? 'Add Credit' : 'Record Payment'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setSelectedAccount(null);
                      setFormData({ customer_id: '', amount: '', description: '', invoice_id: '' });
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

export default CreditLedger;

