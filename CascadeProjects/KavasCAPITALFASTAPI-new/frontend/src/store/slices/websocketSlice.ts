import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface WebSocketState {
    connected: boolean;
    clientId: string | null;
    subscriptions: number[];
    error: string | null;
}

const initialState: WebSocketState = {
    connected: false,
    clientId: null,
    subscriptions: [],
    error: null,
};

export const websocketSlice = createSlice({
    name: 'websocket',
    initialState,
    reducers: {
        setConnected: (state, action: PayloadAction<boolean>) => {
            state.connected = action.payload;
            if (!action.payload) {
                state.error = null;
            }
        },
        setClientId: (state, action: PayloadAction<string>) => {
            state.clientId = action.payload;
        },
        addSubscription: (state, action: PayloadAction<number>) => {
            if (!state.subscriptions.includes(action.payload)) {
                state.subscriptions.push(action.payload);
            }
        },
        removeSubscription: (state, action: PayloadAction<number>) => {
            state.subscriptions = state.subscriptions.filter(id => id !== action.payload);
        },
        setError: (state, action: PayloadAction<string>) => {
            state.error = action.payload;
            state.connected = false;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
});

export const {
    setConnected,
    setClientId,
    addSubscription,
    removeSubscription,
    setError,
    clearError,
} = websocketSlice.actions;

export default websocketSlice.reducer;
