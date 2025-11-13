import { useState, useEffect } from 'react';
import { Package, Warehouse, TrendingUp, AlertCircle, Plus, Edit, Trash2, RefreshCw, Download, FileText, ArrowRightLeft, Calculator } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function AdvancedInventory() {
  const [selectedTab, setSelectedTab] = useState('batches'); // 'batches', 'valuations', 'adjustments', 'transfers', 'reorder-rules'
  const [batches, setBatches] = useState([]);
  const [valuations, setValuations] = useState([]);
  const [adjustments, setAdjustments] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [reorderRules, setReorderRules] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(null);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchWarehouses();
    fetchProducts();
    fetchData();
  }, [selectedTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      switch (selectedTab) {
        case 'batches':
          const batchesRes = await api.get('/inventory/batches/');
          setBatches(batchesRes.data.results || batchesRes.data);
          break;
        case 'valuations':
          const valuationsRes = await api.get('/inventory/valuations/');
          setValuations(valuationsRes.data.results || valuationsRes.data);
          break;
        case 'adjustments':
          const adjustmentsRes = await api.get('/inventory/adjustments/');
          setAdjustments(adjustmentsRes.data.results || adjustmentsRes.data);
          break;
        case 'transfers':
          const transfersRes = await api.get('/inventory/transfers/');
          setTransfers(transfersRes.data.results || transfersRes.data);
          break;
        case 'reorder-rules':
          const reorderRes = await api.get('/inventory/reorder-rules/');
          setReorderRules(reorderRes.data.results || reorderRes.data);
          break;
      }
    } catch (error) {
      console.error(`Failed to fetch ${selectedTab}:`, error);
      toast.error(`Failed to fetch ${selectedTab}`);
    } finally {
      setLoading(false);
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

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/products/');
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const handleRecalculateValuations = async () => {
    try {
      toast.loading('Recalculating valuations...', { id: 'recalculate' });
      await api.post('/inventory/valuations/recalculate/');
      toast.success('Valuations recalculated!', { id: 'recalculate' });
      fetchData();
    } catch (error) {
      toast.error('Failed to recalculate valuations', { id: 'recalculate' });
    }
  };

  const exportToPDF = () => {
    try {
      toast.loading('Generating PDF...', { id: 'pdf-export' });
      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text(`Advanced Inventory - ${selectedTab}`, 14, 15);
      doc.setFontSize(11);
      doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 22);

      let tableData = [];
      let headers = [];

      switch (selectedTab) {
        case 'batches':
          headers = [['Batch Number', 'Product', 'Warehouse', 'Quantity', 'Expiry Date', 'Status']];
          tableData = batches.map(b => [
            b.batch_number || '',
            b.product_name || '',
            b.warehouse_name || '',
            b.quantity || 0,
            b.expiry_date ? new Date(b.expiry_date).toLocaleDateString() : '-',
            b.is_active ? 'Active' : 'Inactive'
          ]);
          break;
        case 'valuations':
          headers = [['Product', 'Warehouse', 'Method', 'Quantity', 'Total Value', 'Avg Cost']];
          tableData = valuations.map(v => [
            v.product_name || '',
            v.warehouse_name || '',
            v.valuation_method || '',
            v.total_quantity || 0,
            `₹${(v.total_value || 0).toLocaleString('en-IN')}`,
            `₹${(v.average_cost || 0).toLocaleString('en-IN')}`
          ]);
          break;
        case 'adjustments':
          headers = [['Adjustment #', 'Warehouse', 'Type', 'Status', 'Date']];
          tableData = adjustments.map(a => [
            a.adjustment_number || '',
            a.warehouse_name || '',
            a.adjustment_type || '',
            a.is_approved ? 'Approved' : 'Pending',
            a.created_at ? new Date(a.created_at).toLocaleDateString() : '-'
          ]);
          break;
        case 'transfers':
          headers = [['Transfer #', 'From', 'To', 'Status', 'Date']];
          tableData = transfers.map(t => [
            t.transfer_number || '',
            t.from_warehouse_name || '',
            t.to_warehouse_name || '',
            t.status || '',
            t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'
          ]);
          break;
        case 'reorder-rules':
          headers = [['Product', 'Warehouse', 'Min Stock', 'Max Stock', 'Reorder Point', 'Status']];
          tableData = reorderRules.map(r => [
            r.product_name || '',
            r.warehouse_name || '',
            r.min_stock || 0,
            r.max_stock || 0,
            r.reorder_point || 0,
            r.is_active ? 'Active' : 'Inactive'
          ]);
          break;
      }

      autoTable(doc, {
        head: headers,
        body: tableData,
        startY: 28,
        styles: { fontSize: 9 },
        headStyles: { fillColor: [66, 139, 202] },
      });

      doc.save(`advanced_inventory_${selectedTab}_${new Date().toISOString().split('T')[0]}.pdf`);
      toast.success('PDF exported successfully!', { id: 'pdf-export' });
    } catch (error) {
      console.error('PDF export error:', error);
      toast.error('Failed to export PDF', { id: 'pdf-export' });
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Advanced Inventory">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Advanced Inventory Management">
      <div className="p-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setSelectedTab('batches')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'batches'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Package className="w-4 h-4 inline mr-2" />
            Batches
          </button>
          <button
            onClick={() => setSelectedTab('valuations')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'valuations'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Calculator className="w-4 h-4 inline mr-2" />
            Valuations
          </button>
          <button
            onClick={() => setSelectedTab('adjustments')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'adjustments'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Edit className="w-4 h-4 inline mr-2" />
            Adjustments
          </button>
          <button
            onClick={() => setSelectedTab('transfers')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'transfers'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <ArrowRightLeft className="w-4 h-4 inline mr-2" />
            Transfers
          </button>
          <button
            onClick={() => setSelectedTab('reorder-rules')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'reorder-rules'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <AlertCircle className="w-4 h-4 inline mr-2" />
            Reorder Rules
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white capitalize">{selectedTab.replace('-', ' ')}</h2>
          <div className="flex gap-2">
            {selectedTab === 'valuations' && (
              <button onClick={handleRecalculateValuations} className="btn-secondary">
                <RefreshCw className="w-4 h-4 mr-2" />
                Recalculate
              </button>
            )}
            <button onClick={exportToPDF} className="btn-secondary">
              <FileText className="w-4 h-4 mr-2" />
              Export PDF
            </button>
            <button onClick={() => { setShowModal(true); setModalType(selectedTab); }} className="btn-primary">
              <Plus className="w-4 h-4 mr-2" />
              Add New
            </button>
          </div>
        </div>

        {/* Batches Tab */}
        {selectedTab === 'batches' && (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Batch Number</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Quantity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Expiry Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {batches.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                        No batches found. Create a batch to get started.
                      </td>
                    </tr>
                  ) : (
                    batches.map((batch) => (
                      <tr key={batch.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {batch.batch_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {batch.product_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {batch.warehouse_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {batch.quantity || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {batch.expiry_date ? new Date(batch.expiry_date).toLocaleDateString() : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            batch.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          }`}>
                            {batch.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Valuations Tab */}
        {selectedTab === 'valuations' && (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Method</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Quantity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Avg Cost</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {valuations.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                        No valuations found. Valuations are calculated automatically.
                      </td>
                    </tr>
                  ) : (
                    valuations.map((valuation) => (
                      <tr key={valuation.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {valuation.product_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {valuation.warehouse_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white capitalize">
                          {valuation.valuation_method || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {valuation.total_quantity || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          ₹{(valuation.total_value || 0).toLocaleString('en-IN')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          ₹{(valuation.average_cost || 0).toLocaleString('en-IN')}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Adjustments Tab */}
        {selectedTab === 'adjustments' && (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Adjustment #</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {adjustments.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                        No adjustments found. Create an adjustment to get started.
                      </td>
                    </tr>
                  ) : (
                    adjustments.map((adjustment) => (
                      <tr key={adjustment.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {adjustment.adjustment_number || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {adjustment.warehouse_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white capitalize">
                          {adjustment.adjustment_type || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            adjustment.is_approved ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          }`}>
                            {adjustment.is_approved ? 'Approved' : 'Pending'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {adjustment.created_at ? new Date(adjustment.created_at).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Transfers Tab */}
        {selectedTab === 'transfers' && (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Transfer #</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">From</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">To</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {transfers.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                        No transfers found. Create a transfer to get started.
                      </td>
                    </tr>
                  ) : (
                    transfers.map((transfer) => (
                      <tr key={transfer.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {transfer.transfer_number || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {transfer.from_warehouse_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {transfer.to_warehouse_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            transfer.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                            transfer.status === 'in_transit' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                            'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                          }`}>
                            {transfer.status || 'Pending'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {transfer.created_at ? new Date(transfer.created_at).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Reorder Rules Tab */}
        {selectedTab === 'reorder-rules' && (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Min Stock</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Max Stock</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Reorder Point</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {reorderRules.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                        No reorder rules found. Create a reorder rule to get started.
                      </td>
                    </tr>
                  ) : (
                    reorderRules.map((rule) => (
                      <tr key={rule.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {rule.product_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {rule.warehouse_name || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {rule.min_stock || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {rule.max_stock || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {rule.reorder_point || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            rule.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          }`}>
                            {rule.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default AdvancedInventory;




