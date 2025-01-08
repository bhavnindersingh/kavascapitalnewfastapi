import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface OIData {
  strike: number;
  callOI: number;
  putOI: number;
}

interface Props {
  data: OIData[];
  title?: string;
}

export const OIChart: React.FC<Props> = ({ data, title = 'Open Interest Analysis' }) => {
  const chartData = {
    labels: data.map(d => d.strike),
    datasets: [
      {
        label: 'Call OI',
        data: data.map(d => d.callOI),
        backgroundColor: 'rgba(76, 175, 80, 0.5)',
        borderColor: 'rgba(76, 175, 80, 1)',
        borderWidth: 1,
      },
      {
        label: 'Put OI',
        data: data.map(d => d.putOI),
        backgroundColor: 'rgba(244, 67, 54, 0.5)',
        borderColor: 'rgba(244, 67, 54, 1)',
        borderWidth: 1,
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
        text: title,
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
          text: 'Open Interest',
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ height: 400 }}>
        <Bar options={options} data={chartData} />
      </Box>
    </Paper>
  );
};
