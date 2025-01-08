import { useState, useEffect } from 'react';
import { marketDataApi } from '../../../services/api/marketDataApi';
import { MarketDepth } from '../../../types/marketData';

export const useMarketDepth = (
    instrumentToken: number,
    interval: number = 1000 // 1 second by default
) => {
    const [depth, setDepth] = useState<MarketDepth | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchDepth = async () => {
            try {
                const depthData = await marketDataApi.getMarketDepth(instrumentToken);
                setDepth(depthData);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch market depth'));
            } finally {
                setLoading(false);
            }
        };

        fetchDepth();
        const intervalId = setInterval(fetchDepth, interval);

        return () => clearInterval(intervalId);
    }, [instrumentToken, interval]);

    return { depth, loading, error };
};
