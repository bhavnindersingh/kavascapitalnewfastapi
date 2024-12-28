import { useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { useWebSocket } from './useWebSocket';
import { setError } from '../store/slices/authSlice';

export const useAuth = (): {
  isAuthenticated: boolean;
  accessToken: string | null;
  loading: boolean;
  error: string | null;
} => {
  const dispatch = useDispatch();
  const { isAuthenticated, accessToken, loading, error } = useSelector(
    (state: RootState) => state.auth
  );
  const { disconnect } = useWebSocket();

  const handleDisconnect = useCallback(() => {
    disconnect();
  }, [disconnect]);

  useEffect(() => {
    // Disconnect WebSocket when component unmounts
    return () => {
      handleDisconnect();
    };
  }, [handleDisconnect]);

  useEffect(() => {
    // Check if token exists in localStorage but not in state
    const storedToken = localStorage.getItem('kite_access_token');
    if (!storedToken) {
      handleDisconnect();
    } else if (storedToken && !accessToken) {
      dispatch(setError('Session expired. Please login again.'));
    }
  }, [accessToken, dispatch, handleDisconnect]);

  return {
    isAuthenticated,
    accessToken,
    loading,
    error,
  };
};
