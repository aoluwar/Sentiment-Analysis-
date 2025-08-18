import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.utils.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config_patcher = patch('src.utils.cache_manager.CACHE_CONFIG', {
            'redis': {
                'enabled': True,
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'ttl': 3600  # 1 hour
            }
        })
        self.config_patcher.start()
        
        # Mock Redis client
        self.redis_patcher = patch('src.utils.cache_manager.Redis')
        self.mock_redis = self.redis_patcher.start()
        self.mock_redis_instance = MagicMock()
        self.mock_redis.return_value = self.mock_redis_instance
        
        # Create cache manager
        self.cache_manager = CacheManager()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.config_patcher.stop()
        self.redis_patcher.stop()
    
    def test_init_redis(self):
        """Test initializing Redis connection"""
        # Check Redis was initialized
        self.mock_redis.assert_called_once_with(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def test_generate_cache_key(self):
        """Test generating cache key"""
        # Generate key
        text = "This is a test"
        model = "vader"
        key = self.cache_manager._generate_cache_key(text, model)
        
        # Check key format
        self.assertTrue(key.startswith("sentiment:"))
        self.assertIn("vader", key)
    
    def test_get_cached_result_hit(self):
        """Test getting cached result - cache hit"""
        # Mock Redis get
        cached_result = json.dumps({
            'text': 'This is a test',
            'sentiment': 'positive',
            'confidence': 0.85,
            'model': 'vader'
        })
        self.mock_redis_instance.get.return_value = cached_result
        
        # Get cached result
        text = "This is a test"
        model = "vader"
        result = self.cache_manager.get_cached_result(text, model)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertEqual(result['sentiment'], 'positive')
        self.assertEqual(result['confidence'], 0.85)
        
        # Check Redis get was called
        self.mock_redis_instance.get.assert_called_once()
    
    def test_get_cached_result_miss(self):
        """Test getting cached result - cache miss"""
        # Mock Redis get
        self.mock_redis_instance.get.return_value = None
        
        # Get cached result
        text = "This is a test"
        model = "vader"
        result = self.cache_manager.get_cached_result(text, model)
        
        # Check result
        self.assertIsNone(result)
        
        # Check Redis get was called
        self.mock_redis_instance.get.assert_called_once()
    
    def test_set_cached_result(self):
        """Test setting cached result"""
        # Set cached result
        analysis = {
            'text': 'This is a test',
            'sentiment': 'positive',
            'confidence': 0.85,
            'model': 'vader'
        }
        self.cache_manager.set_cached_result(analysis)
        
        # Check Redis set was called
        self.mock_redis_instance.setex.assert_called_once()
    
    def test_get_batch_cached_results(self):
        """Test getting batch cached results"""
        # Mock Redis mget
        cached_results = [
            json.dumps({
                'text': 'This is a test',
                'sentiment': 'positive',
                'confidence': 0.85,
                'model': 'vader'
            }),
            None,
            json.dumps({
                'text': 'This is another test',
                'sentiment': 'negative',
                'confidence': 0.75,
                'model': 'vader'
            })
        ]
        self.mock_redis_instance.mget.return_value = cached_results
        
        # Get batch cached results
        texts = [
            "This is a test",
            "This is a missing test",
            "This is another test"
        ]
        model = "vader"
        results = self.cache_manager.get_batch_cached_results(texts, model)
        
        # Check results
        self.assertEqual(len(results), 3)
        self.assertIsNotNone(results[0])
        self.assertIsNone(results[1])
        self.assertIsNotNone(results[2])
        self.assertEqual(results[0]['sentiment'], 'positive')
        self.assertEqual(results[2]['sentiment'], 'negative')
        
        # Check Redis mget was called
        self.mock_redis_instance.mget.assert_called_once()
    
    def test_set_batch_cached_results(self):
        """Test setting batch cached results"""
        # Set batch cached results
        analyses = [
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
        self.cache_manager.set_batch_cached_results(analyses)
        
        # Check Redis pipeline was used
        self.mock_redis_instance.pipeline.assert_called_once()
        self.mock_redis_instance.pipeline.return_value.execute.assert_called_once()
    
    def test_clear_cache(self):
        """Test clearing cache"""
        # Clear cache
        self.cache_manager.clear_cache()
        
        # Check Redis flushdb was called
        self.mock_redis_instance.flushdb.assert_called_once()
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Mock Redis info
        self.mock_redis_instance.info.return_value = {
            'keyspace_hits': 100,
            'keyspace_misses': 50,
            'used_memory_human': '1M',
            'db0': {'keys': 200}
        }
        
        # Get cache stats
        stats = self.cache_manager.get_cache_stats()
        
        # Check stats
        self.assertEqual(stats['hits'], 100)
        self.assertEqual(stats['misses'], 50)
        self.assertEqual(stats['hit_ratio'], 100 / (100 + 50))
        self.assertEqual(stats['memory_usage'], '1M')
        self.assertEqual(stats['total_keys'], 200)
        
        # Check Redis info was called
        self.mock_redis_instance.info.assert_called_once()
    
    def test_close(self):
        """Test closing Redis connection"""
        # Close connection
        self.cache_manager.close()
        
        # Check Redis close was called
        self.mock_redis_instance.close.assert_called_once()
    
    def test_health_check(self):
        """Test health check"""
        # Mock Redis ping
        self.mock_redis_instance.ping.return_value = True
        
        # Run health check
        health = self.cache_manager.health_check()
        
        # Check result
        self.assertEqual(health['status'], 'healthy')
        self.assertTrue(health['redis_connected'])
        
        # Check Redis ping was called
        self.mock_redis_instance.ping.assert_called_once()

if __name__ == '__main__':
    unittest.main()