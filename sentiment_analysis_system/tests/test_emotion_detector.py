import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.core.emotion_detector import EmotionDetector

class TestEmotionDetector(unittest.TestCase):
    """Test cases for EmotionDetector class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config_patcher = patch('src.core.emotion_detector.MODEL_CONFIG', {
            'emotion': {
                'default_model': 'rule_based',
                'transformer': {
                    'model_name': 'j-hartmann/emotion-english-distilroberta-base',
                    'enabled': False
                },
                'rule_based': {
                    'enabled': True
                },
                'custom': {
                    'enabled': False,
                    'model_path': 'models/custom/emotion_model.pkl'
                },
                'ensemble': {
                    'enabled': True,
                    'weights': {
                        'transformer': 0.7,
                        'rule_based': 0.3,
                        'custom': 0.0
                    }
                }
            }
        })
        self.config_patcher.start()
        
        # Create detector
        self.detector = EmotionDetector()
        
        # Mock the models
        self.detector.models = {
            'rule_based': MagicMock(),
            'ensemble': MagicMock()
        }
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.config_patcher.stop()
    
    def test_detect_emotions_rule_based(self):
        """Test detecting emotions with rule-based model"""
        # Mock rule-based result
        self.detector.models['rule_based'].return_value = {
            'joy': 0.8,
            'sadness': 0.1,
            'anger': 0.05,
            'fear': 0.03,
            'surprise': 0.02
        }
        
        # Detect emotions
        result = self.detector.detect_emotions("I am so happy today!", model="rule_based")
        
        # Check result
        self.assertIn('emotions', result)
        self.assertEqual(len(result['emotions']), 5)
        self.assertGreater(result['emotions']['joy'], 0.7)
        self.assertEqual(result['model'], 'rule_based')
        self.assertEqual(result['text'], 'I am so happy today!')
        
        # Verify rule-based model was called
        self.detector.models['rule_based'].assert_called_once_with("I am so happy today!")
    
    def test_detect_emotions_ensemble(self):
        """Test detecting emotions with ensemble model"""
        # Mock rule-based result
        self.detector.models['rule_based'].return_value = {
            'joy': 0.8,
            'sadness': 0.1,
            'anger': 0.05,
            'fear': 0.03,
            'surprise': 0.02
        }
        
        # Detect emotions
        result = self.detector.detect_emotions("I am so happy today!", model="ensemble")
        
        # Check result
        self.assertIn('emotions', result)
        self.assertEqual(len(result['emotions']), 5)
        self.assertGreater(result['emotions']['joy'], 0.7)
        self.assertEqual(result['model'], 'ensemble')
        self.assertEqual(result['text'], 'I am so happy today!')
    
    def test_detect_batch_emotions(self):
        """Test detecting emotions for a batch of texts"""
        # Mock rule-based results
        self.detector.models['rule_based'].side_effect = [
            {
                'joy': 0.8,
                'sadness': 0.1,
                'anger': 0.05,
                'fear': 0.03,
                'surprise': 0.02
            },
            {
                'joy': 0.1,
                'sadness': 0.7,
                'anger': 0.1,
                'fear': 0.05,
                'surprise': 0.05
            }
        ]
        
        # Detect emotions for batch
        texts = ["I am so happy today!", "I am feeling sad and depressed."]
        results = self.detector.detect_batch_emotions(texts, model="rule_based")
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0]['emotions']['joy'], 0.7)
        self.assertGreater(results[1]['emotions']['sadness'], 0.6)
        
        # Verify rule-based model was called twice
        self.assertEqual(self.detector.models['rule_based'].call_count, 2)
    
    def test_health_check(self):
        """Test health check"""
        # Run health check
        health = self.detector.health_check()
        
        # Check result
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('models', health)
        self.assertIn('rule_based', health['models'])

if __name__ == '__main__':
    unittest.main()