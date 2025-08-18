import logging
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import WEB_CONFIG
from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

def create_app():
    """Create FastAPI app for serving the web interface
    
    Returns:
        FastAPI app
    """
    app = FastAPI(title="Sentiment Analysis Web Interface")
    
    # Get frontend build directory
    frontend_dir = Path(__file__).parent / "frontend" / "build"
    
    # Check if frontend build directory exists
    if not frontend_dir.exists():
        logger.warning(f"Frontend build directory not found at {frontend_dir}")
        logger.info("Please build the frontend with 'npm run build' in the frontend directory")
    else:
        # Mount static files
        app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")
        
        # Serve index.html for all other routes
        @app.get("/{full_path:path}")
        async def serve_frontend(request: Request, full_path: str):
            # Check if file exists
            file_path = frontend_dir / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            
            # Otherwise serve index.html
            return FileResponse(str(frontend_dir / "index.html"))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint
        
        Returns:
            Health status
        """
        return {"status": "healthy"}
    
    return app

def start_server():
    """Start the web server"""
    import uvicorn
    
    # Create app
    app = create_app()
    
    # Start server
    uvicorn.run(
        app,
        host=WEB_CONFIG.get("host", "0.0.0.0"),
        port=WEB_CONFIG.get("port", 3000),
        log_level=WEB_CONFIG.get("log_level", "info").lower()
    )

if __name__ == "__main__":
    start_server()