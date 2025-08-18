import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.processors.text_processor import TextProcessor

class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config_patcher = patch('src.processors.text_processor.PROCESSOR_CONFIG', {
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
        })
        self.config_patcher.start()
        
        # Create processor
        self.processor = TextProcessor()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.config_patcher.stop()
    
    def test_process_text_basic(self):
        """Test basic text processing"""
        # Process text
        text = "Hello, world! This is a test."
        processed = self.processor.process_text(text)
        
        # Check result
        self.assertIsInstance(processed, str)
        self.assertNotIn(',', processed)
        self.assertNotIn('!', processed)
        self.assertNotIn('.', processed)
        self.assertEqual(processed.lower(), processed)
    
    def test_process_text_urls(self):
        """Test processing text with URLs"""
        # Process text with URL
        text = "Check out this link: https://example.com/page?param=value"
        processed = self.processor.process_text(text)
        
        # Check result
        self.assertNotIn('https://', processed)
        self.assertNotIn('example.com', processed)
    
    def test_process_text_mentions(self):
        """Test processing text with mentions"""
        # Process text with mentions
        text = "Hey @user1 and @user2, check this out!"
        processed = self.processor.process_text(text)
        
        # Check result
        self.assertNotIn('@user1', processed)
        self.assertNotIn('@user2', processed)
    
    def test_process_text_hashtags(self):
        """Test processing text with hashtags"""
        # Process text with hashtags
        text = "This is #awesome and #cool!"
        processed = self.processor.process_text(text)
        
        # Check result - hashtags should be preserved but without the # symbol
        self.assertIn('awesome', processed)
        self.assertIn('cool', processed)
    
    def test_process_text_html(self):
        """Test processing text with HTML tags"""
        # Process text with HTML
        text = "<p>This is a <b>paragraph</b> with <a href='#'>HTML</a> tags.</p>"
        processed = self.processor.process_text(text)
        
        # Check result
        self.assertNotIn('<p>', processed)
        self.assertNotIn('<b>', processed)
        self.assertNotIn('</b>', processed)
        self.assertNotIn('<a href=', processed)
        self.assertIn('paragraph', processed)
        self.assertIn('html', processed)
    
    def test_process_batch_texts(self):
        """Test processing a batch of texts"""
        # Process batch
        texts = [
            "Hello, world! This is a test.",
            "Check out this link: https://example.com",
            "Hey @user, check this #hashtag!"
        ]
        processed = self.processor.process_batch_texts(texts)
        
        # Check results
        self.assertEqual(len(processed), 3)
        self.assertIsInstance(processed[0], str)
        self.assertIsInstance(processed[1], str)
        self.assertIsInstance(processed[2], str)
        self.assertNotIn('https://', processed[1])
        self.assertNotIn('@user', processed[2])
    
    def test_extract_keywords(self):
        """Test extracting keywords from text"""
        # Extract keywords
        text = "Artificial intelligence and machine learning are transforming the technology landscape."
        keywords = self.processor.extract_keywords(text, top_n=3)
        
        # Check results
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 3)
        
        # Keywords should include important terms
        important_terms = ['artificial', 'intelligence', 'machine', 'learning', 'technology']
        found = False
        for keyword in keywords:
            if keyword in important_terms:
                found = True
                break
        self.assertTrue(found, "No important keywords found")
    
    def test_detect_language(self):
        """Test language detection"""
        # Mock langdetect
        with patch('src.processors.text_processor.detect', return_value='en'):
            # Detect language
            text = "This is English text."
            lang = self.processor.detect_language(text)
            
            # Check result
            self.assertEqual(lang, 'en')
    
    def test_health_check(self):
        """Test health check"""
        # Run health check
        health = self.processor.health_check()
        
        # Check result
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('nltk_resources', health)

if __name__ == '__main__':
    unittest.main()