import { useState, useEffect } from 'react';
import { marketDataApi } from '../../../services/api/marketDataApi';
import { MarketData } from '../../../types/marketData';

export const useMarketData = (
    instrumentToken: number,
    interval: number = 5000 // 5 seconds by default
) => {
    const [data, setData] = useState<MarketData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const endTime = new Date().toISOString();
                const startTime = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(); // Last 24 hours
                const marketData = await marketDataApi.getMarketData(
                    instrumentToken,
                    startTime,
                    endTime
                );
                setData(marketData);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch market data'));
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const intervalId = setInterval(fetchData, interval);

        return () => clearInterval(intervalId);
    }, [instrumentToken, interval]);

    return { data, loading, error };
};
