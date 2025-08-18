import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.core.sentiment_analyzer import SentimentAnalyzer
from src.core.emotion_detector import EmotionDetector
from src.processors.text_processor import TextProcessor
from src.streaming.stream_manager import StreamManager
from src.utils.db_manager import DatabaseManager
from src.utils.cache_manager import CacheManager

class TestIntegration(unittest.TestCase):
    """Integration tests for Sentiment Analysis System"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock configurations
        self.config_patchers = [
            patch('src.core.sentiment_analyzer.MODEL_CONFIG'),
            patch('src.core.emotion_detector.MODEL_CONFIG'),
            patch('src.processors.text_processor.PROCESSOR_CONFIG'),
            patch('src.streaming.stream_manager.STREAM_CONFIG'),
            patch('src.utils.db_manager.DB_CONFIG'),
            patch('src.utils.cache_manager.CACHE_CONFIG')
        ]
        
        # Start patchers
        self.mock_configs = [patcher.start() for patcher in self.config_patchers]
        
        # Set up mock configurations
        self.mock_configs[0].return_value = {
            'sentiment': {
                'default_model': 'vader',
                'vader': {'enabled': True},
                'textblob': {'enabled': True},
                'bert': {'enabled': False},
                'custom': {'enabled': False},
                'ensemble': {'enabled': True}
            }
        }
        
        self.mock_configs[1].return_value = {
            'emotion': {
                'default_model': 'rule_based',
                'transformer': {'enabled': False},
                'rule_based': {'enabled': True},
                'custom': {'enabled': False},
                'ensemble': {'enabled': True}
            }
        }
        
        self.mock_configs[2].return_value = {
            'text': {
                'remove_urls': True,
                'remove_html_tags': True,
                'remove_mentions': True,
                'remove_hashtags': False,
                'remove_punctuation': True,
                'remove_extra_whitespace': True,
                'remove_stopwords': True,
                'lemmatize': True,
                'lowercase': True
            }
        }
        
        self.mock_configs[3].return_value = {
            'twitter': {'enabled': True},
            'reddit': {'enabled': True},
            'kafka': {'enabled': True}
        }
        
        self.mock_configs[4].return_value = {
            'postgres': {'enabled': False},
            'mongodb': {'enabled': False},
            'redis': {'enabled': False}
        }
        
        self.mock_configs[5].return_value = {
            'redis': {'enabled': False}
        }
        
        # Mock external dependencies
        self.nltk_patcher = patch('src.processors.text_processor.nltk')
        self.mock_nltk = self.nltk_patcher.start()
        
        # Create components
        self.text_processor = TextProcessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_detector = EmotionDetector()
        self.stream_manager = StreamManager()
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager()
        
        # Mock the models
        self.sentiment_analyzer.models = {
            'vader': MagicMock(return_value={'compound': 0.8, 'pos': 0.8, 'neg': 0.1, 'neu': 0.1}),
            'textblob': MagicMock(return_value=MagicMock(polarity=0.7, subjectivity=0.6)),
            'ensemble': self.sentiment_analyzer._ensemble_model
        }
        
        self.emotion_detector.models = {
            'rule_based': MagicMock(return_value={
                'joy': 0.8,
                'sadness': 0.1,
                'anger': 0.05,
                'fear': 0.03,
                'surprise': 0.02
            }),
            'ensemble': self.emotion_detector._ensemble_model
        }
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Stop patchers
        for patcher in self.config_patchers:
            patcher.stop()
        self.nltk_patcher.stop()
    
    def test_end_to_end_analysis(self):
        """Test end-to-end text analysis flow"""
        # Original text
        text = "I absolutely love this product! It's amazing and works perfectly. #happy @company"
        
        # Process text
        processed_text = self.text_processor.process_text(text)
        
        # Check processed text
        self.assertIsInstance(processed_text, str)
        self.assertNotIn('@company', processed_text)
        self.assertIn('love', processed_text)
        self.assertIn('product', processed_text)
        self.assertIn('happy', processed_text)  # Hashtag content should be preserved
        
        # Analyze sentiment
        sentiment_result = self.sentiment_analyzer.analyze_text(processed_text, model='vader')
        
        # Check sentiment result
        self.assertIsInstance(sentiment_result, dict)
        self.assertIn('sentiment', sentiment_result)
        self.assertIn('confidence', sentiment_result)
        self.assertEqual(sentiment_result['model'], 'vader')
        self.assertEqual(sentiment_result['sentiment'], 'positive')
        
        # Detect emotions
        emotion_result = self.emotion_detector.detect_emotions(processed_text, model='rule_based')
        
        # Check emotion result
        self.assertIsInstance(emotion_result, dict)
        self.assertIn('emotions', emotion_result)
        self.assertEqual(emotion_result['model'], 'rule_based')
        self.assertGreater(emotion_result['emotions']['joy'], 0.7)
        
        # Store results in database (mocked)
        with patch.object(self.db_manager, 'store_sentiment_analysis') as mock_store_sentiment:
            with patch.object(self.db_manager, 'store_emotion_analysis') as mock_store_emotion:
                self.db_manager.store_sentiment_analysis(sentiment_result)
                self.db_manager.store_emotion_analysis(emotion_result)
                
                mock_store_sentiment.assert_called_once_with(sentiment_result)
                mock_store_emotion.assert_called_once_with(emotion_result)
    
    def test_batch_processing(self):
        """Test batch processing flow"""
        # Original texts
        texts = [
            "I love this product! It's amazing!",
            "This is terrible, I hate it.",
            "It's okay, nothing special."
        ]
        
        # Process texts
        processed_texts = self.text_processor.process_batch_texts(texts)
        
        # Check processed texts
        self.assertEqual(len(processed_texts), 3)
        self.assertIn('love', processed_texts[0])
        self.assertIn('terrible', processed_texts[1])
        self.assertIn('okay', processed_texts[2])
        
        # Analyze sentiments
        sentiment_results = self.sentiment_analyzer.analyze_batch_texts(processed_texts, model='vader')
        
        # Check sentiment results
        self.assertEqual(len(sentiment_results), 3)
        self.assertEqual(sentiment_results[0]['sentiment'], 'positive')
        self.assertEqual(sentiment_results[1]['sentiment'], 'negative')
        
        # Detect emotions
        emotion_results = self.emotion_detector.detect_batch_emotions(processed_texts, model='rule_based')
        
        # Check emotion results
        self.assertEqual(len(emotion_results), 3)
        self.assertGreater(emotion_results[0]['emotions']['joy'], 0.7)
        self.assertGreater(emotion_results[1]['emotions']['anger'], 0.0)
        
        # Store results in database (mocked)
        with patch.object(self.db_manager, 'store_batch_sentiment_analysis') as mock_store_sentiment:
            with patch.object(self.db_manager, 'store_batch_emotion_analysis') as mock_store_emotion:
                self.db_manager.store_batch_sentiment_analysis(sentiment_results)
                self.db_manager.store_batch_emotion_analysis(emotion_results)
                
                mock_store_sentiment.assert_called_once_with(sentiment_results)
                mock_store_emotion.assert_called_once_with(emotion_results)
    
    def test_streaming_integration(self):
        """Test streaming integration"""
        # Start a stream
        with patch.object(self.stream_manager, '_twitter_stream') as mock_twitter_stream:
            stream_id = self.stream_manager.start_stream(
                source="twitter",
                keywords=["python", "programming"],
                languages=["en"],
                limit=50
            )
            
            # Check stream was started
            self.assertIsNotNone(stream_id)
            self.assertIn(stream_id, self.stream_manager._active_streams)
            mock_twitter_stream.assert_called_once()
            
            # Mock processing a tweet
            tweet = {"text": "Python is an amazing programming language! #python"}
            
            # Process the tweet
            with patch.object(self.text_processor, 'process_text', return_value="python amazing programming language") as mock_process:
                with patch.object(self.sentiment_analyzer, 'analyze_text') as mock_analyze:
                    with patch.object(self.db_manager, 'store_stream_data') as mock_store:
                        # Set up mock sentiment result
                        mock_analyze.return_value = {
                            'text': "python amazing programming language",
                            'sentiment': 'positive',
                            'confidence': 0.9,
                            'model': 'vader'
                        }
                        
                        # Process stream data
                        self.stream_manager._process_stream_data(stream_id, tweet)
                        
                        # Check processing flow
                        mock_process.assert_called_once_with(tweet["text"])
                        mock_analyze.assert_called_once()
                        mock_store.assert_called_once_with(stream_id, mock_analyze.return_value)

if __name__ == '__main__':
    unittest.main()