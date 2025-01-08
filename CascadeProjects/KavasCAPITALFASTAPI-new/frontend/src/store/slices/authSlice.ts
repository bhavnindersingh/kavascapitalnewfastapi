import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface AuthState {
    accessToken: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    accessToken: localStorage.getItem('kite_access_token'),
    isAuthenticated: Boolean(localStorage.getItem('kite_access_token')),
    loading: false,
    error: null,
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setAccessToken: (state, action: PayloadAction<string | null>) => {
            state.accessToken = action.payload;
            state.isAuthenticated = Boolean(action.payload);
            state.error = null;
            if (action.payload) {
                localStorage.setItem('kite_access_token', action.payload);
            } else {
                localStorage.removeItem('kite_access_token');
            }
        },
        setLoading: (state, action: PayloadAction<boolean>) => {
            state.loading = action.payload;
        },
        setError: (state, action: PayloadAction<string | null>) => {
            state.error = action.payload;
            if (action.payload) {
                state.loading = false;
                state.isAuthenticated = false;
                state.accessToken = null;
                localStorage.removeItem('kite_access_token');
            }
        },
        logout: (state) => {
            state.accessToken = null;
            state.isAuthenticated = false;
            state.error = null;
            localStorage.removeItem('kite_access_token');
        },
    },
});

export const {
    setAccessToken,
    setLoading,
    setError,
    logout,
} = authSlice.actions;

export default authSlice.reducer;
