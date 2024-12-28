import React, { useState } from 'react';
import { 
  Box, 
  Tabs, 
  Tab, 
  Typography, 
  Container, 
  Alert, 
  Paper,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TimelineIcon from '@mui/icons-material/Timeline';
import BuildIcon from '@mui/icons-material/Build';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import { OptionChainGrid } from './OptionChain/OptionChainGrid';
import { TradeSummary } from './Trade/TradeSummary';
import { VolatilityAnalysis } from './Analysis/VolatilityAnlaysis';
import { StrategyBuilder } from './Strategy/StrategyBuilder';
import { Settings } from './Settings/Settings';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const drawerWidth = 240;

function MainContent() {
  const [value, setValue] = useState(0);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('NIFTY');
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const handleSymbolChange = (event: any) => {
    setSelectedSymbol(event.target.value);
  };

  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        <ListItem button onClick={() => setValue(0)}>
          <ListItemIcon>
            <ShowChartIcon />
          </ListItemIcon>
          <ListItemText primary="Option Chain" />
        </ListItem>
        <ListItem button onClick={() => setValue(1)}>
          <ListItemIcon>
            <TimelineIcon />
          </ListItemIcon>
          <ListItemText primary="Trade Summary" />
        </ListItem>
        <ListItem button onClick={() => setValue(2)}>
          <ListItemIcon>
            <AssessmentIcon />
          </ListItemIcon>
          <ListItemText primary="Analysis" />
        </ListItem>
        <ListItem button onClick={() => setValue(3)}>
          <ListItemIcon>
            <BuildIcon />
          </ListItemIcon>
          <ListItemText primary="Strategy" />
        </ListItem>
        <Divider sx={{ my: 1 }} />
        <ListItem button onClick={() => setValue(4)}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </div>
  );

  if (!isAuthenticated) {
    return (
      <Container>
        <Alert severity="warning">
          Please authenticate with your Kite access token to access trading features.
        </Alert>
      </Container>
    );
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Trading Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8
        }}
      >
        <TabPanel value={value} index={0}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Box sx={{ mb: 2 }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel id="symbol-select-label">Symbol</InputLabel>
                <Select
                  labelId="symbol-select-label"
                  id="symbol-select"
                  value={selectedSymbol}
                  label="Symbol"
                  onChange={handleSymbolChange}
                  size="small"
                >
                  <MenuItem value="NIFTY">NIFTY</MenuItem>
                  <MenuItem value="BANKNIFTY">BANKNIFTY</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <OptionChainGrid symbol={selectedSymbol} />
          </Paper>
        </TabPanel>
        <TabPanel value={value} index={1}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <TradeSummary />
          </Paper>
        </TabPanel>
        <TabPanel value={value} index={2}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <VolatilityAnalysis />
          </Paper>
        </TabPanel>
        <TabPanel value={value} index={3}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <StrategyBuilder />
          </Paper>
        </TabPanel>
        <TabPanel value={value} index={4}>
          <Settings />
        </TabPanel>
      </Box>
    </Box>
  );
}

export default MainContent;
