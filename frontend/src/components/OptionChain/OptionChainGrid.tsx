import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Typography,
  SelectChangeEvent,
  CircularProgress,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { useOptionChainData } from './hooks/useOptionChainData';
import { useMarketData } from '../../hooks/useMarketData';
import { OptionChainData, StrikeData } from '../../types/options';

interface Props {
  symbol: string;
}

export const OptionChainGrid: React.FC<Props> = ({ symbol }) => {
  const [selectedExpiry, setSelectedExpiry] = useState<string>('');
  const [threshold, setThreshold] = useState('0.05');
  const [appliedFilters, setAppliedFilters] = useState({
    symbol,
    expiry: '',
    threshold: '0.05'
  });

  // Get expiry dates and option chain data
  const {
    expiryDates,
    loading: expiryLoading,
    error: expiryError,
    fetchExpiryDates,
  } = useOptionChainData({
    symbol: appliedFilters.symbol,
    expiry: appliedFilters.expiry,
    threshold: parseFloat(appliedFilters.threshold)
  });

  // Get market data
  const { optionChainData } = useMarketData(appliedFilters.symbol, appliedFilters.expiry);

  useEffect(() => {
    fetchExpiryDates(symbol);
  }, [symbol, fetchExpiryDates]);

  const handleExpiryChange = (event: SelectChangeEvent<string>) => {
    setSelectedExpiry(event.target.value);
  };

  const handleThresholdChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setThreshold(event.target.value);
  };

  const handleApply = useCallback(() => {
    setAppliedFilters({
      symbol,
      expiry: selectedExpiry,
      threshold: threshold
    });
  }, [symbol, selectedExpiry, threshold]);

  const handleRefresh = useCallback(() => {
    handleApply();
  }, [handleApply]);

  // Function to render stock info card
  const renderStockInfo = () => {
    if (!optionChainData?.stockInfo) return null;
    
    const change = optionChainData.stockInfo.change ?? 0;
    const isPositive = change >= 0;

    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" component="div">
              {optionChainData.stockInfo.name || '-'}
            </Typography>
            <IconButton onClick={handleRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Box>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Chip
              icon={isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
              label={`LTP: ${optionChainData.stockInfo.ltp || '-'}`}
              color={isPositive ? 'success' : 'error'}
              variant="outlined"
            />
            <Chip
              label={`Change: ${change}%`}
              color={isPositive ? 'success' : 'error'}
              variant="outlined"
            />
            <Chip
              label={`Lot Size: ${optionChainData.stockInfo.lotSize || '-'}`}
              variant="outlined"
            />
            <Chip
              label={`Future: ${optionChainData.stockInfo.future || '-'}`}
              variant="outlined"
            />
            <Chip
              label={`VIX: ${optionChainData.stockInfo.vix || '-'}`}
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Function to render the option chain table
  const renderOptionChainTable = () => {
    if (!optionChainData?.strikes) return null;

    return (
      <TableContainer 
        component={Paper} 
        sx={{ 
          height: 'calc(100vh - 200px)',
          '& .MuiTableCell-root': {
            px: 1,
            py: 0.5,
            whiteSpace: 'nowrap'
          }
        }}
      >
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell colSpan={8} align="center" sx={{ bgcolor: 'success.main', color: 'white' }}>
                CALLS
              </TableCell>
              <TableCell align="center" sx={{ bgcolor: 'grey.300' }}>
                Strike Price
              </TableCell>
              <TableCell colSpan={8} align="center" sx={{ bgcolor: 'error.main', color: 'white' }}>
                PUTS
              </TableCell>
            </TableRow>
            <TableRow>
              {/* CALLS Headers */}
              <TableCell align="center" sx={{ minWidth: 80 }}>OI</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Chng in OI</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Volume</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>IV</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>LTP</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Chng%</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Bid Qty</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Ask Qty</TableCell>
              
              {/* Strike Price */}
              <TableCell align="center" sx={{ bgcolor: 'grey.100', minWidth: 100 }}>
                Strike
              </TableCell>
              
              {/* PUTS Headers */}
              <TableCell align="center" sx={{ minWidth: 80 }}>Bid Qty</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Ask Qty</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Chng%</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>LTP</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>IV</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Volume</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>Chng in OI</TableCell>
              <TableCell align="center" sx={{ minWidth: 80 }}>OI</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {optionChainData.strikes.map((strike: StrikeData) => {
              const callChange = strike.call?.change ?? 0;
              const putChange = strike.put?.change ?? 0;
              
              return (
                <TableRow 
                  key={strike.strikePrice}
                  sx={{ 
                    '&:nth-of-type(odd)': { bgcolor: 'grey.50' },
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  {/* CALLS Data */}
                  <TableCell align="right">{strike.call?.oi?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.call?.oiChange?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.call?.volume?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.call?.iv?.toFixed(2) || '-'}</TableCell>
                  <TableCell 
                    align="right"
                    sx={{ 
                      color: callChange >= 0 ? 'success.main' : 'error.main',
                      fontWeight: 'medium'
                    }}
                  >
                    {strike.call?.ltp?.toFixed(2) || '-'}
                  </TableCell>
                  <TableCell 
                    align="right"
                    sx={{ color: callChange >= 0 ? 'success.main' : 'error.main' }}
                  >
                    {callChange.toFixed(2)}%
                  </TableCell>
                  <TableCell align="right">{strike.call?.bidQty?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.call?.askQty?.toLocaleString() || '-'}</TableCell>
                  
                  {/* Strike Price */}
                  <TableCell 
                    align="center" 
                    sx={{ 
                      bgcolor: 'grey.100',
                      fontWeight: 'bold'
                    }}
                  >
                    {strike.strikePrice}
                  </TableCell>
                  
                  {/* PUTS Data */}
                  <TableCell align="right">{strike.put?.bidQty?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.put?.askQty?.toLocaleString() || '-'}</TableCell>
                  <TableCell 
                    align="right"
                    sx={{ color: putChange >= 0 ? 'success.main' : 'error.main' }}
                  >
                    {putChange.toFixed(2)}%
                  </TableCell>
                  <TableCell 
                    align="right"
                    sx={{ 
                      color: putChange >= 0 ? 'success.main' : 'error.main',
                      fontWeight: 'medium'
                    }}
                  >
                    {strike.put?.ltp?.toFixed(2) || '-'}
                  </TableCell>
                  <TableCell align="right">{strike.put?.iv?.toFixed(2) || '-'}</TableCell>
                  <TableCell align="right">{strike.put?.volume?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.put?.oiChange?.toLocaleString() || '-'}</TableCell>
                  <TableCell align="right">{strike.put?.oi?.toLocaleString() || '-'}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box sx={{ height: '100vh', p: 2 }}>
      {/* Controls */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ 
            display: 'flex', 
            gap: 2, 
            alignItems: 'center',
            flexWrap: 'wrap'
          }}>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Expiry</InputLabel>
              <Select
                value={selectedExpiry}
                label="Expiry"
                onChange={handleExpiryChange}
                disabled={expiryLoading || expiryDates.length === 0}
                size="small"
              >
                {expiryDates.map(date => (
                  <MenuItem key={date} value={date}>{date}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Threshold"
              value={threshold}
              onChange={handleThresholdChange}
              sx={{ width: 100 }}
              disabled={expiryLoading}
              type="number"
              inputProps={{ step: 0.01, min: 0 }}
              size="small"
            />

            <Button 
              variant="contained" 
              onClick={handleApply}
              disabled={expiryLoading || !selectedExpiry}
              sx={{ height: 40 }}
            >
              Apply
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Error Message */}
      {expiryError && (
        <Typography color="error" sx={{ mt: 2 }}>
          {expiryError}
        </Typography>
      )}

      {/* Loading Indicator */}
      {expiryLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Stock Information */}
      {optionChainData?.stockInfo && renderStockInfo()}

      {/* Option Chain Table */}
      {optionChainData?.strikes && renderOptionChainTable()}
    </Box>
  );
};