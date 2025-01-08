import { configureStore } from '@reduxjs/toolkit';
import marketDataReducer, { MarketDataState } from './slices/marketDataSlice';
import websocketReducer, { WebSocketState } from './slices/websocketSlice';
import authReducer, { AuthState } from './slices/authSlice';
import optionChainReducer from './slices/optionChainSlice';

// Create the store with all reducers
export const store = configureStore({
    reducer: {
        marketData: marketDataReducer,
        websocket: websocketReducer,
        auth: authReducer,
        optionChain: optionChainReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: false,
        }),
});

// Export store types
export type RootState = {
    marketData: MarketDataState;
    websocket: WebSocketState;
    auth: AuthState;
    optionChain: ReturnType<typeof optionChainReducer>;
};

export type AppDispatch = typeof store.dispatch;
