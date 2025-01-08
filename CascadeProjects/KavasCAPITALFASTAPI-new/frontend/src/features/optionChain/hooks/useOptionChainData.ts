import { useState, useEffect } from 'react';
import { optionsApi } from '../../../services/api/optionsApi';
import { OptionChain } from '../../../types/options';

export const useOptionChainData = (symbol: string, expiry?: string) => {
    const [data, setData] = useState<OptionChain | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const chainData = await optionsApi.getOptionChain(symbol, expiry);
                setData(chainData);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('Failed to fetch option chain'));
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [symbol, expiry]);

    return { data, loading, error };
};
