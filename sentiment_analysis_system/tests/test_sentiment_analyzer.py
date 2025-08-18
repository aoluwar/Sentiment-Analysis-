import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.core.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for SentimentAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config_patcher = patch('src.core.sentiment_analyzer.MODEL_CONFIG', {
            'default_model': 'vader',
            'bert': {
                'model_name': 'bert-base-uncased',
                'enabled': False
            },
            'vader': {
                'enabled': True
            },
            'textblob': {
                'enabled': True
            },
            'custom': {
                'enabled': False,
                'model_path': 'models/custom/sentiment_model.pkl'
            },
            'ensemble': {
                'enabled': True,
                'weights': {
                    'bert': 0.6,
                    'vader': 0.2,
                    'textblob': 0.2,
                    'custom': 0.0
                }
            }
        })
        self.config_patcher.start()
        
        # Create analyzer
        self.analyzer = SentimentAnalyzer()
        
        # Mock the models
        self.analyzer.models = {
            'vader': MagicMock(),
            'textblob': MagicMock(),
            'ensemble': MagicMock()
        }
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.config_patcher.stop()
    
    def test_analyze_text_vader(self):
        """Test analyzing text with VADER"""
        # Mock VADER result
        self.analyzer.models['vader'].polarity_scores.return_value = {
            'compound': 0.8,
            'pos': 0.8,
            'neu': 0.2,
            'neg': 0.0
        }
        
        # Analyze text
        result = self.analyzer.analyze_text("I love this product!", model="vader")
        
        # Check result
        self.assertEqual(result['sentiment'], 'positive')
        self.assertGreater(result['confidence'], 0.7)
        self.assertEqual(result['model'], 'vader')
        self.assertEqual(result['text'], 'I love this product!')
        
        # Verify VADER was called
        self.analyzer.models['vader'].polarity_scores.assert_called_once_with("I love this product!")
    
    def test_analyze_text_textblob(self):
        """Test analyzing text with TextBlob"""
        # Mock TextBlob
        mock_blob = MagicMock()
        mock_blob.sentiment.polarity = -0.7
        mock_blob.sentiment.subjectivity = 0.8
        
        with patch('src.core.sentiment_analyzer.TextBlob', return_value=mock_blob):
            # Analyze text
            result = self.analyzer.analyze_text("I hate this product!", model="textblob")
            
            # Check result
            self.assertEqual(result['sentiment'], 'negative')
            self.assertGreater(result['confidence'], 0.6)
            self.assertEqual(result['model'], 'textblob')
            self.assertEqual(result['text'], 'I hate this product!')
    
    def test_analyze_text_ensemble(self):
        """Test analyzing text with ensemble model"""
        # Mock VADER result
        self.analyzer.models['vader'].polarity_scores.return_value = {
            'compound': 0.8,
            'pos': 0.8,
            'neu': 0.2,
            'neg': 0.0
        }
        
        # Mock TextBlob
        mock_blob = MagicMock()
        mock_blob.sentiment.polarity = 0.7
        mock_blob.sentiment.subjectivity = 0.8
        
        with patch('src.core.sentiment_analyzer.TextBlob', return_value=mock_blob):
            # Analyze text
            result = self.analyzer.analyze_text("I love this product!", model="ensemble")
            
            # Check result
            self.assertEqual(result['sentiment'], 'positive')
            self.assertGreater(result['confidence'], 0.7)
            self.assertEqual(result['model'], 'ensemble')
            self.assertEqual(result['text'], 'I love this product!')
    
    def test_analyze_batch(self):
        """Test analyzing a batch of texts"""
        # Mock VADER results
        self.analyzer.models['vader'].polarity_scores.side_effect = [
            {'compound': 0.8, 'pos': 0.8, 'neu': 0.2, 'neg': 0.0},
            {'compound': -0.6, 'pos': 0.0, 'neu': 0.4, 'neg': 0.6}
        ]
        
        # Analyze batch
        texts = ["I love this product!", "I hate this product!"]
        results = self.analyzer.analyze_batch(texts, model="vader")
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['sentiment'], 'positive')
        self.assertEqual(results[1]['sentiment'], 'negative')
        
        # Verify VADER was called twice
        self.assertEqual(self.analyzer.models['vader'].polarity_scores.call_count, 2)
    
    def test_health_check(self):
        """Test health check"""
        # Mock models
        self.analyzer.models['vader'] = MagicMock()
        self.analyzer.models['textblob'] = MagicMock()
        
        # Run health check
        health = self.analyzer.health_check()
        
        # Check result
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('models', health)
        self.assertIn('vader', health['models'])
        self.assertIn('textblob', health['models'])

if __name__ == '__main__':
    unittest.main()