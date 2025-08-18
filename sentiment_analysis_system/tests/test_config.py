import unittest
import sys
import os
from unittest.mock import patch, mock_open
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from config import settings

class TestConfig(unittest.TestCase):
    """Tests for the configuration module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Sample configuration data
        self.sample_config = {
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True,
                "workers": 4,
                "timeout": 60
            },
            "web": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": True,
                "workers": 2,
                "timeout": 60
            },
            "models": {
                "sentiment": {
                    "default_model": "ensemble",
                    "vader": {"enabled": True},
                    "textblob": {"enabled": True},
                    "bert": {"enabled": True, "model_path": "models/bert-base-uncased"},
                    "custom": {"enabled": False},
                    "ensemble": {"enabled": True, "weights": {"vader": 0.3, "textblob": 0.2, "bert": 0.5}}
                },
                "emotion": {
                    "default_model": "ensemble",
                    "transformer": {"enabled": True, "model_path": "models/emotion-english-distilroberta-base"},
                    "rule_based": {"enabled": True},
                    "custom": {"enabled": False},
                    "ensemble": {"enabled": True, "weights": {"transformer": 0.7, "rule_based": 0.3}}
                }
            },
            "processors": {
                "text": {
                    "remove_urls": True,
                    "remove_html_tags": True,
                    "remove_mentions": True,
                    "remove_hashtags": False,
                    "remove_punctuation": True,
                    "remove_extra_whitespace": True,
                    "remove_stopwords": True,
                    "lemmatize": True,
                    "lowercase": True
                }
            },
            "streaming": {
                "twitter": {
                    "enabled": True,
                    "api_key": "${TWITTER_API_KEY}",
                    "api_secret": "${TWITTER_API_SECRET}",
                    "access_token": "${TWITTER_ACCESS_TOKEN}",
                    "access_token_secret": "${TWITTER_ACCESS_TOKEN_SECRET}",
                    "max_tweets": 1000,
                    "batch_size": 100
                },
                "reddit": {
                    "enabled": True,
                    "client_id": "${REDDIT_CLIENT_ID}",
                    "client_secret": "${REDDIT_CLIENT_SECRET}",
                    "user_agent": "SentimentAnalysisSystem/1.0",
                    "max_posts": 500,
                    "batch_size": 50
                },
                "kafka": {
                    "enabled": True,
                    "bootstrap_servers": "localhost:9092",
                    "topic": "sentiment-data",
                    "group_id": "sentiment-analysis-group",
                    "batch_size": 100
                }
            },
            "database": {
                "postgres": {
                    "enabled": True,
                    "host": "${POSTGRES_HOST:localhost}",
                    "port": "${POSTGRES_PORT:5432}",
                    "user": "${POSTGRES_USER:postgres}",
                    "password": "${POSTGRES_PASSWORD}",
                    "database": "${POSTGRES_DB:sentiment_analysis}",
                    "pool_size": 10
                },
                "mongodb": {
                    "enabled": True,
                    "uri": "${MONGODB_URI:mongodb://localhost:27017}",
                    "database": "${MONGODB_DB:sentiment_analysis}",
                    "collection_prefix": "sentiment_"
                }
            },
            "cache": {
                "redis": {
                    "enabled": True,
                    "host": "${REDIS_HOST:localhost}",
                    "port": "${REDIS_PORT:6379}",
                    "db": 0,
                    "ttl": 3600
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "console": True,
                "file": {
                    "enabled": True,
                    "path": "logs/sentiment_analysis.log",
                    "max_size": 10485760,  # 10MB
                    "backup_count": 5
                }
            }
        }
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_from_file(self, mock_file, mock_exists):
        """Test loading configuration from a file"""
        # Setup mocks
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.sample_config)
        
        # Test loading config
        with patch.object(settings, '_load_config_from_file') as mock_load:
            mock_load.return_value = self.sample_config
            config = settings._load_config_from_file('config/config.json')
            
            # Verify config loaded correctly
            self.assertEqual(config, self.sample_config)
            self.assertEqual(config['api']['port'], 8000)
            self.assertEqual(config['models']['sentiment']['default_model'], 'ensemble')
            self.assertTrue(config['processors']['text']['remove_urls'])
    
    @patch('os.environ')
    def test_resolve_environment_variables(self, mock_environ):
        """Test resolving environment variables in config"""
        # Setup environment variables
        mock_environ.get.side_effect = lambda key, default=None: {
            'TWITTER_API_KEY': 'test_api_key',
            'TWITTER_API_SECRET': 'test_api_secret',
            'POSTGRES_PASSWORD': 'test_password',
            'MONGODB_URI': 'mongodb://testhost:27017'
        }.get(key, default)
        
        # Test config with environment variables
        config_with_env_vars = {
            'streaming': {
                'twitter': {
                    'api_key': '${TWITTER_API_KEY}',
                    'api_secret': '${TWITTER_API_SECRET}'
                }
            },
            'database': {
                'postgres': {
                    'password': '${POSTGRES_PASSWORD}',
                    'host': '${POSTGRES_HOST:localhost}'
                },
                'mongodb': {
                    'uri': '${MONGODB_URI:mongodb://localhost:27017}'
                }
            }
        }
        
        # Resolve environment variables directly without mocking
        resolved_config = settings._resolve_environment_variables(config_with_env_vars)
        
        # Verify environment variables were resolved
        self.assertEqual(resolved_config['streaming']['twitter']['api_key'], 'test_api_key')
        self.assertEqual(resolved_config['streaming']['twitter']['api_secret'], 'test_api_secret')
        self.assertEqual(resolved_config['database']['postgres']['password'], 'test_password')
        self.assertEqual(resolved_config['database']['postgres']['host'], 'localhost')  # Default value
        self.assertEqual(resolved_config['database']['mongodb']['uri'], 'mongodb://testhost:27017')
    
    def test_get_config(self):
        """Test getting configuration"""
        # Test getting config
        config = settings.get_config()
        
        # Verify config contains all required keys
        for key in self.sample_config:
            self.assertIn(key, config)
        
        # Verify API config
        self.assertEqual(config['api']['host'], self.sample_config['api']['host'])
        self.assertEqual(config['api']['port'], self.sample_config['api']['port'])
        self.assertEqual(config['api']['debug'], self.sample_config['api']['debug'])
    
    @patch.object(settings, 'get_config')
    def test_get_api_config(self, mock_get_config):
        """Test getting API configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting API config
        api_config = settings.get_api_config()
        
        # Verify API config
        self.assertEqual(api_config, self.sample_config['api'])
        self.assertEqual(api_config['host'], '0.0.0.0')
        self.assertEqual(api_config['port'], 8000)
    
    @patch.object(settings, 'get_config')
    def test_get_web_config(self, mock_get_config):
        """Test getting Web configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting Web config
        web_config = settings.get_web_config()
        
        # Verify Web config
        self.assertEqual(web_config, self.sample_config['web'])
        self.assertEqual(web_config['host'], '0.0.0.0')
        self.assertEqual(web_config['port'], 8080)
    
    @patch.object(settings, 'get_config')
    def test_get_model_config(self, mock_get_config):
        """Test getting model configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting model config
        model_config = settings.get_model_config()
        
        # Verify model config
        self.assertEqual(model_config, self.sample_config['models'])
        self.assertEqual(model_config['sentiment']['default_model'], 'ensemble')
        self.assertTrue(model_config['sentiment']['vader']['enabled'])
    
    @patch.object(settings, 'get_config')
    def test_get_processor_config(self, mock_get_config):
        """Test getting processor configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting processor config
        processor_config = settings.get_processor_config()
        
        # Verify processor config
        self.assertEqual(processor_config, self.sample_config['processors'])
        self.assertTrue(processor_config['text']['remove_urls'])
        self.assertFalse(processor_config['text']['remove_hashtags'])
    
    @patch.object(settings, 'get_config')
    def test_get_streaming_config(self, mock_get_config):
        """Test getting streaming configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting streaming config
        streaming_config = settings.get_streaming_config()
        
        # Verify streaming config
        self.assertEqual(streaming_config, self.sample_config['streaming'])
        self.assertTrue(streaming_config['twitter']['enabled'])
        self.assertEqual(streaming_config['kafka']['bootstrap_servers'], 'localhost:9092')
    
    @patch.object(settings, 'get_config')
    def test_get_database_config(self, mock_get_config):
        """Test getting database configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting database config
        database_config = settings.get_database_config()
        
        # Verify database config
        self.assertEqual(database_config, self.sample_config['database'])
        self.assertTrue(database_config['postgres']['enabled'])
        self.assertTrue(database_config['mongodb']['enabled'])
    
    @patch.object(settings, 'get_config')
    def test_get_cache_config(self, mock_get_config):
        """Test getting cache configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting cache config
        cache_config = settings.get_cache_config()
        
        # Verify cache config
        self.assertEqual(cache_config, self.sample_config['cache'])
        self.assertTrue(cache_config['redis']['enabled'])
        self.assertEqual(cache_config['redis']['ttl'], 3600)
    
    @patch.object(settings, 'get_config')
    def test_get_logging_config(self, mock_get_config):
        """Test getting logging configuration"""
        # Setup mock
        mock_get_config.return_value = self.sample_config
        
        # Test getting logging config
        logging_config = settings.get_logging_config()
        
        # Verify logging config
        self.assertEqual(logging_config, self.sample_config['logging'])
        self.assertEqual(logging_config['level'], 'INFO')
        self.assertTrue(logging_config['file']['enabled'])

if __name__ == '__main__':
    unittest.main()