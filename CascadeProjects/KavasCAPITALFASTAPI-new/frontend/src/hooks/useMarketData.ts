import { useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setOptionChainData, setError } from '../store/slices/optionChainSlice';
import { MarketData, OptionChainData, WSMessage, StrikeData } from '../types/options';
import { RootState } from '../store/store';

// Constants
const MAX_RETRIES = 3;
const RETRY_DELAY = 3000;
const HEARTBEAT_INTERVAL = 30000;
const RECONNECT_INTERVAL = 5000;

export const useMarketData = (symbol: string, expiry: string) => {
    const dispatch = useDispatch();
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectAttempts = useRef(0);
    const heartbeatInterval = useRef<NodeJS.Timeout>();
    const { optionChainData, error, isLoading } = useSelector((state: RootState) => state.optionChain);

    // Handle market data updates
    const handleMarketData = useCallback((marketData: MarketData) => {
        if (!optionChainData) return;

        const updatedStrikes = optionChainData.strikes.map((strike: StrikeData) => {
            if (strike.call?.instrument_token === marketData.instrument_token) {
                return {
                    ...strike,
                    call: {
                        ...strike.call,
                        ltp: marketData.last_price,
                        change: marketData.change,
                        volume: marketData.volume,
                        oi: marketData.oi,
                        oiChange: marketData.oiChange,
                        iv: marketData.iv,
                        bidQty: marketData.bidQty,
                        askQty: marketData.askQty
                    }
                };
            }
            if (strike.put?.instrument_token === marketData.instrument_token) {
                return {
                    ...strike,
                    put: {
                        ...strike.put,
                        ltp: marketData.last_price,
                        change: marketData.change,
                        volume: marketData.volume,
                        oi: marketData.oi,
                        oiChange: marketData.oiChange,
                        iv: marketData.iv,
                        bidQty: marketData.bidQty,
                        askQty: marketData.askQty
                    }
                };
            }
            return strike;
        });

        dispatch(setOptionChainData({
            ...optionChainData,
            strikes: updatedStrikes
        }));
    }, [optionChainData, dispatch]);

    // Subscribe to instruments
    const subscribeToInstruments = useCallback(() => {
        if (!wsRef.current || !optionChainData || wsRef.current.readyState !== WebSocket.OPEN) return;

        const instruments = optionChainData.strikes.flatMap((strike: StrikeData) => {
            const tokens: number[] = [];
            if (strike.call?.instrument_token) tokens.push(strike.call.instrument_token);
            if (strike.put?.instrument_token) tokens.push(strike.put.instrument_token);
            return tokens;
        });

        if (instruments.length > 0) {
            wsRef.current.send(JSON.stringify({
                type: 'subscribe',
                instruments
            }));
        }
    }, [optionChainData]);

    // Setup WebSocket connection
    const setupWebSocket = useCallback(() => {
        const token = localStorage.getItem('access_token');
        if (!token || !symbol || !expiry) return;

        // Close existing connection if any
        if (wsRef.current) {
            wsRef.current.close();
            clearInterval(heartbeatInterval.current);
        }

        const ws = new WebSocket(`ws://localhost:8000/options/${symbol}/${expiry}?token=${token}`);
        wsRef.current = ws;

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data) as WSMessage;
                
                switch (message.type) {
                    case 'MARKET_DATA':
                        if (message.data) handleMarketData(message.data as MarketData);
                        break;
                    case 'OPTION_CHAIN':
                        if (message.data) {
                            dispatch(setOptionChainData(message.data as OptionChainData));
                            subscribeToInstruments();
                        }
                        break;
                    case 'ERROR':
                        dispatch(setError(message.error || 'Unknown error occurred'));
                        break;
                    case 'pong':
                        // Heartbeat response received
                        break;
                    default:
                        console.warn('Unknown message type:', message.type);
                }
            } catch (err) {
                console.error('Error processing WebSocket message:', err);
                dispatch(setError('Error processing market data'));
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            dispatch(setError('Connection error occurred'));
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed');
            clearInterval(heartbeatInterval.current);

            // Attempt reconnection if not at max retries
            if (reconnectAttempts.current < MAX_RETRIES) {
                setTimeout(() => {
                    reconnectAttempts.current += 1;
                    setupWebSocket();
                }, RECONNECT_INTERVAL);
            } else {
                dispatch(setError('Maximum reconnection attempts reached'));
            }
        };

        ws.onopen = () => {
            console.log('WebSocket connection established');
            reconnectAttempts.current = 0;
            subscribeToInstruments();

            // Setup heartbeat
            heartbeatInterval.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                }
            }, HEARTBEAT_INTERVAL);
        };
    }, [symbol, expiry, dispatch, handleMarketData, subscribeToInstruments]);

    useEffect(() => {
        setupWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                clearInterval(heartbeatInterval.current);
            }
        };
    }, [setupWebSocket]);

    return { optionChainData, error, isLoading };
};
/