import axios, { AxiosError } from 'axios';
import { MarketData, MarketDepth } from '../../types/marketData';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Interface for API error response
interface ApiErrorResponse {
    detail?: string;
    message?: string;
    status?: number;
}

// Custom error class for API errors
export class ApiError extends Error {
    constructor(
        public status: number,
        public message: string,
        public details?: any
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('kite_access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => {
        // Log successful response
        console.log('API Response:', {
            status: response.status,
            data: response.data,
            headers: response.headers
        });
        return response;
    },
    (error: AxiosError<ApiErrorResponse>) => {
        console.error('API Error:', {
            status: error.response?.status,
            data: error.response?.data,
            headers: error.response?.headers,
            message: error.message
        });
        
        if (error.response) {
            // Server responded with error
            const status = error.response.status;
            const detail = error.response.data?.detail || error.message;
            
            let message = 'An error occurred';
            if (status === 401) {
                message = 'Authentication failed. Please check your access token and try again.';
                localStorage.removeItem('kite_access_token');
            } else if (status === 403) {
                message = 'Access denied. Please check your permissions.';
            } else if (status === 404) {
                message = 'Resource not found.';
            } else if (status >= 500) {
                message = 'Server error. Please try again later.';
            }

            throw new ApiError(status, message, detail);
        } else if (error.request) {
            // Request made but no response
            throw new ApiError(0, 'No response from server. Please check if the backend is running.', error.message);
        } else {
            // Request setup error
            throw new ApiError(0, 'Failed to make request', error.message);
        }
    }
);

export const marketDataApi = {
    async getMarketData(
        instrumentToken: number,
        startTime: string,
        endTime: string,
        limit: number = 1000
    ): Promise<MarketData[]> {
        try {
            const response = await apiClient.get(`/market-data/tick/${instrumentToken}`, {
                params: {
                    start_time: startTime,
                    end_time: endTime,
                    limit
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching market data:', error);
            throw error;
        }
    },

    async getMarketDepth(instrumentToken: number): Promise<MarketDepth> {
        try {
            const response = await apiClient.get(`/market-data/depth/${instrumentToken}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching market depth:', error);
            throw error;
        }
    },

    async validateToken(token: string): Promise<any> {
        try {
            // Log token format check
            console.log('Token validation checks:', {
                length: token.length,
                isAlphanumeric: /^[A-Za-z0-9]+$/.test(token),
                firstFiveChars: token.substring(0, 5)
            });

            // Make the validation request
            const response = await apiClient.get('/kite/validate', {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            // Log successful validation
            console.log('Token validation response:', {
                status: response.status,
                headers: response.headers,
                data: response.data
            });

            return response.data;
        } catch (error) {
            // Enhanced error logging
            if (error instanceof ApiError) {
                console.error('Token validation failed with ApiError:', {
                    status: error.status,
                    message: error.message,
                    details: error.details
                });
            } else if (error instanceof Error) {
                console.error('Token validation failed with Error:', {
                    name: error.name,
                    message: error.message,
                    stack: error.stack
                });
            }
            
            // Check if it's an axios error with response
            if (axios.isAxiosError(error) && error.response) {
                console.error('Axios error details:', {
                    status: error.response.status,
                    statusText: error.response.statusText,
                    headers: error.response.headers,
                    data: error.response.data
                });
            }

            throw error;
        }
    },

    async testKiteApi(token: string): Promise<any> {
        try {
            console.log('Testing Kite API with token:', token.substring(0, 5) + '...');
            
            // Use path parameter instead of query parameter
            const response = await apiClient.get(`/kite/test/${token}`, {
                headers: {
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            console.log('Kite API Test Response:', {
                status: response.status,
                data: response.data,
                headers: response.headers,
                url: response.config.url
            });
            
            return response.data;
        } catch (error) {
            console.error('Kite API Test Error:', error);
            if (axios.isAxiosError(error) && error.response) {
                console.error('API Test Response Details:', {
                    status: error.response.status,
                    statusText: error.response.statusText,
                    data: error.response.data,
                    headers: error.response.headers,
                    url: error.config?.url,
                    method: error.config?.method
                });
            }
            throw error;
        }
    },

    async directTestKiteApi(token: string): Promise<any> {
        try {
            console.log('Testing with token:', token.substring(0, 5) + '...');
            const response = await apiClient.get(`/kite/direct-test/${token}`);
            console.log('Success:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    },

    async getKiteProfile(token: string): Promise<any> {
        const response = await apiClient.get(`/kite/profile/${token}`);
        return response.data;
    },
};
