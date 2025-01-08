import React from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

interface Trade {
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  timestamp: string;
  pnl: number;
}

const mockTrades: Trade[] = [
  {
    symbol: 'NIFTY 21DEC23 21000 CE',
    type: 'BUY',
    quantity: 50,
    price: 150.25,
    timestamp: '2023-12-20 10:30:00',
    pnl: 2500,
  },
  {
    symbol: 'BANKNIFTY 21DEC23 45000 PE',
    type: 'SELL',
    quantity: 25,
    price: 80.50,
    timestamp: '2023-12-20 11:15:00',
    pnl: -1200,
  },
];

export const TradeSummary: React.FC = () => {
  const totalPnL = mockTrades.reduce((sum, trade) => sum + trade.pnl, 0);

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Trading Summary
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, mb: 3 }}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Total P&L
            </Typography>
            <Typography 
              variant="h4" 
              color={totalPnL >= 0 ? 'success.main' : 'error.main'}
              sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
            >
              ₹{totalPnL.toLocaleString()}
              {totalPnL >= 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Total Trades
            </Typography>
            <Typography variant="h4">
              {mockTrades.length}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell>Timestamp</TableCell>
              <TableCell align="right">P&L</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockTrades.map((trade, index) => (
              <TableRow key={index}>
                <TableCell>{trade.symbol}</TableCell>
                <TableCell>
                  <Chip 
                    label={trade.type} 
                    color={trade.type === 'BUY' ? 'success' : 'error'} 
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">{trade.quantity}</TableCell>
                <TableCell align="right">₹{trade.price}</TableCell>
                <TableCell>{trade.timestamp}</TableCell>
                <TableCell 
                  align="right"
                  sx={{ 
                    color: trade.pnl >= 0 ? 'success.main' : 'error.main',
                    fontWeight: 'bold'
                  }}
                >
                  ₹{trade.pnl.toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};