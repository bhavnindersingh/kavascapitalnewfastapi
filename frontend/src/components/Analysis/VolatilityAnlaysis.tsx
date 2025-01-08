import React from 'react';
import { Box, Paper, Typography, Grid, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

interface VolatilityData {
  strike: number;
  impliedVolatility: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
}

const mockData: VolatilityData[] = [
  {
    strike: 21000,
    impliedVolatility: 15.5,
    delta: 0.65,
    gamma: 0.02,
    theta: -0.08,
    vega: 0.15
  },
];

export const VolatilityAnalysis: React.FC = () => {
  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Volatility Analysis
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Expiry</InputLabel>
              <Select
                value=""
                label="Expiry"
              >
                <MenuItem value="21DEC2023">21 DEC 2023</MenuItem>
                <MenuItem value="28DEC2023">28 DEC 2023</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Greeks Analysis
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};