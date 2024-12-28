import { useCallback } from 'react';
import { webSocketService } from '../services/websocket';

export function useWebSocket(defaultSymbol?: string, defaultExpiry?: string) {
  const connect = useCallback((symbol: string, expiry: string) => {
    webSocketService.connect(symbol, expiry);
  }, []);

  const disconnect = useCallback(() => {
    webSocketService.disconnect();
  }, []);

  const subscribe = useCallback((instruments: number | number[]) => {
    if (Array.isArray(instruments)) {
      webSocketService.subscribe(instruments);
    } else {
      webSocketService.subscribe([instruments]);
    }
  }, []);

  const unsubscribe = useCallback((instruments: number | number[]) => {
    if (Array.isArray(instruments)) {
      webSocketService.unsubscribe(instruments);
    } else {
      webSocketService.unsubscribe([instruments]);
    }
  }, []);

  const addMessageHandler = useCallback((handler: (message: any) => void) => {
    webSocketService.addMessageHandler(handler);
  }, []);

  const removeMessageHandler = useCallback((handler: (message: any) => void) => {
    webSocketService.removeMessageHandler(handler);
  }, []);

  // Connect with default values if provided
  useCallback(() => {
    if (defaultSymbol && defaultExpiry) {
      connect(defaultSymbol, defaultExpiry);
    }
  }, [defaultSymbol, defaultExpiry, connect]);

  return {
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    addMessageHandler,
    removeMessageHandler,
  };
}
