import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
import main

class TestMain(unittest.TestCase):
    """Test cases for main.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock uvicorn
        self.uvicorn_patcher = patch('main.uvicorn')
        self.mock_uvicorn = self.uvicorn_patcher.start()
        
        # Mock API app
        self.api_app_patcher = patch('main.api_app')
        self.mock_api_app = self.api_app_patcher.start()
        
        # Mock Web app
        self.web_app_patcher = patch('main.web_app')
        self.mock_web_app = self.web_app_patcher.start()
        
        # Mock threading
        self.threading_patcher = patch('main.threading.Thread')
        self.mock_thread = self.threading_patcher.start()
        
        # Mock logger
        self.logger_patcher = patch('main.logger')
        self.mock_logger = self.logger_patcher.start()
        
        # Mock settings
        self.settings_patcher = patch('main.settings', {
            'api': {
                'host': 'localhost',
                'port': 8000,
                'reload': True
            },
            'web': {
                'host': 'localhost',
                'port': 8080,
                'reload': True
            }
        })
        self.mock_settings = self.settings_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.uvicorn_patcher.stop()
        self.api_app_patcher.stop()
        self.web_app_patcher.stop()
        self.threading_patcher.stop()
        self.logger_patcher.stop()
        self.settings_patcher.stop()
    
    def test_start_api_server(self):
        """Test starting API server"""
        # Call function
        main.start_api_server()
        
        # Check uvicorn.run was called with correct parameters
        self.mock_uvicorn.run.assert_called_once_with(
            self.mock_api_app,
            host='localhost',
            port=8000,
            reload=True
        )
    
    def test_start_web_server(self):
        """Test starting Web server"""
        # Call function
        main.start_web_server()
        
        # Check uvicorn.run was called with correct parameters
        self.mock_uvicorn.run.assert_called_once_with(
            self.mock_web_app,
            host='localhost',
            port=8080,
            reload=True
        )
    
    @patch('main.argparse.ArgumentParser')
    def test_main_api_only(self, mock_arg_parser):
        """Test main function with API only"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.api_only = True
        mock_args.web_only = False
        mock_arg_parser.return_value.parse_args.return_value = mock_args
        
        # Call main
        main.main()
        
        # Check API server was started
        self.mock_uvicorn.run.assert_called_once()
        
        # Check thread was not created
        self.mock_thread.assert_not_called()
    
    @patch('main.argparse.ArgumentParser')
    def test_main_web_only(self, mock_arg_parser):
        """Test main function with Web only"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.api_only = False
        mock_args.web_only = True
        mock_arg_parser.return_value.parse_args.return_value = mock_args
        
        # Call main
        main.main()
        
        # Check Web server was started
        self.mock_uvicorn.run.assert_called_once()
        
        # Check thread was not created
        self.mock_thread.assert_not_called()
    
    @patch('main.argparse.ArgumentParser')
    def test_main_both_servers(self, mock_arg_parser):
        """Test main function with both servers"""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.api_only = False
        mock_args.web_only = False
        mock_arg_parser.return_value.parse_args.return_value = mock_args
        
        # Call main
        main.main()
        
        # Check thread was created for API server
        self.mock_thread.assert_called_once()
        self.mock_thread.return_value.start.assert_called_once()
        
        # Check Web server was started directly
        self.mock_uvicorn.run.assert_called_once()

if __name__ == '__main__':
    unittest.main()