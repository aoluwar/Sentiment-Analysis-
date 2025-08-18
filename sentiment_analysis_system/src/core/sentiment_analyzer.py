import logging
import time
from typing import Dict, Any, List, Tuple, Optional
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import MODEL_CONFIG

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Core sentiment analysis class that handles multiple models and provides unified interface"""
    
    def __init__(self, model_type: str = None):
        """Initialize the sentiment analyzer with specified model type
        
        Args:
            model_type: Type of model to use (bert, vader, textblob, custom)
        """
        self.model_type = model_type or MODEL_CONFIG["default_model"]
        self.models = {}
        self.load_models()
        logger.info(f"Initialized SentimentAnalyzer with model type: {self.model_type}")
    
    def load_models(self):
        """Load the required sentiment analysis models"""
        try:
            # Load BERT model if selected
            if self.model_type == "bert" or self.model_type == "all":
                logger.info("Loading BERT model...")
                self._load_bert_model()
            
            # Load VADER model if selected
            if self.model_type == "vader" or self.model_type == "all":
                logger.info("Loading VADER model...")
                self._load_vader_model()
            
            # Load TextBlob model if selected
            if self.model_type == "textblob" or self.model_type == "all":
                logger.info("Loading TextBlob model...")
                self._load_textblob_model()
            
            # Load custom model if selected
            if self.model_type == "custom" or self.model_type == "all":
                logger.info("Loading custom model...")
                self._load_custom_model()
                
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def _load_bert_model(self):
        """Load the BERT-based sentiment analysis model"""
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch
            
            model_path = MODEL_CONFIG["model_paths"]["bert"]
            
            # Check if model exists locally, otherwise download from HuggingFace
            if os.path.exists(model_path):
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                # Use a pre-trained sentiment analysis model
                model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                
                # Save the model locally
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                tokenizer.save_pretrained(model_path)
                model.save_pretrained(model_path)
            
            self.models["bert"] = {
                "model": model,
                "tokenizer": tokenizer
            }
            
            logger.info("BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading BERT model: {str(e)}")
            raise
    
    def _load_vader_model(self):
        """Load the VADER sentiment analysis model"""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            
            self.models["vader"] = {
                "model": SentimentIntensityAnalyzer()
            }
            
            logger.info("VADER model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading VADER model: {str(e)}")
            raise
    
    def _load_textblob_model(self):
        """Load the TextBlob sentiment analysis model"""
        try:
            from textblob import TextBlob
            
            # TextBlob doesn't need pre-loading, just store the class
            self.models["textblob"] = {
                "model": TextBlob
            }
            
            logger.info("TextBlob model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading TextBlob model: {str(e)}")
            raise
    
    def _load_custom_model(self):
        """Load a custom sentiment analysis model"""
        try:
            # This is a placeholder for loading a custom model
            # In a real implementation, this would load a custom trained model
            
            # For demonstration, we'll create a simple ensemble model
            self.models["custom"] = {
                "model": "ensemble",
                "weights": {
                    "bert": 0.6,
                    "vader": 0.3,
                    "textblob": 0.1
                }
            }
            
            logger.info("Custom model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading custom model: {str(e)}")
            raise
    
    def analyze(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze the sentiment of the given text
        
        Args:
            text: Text to analyze
            language: Language code (ISO 639-1)
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        start_time = time.time()
        
        try:
            # Use the appropriate model based on the model_type
            if self.model_type == "bert":
                result = self._analyze_with_bert(text)
            elif self.model_type == "vader":
                result = self._analyze_with_vader(text)
            elif self.model_type == "textblob":
                result = self._analyze_with_textblob(text)
            elif self.model_type == "custom":
                result = self._analyze_with_custom(text)
            elif self.model_type == "all":
                # Ensemble approach - combine results from all models
                result = self._analyze_with_ensemble(text)
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            # Add processing time
            result["processing_time"] = time.time() - start_time
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            raise
    
    def _analyze_with_bert(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using BERT model
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            import torch
            
            model = self.models["bert"]["model"]
            tokenizer = self.models["bert"]["tokenizer"]
            
            # Tokenize and prepare input
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get prediction
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = outputs.logits
                scores = torch.nn.functional.softmax(predictions, dim=1)
            
            # Get sentiment label and confidence
            sentiment_id = torch.argmax(scores).item()
            confidence = scores[0][sentiment_id].item()
            
            # Map sentiment ID to label (0: negative, 1: positive)
            sentiment = "positive" if sentiment_id == 1 else "negative"
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "model": "bert",
                "scores": {
                    "positive": scores[0][1].item(),
                    "negative": scores[0][0].item()
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing with BERT: {str(e)}")
            raise
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER model
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            analyzer = self.models["vader"]["model"]
            scores = analyzer.polarity_scores(text)
            
            # Determine sentiment based on compound score
            if scores["compound"] >= 0.05:
                sentiment = "positive"
            elif scores["compound"] <= -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Calculate confidence based on the absolute value of the compound score
            confidence = abs(scores["compound"])
            if sentiment == "neutral":
                confidence = 1 - confidence
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "model": "vader",
                "scores": {
                    "positive": scores["pos"],
                    "negative": scores["neg"],
                    "neutral": scores["neu"],
                    "compound": scores["compound"]
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing with VADER: {str(e)}")
            raise
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            TextBlob = self.models["textblob"]["model"]
            blob = TextBlob(text)
            
            # Get polarity and subjectivity
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment based on polarity
            if polarity > 0.05:
                sentiment = "positive"
            elif polarity < -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Calculate confidence based on the absolute value of polarity and subjectivity
            confidence = abs(polarity) * subjectivity
            if sentiment == "neutral":
                confidence = 1 - confidence
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "model": "textblob",
                "scores": {
                    "polarity": polarity,
                    "subjectivity": subjectivity
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing with TextBlob: {str(e)}")
            raise
    
    def _analyze_with_custom(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using custom model (ensemble in this case)
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # For demonstration, our custom model is an ensemble of other models
        return self._analyze_with_ensemble(text)
    
    def _analyze_with_ensemble(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using an ensemble of models
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Get results from individual models
            results = {}
            
            # Only use models that are loaded
            if "bert" in self.models:
                results["bert"] = self._analyze_with_bert(text)
            
            if "vader" in self.models:
                results["vader"] = self._analyze_with_vader(text)
            
            if "textblob" in self.models:
                results["textblob"] = self._analyze_with_textblob(text)
            
            # Get weights for ensemble
            weights = self.models["custom"]["weights"] if "custom" in self.models else {
                "bert": 0.6,
                "vader": 0.3,
                "textblob": 0.1
            }
            
            # Normalize weights based on available models
            available_models = set(results.keys())
            total_weight = sum(weights[model] for model in available_models if model in weights)
            normalized_weights = {model: weights[model] / total_weight for model in available_models if model in weights}
            
            # Calculate weighted scores
            positive_score = 0
            negative_score = 0
            neutral_score = 0
            
            for model, result in results.items():
                if model == "bert":
                    positive_score += result["scores"]["positive"] * normalized_weights[model]
                    negative_score += result["scores"]["negative"] * normalized_weights[model]
                elif model == "vader":
                    positive_score += result["scores"]["positive"] * normalized_weights[model]
                    negative_score += result["scores"]["negative"] * normalized_weights[model]
                    neutral_score += result["scores"]["neutral"] * normalized_weights[model]
                elif model == "textblob":
                    # Convert TextBlob polarity to positive/negative scores
                    polarity = result["scores"]["polarity"]
                    if polarity > 0:
                        positive_score += polarity * normalized_weights[model]
                    elif polarity < 0:
                        negative_score += abs(polarity) * normalized_weights[model]
                    else:
                        neutral_score += normalized_weights[model]
            
            # Determine final sentiment
            if positive_score > negative_score and positive_score > neutral_score:
                sentiment = "positive"
                confidence = positive_score
            elif negative_score > positive_score and negative_score > neutral_score:
                sentiment = "negative"
                confidence = negative_score
            else:
                sentiment = "neutral"
                confidence = neutral_score
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "model": "ensemble",
                "scores": {
                    "positive": positive_score,
                    "negative": negative_score,
                    "neutral": neutral_score
                },
                "individual_results": results
            }
        except Exception as e:
            logger.error(f"Error analyzing with ensemble: {str(e)}")
            raise
    
    def batch_analyze(self, texts: List[str], language: str = "en") -> List[Dict[str, Any]]:
        """Analyze sentiment for a batch of texts
        
        Args:
            texts: List of texts to analyze
            language: Language code (ISO 639-1)
            
        Returns:
            List of dictionaries containing sentiment analysis results
        """
        results = []
        for text in texts:
            result = self.analyze(text, language)
            results.append(result)
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the sentiment analyzer
        
        Returns:
            Dictionary with health status
        """
        return {
            "status": "healthy",
            "model_type": self.model_type,
            "loaded_models": list(self.models.keys())
        }