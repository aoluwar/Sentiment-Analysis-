import logging
import time
from typing import Dict, Any, List, Optional
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for storing and retrieving sentiment analysis data"""
    
    def __init__(self):
        """Initialize the database manager"""
        self.connections = {}
        self.initialize_connections()
        logger.info("Initialized DatabaseManager")
    
    def initialize_connections(self):
        """Initialize database connections"""
        try:
            # Initialize PostgreSQL connection
            self._initialize_postgres()
            
            # Initialize MongoDB connection
            self._initialize_mongodb()
            
            # Initialize Redis connection
            self._initialize_redis()
            
            logger.info("All database connections initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database connections: {str(e)}")
    
    def _initialize_postgres(self):
        """Initialize PostgreSQL connection"""
        try:
            import psycopg2
            from psycopg2.extras import Json
            
            # Get PostgreSQL configuration
            postgres_config = DATABASE_CONFIG["postgres"]
            
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=postgres_config["host"],
                port=postgres_config["port"],
                user=postgres_config["user"],
                password=postgres_config["password"],
                database=postgres_config["database"]
            )
            
            # Create cursor
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sentiment_analysis (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    processed_text TEXT,
                    sentiment VARCHAR(20) NOT NULL,
                    confidence FLOAT NOT NULL,
                    language VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotion_analysis (
                    id SERIAL PRIMARY KEY,
                    sentiment_id INTEGER REFERENCES sentiment_analysis(id),
                    emotion VARCHAR(20) NOT NULL,
                    score FLOAT NOT NULL
                )
            """)
            
            # Commit changes
            conn.commit()
            
            # Store connection and cursor
            self.connections["postgres"] = {
                "conn": conn,
                "cursor": cursor
            }
            
            logger.info("PostgreSQL connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL connection: {str(e)}")
            self.connections["postgres"] = None
    
    def _initialize_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            import pymongo
            
            # Get MongoDB configuration
            mongodb_config = DATABASE_CONFIG["mongodb"]
            
            # Connect to MongoDB
            client = pymongo.MongoClient(
                host=mongodb_config["host"],
                port=mongodb_config["port"],
                username=mongodb_config["user"],
                password=mongodb_config["password"]
            )
            
            # Get database
            db = client[mongodb_config["database"]]
            
            # Create collections
            sentiment_collection = db["sentiment_analysis"]
            stream_collection = db["stream_data"]
            
            # Create indexes
            sentiment_collection.create_index("created_at")
            sentiment_collection.create_index("sentiment")
            stream_collection.create_index("stream_id")
            
            # Store connection and collections
            self.connections["mongodb"] = {
                "client": client,
                "db": db,
                "sentiment_collection": sentiment_collection,
                "stream_collection": stream_collection
            }
            
            logger.info("MongoDB connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MongoDB connection: {str(e)}")
            self.connections["mongodb"] = None
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            
            # Get Redis configuration
            redis_config = DATABASE_CONFIG["redis"]
            
            # Connect to Redis
            client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"]
            )
            
            # Test connection
            client.ping()
            
            # Store connection
            self.connections["redis"] = {
                "client": client
            }
            
            logger.info("Redis connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Redis connection: {str(e)}")
            self.connections["redis"] = None
    
    def store_analysis(self, analysis_result):
        """Store sentiment analysis result
        
        Args:
            analysis_result: Sentiment analysis result to store
        """
        try:
            # Store in PostgreSQL
            self._store_in_postgres(analysis_result)
            
            # Store in MongoDB
            self._store_in_mongodb(analysis_result)
        except Exception as e:
            logger.error(f"Error storing analysis result: {str(e)}")
    
    def _store_in_postgres(self, analysis_result):
        """Store sentiment analysis result in PostgreSQL
        
        Args:
            analysis_result: Sentiment analysis result to store
        """
        try:
            # Check if PostgreSQL connection is available
            if self.connections["postgres"] is None:
                return
            
            # Get connection and cursor
            conn = self.connections["postgres"]["conn"]
            cursor = self.connections["postgres"]["cursor"]
            
            # Insert sentiment analysis result
            cursor.execute("""
                INSERT INTO sentiment_analysis (text, processed_text, sentiment, confidence, language)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                analysis_result.text,
                analysis_result.processed_text,
                analysis_result.sentiment,
                analysis_result.confidence,
                analysis_result.language
            ))
            
            # Get the inserted ID
            sentiment_id = cursor.fetchone()[0]
            
            # Insert emotion analysis results
            if analysis_result.emotions:
                for emotion, score in analysis_result.emotions.items():
                    cursor.execute("""
                        INSERT INTO emotion_analysis (sentiment_id, emotion, score)
                        VALUES (%s, %s, %s)
                    """, (
                        sentiment_id,
                        emotion,
                        score
                    ))
            
            # Commit changes
            conn.commit()
        except Exception as e:
            logger.error(f"Error storing in PostgreSQL: {str(e)}")
    
    def _store_in_mongodb(self, analysis_result):
        """Store sentiment analysis result in MongoDB
        
        Args:
            analysis_result: Sentiment analysis result to store
        """
        try:
            # Check if MongoDB connection is available
            if self.connections["mongodb"] is None:
                return
            
            # Get collection
            collection = self.connections["mongodb"]["sentiment_collection"]
            
            # Convert to dictionary
            result_dict = {
                "text": analysis_result.text,
                "processed_text": analysis_result.processed_text,
                "sentiment": analysis_result.sentiment,
                "confidence": analysis_result.confidence,
                "language": analysis_result.language,
                "emotions": analysis_result.emotions,
                "created_at": datetime.now()
            }
            
            # Insert document
            collection.insert_one(result_dict)
        except Exception as e:
            logger.error(f"Error storing in MongoDB: {str(e)}")
    
    def store_batch_analysis(self, analysis_results):
        """Store batch of sentiment analysis results
        
        Args:
            analysis_results: List of sentiment analysis results to store
        """
        try:
            # Store each result
            for result in analysis_results:
                self.store_analysis(result)
        except Exception as e:
            logger.error(f"Error storing batch analysis results: {str(e)}")
    
    def store_stream_data(self, stream_id: str, stream_data):
        """Store stream data
        
        Args:
            stream_id: Stream ID
            stream_data: Stream data to store
        """
        try:
            # Check if MongoDB connection is available
            if self.connections["mongodb"] is None:
                return
            
            # Get collection
            collection = self.connections["mongodb"]["stream_collection"]
            
            # Convert to dictionary
            data_dict = {
                "stream_id": stream_id,
                "data": stream_data,
                "created_at": datetime.now()
            }
            
            # Insert document
            collection.insert_one(data_dict)
        except Exception as e:
            logger.error(f"Error storing stream data: {str(e)}")
    
    def get_recent_analyses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent sentiment analysis results
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of sentiment analysis results
        """
        try:
            # Check if MongoDB connection is available
            if self.connections["mongodb"] is None:
                return []
            
            # Get collection
            collection = self.connections["mongodb"]["sentiment_collection"]
            
            # Query recent results
            results = list(collection.find().sort("created_at", -1).limit(limit))
            
            # Convert ObjectId to string
            for result in results:
                result["_id"] = str(result["_id"])
            
            return results
        except Exception as e:
            logger.error(f"Error getting recent analyses: {str(e)}")
            return []
    
    def get_sentiment_distribution(self) -> Dict[str, int]:
        """Get distribution of sentiment analysis results
        
        Returns:
            Dictionary mapping sentiment to count
        """
        try:
            # Check if MongoDB connection is available
            if self.connections["mongodb"] is None:
                return {}
            
            # Get collection
            collection = self.connections["mongodb"]["sentiment_collection"]
            
            # Aggregate results
            pipeline = [
                {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
            ]
            results = list(collection.aggregate(pipeline))
            
            # Convert to dictionary
            distribution = {result["_id"]: result["count"] for result in results}
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting sentiment distribution: {str(e)}")
            return {}
    
    def get_emotion_distribution(self) -> Dict[str, float]:
        """Get distribution of emotion analysis results
        
        Returns:
            Dictionary mapping emotion to average score
        """
        try:
            # Check if MongoDB connection is available
            if self.connections["mongodb"] is None:
                return {}
            
            # Get collection
            collection = self.connections["mongodb"]["sentiment_collection"]
            
            # Aggregate results
            pipeline = [
                {"$unwind": "$emotions"},
                {"$group": {"_id": "$emotions.name", "avg_score": {"$avg": "$emotions.score"}}}
            ]
            results = list(collection.aggregate(pipeline))
            
            # Convert to dictionary
            distribution = {result["_id"]: result["avg_score"] for result in results}
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting emotion distribution: {str(e)}")
            return {}
    
    def close_connections(self):
        """Close all database connections"""
        try:
            # Close PostgreSQL connection
            if self.connections["postgres"] is not None:
                self.connections["postgres"]["conn"].close()
            
            # Close MongoDB connection
            if self.connections["mongodb"] is not None:
                self.connections["mongodb"]["client"].close()
            
            # Close Redis connection
            if self.connections["redis"] is not None:
                self.connections["redis"]["client"].close()
            
            logger.info("All database connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the database manager
        
        Returns:
            Dictionary with health status
        """
        status = {
            "status": "healthy",
            "connections": {}
        }
        
        # Check PostgreSQL connection
        if self.connections["postgres"] is not None:
            try:
                cursor = self.connections["postgres"]["cursor"]
                cursor.execute("SELECT 1")
                status["connections"]["postgres"] = "connected"
            except Exception:
                status["connections"]["postgres"] = "disconnected"
                status["status"] = "degraded"
        else:
            status["connections"]["postgres"] = "not_initialized"
            status["status"] = "degraded"
        
        # Check MongoDB connection
        if self.connections["mongodb"] is not None:
            try:
                client = self.connections["mongodb"]["client"]
                client.admin.command("ping")
                status["connections"]["mongodb"] = "connected"
            except Exception:
                status["connections"]["mongodb"] = "disconnected"
                status["status"] = "degraded"
        else:
            status["connections"]["mongodb"] = "not_initialized"
            status["status"] = "degraded"
        
        # Check Redis connection
        if self.connections["redis"] is not None:
            try:
                client = self.connections["redis"]["client"]
                client.ping()
                status["connections"]["redis"] = "connected"
            except Exception:
                status["connections"]["redis"] = "disconnected"
                status["status"] = "degraded"
        else:
            status["connections"]["redis"] = "not_initialized"
            status["status"] = "degraded"
        
        return status