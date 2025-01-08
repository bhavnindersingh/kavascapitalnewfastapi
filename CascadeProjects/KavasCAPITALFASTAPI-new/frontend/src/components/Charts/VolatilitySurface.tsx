import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ScatterController,
} from 'chart.js';
import { Scatter } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ScatterController
);

interface VolatilityPoint {
  strike: number;
  expiry: string;
  iv: number;
}

interface Props {
  data: VolatilityPoint[];
}

export const VolatilitySurface: React.FC<Props> = ({ data }) => {
  const chartData = {
    datasets: [
      {
        label: 'Implied Volatility Surface',
        data: data.map((point) => ({
          x: point.strike,
          y: new Date(point.expiry).getTime(),
          z: point.iv,
        })),
        backgroundColor: 'rgba(25, 118, 210, 0.5)',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Volatility Surface',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Strike Price',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Expiry',
        },
        type: 'timeseries' as const,
        time: {
          unit: 'day' as const,
        },
      },
    },
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Volatility Surface
      </Typography>
      <Box sx={{ height: 400 }}>
        <Scatter options={options} data={chartData} />
      </Box>
    </Paper>
  );
};
