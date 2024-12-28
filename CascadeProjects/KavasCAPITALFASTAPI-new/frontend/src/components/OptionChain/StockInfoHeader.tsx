import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { styled } from '@mui/material/styles';

interface StockInfoHeaderProps {
  symbol: string;
  expiry: string;
  stockInfo?: {
    ltp?: number;
    change?: number;
    lotSize?: number;
    future?: number;
    vix?: number;
  };
}

const HeaderContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  display: 'grid',
  gridTemplateColumns: 'repeat(5, 1fr)',
  gap: theme.spacing(2),
}));

const InfoBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(1),
}));

const Label = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: '0.875rem',
}));

const Value = styled(Typography)(({ theme }) => ({
  fontWeight: 'bold',
  fontSize: '1rem',
}));

export const StockInfoHeader: React.FC<StockInfoHeaderProps> = ({
  symbol,
  expiry,
  stockInfo = {},
}) => {
  const { ltp = 0, change = 0, lotSize = 0, future = 0, vix = 0 } = stockInfo;

  return (
    <HeaderContainer>
      <InfoBox>
        <Label>Stock Name</Label>
        <Value>{symbol}</Value>
      </InfoBox>
      <InfoBox>
        <Label>LTP</Label>
        <Value>{ltp.toFixed(2)}</Value>
        <Typography
          variant="caption"
          color={change >= 0 ? 'success.main' : 'error.main'}
        >
          {change >= 0 ? '+' : ''}{change.toFixed(2)}%
        </Typography>
      </InfoBox>
      <InfoBox>
        <Label>Lot Size</Label>
        <Value>{lotSize}</Value>
      </InfoBox>
      <InfoBox>
        <Label>Future</Label>
        <Value>{future.toFixed(2)}</Value>
      </InfoBox>
      <InfoBox>
        <Label>VIX</Label>
        <Value>{vix.toFixed(2)}</Value>
      </InfoBox>
    </HeaderContainer>
  );
};

export default StockInfoHeader;
