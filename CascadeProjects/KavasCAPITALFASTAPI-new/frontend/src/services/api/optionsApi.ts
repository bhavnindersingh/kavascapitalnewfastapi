import axios from 'axios';
import { OptionChain } from '../../types/options';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('kite_access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const optionsApi = {
    async getOptionChain(symbol: string, expiry?: string): Promise<OptionChain> {
        try {
            const response = await api.get(`/options/chain/${symbol}`, {
                params: { expiry }
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                throw new Error('Please check your access token in settings');
            }
            throw error;
        }
    },

    async getExpiryDates(symbol: string): Promise<string[]> {
        try {
            const response = await api.get(`/options/expiry-dates/${symbol}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                throw new Error('Please check your access token in settings');
            }
            throw error;
        }
    },

    async getStrikes(symbol: string, expiry: string): Promise<number[]> {
        try {
            const response = await api.get(`/options/strikes/${symbol}`, {
                params: { expiry }
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                throw new Error('Please check your access token in settings');
            }
            throw error;
        }
    }
};
