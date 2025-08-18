import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.utils.logger import setup_logger

class TestLogger(unittest.TestCase):
    """Test cases for logger utility"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock logging
        self.getLogger_patcher = patch('src.utils.logger.logging.getLogger')
        self.mock_getLogger = self.getLogger_patcher.start()
        self.mock_logger = MagicMock()
        self.mock_getLogger.return_value = self.mock_logger
        
        # Mock handlers
        self.StreamHandler_patcher = patch('src.utils.logger.logging.StreamHandler')
        self.mock_StreamHandler = self.StreamHandler_patcher.start()
        self.mock_stream_handler = MagicMock()
        self.mock_StreamHandler.return_value = self.mock_stream_handler
        
        self.FileHandler_patcher = patch('src.utils.logger.logging.handlers.RotatingFileHandler')
        self.mock_FileHandler = self.FileHandler_patcher.start()
        self.mock_file_handler = MagicMock()
        self.mock_FileHandler.return_value = self.mock_file_handler
        
        # Mock formatter
        self.Formatter_patcher = patch('src.utils.logger.logging.Formatter')
        self.mock_Formatter = self.Formatter_patcher.start()
        self.mock_formatter = MagicMock()
        self.mock_Formatter.return_value = self.mock_formatter
        
        # Mock os.path.exists and os.makedirs
        self.path_exists_patcher = patch('src.utils.logger.os.path.exists')
        self.mock_path_exists = self.path_exists_patcher.start()
        self.mock_path_exists.return_value = False
        
        self.makedirs_patcher = patch('src.utils.logger.os.makedirs')
        self.mock_makedirs = self.makedirs_patcher.start()
        
        # Mock datetime
        self.datetime_patcher = patch('src.utils.logger.datetime')
        self.mock_datetime = self.datetime_patcher.start()
        self.mock_datetime.now.return_value.strftime.return_value = '2023-01-01'
        
        # Mock settings
        self.settings_patcher = patch('src.utils.logger.LOGGING_CONFIG', {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'log_dir': 'logs',
            'log_file': 'sentiment_analysis.log',
            'max_size_mb': 10,
            'backup_count': 5,
            'console_logging': True,
            'file_logging': True
        })
        self.mock_settings = self.settings_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.getLogger_patcher.stop()
        self.StreamHandler_patcher.stop()
        self.FileHandler_patcher.stop()
        self.Formatter_patcher.stop()
        self.path_exists_patcher.stop()
        self.makedirs_patcher.stop()
        self.datetime_patcher.stop()
        self.settings_patcher.stop()
    
    def test_setup_logger_with_defaults(self):
        """Test setting up logger with default settings"""
        # Call setup_logger
        logger = setup_logger()
        
        # Check logger was configured correctly
        self.mock_getLogger.assert_called_once()
        self.mock_logger.setLevel.assert_called_once_with(logging.INFO)
        
        # Check formatter was created
        self.mock_Formatter.assert_called_once()
        
        # Check console handler was created and configured
        self.mock_StreamHandler.assert_called_once()
        self.mock_stream_handler.setFormatter.assert_called_once_with(self.mock_formatter)
        self.mock_logger.addHandler.assert_any_call(self.mock_stream_handler)
        
        # Check file handler was created and configured
        self.mock_path_exists.assert_called_once_with('logs')
        self.mock_makedirs.assert_called_once_with('logs', exist_ok=True)
        self.mock_FileHandler.assert_called_once()
        self.mock_file_handler.setFormatter.assert_called_once_with(self.mock_formatter)
        self.mock_logger.addHandler.assert_any_call(self.mock_file_handler)
    
    def test_setup_logger_console_only(self):
        """Test setting up logger with console logging only"""
        # Update mock settings
        self.settings_patcher.stop()
        self.settings_patcher = patch('src.utils.logger.LOGGING_CONFIG', {
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'log_dir': 'logs',
            'log_file': 'sentiment_analysis.log',
            'max_size_mb': 10,
            'backup_count': 5,
            'console_logging': True,
            'file_logging': False
        })
        self.mock_settings = self.settings_patcher.start()
        
        # Call setup_logger
        logger = setup_logger()
        
        # Check logger was configured correctly
        self.mock_getLogger.assert_called_once()
        self.mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
        
        # Check console handler was created
        self.mock_StreamHandler.assert_called_once()
        self.mock_logger.addHandler.assert_called_once_with(self.mock_stream_handler)
        
        # Check file handler was not created
        self.mock_FileHandler.assert_not_called()
    
    def test_setup_logger_file_only(self):
        """Test setting up logger with file logging only"""
        # Update mock settings
        self.settings_patcher.stop()
        self.settings_patcher = patch('src.utils.logger.LOGGING_CONFIG', {
            'level': 'WARNING',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'log_dir': 'logs',
            'log_file': 'sentiment_analysis.log',
            'max_size_mb': 10,
            'backup_count': 5,
            'console_logging': False,
            'file_logging': True
        })
        self.mock_settings = self.settings_patcher.start()
        
        # Call setup_logger
        logger = setup_logger()
        
        # Check logger was configured correctly
        self.mock_getLogger.assert_called_once()
        self.mock_logger.setLevel.assert_called_once_with(logging.WARNING)
        
        # Check console handler was not created
        self.mock_StreamHandler.assert_not_called()
        
        # Check file handler was created
        self.mock_FileHandler.assert_called_once()
        self.mock_logger.addHandler.assert_called_once_with(self.mock_file_handler)
    
    def test_setup_logger_custom_name(self):
        """Test setting up logger with custom name"""
        # Call setup_logger with custom name
        logger = setup_logger("custom_logger")
        
        # Check logger was created with custom name
        self.mock_getLogger.assert_called_once_with("custom_logger")
    
    def test_setup_logger_custom_level(self):
        """Test setting up logger with custom level"""
        # Call setup_logger with custom level
        logger = setup_logger(level=logging.ERROR)
        
        # Check logger was configured with custom level
        self.mock_logger.setLevel.assert_called_once_with(logging.ERROR)

if __name__ == '__main__':
    unittest.main()