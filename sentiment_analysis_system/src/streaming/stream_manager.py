import logging
import time
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Callable
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import KAFKA_CONFIG, SOCIAL_MEDIA_CONFIG

logger = logging.getLogger(__name__)

class StreamManager:
    """Manager for real-time data streams from various sources"""
    
    def __init__(self):
        """Initialize the stream manager"""
        self.active_streams = {}
        self.stream_results = {}
        self.stream_callbacks = {}
        logger.info("Initialized StreamManager")
    
    async def start_stream(self, source: str, query: str, duration: int = 60) -> str:
        """Start a new data stream
        
        Args:
            source: Data source (twitter, reddit, kafka, custom)
            query: Search query or filter
            duration: Stream duration in seconds (0 for indefinite)
            
        Returns:
            Stream ID
        """
        try:
            # Generate a unique stream ID
            stream_id = str(uuid.uuid4())
            
            # Initialize stream data
            self.active_streams[stream_id] = {
                "id": stream_id,
                "source": source,
                "query": query,
                "duration": duration,
                "start_time": datetime.now(),
                "status": "initializing",
                "data_count": 0,
                "error": None
            }
            
            self.stream_results[stream_id] = []
            
            # Start the appropriate stream based on source
            if source == "twitter":
                await self._start_twitter_stream(stream_id, query, duration)
            elif source == "reddit":
                await self._start_reddit_stream(stream_id, query, duration)
            elif source == "kafka":
                await self._start_kafka_stream(stream_id, query, duration)
            elif source == "custom":
                await self._start_custom_stream(stream_id, query, duration)
            else:
                raise ValueError(f"Unknown source: {source}")
            
            logger.info(f"Started {source} stream with ID: {stream_id}")
            return stream_id
        except Exception as e:
            logger.error(f"Error starting stream: {str(e)}")
            raise
    
    async def _start_twitter_stream(self, stream_id: str, query: str, duration: int):
        """Start a Twitter stream
        
        Args:
            stream_id: Stream ID
            query: Search query or filter
            duration: Stream duration in seconds
        """
        try:
            import tweepy
            
            # Get Twitter API credentials
            twitter_config = SOCIAL_MEDIA_CONFIG["twitter"]
            
            # Check if credentials are available
            if not all([twitter_config["api_key"], twitter_config["api_secret"],
                      twitter_config["access_token"], twitter_config["access_token_secret"]]):
                raise ValueError("Twitter API credentials not configured")
            
            # Initialize Twitter client
            auth = tweepy.OAuthHandler(twitter_config["api_key"], twitter_config["api_secret"])
            auth.set_access_token(twitter_config["access_token"], twitter_config["access_token_secret"])
            api = tweepy.API(auth)
            
            # Define stream listener
            class TweetListener(tweepy.StreamingClient):
                def __init__(self, bearer_token, stream_manager, stream_id):
                    super().__init__(bearer_token)
                    self.stream_manager = stream_manager
                    self.stream_id = stream_id
                    self.start_time = time.time()
                    self.duration = duration
                
                def on_tweet(self, tweet):
                    # Check if duration has elapsed
                    if self.duration > 0 and time.time() - self.start_time > self.duration:
                        self.disconnect()
                        return
                    
                    # Process tweet
                    self.stream_manager._process_stream_data(self.stream_id, tweet.text)
                
                def on_error(self, status):
                    self.stream_manager.active_streams[self.stream_id]["error"] = f"Twitter API error: {status}"
                    self.disconnect()
            
            # Create and start stream
            stream = TweetListener(twitter_config["bearer_token"], self, stream_id)
            
            # Add rules based on query
            stream.add_rules(tweepy.StreamRule(query))
            
            # Start stream in a separate task
            asyncio.create_task(self._run_twitter_stream(stream, stream_id, duration))
            
            # Update stream status
            self.active_streams[stream_id]["status"] = "running"
        except Exception as e:
            logger.error(f"Error starting Twitter stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _run_twitter_stream(self, stream, stream_id: str, duration: int):
        """Run Twitter stream in background
        
        Args:
            stream: Twitter stream object
            stream_id: Stream ID
            duration: Stream duration in seconds
        """
        try:
            # Start filtering
            stream.filter(tweet_fields=["created_at", "text"])
            
            # If duration is set, stop after duration
            if duration > 0:
                await asyncio.sleep(duration)
                stream.disconnect()
            
            # Update stream status when done
            self.active_streams[stream_id]["status"] = "completed"
        except Exception as e:
            logger.error(f"Error in Twitter stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _start_reddit_stream(self, stream_id: str, query: str, duration: int):
        """Start a Reddit stream
        
        Args:
            stream_id: Stream ID
            query: Search query or filter
            duration: Stream duration in seconds
        """
        try:
            import praw
            
            # Get Reddit API credentials
            reddit_config = SOCIAL_MEDIA_CONFIG["reddit"]
            
            # Check if credentials are available
            if not all([reddit_config["client_id"], reddit_config["client_secret"], reddit_config["user_agent"]]):
                raise ValueError("Reddit API credentials not configured")
            
            # Initialize Reddit client
            reddit = praw.Reddit(
                client_id=reddit_config["client_id"],
                client_secret=reddit_config["client_secret"],
                user_agent=reddit_config["user_agent"]
            )
            
            # Start stream in a separate task
            asyncio.create_task(self._run_reddit_stream(reddit, stream_id, query, duration))
            
            # Update stream status
            self.active_streams[stream_id]["status"] = "running"
        except Exception as e:
            logger.error(f"Error starting Reddit stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _run_reddit_stream(self, reddit, stream_id: str, query: str, duration: int):
        """Run Reddit stream in background
        
        Args:
            reddit: Reddit client
            stream_id: Stream ID
            query: Search query or filter
            duration: Stream duration in seconds
        """
        try:
            start_time = time.time()
            
            # Determine if query is a subreddit or search query
            if query.startswith("r/"):
                # Stream from subreddit
                subreddit_name = query[2:]
                subreddit = reddit.subreddit(subreddit_name)
                
                # Stream comments
                for comment in subreddit.stream.comments():
                    # Check if duration has elapsed
                    if duration > 0 and time.time() - start_time > duration:
                        break
                    
                    # Process comment
                    await self._process_stream_data(stream_id, comment.body)
                    
                    # Yield control to allow other tasks to run
                    await asyncio.sleep(0)
            else:
                # Search for submissions
                while True:
                    # Check if duration has elapsed
                    if duration > 0 and time.time() - start_time > duration:
                        break
                    
                    # Search for submissions
                    for submission in reddit.subreddit("all").search(query, sort="new", limit=10):
                        # Process submission title and text
                        await self._process_stream_data(stream_id, submission.title)
                        if submission.selftext:
                            await self._process_stream_data(stream_id, submission.selftext)
                    
                    # Wait before next search
                    await asyncio.sleep(5)
            
            # Update stream status when done
            self.active_streams[stream_id]["status"] = "completed"
        except Exception as e:
            logger.error(f"Error in Reddit stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _start_kafka_stream(self, stream_id: str, query: str, duration: int):
        """Start a Kafka stream
        
        Args:
            stream_id: Stream ID
            query: Topic name or filter
            duration: Stream duration in seconds
        """
        try:
            from kafka import KafkaConsumer
            import json
            
            # Get Kafka configuration
            kafka_config = KAFKA_CONFIG
            
            # Start stream in a separate task
            asyncio.create_task(self._run_kafka_stream(kafka_config, stream_id, query, duration))
            
            # Update stream status
            self.active_streams[stream_id]["status"] = "running"
        except Exception as e:
            logger.error(f"Error starting Kafka stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _run_kafka_stream(self, kafka_config, stream_id: str, topic: str, duration: int):
        """Run Kafka stream in background
        
        Args:
            kafka_config: Kafka configuration
            stream_id: Stream ID
            topic: Kafka topic
            duration: Stream duration in seconds
        """
        try:
            from kafka import KafkaConsumer
            import json
            
            # Create Kafka consumer
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=kafka_config["bootstrap_servers"],
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            start_time = time.time()
            
            # Process messages
            for message in consumer:
                # Check if duration has elapsed
                if duration > 0 and time.time() - start_time > duration:
                    break
                
                # Extract text from message
                text = message.value.get("text", "")
                if text:
                    await self._process_stream_data(stream_id, text)
                
                # Yield control to allow other tasks to run
                await asyncio.sleep(0)
            
            # Close consumer
            consumer.close()
            
            # Update stream status when done
            self.active_streams[stream_id]["status"] = "completed"
        except Exception as e:
            logger.error(f"Error in Kafka stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _start_custom_stream(self, stream_id: str, query: str, duration: int):
        """Start a custom stream (placeholder)
        
        Args:
            stream_id: Stream ID
            query: Custom query or configuration
            duration: Stream duration in seconds
        """
        try:
            # This is a placeholder for a custom stream implementation
            # In a real implementation, this would connect to a custom data source
            
            # Start stream in a separate task
            asyncio.create_task(self._run_custom_stream(stream_id, query, duration))
            
            # Update stream status
            self.active_streams[stream_id]["status"] = "running"
        except Exception as e:
            logger.error(f"Error starting custom stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _run_custom_stream(self, stream_id: str, query: str, duration: int):
        """Run custom stream in background
        
        Args:
            stream_id: Stream ID
            query: Custom query or configuration
            duration: Stream duration in seconds
        """
        try:
            # This is a placeholder for a custom stream implementation
            # In a real implementation, this would process data from a custom source
            
            start_time = time.time()
            
            # Simulate receiving data
            while True:
                # Check if duration has elapsed
                if duration > 0 and time.time() - start_time > duration:
                    break
                
                # Simulate receiving data every second
                await asyncio.sleep(1)
                
                # Generate some sample data
                sample_text = f"Sample data for query '{query}' at {datetime.now()}"
                await self._process_stream_data(stream_id, sample_text)
            
            # Update stream status when done
            self.active_streams[stream_id]["status"] = "completed"
        except Exception as e:
            logger.error(f"Error in custom stream: {str(e)}")
            self.active_streams[stream_id]["status"] = "error"
            self.active_streams[stream_id]["error"] = str(e)
    
    async def _process_stream_data(self, stream_id: str, text: str):
        """Process data from a stream
        
        Args:
            stream_id: Stream ID
            text: Text data to process
        """
        try:
            # Store the raw text
            self.stream_results[stream_id].append({
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "processed": False,
                "sentiment": None,
                "emotions": None
            })
            
            # Update data count
            self.active_streams[stream_id]["data_count"] += 1
            
            # Call any registered callbacks
            if stream_id in self.stream_callbacks:
                for callback in self.stream_callbacks[stream_id]:
                    await callback(stream_id, text)
        except Exception as e:
            logger.error(f"Error processing stream data: {str(e)}")
    
    async def process_stream(self, stream_id: str, sentiment_analyzer, text_processor):
        """Process all data in a stream with sentiment analysis
        
        Args:
            stream_id: Stream ID
            sentiment_analyzer: Sentiment analyzer instance
            text_processor: Text processor instance
        """
        try:
            # Check if stream exists
            if stream_id not in self.active_streams:
                raise ValueError(f"Stream {stream_id} not found")
            
            # Process all unprocessed data
            for i, item in enumerate(self.stream_results[stream_id]):
                if not item["processed"]:
                    # Process text
                    processed_text = text_processor.process(item["text"])
                    
                    # Analyze sentiment
                    sentiment_result = sentiment_analyzer.analyze(processed_text)
                    
                    # Update item with results
                    self.stream_results[stream_id][i]["processed"] = True
                    self.stream_results[stream_id][i]["processed_text"] = processed_text
                    self.stream_results[stream_id][i]["sentiment"] = sentiment_result
                    
                    # Yield control to allow other tasks to run
                    await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"Error processing stream: {str(e)}")
    
    def register_callback(self, stream_id: str, callback: Callable):
        """Register a callback for stream data
        
        Args:
            stream_id: Stream ID
            callback: Callback function to call when new data arrives
        """
        if stream_id not in self.stream_callbacks:
            self.stream_callbacks[stream_id] = []
        
        self.stream_callbacks[stream_id].append(callback)
    
    def get_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """Get the status of a stream
        
        Args:
            stream_id: Stream ID
            
        Returns:
            Dictionary with stream status
        """
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        return self.active_streams[stream_id]
    
    def get_stream_results(self, stream_id: str, limit: int = 100, processed_only: bool = False) -> List[Dict[str, Any]]:
        """Get the results of a stream
        
        Args:
            stream_id: Stream ID
            limit: Maximum number of results to return
            processed_only: Whether to return only processed results
            
        Returns:
            List of stream results
        """
        if stream_id not in self.stream_results:
            raise ValueError(f"Stream {stream_id} not found")
        
        results = self.stream_results[stream_id]
        
        if processed_only:
            results = [item for item in results if item["processed"]]
        
        return results[-limit:]
    
    def stop_stream(self, stream_id: str):
        """Stop a stream
        
        Args:
            stream_id: Stream ID
        """
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        # Update stream status
        self.active_streams[stream_id]["status"] = "stopped"
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the stream manager
        
        Returns:
            Dictionary with health status
        """
        return {
            "status": "healthy",
            "active_streams": len(self.active_streams),
            "stream_ids": list(self.active_streams.keys())
        }