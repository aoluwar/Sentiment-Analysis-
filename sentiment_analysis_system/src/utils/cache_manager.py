import logging
import json
import time
from typing import Dict, Any, List, Optional
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import CACHE_CONFIG

logger = logging.getLogger(__name__)

class CacheManager:
    """Cache manager for storing and retrieving sentiment analysis data"""
    
    def __init__(self):
        """Initialize the cache manager"""
        self.redis_client = None
        self.initialize_redis()
        self.cache_ttl = CACHE_CONFIG.get("ttl", 3600)  # Default TTL: 1 hour
        logger.info("Initialized CacheManager")
    
    def initialize_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            
            # Get Redis configuration
            redis_config = CACHE_CONFIG["redis"]
            
            # Connect to Redis
            self.redis_client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"]
            )
            
            # Test connection
            self.redis_client.ping()
            
            logger.info("Redis connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Redis connection: {str(e)}")
            self.redis_client = None
    
    def generate_cache_key(self, text: str, model_name: str) -> str:
        """Generate a cache key for the given text and model
        
        Args:
            text: Text to analyze
            model_name: Name of the model
            
        Returns:
            Cache key
        """
        import hashlib
        
        # Generate hash of text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Generate cache key
        cache_key = f"sentiment:{model_name}:{text_hash}"
        
        return cache_key
    
    def get_cached_result(self, text: str, model_name: str) -> Optional[Dict[str, Any]]:
        """Get cached sentiment analysis result
        
        Args:
            text: Text to analyze
            model_name: Name of the model
            
        Returns:
            Cached sentiment analysis result or None if not found
        """
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return None
            
            # Generate cache key
            cache_key = self.generate_cache_key(text, model_name)
            
            # Get cached result
            cached_result = self.redis_client.get(cache_key)
            
            # Return None if not found
            if cached_result is None:
                return None
            
            # Parse JSON
            result = json.loads(cached_result)
            
            return result
        except Exception as e:
            logger.error(f"Error getting cached result: {str(e)}")
            return None
    
    def cache_result(self, text: str, model_name: str, result: Dict[str, Any]):
        """Cache sentiment analysis result
        
        Args:
            text: Text to analyze
            model_name: Name of the model
            result: Sentiment analysis result
        """
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return
            
            # Generate cache key
            cache_key = self.generate_cache_key(text, model_name)
            
            # Convert result to JSON
            result_json = json.dumps(result)
            
            # Cache result
            self.redis_client.setex(cache_key, self.cache_ttl, result_json)
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
    
    def get_batch_cached_results(self, texts: List[str], model_name: str) -> Dict[str, Dict[str, Any]]:
        """Get cached sentiment analysis results for a batch of texts
        
        Args:
            texts: List of texts to analyze
            model_name: Name of the model
            
        Returns:
            Dictionary mapping text to cached sentiment analysis result
        """
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return {}
            
            # Initialize results
            results = {}
            
            # Get cached results for each text
            for text in texts:
                result = self.get_cached_result(text, model_name)
                if result is not None:
                    results[text] = result
            
            return results
        except Exception as e:
            logger.error(f"Error getting batch cached results: {str(e)}")
            return {}
    
    def cache_batch_results(self, texts: List[str], model_name: str, results: List[Dict[str, Any]]):
        """Cache sentiment analysis results for a batch of texts
        
        Args:
            texts: List of texts to analyze
            model_name: Name of the model
            results: List of sentiment analysis results
        """
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return
            
            # Cache results for each text
            for text, result in zip(texts, results):
                self.cache_result(text, model_name, result)
        except Exception as e:
            logger.error(f"Error caching batch results: {str(e)}")
    
    def clear_cache(self):
        """Clear all cached results"""
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return
            
            # Clear all keys with the sentiment prefix
            for key in self.redis_client.scan_iter("sentiment:*"):
                self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return {"status": "disconnected"}
            
            # Get cache statistics
            stats = {
                "status": "connected",
                "total_keys": 0,
                "memory_used": 0,
                "hit_rate": 0.0
            }
            
            # Count sentiment keys
            stats["total_keys"] = len(list(self.redis_client.scan_iter("sentiment:*")))
            
            # Get memory usage
            info = self.redis_client.info("memory")
            stats["memory_used"] = info.get("used_memory_human", "N/A")
            
            # Get hit rate if available
            info = self.redis_client.info("stats")
            keyspace_hits = info.get("keyspace_hits", 0)
            keyspace_misses = info.get("keyspace_misses", 0)
            
            if keyspace_hits + keyspace_misses > 0:
                stats["hit_rate"] = keyspace_hits / (keyspace_hits + keyspace_misses)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def close(self):
        """Close Redis connection"""
        try:
            # Check if Redis client is available
            if self.redis_client is None:
                return
            
            # Close connection
            self.redis_client.close()
            
            logger.info("Redis connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the cache manager
        
        Returns:
            Dictionary with health status
        """
        status = {
            "status": "healthy",
            "redis": "connected"
        }
        
        # Check Redis connection
        if self.redis_client is None:
            status["redis"] = "not_initialized"
            status["status"] = "degraded"
        else:
            try:
                self.redis_client.ping()
                status["redis"] = "connected"
            except Exception:
                status["redis"] = "disconnected"
                status["status"] = "degraded"
        
        return status