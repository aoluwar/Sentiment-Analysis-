import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
  List,
  ListItem,
  Chip,
  Alert,
  IconButton,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { PlayArrow, Stop, Refresh } from '@mui/icons-material';
import { startStream, stopStream, getStreamStatus, getStreamResults, connectWebSocket } from '../services/api';

const StreamingPanel = () => {
  const [source, setSource] = useState('twitter');
  const [config, setConfig] = useState({
    keywords: '',
    limit: 100,
    language: 'en',
  });
  const [streamId, setStreamId] = useState(null);
  const [streamStatus, setStreamStatus] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  const [ws, setWs] = useState(null);
  const [realtime, setRealtime] = useState(true);

  // Handle form input changes
  const handleSourceChange = (e) => {
    setSource(e.target.value);
  };

  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    setConfig({
      ...config,
      [name]: value,
    });
  };

  const handleRealtimeChange = (e) => {
    setRealtime(e.target.checked);
    if (e.target.checked && streamId) {
      connectToWebSocket();
    } else if (ws) {
      ws.close();
      setWs(null);
      setWsConnected(false);
    }
  };

  // Connect to WebSocket for real-time updates
  const connectToWebSocket = () => {
    if (ws) {
      ws.close();
    }

    const newWs = connectWebSocket(
      (data) => {
        // Handle incoming message
        if (data.type === 'analysis') {
          setResults((prevResults) => [data.result, ...prevResults.slice(0, 99)]);
        }
      },
      (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      },
      () => {
        setWsConnected(false);
      }
    );

    newWs.onopen = () => {
      setWsConnected(true);
      // Subscribe to stream
      if (streamId) {
        newWs.send(JSON.stringify({ action: 'subscribe', stream_id: streamId }));
      }
    };

    setWs(newWs);
  };

  // Start a new stream
  const handleStartStream = async () => {
    if (!config.keywords.trim()) {
      setError('Please enter keywords to track');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Prepare config
      const streamConfig = {
        ...config,
        keywords: config.keywords.split(',').map(k => k.trim()),
      };

      // Start stream
      const response = await startStream(source, streamConfig);
      setStreamId(response.stream_id);
      setStreamStatus(response.status);

      // Connect to WebSocket if realtime is enabled
      if (realtime) {
        connectToWebSocket();
      }

      // Fetch initial results
      fetchStreamResults(response.stream_id);
    } catch (err) {
      console.error('Error starting stream:', err);
      setError(err.message || 'An error occurred while starting the stream');
    } finally {
      setLoading(false);
    }
  };

  // Stop the current stream
  const handleStopStream = async () => {
    if (!streamId) return;

    setLoading(true);
    setError('');

    try {
      await stopStream(streamId);
      setStreamStatus('stopped');

      // Close WebSocket connection
      if (ws) {
        ws.close();
        setWs(null);
        setWsConnected(false);
      }
    } catch (err) {
      console.error('Error stopping stream:', err);
      setError(err.message || 'An error occurred while stopping the stream');
    } finally {
      setLoading(false);
    }
  };

  // Refresh stream results
  const fetchStreamResults = async (id = streamId) => {
    if (!id) return;

    setLoading(true);
    setError('');

    try {
      // Get stream status
      const status = await getStreamStatus(id);
      setStreamStatus(status.status);

      // Get stream results
      const streamResults = await getStreamResults(id, 100);
      setResults(streamResults);
    } catch (err) {
      console.error('Error fetching stream results:', err);
      setError(err.message || 'An error occurred while fetching stream results');
    } finally {
      setLoading(false);
    }
  };

  // Refresh results periodically if not using WebSocket
  useEffect(() => {
    let interval;

    if (streamId && streamStatus === 'running' && !realtime) {
      interval = setInterval(() => {
        fetchStreamResults();
      }, 10000); // Refresh every 10 seconds
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [streamId, streamStatus, realtime]);

  // Clean up WebSocket on unmount
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  // Get sentiment color
  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return '#4caf50';
      case 'negative':
        return '#f44336';
      case 'neutral':
        return '#9e9e9e';
      default:
        return '#2196f3';
    }
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Real-time Sentiment Streaming
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Stream real-time sentiment analysis from various sources.
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Source</InputLabel>
              <Select
                value={source}
                onChange={handleSourceChange}
                label="Source"
                disabled={loading || streamStatus === 'running'}
              >
                <MenuItem value="twitter">Twitter</MenuItem>
                <MenuItem value="reddit">Reddit</MenuItem>
                <MenuItem value="kafka">Kafka</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={5}>
            <TextField
              label="Keywords (comma separated)"
              name="keywords"
              value={config.keywords}
              onChange={handleConfigChange}
              fullWidth
              variant="outlined"
              placeholder="Enter keywords to track..."
              disabled={loading || streamStatus === 'running'}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Language</InputLabel>
              <Select
                name="language"
                value={config.language}
                onChange={handleConfigChange}
                label="Language"
                disabled={loading || streamStatus === 'running'}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="es">Spanish</MenuItem>
                <MenuItem value="fr">French</MenuItem>
                <MenuItem value="de">German</MenuItem>
                <MenuItem value="all">All Languages</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={2}>
            <TextField
              label="Result Limit"
              name="limit"
              type="number"
              value={config.limit}
              onChange={handleConfigChange}
              fullWidth
              variant="outlined"
              InputProps={{ inputProps: { min: 10, max: 1000 } }}
              disabled={loading || streamStatus === 'running'}
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                {streamStatus === 'running' ? (
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<Stop />}
                    onClick={handleStopStream}
                    disabled={loading}
                  >
                    Stop Stream
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<PlayArrow />}
                    onClick={handleStartStream}
                    disabled={loading}
                  >
                    Start Stream
                  </Button>
                )}

                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => fetchStreamResults()}
                  disabled={loading || !streamId}
                  sx={{ ml: 2 }}
                >
                  Refresh
                </Button>
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={realtime}
                    onChange={handleRealtimeChange}
                    color="primary"
                  />
                }
                label="Real-time Updates"
              />
            </Box>
          </Grid>

          {error && (
            <Grid item xs={12}>
              <Alert severity="error">{error}</Alert>
            </Grid>
          )}

          {streamId && (
            <Grid item xs={12}>
              <Alert severity="info">
                Stream ID: {streamId} | Status: {streamStatus || 'Unknown'}
                {wsConnected && ' | WebSocket: Connected'}
              </Alert>
            </Grid>
          )}
        </Grid>
      </Paper>

      {loading && !results.length ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Typography variant="h6" gutterBottom>
            Stream Results {results.length > 0 && `(${results.length})`}
          </Typography>

          {results.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                No results yet. Start a stream to see real-time sentiment analysis.
              </Typography>
            </Paper>
          ) : (
            <List sx={{ bgcolor: 'background.paper' }}>
              {results.map((result, index) => (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start" sx={{ flexDirection: 'column' }}>
                    <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle1" component="div" sx={{ fontWeight: 'bold' }}>
                        {result.text.length > 100 ? `${result.text.substring(0, 100)}...` : result.text}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            backgroundColor: getSentimentColor(result.sentiment),
                            mr: 1,
                          }}
                        />
                        <Typography variant="body2">
                          {result.sentiment} ({(result.confidence * 100).toFixed(1)}%)
                        </Typography>
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                      {result.emotions &&
                        Object.entries(result.emotions)
                          .sort(([, a], [, b]) => b - a)
                          .slice(0, 3)
                          .map(([emotion, score]) => (
                            <Chip
                              key={emotion}
                              label={`${emotion}: ${(score * 100).toFixed(1)}%`}
                              size="small"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          ))}
                      <Chip
                        label={result.language || 'Unknown'}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                      {result.source && (
                        <Chip
                          label={result.source}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem' }}
                        />
                      )}
                    </Box>

                    {result.timestamp && (
                      <Typography variant="caption" color="text.secondary">
                        {new Date(result.timestamp).toLocaleString()}
                      </Typography>
                    )}
                  </ListItem>
                  {index < results.length - 1 && <Divider component="li" />}
                </React.Fragment>
              ))}
            </List>
          )}
        </>
      )}
    </Box>
  );
};

export default StreamingPanel;