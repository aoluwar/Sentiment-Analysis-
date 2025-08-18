/**
 * API service for communicating with the backend
 */

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Fetch health status of the system
 * @returns {Promise<Object>} Health status
 */
export const fetchHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
};

/**
 * Analyze text sentiment
 * @param {string} text - Text to analyze
 * @param {string} model - Model to use (bert, vader, textblob, ensemble)
 * @returns {Promise<Object>} Analysis result
 */
export const analyzeText = async (text, model = 'ensemble') => {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, model }),
  });
  
  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Analyze batch of texts
 * @param {Array<string>} texts - Texts to analyze
 * @param {string} model - Model to use (bert, vader, textblob, ensemble)
 * @returns {Promise<Array<Object>>} Analysis results
 */
export const analyzeBatch = async (texts, model = 'ensemble') => {
  const response = await fetch(`${API_BASE_URL}/analyze/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ texts, model }),
  });
  
  if (!response.ok) {
    throw new Error(`Batch analysis failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Start a stream
 * @param {string} source - Stream source (twitter, reddit, kafka)
 * @param {Object} config - Stream configuration
 * @returns {Promise<Object>} Stream information
 */
export const startStream = async (source, config) => {
  const response = await fetch(`${API_BASE_URL}/stream/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ source, config }),
  });
  
  if (!response.ok) {
    throw new Error(`Starting stream failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Stop a stream
 * @param {string} streamId - Stream ID
 * @returns {Promise<Object>} Result
 */
export const stopStream = async (streamId) => {
  const response = await fetch(`${API_BASE_URL}/stream/stop/${streamId}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Stopping stream failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Get stream status
 * @param {string} streamId - Stream ID
 * @returns {Promise<Object>} Stream status
 */
export const getStreamStatus = async (streamId) => {
  const response = await fetch(`${API_BASE_URL}/stream/status/${streamId}`);
  
  if (!response.ok) {
    throw new Error(`Getting stream status failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Get stream results
 * @param {string} streamId - Stream ID
 * @param {number} limit - Maximum number of results to return
 * @returns {Promise<Array<Object>>} Stream results
 */
export const getStreamResults = async (streamId, limit = 100) => {
  const response = await fetch(`${API_BASE_URL}/stream/results/${streamId}?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Getting stream results failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Get recent analyses
 * @param {number} limit - Maximum number of results to return
 * @returns {Promise<Array<Object>>} Recent analyses
 */
export const getRecentAnalyses = async (limit = 100) => {
  const response = await fetch(`${API_BASE_URL}/analyses/recent?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Getting recent analyses failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Get sentiment distribution
 * @returns {Promise<Object>} Sentiment distribution
 */
export const getSentimentDistribution = async () => {
  const response = await fetch(`${API_BASE_URL}/analyses/distribution/sentiment`);
  
  if (!response.ok) {
    throw new Error(`Getting sentiment distribution failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Get emotion distribution
 * @returns {Promise<Object>} Emotion distribution
 */
export const getEmotionDistribution = async () => {
  const response = await fetch(`${API_BASE_URL}/analyses/distribution/emotion`);
  
  if (!response.ok) {
    throw new Error(`Getting emotion distribution failed: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Connect to WebSocket for real-time analysis
 * @param {Function} onMessage - Callback for received messages
 * @param {Function} onError - Callback for errors
 * @param {Function} onClose - Callback for connection close
 * @returns {WebSocket} WebSocket connection
 */
export const connectWebSocket = (onMessage, onError, onClose) => {
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
  const ws = new WebSocket(wsUrl);
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) {
      onError(error);
    }
  };
  
  ws.onclose = (event) => {
    console.log('WebSocket connection closed:', event);
    if (onClose) {
      onClose(event);
    }
  };
  
  return ws;
};