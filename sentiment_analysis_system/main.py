
"""
Main entry point for the Sentiment Analysis System

This script initializes and starts all components of the system.
"""

import argparse
import logging
import os
import sys
import time
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from config.settings import API_CONFIG, WEB_CONFIG
from src.api import create_app as create_api_app
from src.web import create_app as create_web_app
from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger("main")

def start_api_server():
    """Start the API server"""
    import uvicorn
    
    logger.info("Starting API server...")
    
    # Create API app
    app = create_api_app()
    
    # Start server
    uvicorn.run(
        app,
        host=API_CONFIG.get("host", "0.0.0.0"),
        port=API_CONFIG.get("port", 8000),
        log_level=API_CONFIG.get("log_level", "info").lower()
    )

def start_web_server():
    """Start the web server"""
    import uvicorn
    
    logger.info("Starting web server...")
    
    # Create web app
    app = create_web_app()
    
    # Start server
    uvicorn.run(
        app,
        host=WEB_CONFIG.get("host", "0.0.0.0"),
        port=WEB_CONFIG.get("port", 3000),
        log_level=WEB_CONFIG.get("log_level", "info").lower()
    )

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Sentiment Analysis System")
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Start only the API server"
    )
    parser.add_argument(
        "--web-only",
        action="store_true",
        help="Start only the web server"
    )
    args = parser.parse_args()
    
    # Start servers based on arguments
    if args.api_only:
        start_api_server()
    elif args.web_only:
        start_web_server()
    else:
        # Start both servers in separate threads
        api_thread = threading.Thread(target=start_api_server)
        web_thread = threading.Thread(target=start_web_server)
        
        api_thread.daemon = True
        web_thread.daemon = True
        
        api_thread.start()
        web_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sys.exit(0)

if __name__ == "__main__":
    main()
