import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.api.main import app

class TestAPI(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test client
        self.client = TestClient(app)
        
        # Mock the components
        self.sentiment_analyzer_patcher = patch('src.api.main.SentimentAnalyzer')
        self.emotion_detector_patcher = patch('src.api.main.EmotionDetector')
        self.text_processor_patcher = patch('src.api.main.TextProcessor')
        self.stream_manager_patcher = patch('src.api.main.StreamManager')
        self.db_manager_patcher = patch('src.api.main.DatabaseManager')
        self.cache_manager_patcher = patch('src.api.main.CacheManager')
        
        self.mock_sentiment_analyzer = self.sentiment_analyzer_patcher.start()
        self.mock_emotion_detector = self.emotion_detector_patcher.start()
        self.mock_text_processor = self.text_processor_patcher.start()
        self.mock_stream_manager = self.stream_manager_patcher.start()
        self.mock_db_manager = self.db_manager_patcher.start()
        self.mock_cache_manager = self.cache_manager_patcher.start()
        
        # Set up mock instances
        self.mock_sentiment_analyzer_instance = MagicMock()
        self.mock_emotion_detector_instance = MagicMock()
        self.mock_text_processor_instance = MagicMock()
        self.mock_stream_manager_instance = MagicMock()
        self.mock_db_manager_instance = MagicMock()
        self.mock_cache_manager_instance = MagicMock()
        
        self.mock_sentiment_analyzer.return_value = self.mock_sentiment_analyzer_instance
        self.mock_emotion_detector.return_value = self.mock_emotion_detector_instance
        self.mock_text_processor.return_value = self.mock_text_processor_instance
        self.mock_stream_manager.return_value = self.mock_stream_manager_instance
        self.mock_db_manager.return_value = self.mock_db_manager_instance
        self.mock_cache_manager.return_value = self.mock_cache_manager_instance
        
        # Set up mock responses
        self.mock_sentiment_analyzer_instance.analyze_text.return_value = {
            'text': 'This is a test',
            'sentiment': 'positive',
            'confidence': 0.85,
            'model': 'vader'
        }
        
        self.mock_emotion_detector_instance.detect_emotions.return_value = {
            'text': 'This is a test',
            'emotions': {
                'joy': 0.8,
                'sadness': 0.1,
                'anger': 0.05,
                'fear': 0.03,
                'surprise': 0.02
            },
            'model': 'rule_based'
        }
        
        self.mock_text_processor_instance.process_text.return_value = 'processed text'
        self.mock_text_processor_instance.detect_language.return_value = 'en'
        
        self.mock_cache_manager_instance.get_cached_result.return_value = None
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.sentiment_analyzer_patcher.stop()
        self.emotion_detector_patcher.stop()
        self.text_processor_patcher.stop()
        self.stream_manager_patcher.stop()
        self.db_manager_patcher.stop()
        self.cache_manager_patcher.stop()
    
    def test_analyze_text(self):
        """Test analyze text endpoint"""
        # Make request
        response = self.client.post(
            "/api/v1/analyze",
            json={
                "text": "This is a test",
                "model": "vader",
                "include_emotions": True
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['sentiment'], 'positive')
        self.assertEqual(data['confidence'], 0.85)
        self.assertIn('emotions', data)
        self.assertEqual(data['language'], 'en')
        
        # Verify methods were called
        self.mock_text_processor_instance.process_text.assert_called_once()
        self.mock_sentiment_analyzer_instance.analyze_text.assert_called_once()
        self.mock_emotion_detector_instance.detect_emotions.assert_called_once()
        self.mock_db_manager_instance.store_sentiment_analysis.assert_called_once()
    
    def test_analyze_batch(self):
        """Test analyze batch endpoint"""
        # Set up mock batch responses
        self.mock_sentiment_analyzer_instance.analyze_batch_texts.return_value = [
            {
                'text': 'This is a test',
                'sentiment': 'positive',
                'confidence': 0.85,
                'model': 'vader'
            },
            {
                'text': 'This is another test',
                'sentiment': 'negative',
                'confidence': 0.75,
                'model': 'vader'
            }
        ]
        
        self.mock_emotion_detector_instance.detect_batch_emotions.return_value = [
            {
                'text': 'This is a test',
                'emotions': {
                    'joy': 0.8,
                    'sadness': 0.1,
                    'anger': 0.05,
                    'fear': 0.03,
                    'surprise': 0.02
                },
                'model': 'rule_based'
            },
            {
                'text': 'This is another test',
                'emotions': {
                    'joy': 0.1,
                    'sadness': 0.7,
                    'anger': 0.1,
                    'fear': 0.05,
                    'surprise': 0.05
                },
                'model': 'rule_based'
            }
        ]
        
        self.mock_text_processor_instance.process_batch_texts.return_value = [
            'processed text 1',
            'processed text 2'
        ]
        
        self.mock_text_processor_instance.detect_language.side_effect = ['en', 'en']
        
        # Make request
        response = self.client.post(
            "/api/v1/analyze/batch",
            json={
                "texts": ["This is a test", "This is another test"],
                "model": "vader",
                "include_emotions": True
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['sentiment'], 'positive')
        self.assertEqual(data[1]['sentiment'], 'negative')
        self.assertIn('emotions', data[0])
        self.assertIn('emotions', data[1])
        
        # Verify methods were called
        self.mock_text_processor_instance.process_batch_texts.assert_called_once()
        self.mock_sentiment_analyzer_instance.analyze_batch_texts.assert_called_once()
        self.mock_emotion_detector_instance.detect_batch_emotions.assert_called_once()
        self.mock_db_manager_instance.store_batch_sentiment_analysis.assert_called_once()
    
    def test_start_stream(self):
        """Test start stream endpoint"""
        # Set up mock stream response
        self.mock_stream_manager_instance.start_stream.return_value = "stream_123"
        
        # Make request
        response = self.client.post(
            "/api/v1/stream/start",
            json={
                "source": "twitter",
                "keywords": ["python", "programming"],
                "languages": ["en"],
                "limit": 100
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['stream_id'], "stream_123")
        self.assertEqual(data['status'], "started")
        
        # Verify method was called
        self.mock_stream_manager_instance.start_stream.assert_called_once()
    
    def test_stop_stream(self):
        """Test stop stream endpoint"""
        # Set up mock stream response
        self.mock_stream_manager_instance.stop_stream.return_value = True
        
        # Make request
        response = self.client.post(
            "/api/v1/stream/stop",
            json={"stream_id": "stream_123"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['stream_id'], "stream_123")
        self.assertEqual(data['status'], "stopped")
        
        # Verify method was called
        self.mock_stream_manager_instance.stop_stream.assert_called_once_with("stream_123")
    
    def test_get_stream_status(self):
        """Test get stream status endpoint"""
        # Set up mock stream response
        self.mock_stream_manager_instance.get_stream_status.return_value = {
            "status": "running",
            "source": "twitter",
            "keywords": ["python", "programming"],
            "languages": ["en"],
            "limit": 100,
            "count": 50,
            "start_time": "2023-01-01T12:00:00"
        }
        
        # Make request
        response = self.client.get("/api/v1/stream/status/stream_123")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], "running")
        self.assertEqual(data['source'], "twitter")
        self.assertEqual(data['count'], 50)
        
        # Verify method was called
        self.mock_stream_manager_instance.get_stream_status.assert_called_once_with("stream_123")
    
    def test_get_stream_results(self):
        """Test get stream results endpoint"""
        # Set up mock stream response
        self.mock_stream_manager_instance.get_stream_results.return_value = [
            {
                "text": "Python is awesome!",
                "sentiment": "positive",
                "confidence": 0.9,
                "source": "twitter"
            },
            {
                "text": "I hate bugs in my code",
                "sentiment": "negative",
                "confidence": 0.8,
                "source": "twitter"
            }
        ]
        
        # Make request
        response = self.client.get("/api/v1/stream/results/stream_123")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['sentiment'], "positive")
        self.assertEqual(data[1]['sentiment'], "negative")
        
        # Verify method was called
        self.mock_stream_manager_instance.get_stream_results.assert_called_once_with("stream_123")
    
    def test_health(self):
        """Test health endpoint"""
        # Set up mock health responses
        self.mock_sentiment_analyzer_instance.health_check.return_value = {"status": "healthy"}
        self.mock_emotion_detector_instance.health_check.return_value = {"status": "healthy"}
        self.mock_text_processor_instance.health_check.return_value = {"status": "healthy"}
        self.mock_stream_manager_instance.health_check.return_value = {"status": "healthy"}
        self.mock_db_manager_instance.health_check.return_value = {"status": "healthy"}
        self.mock_cache_manager_instance.health_check.return_value = {"status": "healthy"}
        
        # Make request
        response = self.client.get("/api/v1/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], "healthy")
        self.assertIn('components', data)
        self.assertEqual(len(data['components']), 6)
        
        # Verify methods were called
        self.mock_sentiment_analyzer_instance.health_check.assert_called_once()
        self.mock_emotion_detector_instance.health_check.assert_called_once()
        self.mock_text_processor_instance.health_check.assert_called_once()
        self.mock_stream_manager_instance.health_check.assert_called_once()
        self.mock_db_manager_instance.health_check.assert_called_once()
        self.mock_cache_manager_instance.health_check.assert_called_once()

if __name__ == '__main__':
    unittest.main()