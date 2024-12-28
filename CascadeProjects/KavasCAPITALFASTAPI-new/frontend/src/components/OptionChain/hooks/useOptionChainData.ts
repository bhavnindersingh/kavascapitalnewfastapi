import { useState, useCallback } from 'react';
import { optionsApi } from '../../../services/api';

interface UseOptionChainDataProps {
  symbol: string;
  expiry?: string;
  threshold?: number;
}

interface UseOptionChainDataReturn {
  expiryDates: string[];
  loading: boolean;
  error: string | null;
  fetchExpiryDates: (symbol: string) => Promise<void>;
}

export const useOptionChainData = ({
  symbol,
  expiry,
  threshold = 0.05
}: UseOptionChainDataProps): UseOptionChainDataReturn => {
  const [expiryDates, setExpiryDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExpiryDates = useCallback(async (symbol: string) => {
    if (!symbol) {
      setExpiryDates([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await optionsApi.getExpiryDates(symbol);
      
      if (response.data && Array.isArray(response.data)) {
        setExpiryDates(response.data);
      } else {
        throw new Error('Invalid expiry dates format received');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch expiry dates';
      setError(errorMessage);
      setExpiryDates([]);
      console.error('Failed to fetch expiry dates:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    expiryDates,
    loading,
    error,
    fetchExpiryDates,
  };
};