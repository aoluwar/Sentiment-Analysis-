import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box, AppBar, Toolbar, Tab, Tabs } from '@mui/material';
import TextAnalysisPanel from './components/TextAnalysisPanel';
import StreamingPanel from './components/StreamingPanel';
import DashboardPanel from './components/DashboardPanel';
import { fetchHealth } from './services/api';

function App() {
  const [value, setValue] = useState(0);
  const [systemHealth, setSystemHealth] = useState({
    status: 'loading',
    components: {}
  });

  useEffect(() => {
    // Fetch system health status on component mount
    const checkHealth = async () => {
      try {
        const health = await fetchHealth();
        setSystemHealth(health);
      } catch (error) {
        console.error('Error fetching health status:', error);
        setSystemHealth({
          status: 'error',
          message: 'Could not connect to API'
        });
      }
    };

    checkHealth();
    // Set up interval to check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#4caf50';
      case 'degraded':
        return '#ff9800';
      case 'error':
      case 'unhealthy':
        return '#f44336';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Sentiment Analysis Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ mr: 1 }}>
              System Status:
            </Typography>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: getHealthStatusColor(systemHealth.status),
                mr: 1
              }}
            />
            <Typography variant="body2">
              {systemHealth.status === 'loading' ? 'Checking...' : systemHealth.status}
            </Typography>
          </Box>
        </Toolbar>
        <Tabs
          value={value}
          onChange={handleChange}
          indicatorColor="secondary"
          textColor="inherit"
          variant="fullWidth"
        >
          <Tab label="Dashboard" />
          <Tab label="Text Analysis" />
          <Tab label="Streaming" />
        </Tabs>
      </AppBar>

      <Container maxWidth="lg" className="dashboard-container">
        {value === 0 && (
          <DashboardPanel systemHealth={systemHealth} />
        )}
        {value === 1 && (
          <TextAnalysisPanel />
        )}
        {value === 2 && (
          <StreamingPanel />
        )}
      </Container>
    </div>
  );
}

export default App;