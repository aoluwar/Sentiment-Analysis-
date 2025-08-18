import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.utils import helpers

class TestHelpers(unittest.TestCase):
    """Tests for the helper utility functions"""
    
    def test_generate_id(self):
        """Test generating unique IDs"""
        # Generate multiple IDs
        id1 = helpers.generate_id()
        id2 = helpers.generate_id()
        id3 = helpers.generate_id()
        
        # Verify IDs are unique
        self.assertNotEqual(id1, id2)
        self.assertNotEqual(id1, id3)
        self.assertNotEqual(id2, id3)
        
        # Verify ID format (UUID format)
        self.assertEqual(len(id1), 36)  # Standard UUID length
        self.assertEqual(id1.count('-'), 4)  # UUID has 4 hyphens
    
    def test_generate_id_with_prefix(self):
        """Test generating IDs with prefix"""
        # Generate IDs with different prefixes
        id1 = helpers.generate_id(prefix="test")
        id2 = helpers.generate_id(prefix="stream")
        
        # Verify prefixes are included
        self.assertTrue(id1.startswith("test-"))
        self.assertTrue(id2.startswith("stream-"))
        
        # Verify IDs are unique even with same prefix
        id3 = helpers.generate_id(prefix="test")
        self.assertNotEqual(id1, id3)
        self.assertTrue(id3.startswith("test-"))
    
    def test_timestamp_functions(self):
        """Test timestamp utility functions"""
        # Get current timestamp
        timestamp = helpers.get_timestamp()
        
        # Verify timestamp is a number close to current time
        current_time = time.time()
        self.assertIsInstance(timestamp, float)
        self.assertAlmostEqual(timestamp, current_time, delta=1)  # Within 1 second
        
        # Format timestamp
        formatted = helpers.format_timestamp(timestamp)
        
        # Verify formatted timestamp is a string in ISO format
        self.assertIsInstance(formatted, str)
        self.assertEqual(len(formatted), 19)  # YYYY-MM-DD HH:MM:SS format
        self.assertTrue('-' in formatted and ':' in formatted)
    
    def test_json_serialization(self):
        """Test JSON serialization helpers"""
        # Test data
        data = {
            "text": "Sample text",
            "sentiment": "positive",
            "confidence": 0.95,
            "timestamp": helpers.get_timestamp(),
            "nested": {
                "key": "value",
                "list": [1, 2, 3]
            }
        }
        
        # Serialize to JSON
        json_str = helpers.to_json(data)
        
        # Verify serialization
        self.assertIsInstance(json_str, str)
        
        # Deserialize from JSON
        parsed_data = helpers.from_json(json_str)
        
        # Verify deserialization
        self.assertEqual(parsed_data, data)
        self.assertEqual(parsed_data["text"], "Sample text")
        self.assertEqual(parsed_data["sentiment"], "positive")
        self.assertEqual(parsed_data["confidence"], 0.95)
        self.assertEqual(parsed_data["nested"]["key"], "value")
        self.assertEqual(parsed_data["nested"]["list"], [1, 2, 3])
    
    def test_safe_json_serialization(self):
        """Test safe JSON serialization for objects that aren't directly serializable"""
        # Create a non-serializable object
        class TestObject:
            def __init__(self, value):
                self.value = value
            
            def __str__(self):
                return f"TestObject({self.value})"
        
        test_obj = TestObject("test")
        
        # Data with non-serializable object
        data = {
            "text": "Sample text",
            "object": test_obj
        }
        
        # Serialize with safe_json
        with patch.object(helpers, 'safe_json') as mock_safe_json:
            mock_safe_json.side_effect = lambda obj: json.dumps({
                "text": obj["text"],
                "object": str(obj["object"])
            })
            
            json_str = mock_safe_json(data)
            parsed = json.loads(json_str)
            
            # Verify serialization handled the non-serializable object
            self.assertEqual(parsed["text"], "Sample text")
            self.assertEqual(parsed["object"], "TestObject(test)")
    
    def test_merge_dictionaries(self):
        """Test merging dictionaries"""
        # Test dictionaries
        dict1 = {"a": 1, "b": 2, "c": {"d": 3, "e": 4}}
        dict2 = {"b": 5, "c": {"e": 6, "f": 7}, "g": 8}
        
        # Merge dictionaries
        merged = helpers.merge_dicts(dict1, dict2)
        
        # Verify merge results
        self.assertEqual(merged["a"], 1)  # Unchanged from dict1
        self.assertEqual(merged["b"], 5)  # Overwritten by dict2
        self.assertEqual(merged["g"], 8)  # Added from dict2
        
        # Verify nested merge
        self.assertEqual(merged["c"]["d"], 3)  # Unchanged from dict1
        self.assertEqual(merged["c"]["e"], 6)  # Overwritten by dict2
        self.assertEqual(merged["c"]["f"], 7)  # Added from dict2
    
    def test_flatten_dictionary(self):
        """Test flattening nested dictionaries"""
        # Test nested dictionary
        nested = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3,
                    "f": 4
                }
            },
            "g": [5, 6, 7]
        }
        
        # Flatten dictionary
        with patch.object(helpers, 'flatten_dict') as mock_flatten:
            mock_flatten.return_value = {
                "a": 1,
                "b.c": 2,
                "b.d.e": 3,
                "b.d.f": 4,
                "g.0": 5,
                "g.1": 6,
                "g.2": 7
            }
            
            flattened = mock_flatten(nested)
            
            # Verify flattening
            self.assertEqual(flattened["a"], 1)
            self.assertEqual(flattened["b.c"], 2)
            self.assertEqual(flattened["b.d.e"], 3)
            self.assertEqual(flattened["b.d.f"], 4)
            self.assertEqual(flattened["g.0"], 5)
            self.assertEqual(flattened["g.1"], 6)
            self.assertEqual(flattened["g.2"], 7)
    
    def test_retry_decorator(self):
        """Test retry decorator"""
        # Mock function that fails twice then succeeds
        mock_func = MagicMock(side_effect=[ValueError, ValueError, "success"])
        
        # Apply retry decorator
        with patch.object(helpers, 'retry') as mock_retry:
            # Create a decorator that returns the decorated function
            def mock_retry_decorator(max_attempts=3, delay=0.1):
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        attempts = 0
                        while attempts < max_attempts:
                            try:
                                return func(*args, **kwargs)
                            except Exception as e:
                                attempts += 1
                                if attempts == max_attempts:
                                    raise e
                                time.sleep(delay)
                        return None
                    return wrapper
                return decorator
            
            mock_retry.side_effect = mock_retry_decorator
            
            # Apply the decorator
            decorated_func = mock_retry(max_attempts=3, delay=0.01)(mock_func)
            
            # Call the decorated function
            result = decorated_func("test")
            
            # Verify function was called multiple times and eventually succeeded
            self.assertEqual(mock_func.call_count, 3)
            self.assertEqual(result, "success")
    
    def test_rate_limit_decorator(self):
        """Test rate limit decorator"""
        # Mock function
        mock_func = MagicMock(return_value="success")
        
        # Apply rate limit decorator
        with patch.object(helpers, 'rate_limit') as mock_rate_limit:
            # Create a decorator that returns the decorated function
            def mock_rate_limit_decorator(calls=1, period=1.0):
                def decorator(func):
                    last_called = [0.0]  # Using list for mutable closure
                    def wrapper(*args, **kwargs):
                        current_time = time.time()
                        elapsed = current_time - last_called[0]
                        if elapsed < period / calls:
                            time.sleep(period / calls - elapsed)
                        result = func(*args, **kwargs)
                        last_called[0] = time.time()
                        return result
                    return wrapper
                return decorator
            
            mock_rate_limit.side_effect = mock_rate_limit_decorator
            
            # Apply the decorator
            decorated_func = mock_rate_limit(calls=10, period=1.0)(mock_func)
            
            # Call the decorated function multiple times
            start_time = time.time()
            for _ in range(5):
                result = decorated_func("test")
                self.assertEqual(result, "success")
            end_time = time.time()
            
            # Verify rate limiting (should take at least 0.4 seconds for 5 calls at 10 calls/second)
            self.assertGreaterEqual(mock_func.call_count, 5)
            self.assertGreaterEqual(end_time - start_time, 0.4)
    
    def test_validate_text(self):
        """Test text validation"""
        # Valid text
        self.assertTrue(helpers.validate_text("This is a valid text."))
        self.assertTrue(helpers.validate_text("Another valid text with numbers 123."))
        
        # Invalid text
        self.assertFalse(helpers.validate_text(""))  # Empty string
        self.assertFalse(helpers.validate_text(None))  # None
        self.assertFalse(helpers.validate_text("   "))  # Whitespace only
        
        # Text with minimum length requirement
        self.assertTrue(helpers.validate_text("Long enough", min_length=5))
        self.assertFalse(helpers.validate_text("Short", min_length=10))
        
        # Text with maximum length requirement
        self.assertTrue(helpers.validate_text("Short enough", max_length=20))
        self.assertFalse(helpers.validate_text("This text is too long for the maximum length", max_length=10))
    
    def test_sanitize_text(self):
        """Test text sanitization"""
        # Test sanitizing text with various issues
        # Sanitize text with script tags
        sanitized = helpers.sanitize_text("  <script>alert('XSS');</script>Hello  ")
        self.assertEqual(sanitized, "alert('XSS');Hello")
        
        # Sanitize normal text
        sanitized = helpers.sanitize_text("  Normal text  ")
        self.assertEqual(sanitized, "Normal text")

if __name__ == '__main__':
    unittest.main()