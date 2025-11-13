import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      try {
        const authData = JSON.parse(authStorage);
        // Zustand persist stores data in state property
        const token = authData?.state?.token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        } else {
          // Try alternative paths in case the structure is different
          const altToken = authData?.token || authData?.state?.access || authData?.access;
          if (altToken) {
            config.headers.Authorization = `Bearer ${altToken}`;
          } else {
            console.warn('No token found in auth storage. Structure:', authData);
          }
        }
      } catch (error) {
        console.error('Error parsing auth token:', error);
      }
    } else {
      console.warn('No auth storage found in localStorage. Please log in.');
    }
    // Don't set Content-Type for FormData, let axios handle it
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

