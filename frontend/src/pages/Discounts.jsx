import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Edit, Trash2, Tag, Percent, Calendar, Check, X } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';

function Discounts() {
  const [coupons, setCoupons] = useState([]);
  const [discounts, setDiscounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCouponModal, setShowCouponModal] = useState(false);
  const [showDiscountModal, setShowDiscountModal] = useState(false);
  const [editingCoupon, setEditingCoupon] = useState(null);
  const [editingDiscount, setEditingDiscount] = useState(null);
  const [couponData, setCouponData] = useState({
    code: '',
    name: '',
    description: '',
    discount_type: 'percentage',
    discount_value: '',
    max_discount: '',
    min_purchase_amount: '0',
    valid_from: new Date().toISOString().split('T')[0],
    valid_until: '',
    is_active: true,
    max_uses: '',
    max_uses_per_user: '1',
  });
  const [discountData, setDiscountData] = useState({
    name: '',
    description: '',
    discount_percentage: '',
    min_quantity: '1',
    is_active: true,
  });

  useEffect(() => {
    fetchCoupons();
    fetchDiscounts();
  }, []);

  const fetchCoupons = async () => {
    try {
      const response = await api.get('/discounts/coupons/');
      setCoupons(response.data.results || response.data);
      setLoading(false);
    } catch (error) {
      toast.error('Failed to fetch coupons');
      setLoading(false);
    }
  };

  const fetchDiscounts = async () => {
    try {
      const response = await api.get('/discounts/discounts/');
      setDiscounts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch discounts');
    }
  };

  const handleCouponSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCoupon) {
        await api.put(`/discounts/coupons/${editingCoupon.id}/`, couponData);
        toast.success('Coupon updated successfully');
      } else {
        await api.post('/discounts/coupons/', couponData);
        toast.success('Coupon created successfully');
      }
      setShowCouponModal(false);
      setEditingCoupon(null);
      resetCouponForm();
      fetchCoupons();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save coupon');
    }
  };

  const handleDiscountSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingDiscount) {
        await api.put(`/discounts/discounts/${editingDiscount.id}/`, discountData);
        toast.success('Discount updated successfully');
      } else {
        await api.post('/discounts/discounts/', discountData);
        toast.success('Discount created successfully');
      }
      setShowDiscountModal(false);
      setEditingDiscount(null);
      resetDiscountForm();
      fetchDiscounts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save discount');
    }
  };

  const handleDeleteCoupon = async (id) => {
    if (!window.confirm('Are you sure you want to delete this coupon?')) return;
    try {
      await api.delete(`/discounts/coupons/${id}/`);
      toast.success('Coupon deleted successfully');
      fetchCoupons();
    } catch (error) {
      toast.error('Failed to delete coupon');
    }
  };

  const handleDeleteDiscount = async (id) => {
    if (!window.confirm('Are you sure you want to delete this discount?')) return;
    try {
      await api.delete(`/discounts/discounts/${id}/`);
      toast.success('Discount deleted successfully');
      fetchDiscounts();
    } catch (error) {
      toast.error('Failed to delete discount');
    }
  };

  const handleEditCoupon = (coupon) => {
    setEditingCoupon(coupon);
    setCouponData({
      code: coupon.code || '',
      name: coupon.name || '',
      description: coupon.description || '',
      discount_type: coupon.discount_type || 'percentage',
      discount_value: coupon.discount_value || '',
      max_discount: coupon.max_discount || '',
      min_purchase_amount: coupon.min_purchase_amount || '0',
      valid_from: coupon.valid_from?.split('T')[0] || new Date().toISOString().split('T')[0],
      valid_until: coupon.valid_until?.split('T')[0] || '',
      is_active: coupon.is_active ?? true,
      max_uses: coupon.max_uses || '',
      max_uses_per_user: coupon.max_uses_per_user || '1',
    });
    setShowCouponModal(true);
  };

  const handleEditDiscount = (discount) => {
    setEditingDiscount(discount);
    setDiscountData({
      name: discount.name || '',
      description: discount.description || '',
      discount_percentage: discount.discount_percentage || '',
      min_quantity: discount.min_quantity || '1',
      is_active: discount.is_active ?? true,
    });
    setShowDiscountModal(true);
  };

  const resetCouponForm = () => {
    setCouponData({
      code: '',
      name: '',
      description: '',
      discount_type: 'percentage',
      discount_value: '',
      max_discount: '',
      min_purchase_amount: '0',
      valid_from: new Date().toISOString().split('T')[0],
      valid_until: '',
      is_active: true,
      max_uses: '',
      max_uses_per_user: '1',
    });
  };

  const resetDiscountForm = () => {
    setDiscountData({
      name: '',
      description: '',
      discount_percentage: '',
      min_quantity: '1',
      is_active: true,
    });
  };

  const isCouponValid = (coupon) => {
    const now = new Date();
    const validUntil = new Date(coupon.valid_until);
    return coupon.is_active && validUntil > now && (!coupon.max_uses || coupon.used_count < coupon.max_uses);
  };

  return (
    <DashboardLayout title="Discounts & Coupons">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Discounts & Coupons</h1>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setEditingCoupon(null);
                resetCouponForm();
                setShowCouponModal(true);
              }}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              New Coupon
            </button>
            <button
              onClick={() => {
                setEditingDiscount(null);
                resetDiscountForm();
                setShowDiscountModal(true);
              }}
              className="btn-secondary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              New Discount
            </button>
          </div>
        </div>

        {/* Coupons Section */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Coupons</h2>
          {loading ? (
            <div className="text-center py-12">Loading...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {coupons.map((coupon) => (
                <motion.div
                  key={coupon.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 rounded-lg border-2 ${
                    isCouponValid(coupon)
                      ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                      : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800'
                  }`}
                >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-lg text-gray-900 dark:text-white">{coupon.code}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{coupon.name}</p>
                      </div>
                      {isCouponValid(coupon) ? (
                        <Check className="w-5 h-5 text-green-500" />
                      ) : (
                        <X className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                    <div className="space-y-2 mb-3">
                      <p className="text-sm">
                        <span className="font-semibold text-gray-700 dark:text-gray-300">Discount: </span>
                        {coupon.discount_type === 'percentage' ? (
                          <span className="text-gray-900 dark:text-white">{coupon.discount_value}%</span>
                        ) : (
                          <span className="text-gray-900 dark:text-white">₹{coupon.discount_value}</span>
                        )}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Min Purchase: ₹{coupon.min_purchase_amount}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Valid Until: {new Date(coupon.valid_until).toLocaleDateString()}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Used: {coupon.used_count} / {coupon.max_uses || '∞'}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEditCoupon(coupon)}
                        className="btn-secondary text-sm px-3 py-1 flex-1"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteCoupon(coupon.id)}
                        className="btn-secondary text-sm px-3 py-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

        {/* Discounts Section */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Discount Rules</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Name</th>
                  <th className="text-left py-3 px-4 text-gray-700 dark:text-gray-300">Description</th>
                  <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Discount %</th>
                  <th className="text-right py-3 px-4 text-gray-700 dark:text-gray-300">Min Quantity</th>
                  <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Status</th>
                  <th className="text-center py-3 px-4 text-gray-700 dark:text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {discounts.map((discount) => (
                  <tr key={discount.id} className="border-b border-gray-100 dark:border-gray-800">
                    <td className="py-3 px-4 text-gray-900 dark:text-white">{discount.name}</td>
                    <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{discount.description || '-'}</td>
                    <td className="py-3 px-4 text-right text-gray-900 dark:text-white">
                      {discount.discount_percentage}%
                    </td>
                    <td className="py-3 px-4 text-right text-gray-600 dark:text-gray-400">
                      {discount.min_quantity}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        discount.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400'
                      }`}>
                        {discount.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex gap-2 justify-center">
                        <button
                          onClick={() => handleEditDiscount(discount)}
                          className="btn-secondary text-sm px-3 py-1"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteDiscount(discount.id)}
                          className="btn-secondary text-sm px-3 py-1 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
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
        </div>

        {/* Coupon Modal */}
        {showCouponModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                {editingCoupon ? 'Edit Coupon' : 'New Coupon'}
              </h2>
              <form onSubmit={handleCouponSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Code *</label>
                    <input
                      type="text"
                      required
                      value={couponData.code}
                      onChange={(e) => setCouponData({ ...couponData, code: e.target.value.toUpperCase() })}
                      className="input-field w-full"
                      placeholder="COUPON123"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
                    <input
                      type="text"
                      required
                      value={couponData.name}
                      onChange={(e) => setCouponData({ ...couponData, name: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Discount Type *</label>
                    <select
                      required
                      value={couponData.discount_type}
                      onChange={(e) => setCouponData({ ...couponData, discount_type: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="percentage">Percentage</option>
                      <option value="fixed">Fixed Amount</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Discount Value *</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={couponData.discount_value}
                      onChange={(e) => setCouponData({ ...couponData, discount_value: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                  {couponData.discount_type === 'percentage' && (
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Max Discount</label>
                      <input
                        type="number"
                        step="0.01"
                        value={couponData.max_discount}
                        onChange={(e) => setCouponData({ ...couponData, max_discount: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                  )}
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Min Purchase Amount</label>
                    <input
                      type="number"
                      step="0.01"
                      value={couponData.min_purchase_amount}
                      onChange={(e) => setCouponData({ ...couponData, min_purchase_amount: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Valid From *</label>
                    <input
                      type="date"
                      required
                      value={couponData.valid_from}
                      onChange={(e) => setCouponData({ ...couponData, valid_from: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Valid Until *</label>
                    <input
                      type="date"
                      required
                      value={couponData.valid_until}
                      onChange={(e) => setCouponData({ ...couponData, valid_until: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Max Uses</label>
                    <input
                      type="number"
                      value={couponData.max_uses}
                      onChange={(e) => setCouponData({ ...couponData, max_uses: e.target.value || null })}
                      className="input-field w-full"
                      placeholder="Leave empty for unlimited"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Max Uses Per User</label>
                    <input
                      type="number"
                      value={couponData.max_uses_per_user}
                      onChange={(e) => setCouponData({ ...couponData, max_uses_per_user: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                  <textarea
                    value={couponData.description}
                    onChange={(e) => setCouponData({ ...couponData, description: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={couponData.is_active}
                    onChange={(e) => setCouponData({ ...couponData, is_active: e.target.checked })}
                    className="rounded"
                  />
                  <label className="text-sm text-gray-700 dark:text-gray-300">Active</label>
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">
                    {editingCoupon ? 'Update' : 'Create'} Coupon
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCouponModal(false);
                      setEditingCoupon(null);
                      resetCouponForm();
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

        {/* Discount Modal */}
        {showDiscountModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-md w-full"
            >
              <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
                {editingDiscount ? 'Edit Discount' : 'New Discount'}
              </h2>
              <form onSubmit={handleDiscountSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
                  <input
                    type="text"
                    required
                    value={discountData.name}
                    onChange={(e) => setDiscountData({ ...discountData, name: e.target.value })}
                    className="input-field w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                  <textarea
                    value={discountData.description}
                    onChange={(e) => setDiscountData({ ...discountData, description: e.target.value })}
                    className="input-field w-full"
                    rows="3"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Discount % *</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={discountData.discount_percentage}
                      onChange={(e) => setDiscountData({ ...discountData, discount_percentage: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Min Quantity *</label>
                    <input
                      type="number"
                      required
                      value={discountData.min_quantity}
                      onChange={(e) => setDiscountData({ ...discountData, min_quantity: e.target.value })}
                      className="input-field w-full"
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={discountData.is_active}
                    onChange={(e) => setDiscountData({ ...discountData, is_active: e.target.checked })}
                    className="rounded"
                  />
                  <label className="text-sm text-gray-700 dark:text-gray-300">Active</label>
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="submit" className="btn-primary flex-1">
                    {editingDiscount ? 'Update' : 'Create'} Discount
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowDiscountModal(false);
                      setEditingDiscount(null);
                      resetDiscountForm();
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

export default Discounts;

