import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.utils.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config_patcher = patch('src.utils.db_manager.DB_CONFIG', {
            'postgres': {
                'enabled': True,
                'host': 'localhost',
                'port': 5432,
                'database': 'sentiment_db',
                'user': 'postgres',
                'password': 'postgres'
            },
            'mongodb': {
                'enabled': True,
                'host': 'localhost',
                'port': 27017,
                'database': 'sentiment_db'
            },
            'redis': {
                'enabled': True,
                'host': 'localhost',
                'port': 6379,
                'db': 0
            }
        })
        self.config_patcher.start()
        
        # Mock the database connections
        self.pg_conn_patcher = patch('src.utils.db_manager.psycopg2.connect')
        self.mongo_client_patcher = patch('src.utils.db_manager.MongoClient')
        self.redis_client_patcher = patch('src.utils.db_manager.Redis')
        
        self.mock_pg_conn = self.pg_conn_patcher.start()
        self.mock_mongo_client = self.mongo_client_patcher.start()
        self.mock_redis_client = self.redis_client_patcher.start()
        
        # Set up mock cursor
        self.mock_cursor = MagicMock()
        self.mock_pg_conn.return_value.cursor.return_value = self.mock_cursor
        
        # Set up mock MongoDB database and collections
        self.mock_mongo_db = MagicMock()
        self.mock_mongo_client.return_value.__getitem__.return_value = self.mock_mongo_db
        self.mock_sentiment_collection = MagicMock()
        self.mock_emotion_collection = MagicMock()
        self.mock_stream_collection = MagicMock()
        self.mock_mongo_db.__getitem__.side_effect = lambda x: {
            'sentiment_analysis': self.mock_sentiment_collection,
            'emotion_analysis': self.mock_emotion_collection,
            'stream_data': self.mock_stream_collection
        }[x]
        
        # Create database manager
        self.db_manager = DatabaseManager()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.config_patcher.stop()
        self.pg_conn_patcher.stop()
        self.mongo_client_patcher.stop()
        self.redis_client_patcher.stop()
    
    def test_init_connections(self):
        """Test initializing database connections"""
        # Check connections were initialized
        self.mock_pg_conn.assert_called_once()
        self.mock_mongo_client.assert_called_once()
        self.mock_redis_client.assert_called_once()
    
    def test_store_sentiment_analysis_postgres(self):
        """Test storing sentiment analysis in PostgreSQL"""
        # Store analysis
        analysis = {
            'text': 'This is a test',
            'sentiment': 'positive',
            'confidence': 0.85,
            'model': 'vader'
        }
        self.db_manager.store_sentiment_analysis(analysis)
        
        # Check SQL was executed
        self.mock_cursor.execute.assert_called_once()
        self.mock_pg_conn.return_value.commit.assert_called_once()
    
    def test_store_sentiment_analysis_mongodb(self):
        """Test storing sentiment analysis in MongoDB"""
        # Store analysis
        analysis = {
            'text': 'This is a test',
            'sentiment': 'positive',
            'confidence': 0.85,
            'model': 'vader'
        }
        self.db_manager.store_sentiment_analysis(analysis)
        
        # Check MongoDB insert was called
        self.mock_sentiment_collection.insert_one.assert_called_once()
    
    def test_store_emotion_analysis(self):
        """Test storing emotion analysis"""
        # Store analysis
        analysis = {
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
        self.db_manager.store_emotion_analysis(analysis)
        
        # Check MongoDB insert was called
        self.mock_emotion_collection.insert_one.assert_called_once()
    
    def test_store_batch_sentiment_analysis(self):
        """Test storing batch sentiment analysis"""
        # Store batch analysis
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
        self.db_manager.store_batch_sentiment_analysis(analyses)
        
        # Check MongoDB insert_many was called
        self.mock_sentiment_collection.insert_many.assert_called_once()
        
        # Check executemany was called for PostgreSQL
        self.mock_cursor.executemany.assert_called_once()
        self.mock_pg_conn.return_value.commit.assert_called_once()
    
    def test_store_batch_emotion_analysis(self):
        """Test storing batch emotion analysis"""
        # Store batch analysis
        analyses = [
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
        self.db_manager.store_batch_emotion_analysis(analyses)
        
        # Check MongoDB insert_many was called
        self.mock_emotion_collection.insert_many.assert_called_once()
    
    def test_store_stream_data(self):
        """Test storing stream data"""
        # Store stream data
        stream_id = 'test_stream_123'
        data = {
            'text': 'This is a test',
            'sentiment': 'positive',
            'confidence': 0.85,
            'source': 'twitter'
        }
        self.db_manager.store_stream_data(stream_id, data)
        
        # Check MongoDB insert was called
        self.mock_stream_collection.insert_one.assert_called_once()
    
    def test_get_recent_analyses(self):
        """Test getting recent analyses"""
        # Mock MongoDB find
        self.mock_sentiment_collection.find.return_value.sort.return_value.limit.return_value = [
            {
                'text': 'This is a test',
                'sentiment': 'positive',
                'confidence': 0.85,
                'model': 'vader',
                'timestamp': '2023-01-01T12:00:00'
            },
            {
                'text': 'This is another test',
                'sentiment': 'negative',
                'confidence': 0.75,
                'model': 'vader',
                'timestamp': '2023-01-01T12:01:00'
            }
        ]
        
        # Get recent analyses
        results = self.db_manager.get_recent_analyses(limit=2)
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['sentiment'], 'positive')
        self.assertEqual(results[1]['sentiment'], 'negative')
        
        # Check MongoDB find was called
        self.mock_sentiment_collection.find.assert_called_once()
    
    def test_get_sentiment_distribution(self):
        """Test getting sentiment distribution"""
        # Mock MongoDB aggregate
        self.mock_sentiment_collection.aggregate.return_value = [
            {'_id': 'positive', 'count': 10},
            {'_id': 'negative', 'count': 5},
            {'_id': 'neutral', 'count': 3}
        ]
        
        # Get distribution
        distribution = self.db_manager.get_sentiment_distribution()
        
        # Check results
        self.assertEqual(distribution['positive'], 10)
        self.assertEqual(distribution['negative'], 5)
        self.assertEqual(distribution['neutral'], 3)
        
        # Check MongoDB aggregate was called
        self.mock_sentiment_collection.aggregate.assert_called_once()
    
    def test_get_emotion_distribution(self):
        """Test getting emotion distribution"""
        # Mock MongoDB aggregate
        self.mock_emotion_collection.aggregate.return_value = [
            {'_id': 'joy', 'average': 0.6},
            {'_id': 'sadness', 'average': 0.2},
            {'_id': 'anger', 'average': 0.1},
            {'_id': 'fear', 'average': 0.05},
            {'_id': 'surprise', 'average': 0.05}
        ]
        
        # Get distribution
        distribution = self.db_manager.get_emotion_distribution()
        
        # Check results
        self.assertEqual(distribution['joy'], 0.6)
        self.assertEqual(distribution['sadness'], 0.2)
        self.assertEqual(distribution['anger'], 0.1)
        
        # Check MongoDB aggregate was called
        self.mock_emotion_collection.aggregate.assert_called_once()
    
    def test_health_check(self):
        """Test health check"""
        # Run health check
        health = self.db_manager.health_check()
        
        # Check result
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('postgres', health)
        self.assertIn('mongodb', health)
        self.assertIn('redis', health)

if __name__ == '__main__':
    unittest.main()