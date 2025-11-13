import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, Store, Lock, User, Eye, EyeOff } from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore';
import { authService } from '../services/authService';

const ROLE_OPTIONS = [
  { value: 'admin', label: 'Admin', icon: '👑', color: 'bg-purple-500' },
  { value: 'owner', label: 'Owner', icon: '🏢', color: 'bg-blue-500' },
  { value: 'manager', label: 'Manager', icon: '👔', color: 'bg-green-500' },
  { value: 'employee', label: 'Cash Counter Employee', icon: '💼', color: 'bg-orange-500' },
];

function Login() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [selectedRole, setSelectedRole] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  // Force light theme on login page
  useEffect(() => {
    // Remove dark class when login page mounts
    document.documentElement.classList.remove('dark');
    
    // Cleanup: restore theme when component unmounts
    return () => {
      // Get saved theme from localStorage
      const savedTheme = localStorage.getItem('theme-storage');
      if (savedTheme) {
        try {
          const parsed = JSON.parse(savedTheme);
          if (parsed?.state?.theme === 'dark') {
            document.documentElement.classList.add('dark');
          }
        } catch (e) {
          // If error, don't add dark class
        }
      }
    };
  }, []);

  const onSubmit = async (data) => {
    if (!selectedRole) {
      toast.error('Please select your role');
      return;
    }

    setIsLoading(true);
    try {
      const response = await authService.login(data.username, data.password);
      
      if (response.access) {
        // Verify role matches
        if (response.user?.role !== selectedRole) {
          toast.error('Invalid role for this account');
          setIsLoading(false);
          return;
        }

        login(response.user, response.access, selectedRole);
        toast.success(`Welcome back, ${response.user.name || response.user.username}!`);
        
        // Navigate based on role
        const roleRoutes = {
          admin: '/dashboard/admin',
          owner: '/dashboard/owner',
          manager: '/dashboard/manager',
          employee: '/dashboard/employee',
        };
        
        navigate(roleRoutes[selectedRole] || '/dashboard');
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail || 
        error.response?.data?.message || 
        'Login failed. Please check your credentials.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo and Title */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600 rounded-2xl shadow-lg mb-4">
            <Store className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            POS System
          </h1>
          <p className="text-gray-600 mt-2">Sign in to your account</p>
        </motion.div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Your Role
              </label>
              <div className="grid grid-cols-2 gap-3">
                {ROLE_OPTIONS.map((role) => (
                  <motion.button
                    key={role.value}
                    type="button"
                    onClick={() => setSelectedRole(role.value)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      selectedRole === role.value
                        ? `${role.color} border-transparent text-white shadow-lg`
                        : 'bg-white border-gray-200 text-gray-700 hover:border-primary-300'
                    }`}
                  >
                    <div className="text-2xl mb-1">{role.icon}</div>
                    <div className="text-xs font-medium">{role.label}</div>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Username Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  {...register('username', {
                    required: 'Username is required',
                  })}
                  className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all duration-200 bg-white text-gray-900"
                  placeholder="Enter your username"
                />
              </div>
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters',
                    },
                  })}
                  className="w-full px-4 py-2 pl-10 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all duration-200 bg-white text-gray-900"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-medium w-full py-3 text-lg font-semibold rounded-lg transition-all duration-200 shadow-lg shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  Sign In
                </>
              )}
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center text-sm text-gray-600">
            <p>© 2024 POS System. All rights reserved.</p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

export default Login;

