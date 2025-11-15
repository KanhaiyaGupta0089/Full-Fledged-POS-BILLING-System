import { useState } from 'react';
import { motion } from 'framer-motion';
import { Calculator, Percent, TrendingUp, DollarSign, Tag, Target, PieChart } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import toast from 'react-hot-toast';

function Tools() {
  const [activeTool, setActiveTool] = useState('gst');

  return (
    <DashboardLayout title="Business Tools">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Business Tools</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Essential calculators for your business</p>
        </div>

        {/* Tool Selector */}
        <div className="card p-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            <ToolButton
              icon={Percent}
              label="GST Calculator"
              active={activeTool === 'gst'}
              onClick={() => setActiveTool('gst')}
            />
            <ToolButton
              icon={TrendingUp}
              label="Profit Calculator"
              active={activeTool === 'profit'}
              onClick={() => setActiveTool('profit')}
            />
            <ToolButton
              icon={Tag}
              label="Discount Calculator"
              active={activeTool === 'discount'}
              onClick={() => setActiveTool('discount')}
            />
            <ToolButton
              icon={DollarSign}
              label="Markup Calculator"
              active={activeTool === 'markup'}
              onClick={() => setActiveTool('markup')}
            />
            <ToolButton
              icon={Target}
              label="Break-Even Calculator"
              active={activeTool === 'breakeven'}
              onClick={() => setActiveTool('breakeven')}
            />
          </div>
        </div>

        {/* Tool Content */}
        <div className="card p-6">
          {activeTool === 'gst' && <GSTCalculator />}
          {activeTool === 'profit' && <ProfitCalculator />}
          {activeTool === 'discount' && <DiscountCalculator />}
          {activeTool === 'markup' && <MarkupCalculator />}
          {activeTool === 'breakeven' && <BreakEvenCalculator />}
        </div>
      </div>
    </DashboardLayout>
  );
}

function ToolButton({ icon: Icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-xl border-2 transition-all duration-200 ${
        active
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 text-gray-700 dark:text-gray-300'
      }`}
    >
      <Icon className="w-6 h-6 mx-auto mb-2" />
      <p className="text-sm font-medium">{label}</p>
    </button>
  );
}

function GSTCalculator() {
  const [amount, setAmount] = useState('');
  const [gstRate, setGstRate] = useState('18');
  const [calculationType, setCalculationType] = useState('forward'); // forward or reverse

  const calculateGST = () => {
    const amt = parseFloat(amount) || 0;
    const rate = parseFloat(gstRate) || 0;

    if (amt <= 0) return null;

    if (calculationType === 'forward') {
      // Calculate GST on amount
      const gstAmount = (amt * rate) / 100;
      const totalWithGST = amt + gstAmount;
      const cgst = gstAmount / 2;
      const sgst = gstAmount / 2;

      return {
        baseAmount: amt,
        gstRate: rate,
        gstAmount: gstAmount,
        cgst: cgst,
        sgst: sgst,
        totalWithGST: totalWithGST,
      };
    } else {
      // Reverse GST - amount includes GST
      const baseAmount = (amt * 100) / (100 + rate);
      const gstAmount = amt - baseAmount;
      const cgst = gstAmount / 2;
      const sgst = gstAmount / 2;

      return {
        baseAmount: baseAmount,
        gstRate: rate,
        gstAmount: gstAmount,
        cgst: cgst,
        sgst: sgst,
        totalWithGST: amt,
      };
    }
  };

  const result = calculateGST();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Percent className="w-8 h-8 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">GST Calculator</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Calculation Type
          </label>
          <select
            value={calculationType}
            onChange={(e) => setCalculationType(e.target.value)}
            className="input-field w-full"
          >
            <option value="forward">Calculate GST on Amount</option>
            <option value="reverse">Extract GST from Total</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            {calculationType === 'forward' ? 'Base Amount' : 'Total Amount (Including GST)'}
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Enter amount"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            GST Rate (%)
          </label>
          <select
            value={gstRate}
            onChange={(e) => setGstRate(e.target.value)}
            className="input-field w-full"
          >
            <option value="0">0%</option>
            <option value="5">5%</option>
            <option value="12">12%</option>
            <option value="18">18%</option>
            <option value="28">28%</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        {gstRate === 'custom' && (
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
              Custom GST Rate (%)
            </label>
            <input
              type="number"
              value={gstRate === 'custom' ? '' : gstRate}
              onChange={(e) => setGstRate(e.target.value)}
              placeholder="Enter custom rate"
              className="input-field w-full"
              min="0"
              max="100"
              step="0.01"
            />
          </div>
        )}
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-6 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-xl border border-primary-200 dark:border-primary-800"
        >
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Calculation Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Base Amount</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ₹{result.baseAmount.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">GST Amount ({result.gstRate}%)</p>
              <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                ₹{result.gstAmount.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">CGST ({result.gstRate / 2}%)</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">
                ₹{result.cgst.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">SGST ({result.gstRate / 2}%)</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">
                ₹{result.sgst.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg md:col-span-2">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Amount (Including GST)</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                ₹{result.totalWithGST.toFixed(2)}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function ProfitCalculator() {
  const [costPrice, setCostPrice] = useState('');
  const [sellingPrice, setSellingPrice] = useState('');
  const [quantity, setQuantity] = useState('1');

  const calculateProfit = () => {
    const cost = parseFloat(costPrice) || 0;
    const selling = parseFloat(sellingPrice) || 0;
    const qty = parseFloat(quantity) || 1;

    if (cost <= 0 || selling <= 0) return null;

    const profitPerUnit = selling - cost;
    const totalProfit = profitPerUnit * qty;
    const profitMargin = (profitPerUnit / selling) * 100;
    const markupPercentage = (profitPerUnit / cost) * 100;
    const totalRevenue = selling * qty;
    const totalCost = cost * qty;

    return {
      costPrice: cost,
      sellingPrice: selling,
      quantity: qty,
      profitPerUnit: profitPerUnit,
      totalProfit: totalProfit,
      profitMargin: profitMargin,
      markupPercentage: markupPercentage,
      totalRevenue: totalRevenue,
      totalCost: totalCost,
    };
  };

  const result = calculateProfit();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <TrendingUp className="w-8 h-8 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Profit Calculator</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Cost Price (₹)
          </label>
          <input
            type="number"
            value={costPrice}
            onChange={(e) => setCostPrice(e.target.value)}
            placeholder="Enter cost price"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Selling Price (₹)
          </label>
          <input
            type="number"
            value={sellingPrice}
            onChange={(e) => setSellingPrice(e.target.value)}
            placeholder="Enter selling price"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Quantity
          </label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="Enter quantity"
            className="input-field w-full"
            min="1"
            step="1"
          />
        </div>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 space-y-4"
        >
          <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl border border-green-200 dark:border-green-800">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Profit Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Profit per Unit</p>
                <p className={`text-2xl font-bold ${result.profitPerUnit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ₹{result.profitPerUnit.toFixed(2)}
                </p>
              </div>
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Profit</p>
                <p className={`text-2xl font-bold ${result.totalProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ₹{result.totalProfit.toFixed(2)}
                </p>
              </div>
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Profit Margin</p>
                <p className={`text-2xl font-bold ${result.profitMargin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {result.profitMargin.toFixed(2)}%
                </p>
              </div>
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Markup Percentage</p>
                <p className="text-xl font-semibold text-blue-600 dark:text-blue-400">
                  {result.markupPercentage.toFixed(2)}%
                </p>
              </div>
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Revenue</p>
                <p className="text-xl font-semibold text-gray-900 dark:text-white">
                  ₹{result.totalRevenue.toFixed(2)}
                </p>
              </div>
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Cost</p>
                <p className="text-xl font-semibold text-gray-900 dark:text-white">
                  ₹{result.totalCost.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function DiscountCalculator() {
  const [originalPrice, setOriginalPrice] = useState('');
  const [discountType, setDiscountType] = useState('percentage'); // percentage or fixed
  const [discountValue, setDiscountValue] = useState('');

  const calculateDiscount = () => {
    const price = parseFloat(originalPrice) || 0;
    const discount = parseFloat(discountValue) || 0;

    if (price <= 0 || discount < 0) return null;

    let discountAmount = 0;
    let finalPrice = 0;

    if (discountType === 'percentage') {
      if (discount > 100) {
        toast.error('Discount percentage cannot exceed 100%');
        return null;
      }
      discountAmount = (price * discount) / 100;
      finalPrice = price - discountAmount;
    } else {
      if (discount > price) {
        toast.error('Discount amount cannot exceed original price');
        return null;
      }
      discountAmount = discount;
      finalPrice = price - discountAmount;
    }

    const savingsPercentage = (discountAmount / price) * 100;

    return {
      originalPrice: price,
      discountType: discountType,
      discountValue: discount,
      discountAmount: discountAmount,
      finalPrice: finalPrice,
      savingsPercentage: savingsPercentage,
    };
  };

  const result = calculateDiscount();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Tag className="w-8 h-8 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Discount Calculator</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Original Price (₹)
          </label>
          <input
            type="number"
            value={originalPrice}
            onChange={(e) => setOriginalPrice(e.target.value)}
            placeholder="Enter original price"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Discount Type
          </label>
          <select
            value={discountType}
            onChange={(e) => setDiscountType(e.target.value)}
            className="input-field w-full"
          >
            <option value="percentage">Percentage (%)</option>
            <option value="fixed">Fixed Amount (₹)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            {discountType === 'percentage' ? 'Discount Percentage (%)' : 'Discount Amount (₹)'}
          </label>
          <input
            type="number"
            value={discountValue}
            onChange={(e) => setDiscountValue(e.target.value)}
            placeholder={discountType === 'percentage' ? 'Enter percentage' : 'Enter amount'}
            className="input-field w-full"
            min="0"
            step={discountType === 'percentage' ? '0.01' : '0.01'}
            max={discountType === 'percentage' ? '100' : undefined}
          />
        </div>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border border-blue-200 dark:border-blue-800"
        >
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Discount Calculation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Original Price</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ₹{result.originalPrice.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Discount Amount</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                -₹{result.discountAmount.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Final Price</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                ₹{result.finalPrice.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">You Save</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {result.savingsPercentage.toFixed(2)}%
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function MarkupCalculator() {
  const [costPrice, setCostPrice] = useState('');
  const [markupPercentage, setMarkupPercentage] = useState('');

  const calculateMarkup = () => {
    const cost = parseFloat(costPrice) || 0;
    const markup = parseFloat(markupPercentage) || 0;

    if (cost <= 0 || markup < 0) return null;

    const markupAmount = (cost * markup) / 100;
    const sellingPrice = cost + markupAmount;
    const profitMargin = (markupAmount / sellingPrice) * 100;

    return {
      costPrice: cost,
      markupPercentage: markup,
      markupAmount: markupAmount,
      sellingPrice: sellingPrice,
      profitMargin: profitMargin,
    };
  };

  const result = calculateMarkup();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <DollarSign className="w-8 h-8 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Markup Calculator</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Cost Price (₹)
          </label>
          <input
            type="number"
            value={costPrice}
            onChange={(e) => setCostPrice(e.target.value)}
            placeholder="Enter cost price"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Markup Percentage (%)
          </label>
          <input
            type="number"
            value={markupPercentage}
            onChange={(e) => setMarkupPercentage(e.target.value)}
            placeholder="Enter markup %"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl border border-purple-200 dark:border-purple-800"
        >
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Markup Calculation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Cost Price</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ₹{result.costPrice.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Markup Amount ({result.markupPercentage}%)</p>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                ₹{result.markupAmount.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Selling Price</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                ₹{result.sellingPrice.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Profit Margin</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {result.profitMargin.toFixed(2)}%
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function BreakEvenCalculator() {
  const [fixedCosts, setFixedCosts] = useState('');
  const [variableCostPerUnit, setVariableCostPerUnit] = useState('');
  const [sellingPricePerUnit, setSellingPricePerUnit] = useState('');

  const calculateBreakEven = () => {
    const fixed = parseFloat(fixedCosts) || 0;
    const variable = parseFloat(variableCostPerUnit) || 0;
    const selling = parseFloat(sellingPricePerUnit) || 0;

    if (fixed <= 0 || selling <= 0) return null;
    if (selling <= variable) {
      toast.error('Selling price must be greater than variable cost per unit');
      return null;
    }

    const contributionMargin = selling - variable;
    const breakEvenUnits = fixed / contributionMargin;
    const breakEvenRevenue = breakEvenUnits * selling;

    return {
      fixedCosts: fixed,
      variableCostPerUnit: variable,
      sellingPricePerUnit: selling,
      contributionMargin: contributionMargin,
      breakEvenUnits: breakEvenUnits,
      breakEvenRevenue: breakEvenRevenue,
    };
  };

  const result = calculateBreakEven();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Target className="w-8 h-8 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Break-Even Calculator</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Fixed Costs (₹)
          </label>
          <input
            type="number"
            value={fixedCosts}
            onChange={(e) => setFixedCosts(e.target.value)}
            placeholder="Enter fixed costs"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Rent, salaries, etc.</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Variable Cost per Unit (₹)
          </label>
          <input
            type="number"
            value={variableCostPerUnit}
            onChange={(e) => setVariableCostPerUnit(e.target.value)}
            placeholder="Enter variable cost"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Cost per product</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
            Selling Price per Unit (₹)
          </label>
          <input
            type="number"
            value={sellingPricePerUnit}
            onChange={(e) => setSellingPricePerUnit(e.target.value)}
            placeholder="Enter selling price"
            className="input-field w-full"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-6 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl border border-orange-200 dark:border-orange-800"
        >
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Break-Even Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Contribution Margin per Unit</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                ₹{result.contributionMargin.toFixed(2)}
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400">Break-Even Units</p>
              <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                {Math.ceil(result.breakEvenUnits).toLocaleString()} units
              </p>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg md:col-span-2">
              <p className="text-sm text-gray-600 dark:text-gray-400">Break-Even Revenue</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                ₹{result.breakEvenRevenue.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                You need to sell {Math.ceil(result.breakEvenUnits).toLocaleString()} units to cover all costs
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default Tools;








