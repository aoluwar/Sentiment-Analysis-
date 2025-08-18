import logging
import re
import string
from typing import Dict, Any, List, Optional
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processing class for cleaning and normalizing text data"""
    
    def __init__(self):
        """Initialize the text processor"""
        self.load_resources()
        logger.info("Initialized TextProcessor")
    
    def load_resources(self):
        """Load required resources for text processing"""
        try:
            import nltk
            from nltk.corpus import stopwords
            
            # Download required NLTK resources
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            
            # Load stopwords for multiple languages
            self.stopwords = {}
            for lang in ['english', 'spanish', 'french', 'german', 'italian']:
                try:
                    self.stopwords[lang] = set(stopwords.words(lang))
                except:
                    self.stopwords[lang] = set()
            
            # Map ISO language codes to NLTK language names
            self.lang_map = {
                'en': 'english',
                'es': 'spanish',
                'fr': 'french',
                'de': 'german',
                'it': 'italian'
            }
            
            # Initialize lemmatizer
            from nltk.stem import WordNetLemmatizer
            self.lemmatizer = WordNetLemmatizer()
            
            logger.info("Text processing resources loaded successfully")
        except Exception as e:
            logger.error(f"Error loading text processing resources: {str(e)}")
            # Initialize with empty resources as fallback
            self.stopwords = {}
            self.lang_map = {}
            self.lemmatizer = None
    
    def process(self, text: str, language: str = "en", remove_stopwords: bool = False, lemmatize: bool = False) -> str:
        """Process the input text
        
        Args:
            text: Text to process
            language: Language code (ISO 639-1)
            remove_stopwords: Whether to remove stopwords
            lemmatize: Whether to lemmatize words (only for English)
            
        Returns:
            Processed text
        """
        try:
            # Convert to lowercase
            processed_text = text.lower()
            
            # Remove URLs
            processed_text = re.sub(r'https?://\S+|www\.\S+', '', processed_text)
            
            # Remove HTML tags
            processed_text = re.sub(r'<.*?>', '', processed_text)
            
            # Remove mentions and hashtags for social media text
            processed_text = re.sub(r'@\w+|#\w+', '', processed_text)
            
            # Remove punctuation
            processed_text = processed_text.translate(str.maketrans('', '', string.punctuation))
            
            # Remove extra whitespace
            processed_text = re.sub(r'\s+', ' ', processed_text).strip()
            
            # Tokenize
            import nltk
            tokens = nltk.word_tokenize(processed_text)
            
            # Remove stopwords if requested
            if remove_stopwords:
                nltk_lang = self.lang_map.get(language, 'english')
                if nltk_lang in self.stopwords:
                    tokens = [token for token in tokens if token not in self.stopwords[nltk_lang]]
            
            # Lemmatize if requested (only for English)
            if lemmatize and language == 'en' and self.lemmatizer is not None:
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            # Join tokens back into text
            processed_text = ' '.join(tokens)
            
            return processed_text
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            # Return original text as fallback
            return text
    
    def batch_process(self, texts: List[str], language: str = "en", remove_stopwords: bool = False, lemmatize: bool = False) -> List[str]:
        """Process a batch of texts
        
        Args:
            texts: List of texts to process
            language: Language code (ISO 639-1)
            remove_stopwords: Whether to remove stopwords
            lemmatize: Whether to lemmatize words (only for English)
            
        Returns:
            List of processed texts
        """
        processed_texts = []
        for text in texts:
            processed_text = self.process(text, language, remove_stopwords, lemmatize)
            processed_texts.append(processed_text)
        return processed_texts
    
    def extract_keywords(self, text: str, language: str = "en", num_keywords: int = 10) -> List[str]:
        """Extract keywords from text
        
        Args:
            text: Text to extract keywords from
            language: Language code (ISO 639-1)
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        try:
            # Process text first
            processed_text = self.process(text, language, remove_stopwords=True)
            
            # Tokenize
            import nltk
            tokens = nltk.word_tokenize(processed_text)
            
            # Calculate word frequencies
            from collections import Counter
            word_freq = Counter(tokens)
            
            # Get most common words
            keywords = [word for word, freq in word_freq.most_common(num_keywords)]
            
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code (ISO 639-1)
        """
        try:
            from langdetect import detect
            
            # Detect language
            lang_code = detect(text)
            
            return lang_code
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            # Default to English
            return "en"
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the text processor
        
        Returns:
            Dictionary with health status
        """
        return {
            "status": "healthy",
            "supported_languages": list(self.lang_map.keys()),
            "resources_loaded": {
                "stopwords": len(self.stopwords) > 0,
                "lemmatizer": self.lemmatizer is not None
            }
        }