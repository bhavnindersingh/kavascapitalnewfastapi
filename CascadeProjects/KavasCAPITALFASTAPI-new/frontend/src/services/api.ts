import axios from 'axios';
import { store } from '../store';
import { MarketData, OptionChainData } from '../types/market';

const API_URL = 'http://localhost:8000/api/v1';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include access token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('kite_access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('kite_access_token');
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const kiteApi = {
  validateToken: (token: string) => api.get(`/kite/verify-token/${token}`),
  getProfile: () => api.get('/kite/profile'),
};

export const optionsApi = {
  getExpiryDates: (symbol: string) => 
    api.get(`/options/expiry-dates/${symbol}`),
  getOptionChain: (symbol: string, expiry: string) => 
    api.get(`/options/chain/${symbol}/${expiry}`),
};

export default api;
