from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from config.settings import API_HOST, API_PORT, API_DEBUG
from src.core.sentiment_analyzer import SentimentAnalyzer
from src.core.emotion_detector import EmotionDetector
from src.processors.text_processor import TextProcessor
from src.streaming.stream_manager import StreamManager
from src.utils.db_manager import DatabaseManager
from src.utils.cache_manager import CacheManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/api.log"),
    ],
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Sentiment Analysis API",
    description="API for real-time sentiment analysis of text data",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sentiment_analyzer = SentimentAnalyzer()
emotion_detector = EmotionDetector()
text_processor = TextProcessor()
stream_manager = StreamManager()
db_manager = DatabaseManager()
cache_manager = CacheManager()

# Create required directories
os.makedirs("logs", exist_ok=True)

# Pydantic models for request/response
class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")
    language: Optional[str] = Field("en", description="Language code (ISO 639-1)")
    
class BatchTextInput(BaseModel):
    texts: List[TextInput] = Field(..., min_items=1, max_items=100)
    
class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    emotions: Dict[str, float] = None
    language: str
    processed_text: str = None
    
class BatchSentimentResponse(BaseModel):
    results: List[SentimentResponse]
    count: int
    processing_time: float

class StreamConfig(BaseModel):
    source: str = Field(..., description="Data source (twitter, reddit, custom)")
    query: str = Field(..., description="Search query or filter")
    duration: Optional[int] = Field(60, description="Stream duration in seconds")

# API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the Real-Time Sentiment Analysis API"}

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_text(text_input: TextInput):
    try:
        # Process text
        processed_text = text_processor.process(text_input.text, text_input.language)
        
        # Check cache
        cached_result = cache_manager.get(processed_text)
        if cached_result:
            logger.info(f"Cache hit for text: {text_input.text[:50]}...")
            return cached_result
        
        # Analyze sentiment
        sentiment_result = sentiment_analyzer.analyze(processed_text, text_input.language)
        
        # Detect emotions
        emotions = emotion_detector.detect(processed_text, text_input.language)
        
        # Create response
        response = SentimentResponse(
            text=text_input.text,
            sentiment=sentiment_result["sentiment"],
            confidence=sentiment_result["confidence"],
            emotions=emotions,
            language=text_input.language,
            processed_text=processed_text
        )
        
        # Cache result
        cache_manager.set(processed_text, response)
        
        # Store in database
        db_manager.store_analysis(response)
        
        return response
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/batch", response_model=BatchSentimentResponse)
async def analyze_batch(batch_input: BatchTextInput, background_tasks: BackgroundTasks):
    try:
        import time
        start_time = time.time()
        
        results = []
        for text_input in batch_input.texts:
            result = await analyze_text(text_input)
            results.append(result)
        
        # Store batch results in background
        background_tasks.add_task(db_manager.store_batch_analysis, results)
        
        processing_time = time.time() - start_time
        
        return BatchSentimentResponse(
            results=results,
            count=len(results),
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error analyzing batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream/start")
async def start_stream(config: StreamConfig, background_tasks: BackgroundTasks):
    try:
        stream_id = stream_manager.start_stream(config.source, config.query, config.duration)
        background_tasks.add_task(stream_manager.process_stream, stream_id, sentiment_analyzer, text_processor)
        return {"stream_id": stream_id, "status": "started"}
    except Exception as e:
        logger.error(f"Error starting stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/{stream_id}/status")
async def get_stream_status(stream_id: str):
    try:
        status = stream_manager.get_stream_status(stream_id)
        return status
    except Exception as e:
        logger.error(f"Error getting stream status: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found")

@app.post("/stream/{stream_id}/stop")
async def stop_stream(stream_id: str):
    try:
        stream_manager.stop_stream(stream_id)
        return {"stream_id": stream_id, "status": "stopped"}
    except Exception as e:
        logger.error(f"Error stopping stream: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Stream {stream_id} not found")

# WebSocket endpoint for real-time analysis
@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Parse input
                input_data = json.loads(data)
                text = input_data.get("text", "")
                language = input_data.get("language", "en")
                
                if not text:
                    await websocket.send_json({"error": "Text is required"})
                    continue
                
                # Create text input
                text_input = TextInput(text=text, language=language)
                
                # Analyze
                result = await analyze_text(text_input)
                
                # Send result
                await websocket.send_json(result.dict())
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "components": {
            "sentiment_analyzer": sentiment_analyzer.health_check(),
            "emotion_detector": emotion_detector.health_check(),
            "text_processor": text_processor.health_check(),
            "stream_manager": stream_manager.health_check(),
            "db_manager": db_manager.health_check(),
            "cache_manager": cache_manager.health_check(),
        }
    }

# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=API_DEBUG)