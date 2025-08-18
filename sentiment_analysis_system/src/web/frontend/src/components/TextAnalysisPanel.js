import React, { useState } from 'react';
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
  Chip,
} from '@mui/material';
import { analyzeText } from '../services/api';

const TextAnalysisPanel = () => {
  const [text, setText] = useState('');
  const [model, setModel] = useState('ensemble');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleModelChange = (e) => {
    setModel(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const analysisResult = await analyzeText(text, model);
      setResult(analysisResult);
    } catch (err) {
      console.error('Error analyzing text:', err);
      setError(err.message || 'An error occurred while analyzing the text');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
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

  const getEmotionColor = (emotion) => {
    switch (emotion.toLowerCase()) {
      case 'joy':
      case 'happy':
        return '#ffc107';
      case 'sadness':
      case 'sad':
        return '#2196f3';
      case 'anger':
      case 'angry':
        return '#f44336';
      case 'fear':
      case 'scared':
        return '#9c27b0';
      case 'surprise':
      case 'surprised':
        return '#ff9800';
      case 'disgust':
      case 'disgusted':
        return '#795548';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Text Sentiment Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Enter text to analyze its sentiment and emotions. Choose a model to use for analysis.
        </Typography>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="Text to analyze"
                multiline
                rows={4}
                value={text}
                onChange={handleTextChange}
                fullWidth
                variant="outlined"
                placeholder="Enter text here..."
                error={!!error}
                helperText={error}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth variant="outlined">
                <InputLabel>Model</InputLabel>
                <Select
                  value={model}
                  onChange={handleModelChange}
                  label="Model"
                >
                  <MenuItem value="bert">BERT</MenuItem>
                  <MenuItem value="vader">VADER</MenuItem>
                  <MenuItem value="textblob">TextBlob</MenuItem>
                  <MenuItem value="ensemble">Ensemble (Recommended)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} sx={{ display: 'flex', alignItems: 'center' }}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                disabled={loading}
                sx={{ height: 56 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {result && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Analysis Results
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Sentiment
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box
                  sx={{
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    backgroundColor: getSentimentColor(result.sentiment),
                    mr: 1,
                  }}
                />
                <Typography variant="h5" sx={{ mr: 2 }}>
                  {result.sentiment}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Confidence: {(result.confidence * 100).toFixed(2)}%
                </Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            {result.emotions && Object.keys(result.emotions).length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Emotions
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {Object.entries(result.emotions)
                    .sort(([, a], [, b]) => b - a)
                    .map(([emotion, score]) => (
                      <Chip
                        key={emotion}
                        label={`${emotion}: ${(score * 100).toFixed(1)}%`}
                        sx={{
                          backgroundColor: getEmotionColor(emotion),
                          color: 'white',
                        }}
                      />
                    ))}
                </Box>
              </Box>
            )}

            <Divider sx={{ my: 2 }} />

            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Language
              </Typography>
              <Chip label={result.language || 'Unknown'} />
            </Box>

            {result.processed_text && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Processed Text
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                  <Typography variant="body2">{result.processed_text}</Typography>
                </Paper>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TextAnalysisPanel;