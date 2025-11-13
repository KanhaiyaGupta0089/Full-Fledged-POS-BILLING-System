import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Save, Bell, Mail, Database, Shield } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore';

function Settings() {
  const { user, updateUser } = useAuthStore();
  const [settings, setSettings] = useState({
    email_notifications: true,
    low_stock_alerts: true,
    auto_email_invoices: true,
    daily_summary: true,
    company_name: '',
    company_address: '',
    company_phone: '',
    company_email: '',
    tax_rate: '18',
    currency: 'INR',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load settings from localStorage or API
    const savedSettings = localStorage.getItem('app_settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = async () => {
    setLoading(true);
    try {
      // Save to localStorage (in production, save to API)
      localStorage.setItem('app_settings', JSON.stringify(settings));
      toast.success('Settings saved successfully');
      setLoading(false);
    } catch (error) {
      toast.error('Failed to save settings');
      setLoading(false);
    }
  };

  return (
    <DashboardLayout title="Settings">
      <div className="p-6 space-y-6 max-w-4xl">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>

        {/* Company Information */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Database className="w-5 h-5" />
            Company Information
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Company Name</label>
              <input
                type="text"
                value={settings.company_name}
                onChange={(e) => setSettings({ ...settings, company_name: e.target.value })}
                className="input-field w-full"
                placeholder="Enter company name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Address</label>
              <textarea
                value={settings.company_address}
                onChange={(e) => setSettings({ ...settings, company_address: e.target.value })}
                className="input-field w-full"
                rows="3"
                placeholder="Enter company address"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Phone</label>
                <input
                  type="text"
                  value={settings.company_phone}
                  onChange={(e) => setSettings({ ...settings, company_phone: e.target.value })}
                  className="input-field w-full"
                  placeholder="Enter phone number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Email</label>
                <input
                  type="email"
                  value={settings.company_email}
                  onChange={(e) => setSettings({ ...settings, company_email: e.target.value })}
                  className="input-field w-full"
                  placeholder="Enter email address"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Business Settings */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Business Settings
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Default Tax Rate (%)</label>
                <input
                  type="number"
                  value={settings.tax_rate}
                  onChange={(e) => setSettings({ ...settings, tax_rate: e.target.value })}
                  className="input-field w-full"
                  min="0"
                  max="100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Currency</label>
                <select
                  value={settings.currency}
                  onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
                  className="input-field w-full"
                >
                  <option value="INR">INR (₹)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notification Settings
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email Notifications</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">Receive email notifications</p>
              </div>
              <input
                type="checkbox"
                checked={settings.email_notifications}
                onChange={(e) => setSettings({ ...settings, email_notifications: e.target.checked })}
                className="w-5 h-5 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Low Stock Alerts</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">Get notified when stock is low</p>
              </div>
              <input
                type="checkbox"
                checked={settings.low_stock_alerts}
                onChange={(e) => setSettings({ ...settings, low_stock_alerts: e.target.checked })}
                className="w-5 h-5 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Auto Email Invoices</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">Automatically email invoices to customers</p>
              </div>
              <input
                type="checkbox"
                checked={settings.auto_email_invoices}
                onChange={(e) => setSettings({ ...settings, auto_email_invoices: e.target.checked })}
                className="w-5 h-5 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Daily Summary</label>
                <p className="text-xs text-gray-500 dark:text-gray-400">Receive daily business summary at 9 AM</p>
              </div>
              <input
                type="checkbox"
                checked={settings.daily_summary}
                onChange={(e) => setSettings({ ...settings, daily_summary: e.target.checked })}
                className="w-5 h-5 rounded"
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            <Save className="w-5 h-5" />
            {loading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default Settings;

