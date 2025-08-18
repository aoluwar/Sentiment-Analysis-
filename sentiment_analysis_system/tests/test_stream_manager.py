import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.streaming.stream_manager import StreamManager

class TestStreamManager(unittest.TestCase):
    """Test cases for StreamManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config_patcher = patch('src.streaming.stream_manager.STREAM_CONFIG', {
            'twitter': {
                'enabled': True,
                'api_key': 'mock_api_key',
                'api_secret': 'mock_api_secret',
                'access_token': 'mock_access_token',
                'access_token_secret': 'mock_token_secret',
                'max_results': 100
            },
            'reddit': {
                'enabled': True,
                'client_id': 'mock_client_id',
                'client_secret': 'mock_client_secret',
                'user_agent': 'mock_user_agent',
                'max_results': 100
            },
            'kafka': {
                'enabled': True,
                'bootstrap_servers': 'localhost:9092',
                'topic': 'sentiment_data',
                'group_id': 'sentiment_group'
            }
        })
        self.config_patcher.start()
        
        # Create stream manager
        self.stream_manager = StreamManager()
        
        # Mock the stream implementations
        self.stream_manager._twitter_stream = MagicMock()
        self.stream_manager._reddit_stream = MagicMock()
        self.stream_manager._kafka_stream = MagicMock()
        
        # Mock the callback registry
        self.stream_manager._callbacks = {}
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.config_patcher.stop()
    
    def test_start_twitter_stream(self):
        """Test starting a Twitter stream"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="twitter",
            keywords=["python", "programming"],
            languages=["en"],
            limit=50
        )
        
        # Check result
        self.assertIsNotNone(stream_id)
        self.assertIn(stream_id, self.stream_manager._active_streams)
        self.assertEqual(self.stream_manager._active_streams[stream_id]['source'], 'twitter')
        self.assertEqual(self.stream_manager._active_streams[stream_id]['status'], 'running')
        
        # Verify Twitter stream was called
        self.stream_manager._twitter_stream.assert_called_once()
    
    def test_start_reddit_stream(self):
        """Test starting a Reddit stream"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="reddit",
            keywords=["python", "programming"],
            subreddits=["programming", "python"],
            limit=50
        )
        
        # Check result
        self.assertIsNotNone(stream_id)
        self.assertIn(stream_id, self.stream_manager._active_streams)
        self.assertEqual(self.stream_manager._active_streams[stream_id]['source'], 'reddit')
        self.assertEqual(self.stream_manager._active_streams[stream_id]['status'], 'running')
        
        # Verify Reddit stream was called
        self.stream_manager._reddit_stream.assert_called_once()
    
    def test_start_kafka_stream(self):
        """Test starting a Kafka stream"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="kafka",
            topic="test_topic",
            limit=50
        )
        
        # Check result
        self.assertIsNotNone(stream_id)
        self.assertIn(stream_id, self.stream_manager._active_streams)
        self.assertEqual(self.stream_manager._active_streams[stream_id]['source'], 'kafka')
        self.assertEqual(self.stream_manager._active_streams[stream_id]['status'], 'running')
        
        # Verify Kafka stream was called
        self.stream_manager._kafka_stream.assert_called_once()
    
    def test_stop_stream(self):
        """Test stopping a stream"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="twitter",
            keywords=["python"],
            languages=["en"],
            limit=50
        )
        
        # Stop stream
        result = self.stream_manager.stop_stream(stream_id)
        
        # Check result
        self.assertTrue(result)
        self.assertEqual(self.stream_manager._active_streams[stream_id]['status'], 'stopped')
    
    def test_get_stream_status(self):
        """Test getting stream status"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="twitter",
            keywords=["python"],
            languages=["en"],
            limit=50
        )
        
        # Get status
        status = self.stream_manager.get_stream_status(stream_id)
        
        # Check result
        self.assertEqual(status['status'], 'running')
        self.assertEqual(status['source'], 'twitter')
        self.assertEqual(status['keywords'], ["python"])
        self.assertEqual(status['languages'], ["en"])
        self.assertEqual(status['limit'], 50)
    
    def test_get_stream_results(self):
        """Test getting stream results"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="twitter",
            keywords=["python"],
            languages=["en"],
            limit=50
        )
        
        # Mock some results
        self.stream_manager._active_streams[stream_id]['results'] = [
            {"text": "Python is awesome!", "sentiment": "positive"},
            {"text": "I hate bugs in my code", "sentiment": "negative"}
        ]
        
        # Get results
        results = self.stream_manager.get_stream_results(stream_id)
        
        # Check result
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['text'], "Python is awesome!")
        self.assertEqual(results[1]['sentiment'], "negative")
    
    def test_register_callback(self):
        """Test registering a callback"""
        # Create mock callback
        callback = MagicMock()
        
        # Register callback
        self.stream_manager.register_callback(callback)
        
        # Check callback was registered
        self.assertIn(callback, self.stream_manager._callbacks)
    
    def test_process_stream_data(self):
        """Test processing stream data"""
        # Start stream
        stream_id = self.stream_manager.start_stream(
            source="twitter",
            keywords=["python"],
            languages=["en"],
            limit=50
        )
        
        # Create mock callback
        callback = MagicMock()
        self.stream_manager.register_callback(callback)
        
        # Process data
        data = {"text": "Python is awesome!", "sentiment": "positive"}
        self.stream_manager._process_stream_data(stream_id, data)
        
        # Check result was added
        self.assertIn(data, self.stream_manager._active_streams[stream_id]['results'])
        
        # Check callback was called
        callback.assert_called_once_with(stream_id, data)
    
    def test_health_check(self):
        """Test health check"""
        # Run health check
        health = self.stream_manager.health_check()
        
        # Check result
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('active_streams', health)
        self.assertIn('sources', health)

if __name__ == '__main__':
    unittest.main()