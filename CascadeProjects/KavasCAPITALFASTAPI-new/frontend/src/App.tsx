import React from 'react';
import { Box, ThemeProvider, CssBaseline, AppBar, Toolbar, Typography } from '@mui/material';
import { Provider } from 'react-redux';
import { store } from './store/index';
import { theme } from './theme';
import MainContent from './components/MainContent';
import { AccessTokenInput } from './components/Auth/AccessTokenInput';
import { useSelector } from 'react-redux';
import type { RootState } from './store';

function AppContent() {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            KAVAS CAPITAL
          </Typography>
        </Toolbar>
      </AppBar>
      <Box sx={{ mt: 8, flexGrow: 1 }}>
        {!isAuthenticated ? (
          <AccessTokenInput />
        ) : (
          <MainContent />
        )}
      </Box>
    </Box>
  );
}

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppContent />
      </ThemeProvider>
    </Provider>
  );
}

export default App;
