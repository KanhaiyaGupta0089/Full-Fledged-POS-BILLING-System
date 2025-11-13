import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Plus, Search, X, QrCode, Barcode, Trash2, CreditCard, Receipt, Check, Download, Mail, Printer } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import { Html5Qrcode } from 'html5-qrcode';

function Billing() {
  const [cart, setCart] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showScanner, setShowScanner] = useState(false);
  const [customer, setCustomer] = useState({ name: '', phone: '', email: '' });
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [discountCode, setDiscountCode] = useState('');
  const [discountAmount, setDiscountAmount] = useState(0);
  const [availableCoupons, setAvailableCoupons] = useState([]);
  const [selectedCoupon, setSelectedCoupon] = useState(null);
  const [scanner, setScanner] = useState(null);
  const scannerRef = useRef(null);
  const isScanningRef = useRef(false);
  const isProcessingScanRef = useRef(false);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [createdInvoice, setCreatedInvoice] = useState(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (scanner && isScanningRef.current) {
        scanner.stop().catch(() => {});
        scanner.clear().catch(() => {});
      }
    };
  }, [scanner]);

  // Fetch available coupons when cart changes
  useEffect(() => {
    const fetchAvailableCoupons = async () => {
      try {
        const { subtotal } = calculateTotals();
        const response = await api.get(`/discounts/coupons/available/?amount=${subtotal}`);
        setAvailableCoupons(response.data || []);
      } catch (error) {
        console.error('Failed to fetch available coupons:', error);
        setAvailableCoupons([]);
      }
    };

    if (cart.length > 0) {
      fetchAvailableCoupons();
    } else {
      setAvailableCoupons([]);
      setSelectedCoupon(null);
      setDiscountAmount(0);
      setDiscountCode('');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cart]);

  const searchProducts = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const response = await api.get(`/products/products/search/?q=${encodeURIComponent(query)}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    searchProducts(query);
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product.id === product.id);
    if (existingItem) {
      setCart(cart.map(item =>
        item.product.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, {
        product,
        quantity: 1,
        unit_price: parseFloat(product.selling_price),
        discount: 0,
        tax_rate: parseFloat(product.tax_rate || 0),
      }]);
    }
    setSearchQuery('');
    setSearchResults([]);
    toast.success(`${product.name} added to cart`);
  };

  const removeFromCart = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const updateQuantity = (index, quantity) => {
    if (quantity <= 0) {
      removeFromCart(index);
      return;
    }
    setCart(cart.map((item, i) =>
      i === index ? { ...item, quantity: parseInt(quantity) } : item
    ));
  };

  const calculateTotals = () => {
    const subtotal = cart.reduce((sum, item) => {
      const itemTotal = item.unit_price * item.quantity - item.discount;
      return sum + itemTotal;
    }, 0);
    const tax = cart.reduce((sum, item) => {
      const itemTotal = item.unit_price * item.quantity - item.discount;
      return sum + (itemTotal * item.tax_rate / 100);
    }, 0);
    const total = subtotal + tax - discountAmount;
    return { subtotal, tax, total };
  };

  const startQRScanner = async () => {
    try {
      // Clear any existing scanner first
      if (scanner && isScanningRef.current) {
        try {
          await scanner.stop();
          scanner.clear();
        } catch (e) {
          // Ignore cleanup errors - scanner might already be stopped
          console.debug('Cleanup error (ignored):', e.message);
        }
        setScanner(null);
        isScanningRef.current = false;
      }
      
      // Small delay to ensure cleanup is complete
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const html5QrCode = new Html5Qrcode("qr-reader");
      isScanningRef.current = true;
      
      await html5QrCode.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0
        },
        async (decodedText) => {
          // Prevent multiple scans from being processed simultaneously
          if (isProcessingScanRef.current) {
            return;
          }
          
          isProcessingScanRef.current = true;
          
          // Stop scanner immediately after successful scan
          if (isScanningRef.current) {
            try {
              await html5QrCode.stop();
              html5QrCode.clear();
              isScanningRef.current = false;
              setScanner(null);
              setShowScanner(false);
            } catch (e) {
              // Ignore errors if scanner is already stopped
              console.debug('Stop error (ignored):', e.message);
              isScanningRef.current = false;
              setScanner(null);
              setShowScanner(false);
            }
          }
          
          // Process the scanned QR code
          try {
            await handleQRScan(decodedText);
          } finally {
            isProcessingScanRef.current = false;
          }
        },
        (errorMessage) => {
          // Ignore scanning errors (they're frequent during scanning)
          // Only log if it's a critical error
          if (errorMessage && !errorMessage.includes('NotFoundException')) {
            console.debug('QR scan error:', errorMessage);
          }
        }
      );
      setScanner(html5QrCode);
    } catch (err) {
      console.error('Failed to start camera:', err);
      toast.error('Failed to start camera. Please check permissions.');
      isScanningRef.current = false;
      setScanner(null);
      setShowScanner(false);
    }
  };

  const stopQRScanner = async () => {
    if (scanner && isScanningRef.current) {
      try {
        await scanner.stop();
        scanner.clear();
        isScanningRef.current = false;
      } catch (e) {
        // Ignore errors if scanner is already stopped
        console.debug('Stop error (ignored):', e.message);
        isScanningRef.current = false;
      }
      setScanner(null);
    }
    setShowScanner(false);
  };

  const handleQRScan = async (qrCode) => {
    try {
      // Clean the QR code - remove whitespace and newlines
      const cleanedQR = qrCode.trim().replace(/\s+/g, '');
      
      if (!cleanedQR) {
        toast.error('Invalid QR code scanned');
        return;
      }
      
      console.log('Scanning QR code:', cleanedQR);
      
      const response = await api.get(`/products/products/by_qr/?qr=${encodeURIComponent(cleanedQR)}`);
      
      if (response.data) {
        addToCart(response.data);
        toast.success('Product added to cart');
      } else {
        toast.error('Product not found');
      }
    } catch (error) {
      console.error('QR scan error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Product not found';
      toast.error(errorMessage);
    }
  };

  const handleBarcodeScan = async (barcode) => {
    try {
      const response = await api.get(`/products/products/by_barcode/?barcode=${encodeURIComponent(barcode)}`);
      addToCart(response.data);
    } catch (error) {
      toast.error('Product not found');
    }
  };

  const applyDiscount = async () => {
    if (!discountCode.trim()) return;
    try {
      const { subtotal } = calculateTotals();
      const response = await api.get(`/discounts/coupons/validate/?code=${encodeURIComponent(discountCode)}&amount=${subtotal}`);
      if (response.data.valid) {
        setDiscountAmount(response.data.discount_amount);
        toast.success('Discount applied');
      } else {
        toast.error('Invalid discount code');
      }
    } catch (error) {
      toast.error('Failed to validate discount code');
    }
  };

  const handleCouponSelect = (couponId) => {
    if (!couponId) {
      setSelectedCoupon(null);
      setDiscountCode('');
      setDiscountAmount(0);
      return;
    }

    const coupon = availableCoupons.find(c => c.id === parseInt(couponId));
    if (coupon) {
      setSelectedCoupon(coupon);
      setDiscountCode(coupon.code);
      setDiscountAmount(coupon.calculated_discount || 0);
      toast.success(`Coupon "${coupon.code}" applied!`);
    }
  };

  const formatCouponDisplay = (coupon) => {
    let discountText = '';
    if (coupon.discount_type === 'percentage') {
      discountText = `${coupon.discount_value}% off`;
      if (coupon.max_discount) {
        discountText += ` (max Rs. ${coupon.max_discount})`;
      }
    } else {
      discountText = `Rs. ${coupon.discount_value} off`;
    }
    
    let minPurchase = '';
    if (coupon.min_purchase_amount > 0) {
      minPurchase = ` - Min: Rs. ${coupon.min_purchase_amount}`;
    }

    return `${coupon.code} - ${coupon.name} (${discountText}${minPurchase})`;
  };

  const createInvoice = async () => {
    if (cart.length === 0) {
      toast.error('Cart is empty');
      return;
    }

    const { subtotal, tax, total } = calculateTotals();

    try {
      // Create or get customer if name/phone provided
      let customerId = null;
      if (customer.name && customer.phone) {
        try {
          // Try to find existing customer
          const customersResponse = await api.get(`/billing/customers/?phone=${customer.phone}`);
          if (customersResponse.data.results && customersResponse.data.results.length > 0) {
            customerId = customersResponse.data.results[0].id;
          } else {
            // Create new customer
            const newCustomer = await api.post('/billing/customers/', {
              name: customer.name,
              phone: customer.phone,
              email: customer.email || '',
            });
            customerId = newCustomer.data.id;
          }
        } catch (error) {
          console.error('Error creating/finding customer:', error);
        }
      }

      const invoiceData = {
        customer: customerId,
        customer_name: customer.name || 'Walk-in Customer',
        customer_phone: customer.phone || '',
        customer_email: customer.email || '',
        subtotal: subtotal.toFixed(2),
        discount_amount: discountAmount.toFixed(2),
        tax_amount: tax.toFixed(2),
        total_amount: total.toFixed(2),
        paid_amount: paymentMethod === 'cash' ? total.toFixed(2) : (paymentMethod === 'credit' ? '0.00' : '0.00'),
        payment_method: paymentMethod === 'online' ? 'upi' : paymentMethod, // Map online to upi for backend
        status: paymentMethod === 'cash' ? 'paid' : (paymentMethod === 'credit' ? 'pending' : 'pending'),
        items: cart.map(item => ({
          product: item.product.id,
          quantity: item.quantity,
          unit_price: item.unit_price.toFixed(2),
          discount: item.discount.toFixed(2),
          tax_rate: item.tax_rate.toFixed(2),
        })),
      };

      const response = await api.post('/billing/invoices/', invoiceData);
      const invoiceData_full = response.data;
      
      // If online payment, initiate Razorpay checkout
      if (paymentMethod === 'online') {
        await initiateRazorpayPayment(invoiceData_full);
        return; // Don't show invoice modal yet, wait for payment
      }
      
      // The invoice ID should be in the response
      // If not, try to use the invoice_number to fetch it
      if (invoiceData_full && invoiceData_full.id) {
        try {
          const fullInvoiceResponse = await api.get(`/billing/invoices/${invoiceData_full.id}/`);
          setCreatedInvoice(fullInvoiceResponse.data);
          setShowInvoiceModal(true);
        } catch (error) {
          console.error('Failed to fetch invoice details:', error);
          // Still show success but without modal
          setCreatedInvoice(invoiceData_full);
          setShowInvoiceModal(true);
        }
      } else if (invoiceData_full && invoiceData_full.invoice_number) {
        // Fallback: try to find invoice by invoice_number
        try {
          const invoicesResponse = await api.get(`/billing/invoices/?invoice_number=${invoiceData_full.invoice_number}`);
          const invoices = invoicesResponse.data.results || invoicesResponse.data;
          if (invoices && invoices.length > 0) {
            const fullInvoiceResponse = await api.get(`/billing/invoices/${invoices[0].id}/`);
            setCreatedInvoice(fullInvoiceResponse.data);
            setShowInvoiceModal(true);
          } else {
            setCreatedInvoice(invoiceData_full);
            setShowInvoiceModal(true);
          }
        } catch (error) {
          console.error('Failed to fetch invoice by number:', error);
          setCreatedInvoice(invoiceData_full);
          setShowInvoiceModal(true);
        }
      } else {
        // Fallback: use the response data directly
        setCreatedInvoice(invoiceData_full);
        setShowInvoiceModal(true);
      }
      
      // Check if email was sent
      const customerEmail = invoiceData_full.customer_email || (invoiceData_full.customer?.email);
      let successMessage = `Invoice ${invoiceData_full.invoice_number} created successfully!`;
      if (customerEmail) {
        successMessage += ` Invoice sent to ${customerEmail}`;
      }
      
      toast.success(successMessage, {
        duration: 5000,
        style: {
          background: '#10b981',
          color: '#fff',
          fontSize: '16px',
          fontWeight: 'bold',
        },
      });
      
      // Reset form
      setCart([]);
      setCustomer({ name: '', phone: '', email: '' });
      setPaymentMethod('cash');
      setDiscountCode('');
      setDiscountAmount(0);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create invoice');
    }
  };

  const initiateRazorpayPayment = async (invoice) => {
    try {
      // Get Razorpay key from backend or env
      const RAZORPAY_KEY_ID = import.meta.env.VITE_RAZORPAY_KEY_ID || '';
      
      if (!RAZORPAY_KEY_ID) {
        toast.error('Razorpay key not configured. Please contact administrator.');
        // Still show invoice modal
        setCreatedInvoice(invoice);
        setShowInvoiceModal(true);
        return;
      }

      // Create Razorpay order
      const orderResponse = await api.post('/payments/transactions/create_order/', {
        invoice_id: invoice.id,
        key_id: RAZORPAY_KEY_ID,
      }).catch(error => {
        console.error('Create order error:', error);
        console.error('Error response:', error.response);
        throw error;
      });

      const { order_id, amount, currency, amount_to_pay } = orderResponse.data;

      // Initialize Razorpay checkout
      const options = {
        key: RAZORPAY_KEY_ID,
        amount: amount, // Amount in paise
        currency: currency,
        name: 'POS Billing System',
        description: `Payment for Invoice ${invoice.invoice_number}`,
        order_id: order_id,
        handler: async function (response) {
          // Payment successful
          try {
            // Verify payment with backend
            const verifyResponse = await api.post('/payments/transactions/verify_payment/', {
              invoice_id: invoice.id,
              order_id: response.razorpay_order_id,
              payment_id: response.razorpay_payment_id,
              signature: response.razorpay_signature,
            });

            if (verifyResponse.data.success) {
              // Fetch updated invoice
              const updatedInvoice = await api.get(`/billing/invoices/${invoice.id}/`);
              setCreatedInvoice(updatedInvoice.data);
              
              // Check if email was sent
              const customerEmail = updatedInvoice.data.customer_email || (updatedInvoice.data.customer?.email);
              let successMessage = 'Payment successful! Invoice updated.';
              if (customerEmail) {
                successMessage += ` Invoice sent to ${customerEmail}`;
              }
              toast.success(successMessage);
              
              setShowInvoiceModal(true);
              
              // Clear cart
              setCart([]);
              setCustomer({ name: '', phone: '', email: '' });
              setPaymentMethod('cash');
              setDiscountCode('');
              setDiscountAmount(0);
              setSelectedCoupon(null);
            } else {
              toast.error('Payment verification failed. Please contact support.');
            }
          } catch (error) {
            console.error('Payment verification error:', error);
            toast.error('Payment verification failed. Please contact support with payment ID: ' + response.razorpay_payment_id);
          }
        },
        prefill: {
          name: invoice.customer_name || 'Customer',
          email: invoice.customer_email || '',
          contact: invoice.customer_phone || '',
        },
        theme: {
          color: '#3b82f6',
        },
        modal: {
          ondismiss: function() {
            toast.info('Payment cancelled. Invoice created but not paid.');
            // Still show invoice modal
            setCreatedInvoice(invoice);
            setShowInvoiceModal(true);
          }
        }
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error) {
      console.error('Razorpay payment initiation error:', error);
      toast.error(error.response?.data?.error || 'Failed to initiate payment. Please try again.');
      // Still show invoice modal
      setCreatedInvoice(invoice);
      setShowInvoiceModal(true);
    }
  };

  const { subtotal, tax, total } = calculateTotals();

  return (
    <DashboardLayout title="Billing">
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Product Search & Cart */}
          <div className="lg:col-span-2 space-y-6">
            {/* Search Bar */}
            <div className="card p-4">
              <div className="flex gap-2 mb-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search by name, SKU, barcode, or product ID..."
                    value={searchQuery}
                    onChange={handleSearch}
                    className="input-field pl-10 w-full"
                  />
                </div>
                <button
                  onClick={() => {
                    setShowScanner(true);
                    setTimeout(startQRScanner, 100);
                  }}
                  className="btn-secondary px-4"
                  title="Scan QR Code"
                >
                  <QrCode className="w-5 h-5" />
                </button>
                <button
                  onClick={() => {
                    const barcode = prompt('Enter barcode:');
                    if (barcode) handleBarcodeScan(barcode);
                  }}
                  className="btn-secondary px-4"
                  title="Scan Barcode"
                >
                  <Barcode className="w-5 h-5" />
                </button>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="mt-4 space-y-2 max-h-60 overflow-y-auto">
                  {searchResults.map((product) => (
                    <div
                      key={product.id}
                      onClick={() => addToCart(product)}
                      className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">{product.name}</h4>
                          <p className="text-sm text-gray-500 dark:text-gray-400">SKU: {product.sku} | ₹{product.selling_price}</p>
                        </div>
                        <button className="btn-primary text-sm px-3 py-1">
                          Add
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* QR Scanner Modal */}
              {showScanner && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="card max-w-md w-full"
                  >
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">Scan QR Code</h3>
                      <button onClick={stopQRScanner} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                        <X className="w-6 h-6" />
                      </button>
                    </div>
                    <div id="qr-reader" className="w-full"></div>
                  </motion.div>
                </div>
              )}
            </div>

            {/* Cart */}
            <div className="card p-4">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Cart</h2>
              {cart.length === 0 ? (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">Cart is empty</p>
              ) : (
                <div className="space-y-3">
                  {cart.map((item, index) => (
                    <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 dark:text-white">{item.product.name}</h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400">₹{item.unit_price} × {item.quantity}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => updateQuantity(index, item.quantity - 1)}
                          className="btn-secondary px-2 py-1"
                        >
                          -
                        </button>
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => updateQuantity(index, parseInt(e.target.value) || 0)}
                          className="w-16 text-center input-field"
                          min="1"
                        />
                        <button
                          onClick={() => updateQuantity(index, item.quantity + 1)}
                          className="btn-secondary px-2 py-1"
                        >
                          +
                        </button>
                        <button
                          onClick={() => removeFromCart(index)}
                          className="text-red-600 hover:text-red-700 ml-2"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900 dark:text-white">
                          ₹{(item.unit_price * item.quantity).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Customer & Payment */}
          <div className="space-y-6">
            {/* Customer Info */}
            <div className="card p-4">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Customer</h2>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Customer Name"
                  value={customer.name}
                  onChange={(e) => setCustomer({ ...customer, name: e.target.value })}
                  className="input-field w-full"
                />
                <input
                  type="tel"
                  placeholder="Phone"
                  value={customer.phone}
                  onChange={(e) => setCustomer({ ...customer, phone: e.target.value })}
                  className="input-field w-full"
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={customer.email}
                  onChange={(e) => setCustomer({ ...customer, email: e.target.value })}
                  className="input-field w-full"
                />
              </div>
            </div>

            {/* Discount */}
            <div className="card p-4">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Discount</h2>
              <div className="space-y-3">
                <select
                  value={selectedCoupon?.id || ''}
                  onChange={(e) => handleCouponSelect(e.target.value)}
                  className="input-field w-full"
                >
                  <option value="">Select a coupon (or enter code manually)</option>
                  {availableCoupons.map((coupon) => (
                    <option key={coupon.id} value={coupon.id}>
                      {formatCouponDisplay(coupon)}
                    </option>
                  ))}
                </select>
                
                {/* Manual coupon code input (optional) */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Or enter coupon code manually"
                    value={discountCode}
                    onChange={(e) => setDiscountCode(e.target.value)}
                    className="input-field flex-1"
                    disabled={!!selectedCoupon}
                  />
                  {!selectedCoupon && (
                    <button onClick={applyDiscount} className="btn-secondary px-4">
                      Apply
                    </button>
                  )}
                  {selectedCoupon && (
                    <button 
                      onClick={() => handleCouponSelect('')} 
                      className="btn-secondary px-4 bg-red-600 hover:bg-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>
                
                {discountAmount > 0 && (
                  <div className="mt-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-green-700 dark:text-green-400 font-semibold">
                      Discount Applied: ₹{discountAmount.toFixed(2)}
                    </p>
                    {selectedCoupon && (
                      <p className="text-sm text-green-600 dark:text-green-500 mt-1">
                        {selectedCoupon.name} - {selectedCoupon.description}
                      </p>
                    )}
                  </div>
                )}
                
                {availableCoupons.length === 0 && cart.length > 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    No coupons available for this purchase amount.
                  </p>
                )}
              </div>
            </div>

            {/* Payment */}
            <div className="card p-4">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Payment</h2>
              <div className="space-y-3">
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="input-field w-full"
                >
                  <option value="cash">Cash</option>
                  <option value="online">Online Payment (Razorpay)</option>
                  <option value="card">Card</option>
                  <option value="upi">UPI</option>
                  <option value="credit">Credit (Udhar)</option>
                </select>
                
                {paymentMethod === 'upi' && (
                  <div className="space-y-2">
                    <input
                      type="text"
                      placeholder="UPI Transaction ID"
                      className="input-field w-full"
                      id="upi_transaction_id"
                    />
                    <input
                      type="text"
                      placeholder="UPI Reference"
                      className="input-field w-full"
                      id="upi_reference"
                    />
                  </div>
                )}
                
                {paymentMethod === 'card' && (
                  <div className="space-y-2">
                    <input
                      type="text"
                      placeholder="Card Last 4 Digits"
                      className="input-field w-full"
                      id="card_last4"
                    />
                    <input
                      type="text"
                      placeholder="Transaction ID"
                      className="input-field w-full"
                      id="card_transaction_id"
                    />
                  </div>
                )}
                
                {paymentMethod === 'online' && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      Online payment will be processed via Razorpay (UPI, Cards, Net Banking, Wallets)
                    </p>
                  </div>
                )}
                
                {paymentMethod === 'credit' && (
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">
                      This will be automatically added to customer's credit ledger (Udhar Khata)
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Totals */}
            <div className="card p-4">
              <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Summary</h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Subtotal:</span>
                  <span className="text-gray-900 dark:text-white">₹{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Tax:</span>
                  <span className="text-gray-900 dark:text-white">₹{tax.toFixed(2)}</span>
                </div>
                {discountAmount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount:</span>
                    <span>-₹{discountAmount.toFixed(2)}</span>
                  </div>
                )}
                <div className="border-t pt-2 mt-2">
                  <div className="flex justify-between">
                    <span className="font-bold text-lg text-gray-900 dark:text-white">Total:</span>
                    <span className="font-bold text-lg text-green-600">₹{total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={createInvoice}
                className="btn-primary w-full mt-4 flex items-center justify-center gap-2"
                disabled={cart.length === 0}
              >
                <Receipt className="w-5 h-5" />
                Create Invoice
              </button>
            </div>
          </div>
        </div>

        {/* Invoice Modal */}
        {showInvoiceModal && createdInvoice && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card max-w-4xl w-full max-h-[90vh] overflow-y-auto bg-white dark:bg-slate-800"
            >
              <div className="flex justify-between items-center mb-6 border-b pb-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Invoice {createdInvoice.invoice_number}
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={async () => {
                      try {
                        const pdfResponse = await api.get(`/billing/invoices/${createdInvoice.id}/pdf/`, {
                          responseType: 'blob',
                        });
                        const url = window.URL.createObjectURL(new Blob([pdfResponse.data]));
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', `invoice_${createdInvoice.invoice_number}.pdf`);
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        toast.success('PDF downloaded');
                      } catch (error) {
                        toast.error('Failed to download PDF');
                      }
                    }}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download PDF
                  </button>
                  <button
                    onClick={async () => {
                      try {
                        const response = await api.post(`/billing/invoices/${createdInvoice.id}/send_email/`);
                        toast.success(response.data.message || 'Invoice sent via email');
                      } catch (error) {
                        console.error('Email send error:', error);
                        const errorMessage = error.response?.data?.error || 
                                            error.response?.data?.detail || 
                                            'Failed to send email. Please check email configuration.';
                        toast.error(errorMessage);
                      }
                    }}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Mail className="w-4 h-4" />
                    Send Email
                  </button>
                  <button
                    onClick={() => {
                      setShowInvoiceModal(false);
                      setCreatedInvoice(null);
                    }}
                    className="btn-secondary"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Invoice Content */}
              <div className="space-y-6">
                {/* Company & Customer Info */}
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Bill To:</h3>
                    <p className="text-gray-700 dark:text-gray-300">
                      {createdInvoice.customer_name || createdInvoice.customer?.name || 'Walk-in Customer'}
                    </p>
                    {createdInvoice.customer_phone && (
                      <p className="text-gray-700 dark:text-gray-300">Phone: {createdInvoice.customer_phone}</p>
                    )}
                    {createdInvoice.customer_email && (
                      <p className="text-gray-700 dark:text-gray-300">Email: {createdInvoice.customer_email}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-gray-700 dark:text-gray-300">
                      <strong>Invoice #:</strong> {createdInvoice.invoice_number}
                    </p>
                    <p className="text-gray-700 dark:text-gray-300">
                      <strong>Date:</strong> {new Date(createdInvoice.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-gray-700 dark:text-gray-300">
                      <strong>Status:</strong> {createdInvoice.status}
                    </p>
                    <p className="text-gray-700 dark:text-gray-300">
                      <strong>Payment:</strong> {createdInvoice.payment_method}
                    </p>
                  </div>
                </div>

                {/* Items Table */}
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-gray-100 dark:bg-gray-700">
                        <th className="text-left py-3 px-4 text-gray-900 dark:text-white font-semibold">Item</th>
                        <th className="text-right py-3 px-4 text-gray-900 dark:text-white font-semibold">Qty</th>
                        <th className="text-right py-3 px-4 text-gray-900 dark:text-white font-semibold">Price</th>
                        <th className="text-right py-3 px-4 text-gray-900 dark:text-white font-semibold">Tax</th>
                        <th className="text-right py-3 px-4 text-gray-900 dark:text-white font-semibold">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {createdInvoice.items?.map((item, index) => (
                        <tr key={index} className="border-b border-gray-200 dark:border-gray-700">
                          <td className="py-3 px-4 text-gray-900 dark:text-white">
                            {item.product?.name || 'N/A'}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                            {item.quantity}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                            ₹{parseFloat(item.unit_price || 0).toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-700 dark:text-gray-300">
                            ₹{parseFloat(item.tax_amount || 0).toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                            ₹{parseFloat(item.total || 0).toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Totals */}
                <div className="flex justify-end">
                  <div className="w-64 space-y-2">
                    <div className="flex justify-between text-gray-700 dark:text-gray-300">
                      <span>Subtotal:</span>
                      <span>₹{parseFloat(createdInvoice.subtotal || 0).toFixed(2)}</span>
                    </div>
                    {createdInvoice.discount_amount > 0 && (
                      <div className="flex justify-between text-gray-700 dark:text-gray-300">
                        <span>Discount:</span>
                        <span className="text-green-600">-₹{parseFloat(createdInvoice.discount_amount || 0).toFixed(2)}</span>
                      </div>
                    )}
                    <div className="flex justify-between text-gray-700 dark:text-gray-300">
                      <span>Tax:</span>
                      <span>₹{parseFloat(createdInvoice.tax_amount || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-lg font-bold text-gray-900 dark:text-white border-t pt-2">
                      <span>Total:</span>
                      <span>₹{parseFloat(createdInvoice.total_amount || 0).toFixed(2)}</span>
                    </div>
                    {createdInvoice.paid_amount > 0 && (
                      <div className="flex justify-between text-gray-700 dark:text-gray-300">
                        <span>Paid:</span>
                        <span className="text-green-600">₹{parseFloat(createdInvoice.paid_amount || 0).toFixed(2)}</span>
                      </div>
                    )}
                    {createdInvoice.balance_amount > 0 && (
                      <div className="flex justify-between text-gray-700 dark:text-gray-300">
                        <span>Balance:</span>
                        <span className="text-red-600">₹{parseFloat(createdInvoice.balance_amount || 0).toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Billing;

