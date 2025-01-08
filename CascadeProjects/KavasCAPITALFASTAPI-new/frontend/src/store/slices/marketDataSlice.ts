import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MarketData, OptionChainData } from '../../types/market';

export interface MarketDataState {
    optionChainData: OptionChainData | null;
    selectedExpiry: string | null;
    marketData: { [key: number]: MarketData };
    loading: boolean;
    error: string | null;
}

const initialState: MarketDataState = {
    optionChainData: null,
    selectedExpiry: null,
    marketData: {},
    loading: false,
    error: null,
};

export const marketDataSlice = createSlice({
    name: 'marketData',
    initialState,
    reducers: {
        setOptionChainData: (state, action: PayloadAction<OptionChainData>) => {
            state.optionChainData = action.payload;
            state.error = null;
        },
        setSelectedExpiry: (state, action: PayloadAction<string>) => {
            state.selectedExpiry = action.payload;
        },
        updateMarketData: (state, action: PayloadAction<MarketData>) => {
            state.marketData[action.payload.instrument_token] = action.payload;
        },
        setLoading: (state, action: PayloadAction<boolean>) => {
            state.loading = action.payload;
        },
        setError: (state, action: PayloadAction<string>) => {
            state.error = action.payload;
            state.loading = false;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
});

export const {
    setOptionChainData,
    setSelectedExpiry,
    updateMarketData,
    setLoading,
    setError,
    clearError,
} = marketDataSlice.actions;

export default marketDataSlice.reducer;
