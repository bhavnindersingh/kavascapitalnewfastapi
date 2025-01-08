import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Link,
  Paper,
  CircularProgress,
  Snackbar
} from '@mui/material';
import { setAccessToken, setError, setLoading } from '../../store/slices/authSlice';
import { kiteApi } from '../../services/api';
import type { RootState } from '../../store';

const steps = [
  'Visit Kite Developer',
  'Create an App',
  'Get Access Token'
];

export const AccessTokenInput: React.FC = () => {
  const [token, setToken] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const dispatch = useDispatch();
  const { error: authError, loading: authLoading } = useSelector((state: RootState) => state.auth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) {
      setValidationError('Please enter an access token');
      return;
    }

    dispatch(setLoading(true));
    try {
      await kiteApi.validateToken(token);
      dispatch(setAccessToken(token));
      setValidationError(null);
    } catch (error: any) {
      console.error('Token validation failed:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to validate token';
      setValidationError(errorMessage);
      dispatch(setError(errorMessage));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom color="primary">
        Kite Access Token Setup
      </Typography>

      <Stepper activeStep={2} alternativeLabel sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mb: 3 }}>
        <Typography variant="body1" paragraph>
          To get your access token:
        </Typography>
        <ol>
          <li>
            <Typography>
              Visit{' '}
              <Link
                href="https://developers.kite.trade/"
                target="_blank"
                rel="noopener noreferrer"
              >
                Kite Developer
              </Link>
            </Typography>
          </li>
          <li>
            <Typography>Create an app in the developer console</Typography>
          </li>
          <li>
            <Typography>Generate and copy your access token</Typography>
          </li>
        </ol>
      </Box>

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Access Token"
          variant="outlined"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          error={!!validationError || !!authError}
          helperText={validationError || authError}
          sx={{ mb: 2 }}
          disabled={authLoading}
        />
        
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          disabled={authLoading}
        >
          {authLoading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            'Validate Token'
          )}
        </Button>
      </form>

      <Snackbar 
        open={!!authError} 
        autoHideDuration={6000} 
        onClose={() => dispatch(setError(null))}
      >
        <Alert severity="error" onClose={() => dispatch(setError(null))}>
          {authError}
        </Alert>
      </Snackbar>
    </Paper>
  );
};
