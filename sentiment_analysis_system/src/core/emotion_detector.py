import logging
import time
from typing import Dict, Any, List, Optional
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import MODEL_CONFIG

logger = logging.getLogger(__name__)

class EmotionDetector:
    """Emotion detection class that identifies emotions in text"""
    
    def __init__(self, model_type: str = None):
        """Initialize the emotion detector with specified model type
        
        Args:
            model_type: Type of model to use (transformer, rule-based, custom)
        """
        self.model_type = model_type or "transformer"
        self.models = {}
        self.emotions = ["joy", "anger", "fear", "sadness", "surprise", "disgust"]
        self.load_models()
        logger.info(f"Initialized EmotionDetector with model type: {self.model_type}")
    
    def load_models(self):
        """Load the required emotion detection models"""
        try:
            # Load transformer model
            if self.model_type == "transformer" or self.model_type == "all":
                logger.info("Loading transformer emotion detection model...")
                self._load_transformer_model()
            
            # Load rule-based model
            if self.model_type == "rule-based" or self.model_type == "all":
                logger.info("Loading rule-based emotion detection model...")
                self._load_rule_based_model()
            
            # Load custom model
            if self.model_type == "custom" or self.model_type == "all":
                logger.info("Loading custom emotion detection model...")
                self._load_custom_model()
                
            logger.info("All emotion detection models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading emotion detection models: {str(e)}")
            raise
    
    def _load_transformer_model(self):
        """Load the transformer-based emotion detection model"""
        try:
            from transformers import pipeline
            
            # Use a pre-trained emotion detection model
            # This will download the model if it's not already available
            emotion_classifier = pipeline(
                "text-classification", 
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )
            
            self.models["transformer"] = {
                "model": emotion_classifier
            }
            
            logger.info("Transformer emotion detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading transformer emotion detection model: {str(e)}")
            # Fallback to a simpler model or approach
            self._load_rule_based_model()
    
    def _load_rule_based_model(self):
        """Load a rule-based emotion detection model"""
        try:
            import nltk
            from nltk.corpus import stopwords
            
            # Download required NLTK resources
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Create emotion lexicon (simplified for demonstration)
            emotion_lexicon = {
                "joy": ["happy", "joy", "delighted", "pleased", "glad", "excited", "cheerful"],
                "anger": ["angry", "furious", "outraged", "annoyed", "irritated", "enraged"],
                "fear": ["afraid", "scared", "frightened", "terrified", "anxious", "worried"],
                "sadness": ["sad", "unhappy", "depressed", "gloomy", "miserable", "heartbroken"],
                "surprise": ["surprised", "amazed", "astonished", "shocked", "stunned"],
                "disgust": ["disgusted", "revolted", "nauseated", "repulsed", "appalled"]
            }
            
            self.models["rule-based"] = {
                "model": "lexicon",
                "lexicon": emotion_lexicon,
                "stopwords": set(stopwords.words('english'))
            }
            
            logger.info("Rule-based emotion detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading rule-based emotion detection model: {str(e)}")
            raise
    
    def _load_custom_model(self):
        """Load a custom emotion detection model"""
        try:
            # This is a placeholder for loading a custom model
            # In a real implementation, this would load a custom trained model
            
            # For demonstration, we'll create a simple ensemble model
            self.models["custom"] = {
                "model": "ensemble",
                "weights": {
                    "transformer": 0.7,
                    "rule-based": 0.3
                }
            }
            
            logger.info("Custom emotion detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading custom emotion detection model: {str(e)}")
            raise
    
    def detect(self, text: str, language: str = "en") -> Dict[str, float]:
        """Detect emotions in the given text
        
        Args:
            text: Text to analyze
            language: Language code (ISO 639-1)
            
        Returns:
            Dictionary mapping emotions to their scores
        """
        start_time = time.time()
        
        try:
            # Use the appropriate model based on the model_type
            if self.model_type == "transformer" and "transformer" in self.models:
                result = self._detect_with_transformer(text)
            elif self.model_type == "rule-based" or (self.model_type == "transformer" and "transformer" not in self.models):
                result = self._detect_with_rule_based(text)
            elif self.model_type == "custom":
                result = self._detect_with_custom(text)
            elif self.model_type == "all":
                # Ensemble approach - combine results from all models
                result = self._detect_with_ensemble(text)
            else:
                # Fallback to rule-based if no other model is available
                result = self._detect_with_rule_based(text)
            
            # Add processing time
            result["processing_time"] = time.time() - start_time
            
            # Extract just the emotion scores
            emotion_scores = {emotion: score for emotion, score in result.items() if emotion in self.emotions}
            
            return emotion_scores
        except Exception as e:
            logger.error(f"Error detecting emotions: {str(e)}")
            # Return empty results in case of error
            return {emotion: 0.0 for emotion in self.emotions}
    
    def _detect_with_transformer(self, text: str) -> Dict[str, float]:
        """Detect emotions using transformer model
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotions to their scores
        """
        try:
            model = self.models["transformer"]["model"]
            
            # Get predictions
            predictions = model(text)[0]
            
            # Convert to dictionary
            emotion_scores = {}
            for pred in predictions:
                emotion = pred["label"].lower()
                score = pred["score"]
                emotion_scores[emotion] = score
            
            # Ensure all emotions are present
            for emotion in self.emotions:
                if emotion not in emotion_scores:
                    emotion_scores[emotion] = 0.0
            
            return emotion_scores
        except Exception as e:
            logger.error(f"Error detecting emotions with transformer: {str(e)}")
            # Fallback to rule-based
            return self._detect_with_rule_based(text)
    
    def _detect_with_rule_based(self, text: str) -> Dict[str, float]:
        """Detect emotions using rule-based model
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotions to their scores
        """
        try:
            import nltk
            
            lexicon = self.models["rule-based"]["lexicon"]
            stopwords = self.models["rule-based"]["stopwords"]
            
            # Tokenize and preprocess text
            tokens = nltk.word_tokenize(text.lower())
            tokens = [token for token in tokens if token.isalpha() and token not in stopwords]
            
            # Count emotion words
            emotion_counts = {emotion: 0 for emotion in self.emotions}
            for token in tokens:
                for emotion, words in lexicon.items():
                    if token in words:
                        emotion_counts[emotion] += 1
            
            # Calculate scores
            total_count = sum(emotion_counts.values()) or 1  # Avoid division by zero
            emotion_scores = {emotion: count / total_count for emotion, count in emotion_counts.items()}
            
            # If no emotions detected, assign small values to prevent all zeros
            if all(score == 0 for score in emotion_scores.values()):
                emotion_scores = {emotion: 0.1 for emotion in self.emotions}
                # Normalize
                total = sum(emotion_scores.values())
                emotion_scores = {emotion: score / total for emotion, score in emotion_scores.items()}
            
            return emotion_scores
        except Exception as e:
            logger.error(f"Error detecting emotions with rule-based: {str(e)}")
            # Return default values
            return {emotion: 1.0 / len(self.emotions) for emotion in self.emotions}
    
    def _detect_with_custom(self, text: str) -> Dict[str, float]:
        """Detect emotions using custom model (ensemble in this case)
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotions to their scores
        """
        # For demonstration, our custom model is an ensemble of other models
        return self._detect_with_ensemble(text)
    
    def _detect_with_ensemble(self, text: str) -> Dict[str, float]:
        """Detect emotions using an ensemble of models
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotions to their scores
        """
        try:
            # Get results from individual models
            results = {}
            
            # Only use models that are loaded
            if "transformer" in self.models:
                results["transformer"] = self._detect_with_transformer(text)
            
            if "rule-based" in self.models:
                results["rule-based"] = self._detect_with_rule_based(text)
            
            # Get weights for ensemble
            weights = self.models["custom"]["weights"] if "custom" in self.models else {
                "transformer": 0.7,
                "rule-based": 0.3
            }
            
            # Normalize weights based on available models
            available_models = set(results.keys())
            total_weight = sum(weights[model] for model in available_models if model in weights)
            normalized_weights = {model: weights[model] / total_weight for model in available_models if model in weights}
            
            # Calculate weighted scores
            emotion_scores = {emotion: 0.0 for emotion in self.emotions}
            
            for model, result in results.items():
                for emotion in self.emotions:
                    if emotion in result:
                        emotion_scores[emotion] += result[emotion] * normalized_weights[model]
            
            return emotion_scores
        except Exception as e:
            logger.error(f"Error detecting emotions with ensemble: {str(e)}")
            # Return default values
            return {emotion: 1.0 / len(self.emotions) for emotion in self.emotions}
    
    def batch_detect(self, texts: List[str], language: str = "en") -> List[Dict[str, float]]:
        """Detect emotions for a batch of texts
        
        Args:
            texts: List of texts to analyze
            language: Language code (ISO 639-1)
            
        Returns:
            List of dictionaries mapping emotions to their scores
        """
        results = []
        for text in texts:
            result = self.detect(text, language)
            results.append(result)
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the emotion detector
        
        Returns:
            Dictionary with health status
        """
        # Create a dictionary of model statuses
        model_statuses = {}
        for model_name in self.models.keys():
            model_statuses[model_name] = "loaded"
            
        return {
            "status": "healthy",
            "model_type": self.model_type,
            "loaded_models": list(self.models.keys()),
            "supported_emotions": self.emotions,
            "models": model_statuses
        }