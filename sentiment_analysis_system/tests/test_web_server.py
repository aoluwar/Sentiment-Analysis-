import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.web.server import create_app

class TestWebServer(unittest.TestCase):
    """Test cases for Web Server"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the static files directory
        self.static_dir_patcher = patch('src.web.server.STATIC_DIR', './mock_static')
        self.static_dir_patcher.start()
        
        # Create a temporary directory for static files
        os.makedirs('./mock_static', exist_ok=True)
        with open('./mock_static/index.html', 'w') as f:
            f.write('<html><body>Test Frontend</body></html>')
        
        # Create app and test client
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.static_dir_patcher.stop()
        
        # Clean up temporary directory
        if os.path.exists('./mock_static/index.html'):
            os.remove('./mock_static/index.html')
        if os.path.exists('./mock_static'):
            os.rmdir('./mock_static')
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        # Make request
        response = self.client.get("/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], "healthy")
    
    def test_serve_index_html(self):
        """Test serving index.html for various routes"""
        # Test root path
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Frontend", response.text)
        
        # Test other paths that should serve index.html
        paths = ["/dashboard", "/analysis", "/streaming", "/nonexistent"]
        for path in paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Test Frontend", response.text)

if __name__ == '__main__':
    unittest.main()