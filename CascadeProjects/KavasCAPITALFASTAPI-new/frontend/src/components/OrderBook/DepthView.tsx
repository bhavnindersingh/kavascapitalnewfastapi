import React from 'react';
import { styled } from '@mui/material/styles';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
} from '@mui/material';
import { MarketDepth } from '../../types/marketData';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  padding: theme.spacing(1),
  textAlign: 'center',
  '&.header': {
    backgroundColor: theme.palette.grey[100],
    fontWeight: 600,
  },
}));

const BuyQuantity = styled(Typography)(({ theme }) => ({
  color: theme.palette.success.main,
  fontWeight: 500,
}));

const SellQuantity = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  fontWeight: 500,
}));

interface Props {
  depth: MarketDepth;
}

export const DepthView: React.FC<Props> = ({ depth }) => {
  const maxRows = Math.max(depth.buys.length, depth.sells.length);
  const rows = Array.from({ length: maxRows }, (_, i) => ({
    buy: depth.buys[i],
    sell: depth.sells[i],
  }));

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Market Depth
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <StyledTableCell className="header">Bid Qty</StyledTableCell>
              <StyledTableCell className="header">Bid Price</StyledTableCell>
              <StyledTableCell className="header">Ask Price</StyledTableCell>
              <StyledTableCell className="header">Ask Qty</StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row, index) => (
              <TableRow key={index}>
                <StyledTableCell>
                  {row.buy && (
                    <BuyQuantity variant="body2">
                      {row.buy.buy_quantity.toLocaleString()}
                    </BuyQuantity>
                  )}
                </StyledTableCell>
                <StyledTableCell>
                  {row.buy && row.buy.buy_price.toFixed(2)}
                </StyledTableCell>
                <StyledTableCell>
                  {row.sell && row.sell.sell_price.toFixed(2)}
                </StyledTableCell>
                <StyledTableCell>
                  {row.sell && (
                    <SellQuantity variant="body2">
                      {row.sell.sell_quantity.toLocaleString()}
                    </SellQuantity>
                  )}
                </StyledTableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};
