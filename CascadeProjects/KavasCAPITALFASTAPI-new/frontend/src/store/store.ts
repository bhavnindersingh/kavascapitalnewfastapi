import { configureStore } from '@reduxjs/toolkit';
import optionChainReducer from './slices/optionChainSlice';

export const store = configureStore({
  reducer: {
    optionChain: optionChainReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
