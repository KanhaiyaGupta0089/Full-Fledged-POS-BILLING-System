import { useState, useEffect } from 'react';
import { Plus, Search, Eye, Check, X, Download, FileText, Package, Building2, Receipt } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';

function PurchaseOrders() {
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [grns, setGrns] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState('pos'); // 'pos', 'suppliers', 'grns'
  const [showPOModal, setShowPOModal] = useState(false);
  const [showSupplierModal, setShowSupplierModal] = useState(false);
  const [showGRNModal, setShowGRNModal] = useState(false);
  const [editingPO, setEditingPO] = useState(null);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [poFormData, setPOFormData] = useState({
    supplier_id: '',
    warehouse_id: '',
    expected_delivery_date: '',
    notes: '',
    auto_approve: false,
  });
  const [poItems, setPOItems] = useState([]);
  const [currentItem, setCurrentItem] = useState({
    product_id: '',
    quantity: '',
    unit_price: '',
    tax_rate: '',
    discount: '',
  });
  const [supplierFormData, setSupplierFormData] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: '',
    address: '',
    gstin: '',
    payment_terms: '',
    credit_limit: '',
    is_preferred: false,
  });

  useEffect(() => {
    fetchPurchaseOrders();
    fetchSuppliers();
    fetchGRNs();
    fetchWarehouses();
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/products/');
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const fetchPurchaseOrders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/purchases/purchase-orders/');
      setPurchaseOrders(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch purchase orders:', error);
      toast.error('Failed to fetch purchase orders');
    } finally {
      setLoading(false);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const response = await api.get('/purchases/suppliers/');
      setSuppliers(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch suppliers:', error);
    }
  };

  const fetchGRNs = async () => {
    try {
      const response = await api.get('/purchases/grns/');
      setGrns(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch GRNs:', error);
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

  const handleApprove = async (poId) => {
    try {
      await api.post(`/purchases/purchase-orders/${poId}/approve/`);
      toast.success('Purchase order approved');
      fetchPurchaseOrders();
    } catch (error) {
      toast.error('Failed to approve purchase order');
    }
  };

  const handleCreateSupplier = async (e) => {
    e.preventDefault();
    try {
      // Prepare data - convert empty strings to null/0 for numeric fields
      const submitData = {
        ...supplierFormData,
        credit_limit: supplierFormData.credit_limit === '' || supplierFormData.credit_limit === null 
          ? '0.00' 
          : parseFloat(supplierFormData.credit_limit) || '0.00',
      };
      
      if (editingSupplier) {
        await api.patch(`/purchases/suppliers/${editingSupplier.id}/`, submitData);
        toast.success('Supplier updated');
      } else {
        await api.post('/purchases/suppliers/', submitData);
        toast.success('Supplier created');
      }
      setShowSupplierModal(false);
      setEditingSupplier(null);
      setSupplierFormData({
        name: '',
        company_name: '',
        email: '',
        phone: '',
        address: '',
        gstin: '',
        payment_terms: '',
        credit_limit: '',
        is_preferred: false,
      });
      fetchSuppliers();
    } catch (error) {
      console.error('Supplier error:', error.response?.data);
      const errorMsg = error.response?.data?.detail || 
                      error.response?.data?.name?.[0] ||
                      error.response?.data?.credit_limit?.[0] ||
                      error.response?.data?.non_field_errors?.[0] ||
                      'Failed to save supplier';
      toast.error(errorMsg);
    }
  };

  const handleAddPOItem = () => {
    if (!currentItem.product_id || !currentItem.quantity || !currentItem.unit_price) {
      toast.error('Please fill in product, quantity, and unit price');
      return;
    }
    
    const product = products.find(p => p.id === parseInt(currentItem.product_id));
    const item = {
      product: parseInt(currentItem.product_id),
      quantity: parseInt(currentItem.quantity),
      unit_price: parseFloat(currentItem.unit_price),
      tax_rate: parseFloat(currentItem.tax_rate) || (product?.tax_rate || 0),
      discount: parseFloat(currentItem.discount) || 0,
    };
    
    setPOItems([...poItems, item]);
    setCurrentItem({
      product_id: '',
      quantity: '',
      unit_price: '',
      tax_rate: '',
      discount: '',
    });
  };

  const handleRemovePOItem = (index) => {
    setPOItems(poItems.filter((_, i) => i !== index));
  };

  const handleCreatePO = async (e) => {
    e.preventDefault();
    if (!poFormData.supplier_id || !poFormData.warehouse_id) {
      toast.error('Please select supplier and warehouse');
      return;
    }
    if (poItems.length === 0) {
      toast.error('Please add at least one item');
      return;
    }
    
    try {
      const submitData = {
        ...poFormData,
        items_data: poItems,
      };
      
      await api.post('/purchases/purchase-orders/', submitData);
      toast.success('Purchase order created successfully');
      setShowPOModal(false);
      setPOFormData({
        supplier_id: '',
        warehouse_id: '',
        expected_delivery_date: '',
        notes: '',
        auto_approve: false,
      });
      setPOItems([]);
      fetchPurchaseOrders();
    } catch (error) {
      console.error('PO error:', error.response?.data);
      const errorMsg = error.response?.data?.detail || 
                      error.response?.data?.non_field_errors?.[0] ||
                      'Failed to create purchase order';
      toast.error(errorMsg);
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Purchase Orders">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Purchase Orders & Suppliers">
      <div className="p-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setSelectedTab('pos')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'pos'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Package className="w-4 h-4 inline mr-2" />
            Purchase Orders
          </button>
          <button
            onClick={() => setSelectedTab('suppliers')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'suppliers'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Building2 className="w-4 h-4 inline mr-2" />
            Suppliers
          </button>
          <button
            onClick={() => setSelectedTab('grns')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'grns'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Receipt className="w-4 h-4 inline mr-2" />
            GRNs
          </button>
        </div>

        {/* Purchase Orders Tab */}
        {selectedTab === 'pos' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search purchase orders..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>
              <button onClick={() => setShowPOModal(true)} className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                Create PO
              </button>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">PO Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Supplier</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {purchaseOrders.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                          No purchase orders found
                        </td>
                      </tr>
                    ) : (
                      purchaseOrders.filter(po => 
                        po.po_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        po.supplier_name?.toLowerCase().includes(searchQuery.toLowerCase())
                      ).map((po) => (
                        <tr key={po.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {po.po_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {po.supplier_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {po.warehouse_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            ₹{parseFloat(po.total_amount || 0).toLocaleString('en-IN')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              po.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              po.status === 'received' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                              po.status === 'cancelled' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                            }`}>
                              {po.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {po.order_date ? new Date(po.order_date).toLocaleDateString() : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex justify-end gap-2">
                              {po.status === 'draft' && (
                                <button
                                  onClick={() => handleApprove(po.id)}
                                  className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                                  title="Approve"
                                >
                                  <Check className="w-4 h-4" />
                                </button>
                              )}
                              <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300" title="View">
                                <Eye className="w-4 h-4" />
                              </button>
                            </div>
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

        {/* Suppliers Tab */}
        {selectedTab === 'suppliers' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search suppliers..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>
              <button onClick={() => { setShowSupplierModal(true); setEditingSupplier(null); }} className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                Add Supplier
              </button>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Company</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Contact</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total Purchases</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Rating</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {suppliers.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                          No suppliers found
                        </td>
                      </tr>
                    ) : (
                      suppliers.filter(s => 
                        s.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        s.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
                      ).map((supplier) => (
                        <tr key={supplier.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {supplier.name}
                            {supplier.is_preferred && (
                              <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 rounded">
                                Preferred
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {supplier.company_name || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            <div>{supplier.email || '-'}</div>
                            <div className="text-xs text-gray-500">{supplier.phone || '-'}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            ₹{parseFloat(supplier.total_purchases || 0).toLocaleString('en-IN')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className="text-sm font-medium">{supplier.rating || '5.0'}</span>
                              <span className="text-yellow-500 ml-1">★</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => {
                                setEditingSupplier(supplier);
                                setSupplierFormData({
                                  name: supplier.name || '',
                                  company_name: supplier.company_name || '',
                                  email: supplier.email || '',
                                  phone: supplier.phone || '',
                                  address: supplier.address || '',
                                  gstin: supplier.gstin || '',
                                  payment_terms: supplier.payment_terms || '',
                                  credit_limit: supplier.credit_limit || '',
                                  is_preferred: supplier.is_preferred || false,
                                });
                                setShowSupplierModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                            >
                              <Eye className="w-4 h-4" />
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

        {/* GRNs Tab */}
        {selectedTab === 'grns' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search GRNs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>
              <button onClick={() => setShowGRNModal(true)} className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                Create GRN
              </button>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">GRN Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">PO Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Warehouse</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {grns.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                          No GRNs found
                        </td>
                      </tr>
                    ) : (
                      grns.filter(grn => 
                        grn.grn_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        grn.purchase_order_number?.toLowerCase().includes(searchQuery.toLowerCase())
                      ).map((grn) => (
                        <tr key={grn.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {grn.grn_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {grn.purchase_order_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {grn.warehouse_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            ₹{parseFloat(grn.total_amount || 0).toLocaleString('en-IN')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              grn.is_verified ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                            }`}>
                              {grn.is_verified ? 'Verified' : 'Pending'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {grn.received_at ? new Date(grn.received_at).toLocaleDateString() : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300" title="View">
                              <Eye className="w-4 h-4" />
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

        {/* Supplier Modal */}
        {showSupplierModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                  {editingSupplier ? 'Edit Supplier' : 'Add Supplier'}
                </h2>
                <form onSubmit={handleCreateSupplier} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
                      <input
                        type="text"
                        required
                        value={supplierFormData.name}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, name: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Company Name</label>
                      <input
                        type="text"
                        value={supplierFormData.company_name}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, company_name: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Email</label>
                      <input
                        type="email"
                        value={supplierFormData.email}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, email: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Phone</label>
                      <input
                        type="tel"
                        value={supplierFormData.phone}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, phone: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Address</label>
                      <textarea
                        value={supplierFormData.address}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, address: e.target.value })}
                        className="input-field w-full"
                        rows="2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">GSTIN</label>
                      <input
                        type="text"
                        value={supplierFormData.gstin}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, gstin: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Payment Terms</label>
                      <input
                        type="text"
                        value={supplierFormData.payment_terms}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, payment_terms: e.target.value })}
                        placeholder="e.g., Net 30"
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Credit Limit</label>
                      <input
                        type="number"
                        step="0.01"
                        value={supplierFormData.credit_limit}
                        onChange={(e) => setSupplierFormData({ ...supplierFormData, credit_limit: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={supplierFormData.is_preferred}
                          onChange={(e) => setSupplierFormData({ ...supplierFormData, is_preferred: e.target.checked })}
                          className="rounded"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Preferred Supplier</span>
                      </label>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => { setShowSupplierModal(false); setEditingSupplier(null); }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      {editingSupplier ? 'Update' : 'Create'} Supplier
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Purchase Order Modal */}
        {showPOModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                  {editingPO ? 'Edit Purchase Order' : 'Create Purchase Order'}
                </h2>
                <form onSubmit={handleCreatePO} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Supplier *</label>
                      <select
                        required
                        value={poFormData.supplier_id}
                        onChange={(e) => setPOFormData({ ...poFormData, supplier_id: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">Select Supplier</option>
                        {suppliers.map(s => (
                          <option key={s.id} value={s.id}>{s.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Warehouse *</label>
                      <select
                        required
                        value={poFormData.warehouse_id}
                        onChange={(e) => setPOFormData({ ...poFormData, warehouse_id: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">Select Warehouse</option>
                        {warehouses.map(w => (
                          <option key={w.id} value={w.id}>{w.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Expected Delivery Date</label>
                      <input
                        type="date"
                        value={poFormData.expected_delivery_date}
                        onChange={(e) => setPOFormData({ ...poFormData, expected_delivery_date: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div className="flex items-center">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={poFormData.auto_approve}
                          onChange={(e) => setPOFormData({ ...poFormData, auto_approve: e.target.checked })}
                          className="rounded"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Auto Approve</span>
                      </label>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Notes</label>
                      <textarea
                        value={poFormData.notes}
                        onChange={(e) => setPOFormData({ ...poFormData, notes: e.target.value })}
                        className="input-field w-full"
                        rows="2"
                      />
                    </div>
                  </div>

                  {/* Add Items Section */}
                  <div className="border-t pt-4 mt-4">
                    <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">Items</h3>
                    <div className="grid grid-cols-5 gap-2 mb-2">
                      <select
                        value={currentItem.product_id}
                        onChange={(e) => {
                          const product = products.find(p => p.id === parseInt(e.target.value));
                          setCurrentItem({
                            ...currentItem,
                            product_id: e.target.value,
                            unit_price: product?.cost_price || '',
                            tax_rate: product?.tax_rate || '',
                          });
                        }}
                        className="input-field"
                      >
                        <option value="">Select Product</option>
                        {products.map(p => (
                          <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                      </select>
                      <input
                        type="number"
                        placeholder="Quantity"
                        value={currentItem.quantity}
                        onChange={(e) => setCurrentItem({ ...currentItem, quantity: e.target.value })}
                        className="input-field"
                        min="1"
                      />
                      <input
                        type="number"
                        step="0.01"
                        placeholder="Unit Price"
                        value={currentItem.unit_price}
                        onChange={(e) => setCurrentItem({ ...currentItem, unit_price: e.target.value })}
                        className="input-field"
                      />
                      <input
                        type="number"
                        step="0.01"
                        placeholder="Tax %"
                        value={currentItem.tax_rate}
                        onChange={(e) => setCurrentItem({ ...currentItem, tax_rate: e.target.value })}
                        className="input-field"
                      />
                      <div className="flex gap-2">
                        <input
                          type="number"
                          step="0.01"
                          placeholder="Discount"
                          value={currentItem.discount}
                          onChange={(e) => setCurrentItem({ ...currentItem, discount: e.target.value })}
                          className="input-field flex-1"
                        />
                        <button
                          type="button"
                          onClick={handleAddPOItem}
                          className="btn-primary px-3"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Items List */}
                    {poItems.length > 0 && (
                      <div className="mt-4 border rounded-lg overflow-hidden">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                          <thead className="bg-gray-50 dark:bg-gray-800">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Product</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Qty</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Price</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Tax %</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Discount</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Total</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Action</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                            {poItems.map((item, index) => {
                              const product = products.find(p => p.id === item.product);
                              const subtotal = item.unit_price * item.quantity;
                              const afterDiscount = subtotal - (item.discount || 0);
                              const tax = (afterDiscount * (item.tax_rate || 0)) / 100;
                              const total = afterDiscount + tax;
                              return (
                                <tr key={index}>
                                  <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{product?.name || 'N/A'}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{item.quantity}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">₹{item.unit_price.toFixed(2)}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">{item.tax_rate || 0}%</td>
                                  <td className="px-4 py-2 text-sm text-gray-900 dark:text-white">₹{(item.discount || 0).toFixed(2)}</td>
                                  <td className="px-4 py-2 text-sm text-right text-gray-900 dark:text-white">₹{total.toFixed(2)}</td>
                                  <td className="px-4 py-2 text-right">
                                    <button
                                      type="button"
                                      onClick={() => handleRemovePOItem(index)}
                                      className="text-red-600 hover:text-red-900 dark:text-red-400"
                                    >
                                      <X className="w-4 h-4" />
                                    </button>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowPOModal(false);
                        setEditingPO(null);
                        setPOFormData({
                          supplier_id: '',
                          warehouse_id: '',
                          expected_delivery_date: '',
                          notes: '',
                          auto_approve: false,
                        });
                        setPOItems([]);
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      {editingPO ? 'Update' : 'Create'} Purchase Order
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

export default PurchaseOrders;
