import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { OptionChainData } from '../../types/options';

interface OptionChainState {
  optionChainData: OptionChainData | null;
  error: string | null;
  isLoading: boolean;
}

const initialState: OptionChainState = {
  optionChainData: null,
  error: null,
  isLoading: false,
};

const optionChainSlice = createSlice({
  name: 'optionChain',
  initialState,
  reducers: {
    setOptionChainData: (state, action: PayloadAction<OptionChainData | null>) => {
      state.optionChainData = action.payload;
      state.error = null;
      state.isLoading = false;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { setOptionChainData, setError, setLoading } = optionChainSlice.actions;
export default optionChainSlice.reducer;