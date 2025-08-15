import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', //  esta URL debe ser la del backend
  headers: {
    'Content-Type': 'application/json',
  },
});

const token = localStorage.getItem('access_token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

export const login = (email, password) => api.post('/auth/login', { email, password });
export const register = (userData) => api.post('/auth/register', userData);
export const forgotPassword = (email) => api.post('/auth/forgot-password', { email });
export const resetPassword = (token, password) => api.post('/auth/reset-password', { token, password: password });

export default api;