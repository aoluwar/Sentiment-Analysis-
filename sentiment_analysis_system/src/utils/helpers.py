import uuid
import time
import json
import functools
import re

def generate_id(prefix=None):
    """Generate a unique ID
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}-{unique_id}"
    return unique_id

def get_timestamp():
    """Get current timestamp
    
    Returns:
        Current timestamp as float
    """
    return time.time()

def format_timestamp(timestamp=None, format_str="%Y-%m-%d %H:%M:%S"):
    """Format timestamp to string
    
    Args:
        timestamp: Timestamp to format (default: current time)
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = get_timestamp()
    return time.strftime(format_str, time.localtime(timestamp))

def to_json(obj):
    """Convert object to JSON string
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON string
    """
    return json.dumps(obj)

def from_json(json_str):
    """Convert JSON string to object
    
    Args:
        json_str: JSON string
        
    Returns:
        Python object
    """
    return json.loads(json_str)

def safe_json(obj):
    """Safely convert object to JSON-serializable format
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [safe_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): safe_json(v) for k, v in obj.items()}
    else:
        return str(obj)

def merge_dicts(dict1, dict2):
    """Merge two dictionaries recursively
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
            
    return result

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested items
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def retry(max_attempts=3, delay=1):
    """Retry decorator for functions
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
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
        return wrapper
    return decorator

def rate_limit(calls_per_second=10):
    """Rate limit decorator
    
    Args:
        calls_per_second: Maximum calls per second
        
    Returns:
        Decorated function
    """
    min_interval = 1.0 / calls_per_second
    last_call_time = [0.0]
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            elapsed = current_time - last_call_time[0]
            
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
                
            result = func(*args, **kwargs)
            last_call_time[0] = time.time()
            return result
        return wrapper
    return decorator

def validate_text(text, min_length=0, max_length=None):
    """Validate text input
    
    Args:
        text: Text to validate
        min_length: Minimum text length (default: 0)
        max_length: Maximum text length (default: None)
        
    Returns:
        True if valid, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    if len(text.strip()) == 0:
        return False
    
    text_length = len(text)
    if text_length < min_length:
        return False
    if max_length is not None and text_length > max_length:
        return False
    
    return True

def sanitize_text(text):
    """Sanitize text input
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    # Remove script tags
    text = re.sub(r'<script>|</script>', '', text)
    # Trim whitespace
    return text.strip()