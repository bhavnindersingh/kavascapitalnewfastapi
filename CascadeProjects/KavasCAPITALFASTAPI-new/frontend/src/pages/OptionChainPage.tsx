import React, { useState, useEffect } from 'react';
import { Box, Container, TextField, Select, MenuItem, Button, Paper, SelectChangeEvent } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useOptionChainData } from '../components/OptionChain/hooks/useOptionChainData';
import { OptionChainGrid } from '../components/OptionChain/OptionChainGrid';
import { StockInfoHeader } from '../components/OptionChain/StockInfoHeader';

const StyledContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
}));

const ControlsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(2),
  marginBottom: theme.spacing(3),
  alignItems: 'center',
}));

const OptionChainPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AJANTPHARM');
  const [selectedExpiry, setSelectedExpiry] = useState<string>('');
  const [strikeFilter, setStrikeFilter] = useState<string>('0.05');

  const { expiryDates, fetchExpiryDates } = useOptionChainData({
    symbol: selectedSymbol,
    expiry: selectedExpiry,
    threshold: parseFloat(strikeFilter)
  });

  useEffect(() => {
    if (selectedSymbol) {
      fetchExpiryDates(selectedSymbol);
    }
  }, [selectedSymbol, fetchExpiryDates]);

  const handleSymbolChange = (event: SelectChangeEvent<string>) => {
    const newSymbol = event.target.value;
    setSelectedSymbol(newSymbol);
    setSelectedExpiry(''); // Reset expiry when symbol changes
  };

  const handleExpiryChange = (event: SelectChangeEvent<string>) => {
    setSelectedExpiry(event.target.value);
  };

  const handleStrikeFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setStrikeFilter(event.target.value);
  };

  return (
    <StyledContainer maxWidth="xl">
      <Paper elevation={2} sx={{ p: 3 }}>
        <ControlsContainer>
          <Select
            value={selectedSymbol}
            onChange={handleSymbolChange}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="AJANTPHARM">AJANTPHARM</MenuItem>
            <MenuItem value="NIFTY">NIFTY</MenuItem>
            <MenuItem value="BANKNIFTY">BANKNIFTY</MenuItem>
          </Select>

          <Select
            value={selectedExpiry}
            onChange={handleExpiryChange}
            sx={{ minWidth: 150 }}
            displayEmpty
          >
            <MenuItem value="" disabled>
              Expiry
            </MenuItem>
            {expiryDates.map((date) => (
              <MenuItem key={date} value={date}>
                {date}
              </MenuItem>
            ))}
          </Select>

          <TextField
            label="Strike Filter"
            value={strikeFilter}
            onChange={handleStrikeFilterChange}
            sx={{ width: 150 }}
          />

          <Button 
            variant="contained" 
            color="primary"
            disabled={!selectedSymbol || !selectedExpiry}
          >
            Show
          </Button>
        </ControlsContainer>

        {selectedSymbol && selectedExpiry && (
          <>
            <StockInfoHeader
              symbol={selectedSymbol}
              expiry={selectedExpiry}
              stockInfo={{
                ltp: 0,
                change: 0,
                lotSize: 0,
                future: 0,
                vix: 0
              }}
            />
            <OptionChainGrid
              symbol={selectedSymbol}
            />
          </>
        )}
      </Paper>
    </StyledContainer>
  );
};

export default OptionChainPage;
