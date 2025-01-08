import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  Alert,
  Chip,
  Stack
} from '@mui/material';
import { AccessTokenInput } from '../Auth/AccessTokenInput';
import type { RootState } from '../../store';
import { setAccessToken } from '../../store/slices/authSlice';

export const Settings: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth);
  const token = localStorage.getItem('kite_access_token');

  const handleClearToken = () => {
    localStorage.removeItem('kite_access_token');
    dispatch(setAccessToken(null));
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom color="primary">
        Settings
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Authentication Status
        </Typography>
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body1">Status:</Typography>
            <Chip 
              label={isAuthenticated ? "Authenticated" : "Not Authenticated"} 
              color={isAuthenticated ? "success" : "error"}
            />
          </Box>
          
          {isAuthenticated && token && (
            <>
              <Box>
                <Typography variant="body1" gutterBottom>Access Token:</Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    bgcolor: 'grey.100', 
                    p: 1, 
                    borderRadius: 1,
                    wordBreak: 'break-all'
                  }}
                >
                  {token}
                </Typography>
              </Box>
              <Button 
                variant="outlined" 
                color="error" 
                onClick={handleClearToken}
                disabled={loading}
              >
                Clear Token
              </Button>
            </>
          )}
        </Stack>
      </Paper>

      {!isAuthenticated && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Update Access Token
          </Typography>
          <AccessTokenInput />
        </Paper>
      )}
    </Box>
  );
};
