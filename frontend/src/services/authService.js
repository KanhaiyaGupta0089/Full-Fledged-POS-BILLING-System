import api from './api';

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login/', {
      username,
      password,
    });
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout/');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/user/');
    return response.data;
  },
  
  refreshToken: async (refresh) => {
    const response = await api.post('/auth/refresh/', { refresh });
    return response.data;
  },
};

