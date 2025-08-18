import os
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "True").lower() in ("true", "1", "t")
API_WORKERS = int(os.getenv("API_WORKERS", 4))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 60))

# Database Settings
DATABASE_CONFIG = {
    "postgres": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "database": os.getenv("POSTGRES_DB", "sentiment_analysis"),
    },
    "mongodb": {
        "host": os.getenv("MONGODB_HOST", "localhost"),
        "port": int(os.getenv("MONGODB_PORT", 27017)),
        "user": os.getenv("MONGODB_USER", "mongo"),
        "password": os.getenv("MONGODB_PASSWORD", "mongo"),
        "database": os.getenv("MONGODB_DB", "sentiment_analysis"),
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": int(os.getenv("REDIS_DB", 0)),
        "password": os.getenv("REDIS_PASSWORD", None),
    },
}

# Model Settings
MODEL_CONFIG = {
    "sentiment": {
        "default_model": os.getenv("DEFAULT_SENTIMENT_MODEL", "ensemble"),
        "vader": {"enabled": os.getenv("VADER_ENABLED", "True").lower() in ("true", "1", "t")},
        "textblob": {"enabled": os.getenv("TEXTBLOB_ENABLED", "True").lower() in ("true", "1", "t")},
        "bert": {
            "enabled": os.getenv("BERT_ENABLED", "True").lower() in ("true", "1", "t"),
            "model_path": os.getenv("BERT_MODEL_PATH", "models/bert-base-uncased")
        },
        "custom": {"enabled": os.getenv("CUSTOM_SENTIMENT_ENABLED", "False").lower() in ("true", "1", "t")},
        "ensemble": {
            "enabled": os.getenv("ENSEMBLE_SENTIMENT_ENABLED", "True").lower() in ("true", "1", "t"),
            "weights": {
                "vader": float(os.getenv("ENSEMBLE_VADER_WEIGHT", 0.3)),
                "textblob": float(os.getenv("ENSEMBLE_TEXTBLOB_WEIGHT", 0.2)),
                "bert": float(os.getenv("ENSEMBLE_BERT_WEIGHT", 0.5))
            }
        }
    },
    "emotion": {
        "default_model": os.getenv("DEFAULT_EMOTION_MODEL", "ensemble"),
        "transformer": {
            "enabled": os.getenv("TRANSFORMER_EMOTION_ENABLED", "True").lower() in ("true", "1", "t"),
            "model_path": os.getenv("EMOTION_MODEL_PATH", "models/emotion-english-distilroberta-base")
        },
        "rule_based": {"enabled": os.getenv("RULE_BASED_EMOTION_ENABLED", "True").lower() in ("true", "1", "t")},
        "custom": {"enabled": os.getenv("CUSTOM_EMOTION_ENABLED", "False").lower() in ("true", "1", "t")},
        "ensemble": {
            "enabled": os.getenv("ENSEMBLE_EMOTION_ENABLED", "True").lower() in ("true", "1", "t"),
            "weights": {
                "transformer": float(os.getenv("ENSEMBLE_TRANSFORMER_WEIGHT", 0.7)),
                "rule_based": float(os.getenv("ENSEMBLE_RULE_BASED_WEIGHT", 0.3))
            }
        }
    }
}

# Processor Settings
PROCESSOR_CONFIG = {
    "text": {
        "remove_urls": os.getenv("REMOVE_URLS", "True").lower() in ("true", "1", "t"),
        "remove_html_tags": os.getenv("REMOVE_HTML_TAGS", "True").lower() in ("true", "1", "t"),
        "remove_mentions": os.getenv("REMOVE_MENTIONS", "True").lower() in ("true", "1", "t"),
        "remove_hashtags": os.getenv("REMOVE_HASHTAGS", "False").lower() in ("true", "1", "t"),
        "remove_punctuation": os.getenv("REMOVE_PUNCTUATION", "True").lower() in ("true", "1", "t"),
        "remove_extra_whitespace": os.getenv("REMOVE_EXTRA_WHITESPACE", "True").lower() in ("true", "1", "t"),
        "remove_stopwords": os.getenv("REMOVE_STOPWORDS", "True").lower() in ("true", "1", "t"),
        "lemmatize": os.getenv("LEMMATIZE", "True").lower() in ("true", "1", "t"),
        "lowercase": os.getenv("LOWERCASE", "True").lower() in ("true", "1", "t")
    }
}

# Model Settings
MODEL_CONFIG = {
    "default_model": os.getenv("DEFAULT_MODEL", "bert"),  # Options: bert, vader, textblob, custom
    "model_paths": {
        "bert": os.getenv("BERT_MODEL_PATH", "models/pretrained/bert-base-uncased"),
        "custom": os.getenv("CUSTOM_MODEL_PATH", "models/custom/sentiment_transformer"),
    },
    "batch_size": int(os.getenv("MODEL_BATCH_SIZE", 32)),
    "cache_results": os.getenv("CACHE_RESULTS", "True").lower() in ("true", "1", "t"),
    "cache_ttl": int(os.getenv("CACHE_TTL", 3600)),  # Time to live in seconds
}

# Social Media API Settings
SOCIAL_MEDIA_CONFIG = {
    "twitter": {
        "api_key": os.getenv("TWITTER_API_KEY", ""),
        "api_secret": os.getenv("TWITTER_API_SECRET", ""),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
    },
    "reddit": {
        "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
        "user_agent": os.getenv("REDDIT_USER_AGENT", "sentiment_analysis_bot/1.0"),
    },
}

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = os.getenv("LOG_FILE", "logs/sentiment_analysis.log")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10485760))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# Logging Config Dictionary
LOGGING_CONFIG = {
    "level": LOG_LEVEL,
    "format": LOG_FORMAT,
    "console": os.getenv("LOG_CONSOLE", "True").lower() in ("true", "1", "t"),
    "file": {
        "enabled": os.getenv("LOG_FILE_ENABLED", "True").lower() in ("true", "1", "t"),
        "path": LOG_FILE,
        "max_size": LOG_MAX_SIZE,
        "backup_count": LOG_BACKUP_COUNT
    }
}

# Web Interface Settings
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8080))
WEB_DEBUG = os.getenv("WEB_DEBUG", "True").lower() in ("true", "1", "t")
WEB_WORKERS = int(os.getenv("WEB_WORKERS", 2))
WEB_TIMEOUT = int(os.getenv("WEB_TIMEOUT", 60))

# Web Config Dictionary
WEB_CONFIG = {
    "host": WEB_HOST,
    "port": WEB_PORT,
    "debug": WEB_DEBUG,
    "workers": WEB_WORKERS,
    "timeout": WEB_TIMEOUT
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "workers": int(os.getenv("WORKERS", 4)),
    "max_connections": int(os.getenv("MAX_CONNECTIONS", 100)),
    "timeout": int(os.getenv("TIMEOUT", 60)),
}

# Streaming Settings
STREAMING_CONFIG = {
    "twitter": {
        "enabled": os.getenv("TWITTER_ENABLED", "True").lower() in ("true", "1", "t"),
        "api_key": os.getenv("TWITTER_API_KEY", ""),
        "api_secret": os.getenv("TWITTER_API_SECRET", ""),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
        "max_tweets": int(os.getenv("TWITTER_MAX_TWEETS", 1000)),
        "batch_size": int(os.getenv("TWITTER_BATCH_SIZE", 100))
    },
    "reddit": {
        "enabled": os.getenv("REDDIT_ENABLED", "True").lower() in ("true", "1", "t"),
        "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
        "user_agent": os.getenv("REDDIT_USER_AGENT", "SentimentAnalysisSystem/1.0"),
        "max_posts": int(os.getenv("REDDIT_MAX_POSTS", 500)),
        "batch_size": int(os.getenv("REDDIT_BATCH_SIZE", 50))
    },
    "kafka": {
        "enabled": os.getenv("KAFKA_ENABLED", "True").lower() in ("true", "1", "t"),
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "topic": os.getenv("KAFKA_TOPIC", "sentiment-data"),
        "group_id": os.getenv("KAFKA_GROUP_ID", "sentiment-analysis-group"),
        "batch_size": int(os.getenv("KAFKA_BATCH_SIZE", 100))
    }
}

# Cache Settings
CACHE_CONFIG = {
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": int(os.getenv("REDIS_DB", 0)),
        "password": os.getenv("REDIS_PASSWORD", None),
        "ttl": int(os.getenv("CACHE_TTL", 3600)),
        "enabled": os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "t"),
    }
}

# Helper functions for configuration
def _load_config_from_file(file_path):
    """Load configuration from a file
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config from {file_path}: {e}")
        return {}

def _resolve_environment_variables(config):
    """Resolve environment variables in configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configuration with resolved environment variables
    """
    if isinstance(config, dict):
        return {k: _resolve_environment_variables(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_resolve_environment_variables(item) for item in config]
    elif isinstance(config, str):
        # Match ${ENV_VAR:default_value} pattern
        pattern = r'\${([^:}]+)(?::([^}]+))?}'
        match = re.search(pattern, config)
        if match:
            env_var, default = match.groups()
            value = os.getenv(env_var, default)
            return config.replace(match.group(0), value)
        return config
    else:
        return config

def get_config(config_file=None):
    """Get configuration
    
    Args:
        config_file: Path to configuration file (optional)
        
    Returns:
        Configuration dictionary
    """
    if config_file and os.path.exists(config_file):
        config = _load_config_from_file(config_file)
        return _resolve_environment_variables(config)
    
    # Return default configuration
    return {
        "api": {
            "host": API_HOST,
            "port": API_PORT,
            "debug": API_DEBUG,
            "workers": API_WORKERS,
            "timeout": API_TIMEOUT
        },
        "database": DATABASE_CONFIG,
        "cache": CACHE_CONFIG,
        "models": MODEL_CONFIG,
        "processors": PROCESSOR_CONFIG,
        "streaming": STREAMING_CONFIG,
        "web": WEB_CONFIG,
        "logging": LOGGING_CONFIG
    }

def get_api_config():
    """Get API configuration
    
    Returns:
        API configuration dictionary
    """
    return get_config()["api"]

def get_database_config():
    """Get database configuration
    
    Returns:
        Database configuration dictionary
    """
    return get_config()["database"]

def get_model_config():
    """Get model configuration
    
    Returns:
        Model configuration dictionary
    """
    return get_config()["models"]

def get_processor_config():
    """Get processor configuration
    
    Returns:
        Processor configuration dictionary
    """
    return get_config().get("processors", {})

def get_streaming_config():
    """Get streaming configuration
    
    Returns:
        Streaming configuration dictionary
    """
    return get_config()["streaming"]

def get_web_config():
    """Get web configuration
    
    Returns:
        Web configuration dictionary
    """
    return get_config()["web"]

def get_cache_config():
    """Get cache configuration
    
    Returns:
        Cache configuration dictionary
    """
    return get_config()["cache"]

def get_logging_config():
    """Get logging configuration
    
    Returns:
        Logging configuration dictionary
    """
    return get_config()["logging"]