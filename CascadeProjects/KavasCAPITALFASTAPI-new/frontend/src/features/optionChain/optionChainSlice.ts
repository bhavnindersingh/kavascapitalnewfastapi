import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface OptionData {
  strikePrice: number;
  callOption: {
    lastPrice: number;
    change: number;
    volume: number;
    oi: number;
    iv: number;
  };
  putOption: {
    lastPrice: number;
    change: number;
    volume: number;
    oi: number;
    iv: number;
  };
}

interface OptionChainState {
  data: OptionData[];
  loading: boolean;
  error: string | null;
  selectedExpiry: string;
  spotPrice: number;
}

const initialState: OptionChainState = {
  data: [],
  loading: false,
  error: null,
  selectedExpiry: '',
  spotPrice: 0,
};

const optionChainSlice = createSlice({
  name: 'optionChain',
  initialState,
  reducers: {
    setOptionChainData: (state, action: PayloadAction<OptionData[]>) => {
      state.data = action.payload;
      state.loading = false;
      state.error = null;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    setSelectedExpiry: (state, action: PayloadAction<string>) => {
      state.selectedExpiry = action.payload;
    },
    setSpotPrice: (state, action: PayloadAction<number>) => {
      state.spotPrice = action.payload;
    },
  },
});

export const {
  setOptionChainData,
  setLoading,
  setError,
  setSelectedExpiry,
  setSpotPrice,
} = optionChainSlice.actions;

export default optionChainSlice.reducer;
