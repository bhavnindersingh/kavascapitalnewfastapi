import React from 'react';
import { Box, Paper, Typography, Grid, Button, TextField } from '@mui/material';

interface Strategy {
  name: string;
  legs: StrategyLeg[];
}

interface StrategyLeg {
  type: 'BUY' | 'SELL';
  strike: number;
  quantity: number;
}

export const StrategyBuilder: React.FC = () => {
  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Strategy Builder
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Strategy Name"
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" color="primary">
              Add Leg
            </Button>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Strategy Preview
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};