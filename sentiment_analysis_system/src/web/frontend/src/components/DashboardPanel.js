import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  Language as LanguageIcon,
  Psychology as PsychologyIcon,
  Stream as StreamIcon,
  DataObject as DataObjectIcon,
} from '@mui/icons-material';
import { getRecentAnalyses, getSentimentDistribution, getEmotionDistribution } from '../services/api';

// Import chart components (assuming you're using recharts)
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const DashboardPanel = ({ systemHealth }) => {
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [sentimentDistribution, setSentimentDistribution] = useState([]);
  const [emotionDistribution, setEmotionDistribution] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Colors for charts
  const SENTIMENT_COLORS = {
    positive: '#4caf50',
    negative: '#f44336',
    neutral: '#9e9e9e',
    mixed: '#2196f3',
  };

  const EMOTION_COLORS = {
    joy: '#ffc107',
    sadness: '#2196f3',
    anger: '#f44336',
    fear: '#9c27b0',
    surprise: '#ff9800',
    disgust: '#795548',
    // Fallback colors for other emotions
    love: '#e91e63',
    optimism: '#8bc34a',
    pessimism: '#607d8b',
    trust: '#00bcd4',
    anticipation: '#ff5722',
  };

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError('');

      try {
        // Fetch data in parallel
        const [analyses, sentiments, emotions] = await Promise.all([
          getRecentAnalyses(5),
          getSentimentDistribution(),
          getEmotionDistribution(),
        ]);

        setRecentAnalyses(analyses);

        // Format sentiment distribution for chart
        const sentimentData = Object.entries(sentiments).map(([sentiment, count]) => ({
          name: sentiment,
          value: count,
          color: SENTIMENT_COLORS[sentiment.toLowerCase()] || '#9e9e9e',
        }));
        setSentimentDistribution(sentimentData);

        // Format emotion distribution for chart
        const emotionData = Object.entries(emotions).map(([emotion, score]) => ({
          name: emotion,
          value: score,
          color: EMOTION_COLORS[emotion.toLowerCase()] || '#9e9e9e',
        }));
        setEmotionDistribution(emotionData);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh data every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);

    return () => clearInterval(interval);
  }, []);

  // Get status icon based on status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'degraded':
        return <WarningIcon sx={{ color: '#ff9800' }} />;
      case 'error':
      case 'unhealthy':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return <CircularProgress size={20} />;
    }
  };

  // Get component icon based on component name
  const getComponentIcon = (component) => {
    switch (component.toLowerCase()) {
      case 'database':
      case 'postgres':
      case 'mongodb':
        return <StorageIcon />;
      case 'redis':
      case 'cache':
        return <MemoryIcon />;
      case 'sentiment_analyzer':
      case 'emotion_detector':
        return <PsychologyIcon />;
      case 'text_processor':
        return <LanguageIcon />;
      case 'stream_manager':
        return <StreamIcon />;
      default:
        return <DataObjectIcon />;
    }
  };

  return (
    <Box sx={{ mt: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* System Health Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {systemHealth.status === 'loading' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List>
                  <ListItem>
                    <ListItemIcon>{getStatusIcon(systemHealth.status)}</ListItemIcon>
                    <ListItemText
                      primary="Overall Status"
                      secondary={systemHealth.status}
                      primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                  </ListItem>

                  <Divider component="li" />

                  {systemHealth.components &&
                    Object.entries(systemHealth.components).map(([component, status]) => (
                      <ListItem key={component}>
                        <ListItemIcon>{getComponentIcon(component)}</ListItemIcon>
                        <ListItemText
                          primary={component.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                          secondary={status}
                          primaryTypographyProps={{ fontWeight: 'medium' }}
                        />
                      </ListItem>
                    ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Analyses Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Analyses
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {loading && !recentAnalyses.length ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : recentAnalyses.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                  No recent analyses available.
                </Typography>
              ) : (
                <List>
                  {recentAnalyses.map((analysis, index) => (
                    <React.Fragment key={index}>
                      <ListItem alignItems="flex-start">
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Box
                                sx={{
                                  width: 12,
                                  height: 12,
                                  borderRadius: '50%',
                                  backgroundColor: SENTIMENT_COLORS[analysis.sentiment?.toLowerCase()] || '#9e9e9e',
                                  mr: 1,
                                }}
                              />
                              <Typography variant="body1" component="span">
                                {analysis.sentiment} ({(analysis.confidence * 100).toFixed(1)}%)
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <>
                              <Typography variant="body2" component="span" color="text.primary">
                                {analysis.text.length > 60 ? `${analysis.text.substring(0, 60)}...` : analysis.text}
                              </Typography>
                              {analysis.timestamp && (
                                <Typography variant="caption" display="block" color="text.secondary">
                                  {new Date(analysis.timestamp).toLocaleString()}
                                </Typography>
                              )}
                            </>
                          }
                        />
                      </ListItem>
                      {index < recentAnalyses.length - 1 && <Divider component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Sentiment Distribution Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} className="chart-container">
            <Typography variant="h6" gutterBottom>
              Sentiment Distribution
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {loading && !sentimentDistribution.length ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : sentimentDistribution.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                No sentiment data available.
              </Typography>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} analyses`, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Emotion Distribution Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }} className="chart-container">
            <Typography variant="h6" gutterBottom>
              Emotion Distribution
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {loading && !emotionDistribution.length ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : emotionDistribution.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                No emotion data available.
              </Typography>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={emotionDistribution.sort((a, b) => b.value - a.value)}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Score']} />
                  <Legend />
                  <Bar dataKey="value" name="Average Score">
                    {emotionDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPanel;