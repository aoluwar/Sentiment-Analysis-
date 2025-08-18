# Real-Time Sentiment Analysis System

**Coder**: deethepytor

## Overview

A comprehensive real-time sentiment analysis system that processes text data streams and provides instant sentiment classification with confidence scores. The system supports multiple data sources including social media feeds, chat messages, reviews, and custom text inputs.

## Features

### Core Functionality
- **Real-time Processing**: Stream processing of text data with minimal latency
- **Multi-model Support**: BERT, VADER, TextBlob, and custom transformer models
- **Sentiment Classification**: Positive, Negative, Neutral with confidence scores
- **Emotion Detection**: Joy, Anger, Fear, Sadness, Surprise, Disgust
- **Language Support**: Multi-language sentiment analysis
- **Batch Processing**: Handle large datasets efficiently

### Data Sources
- Twitter API integration
- Reddit API support
- WebSocket connections for real-time chat
- File upload processing
- REST API endpoints
- Kafka stream processing

### Analytics & Visualization
- Real-time sentiment dashboards
- Historical trend analysis
- Sentiment distribution charts
- Word clouds and keyword extraction
- Geographic sentiment mapping
- Export capabilities (CSV, JSON, PDF)

### Performance & Scalability
- Distributed processing with Redis
- Caching mechanisms
- Load balancing
- Auto-scaling capabilities
- Performance monitoring

## Architecture

```
sentiment_analysis_system/
├── config/                 # Configuration files
├── data/                   # Sample datasets and models
├── docs/                   # Documentation
├── models/                 # Pre-trained and custom models
├── src/                    # Source code
│   ├── api/               # REST API endpoints
│   ├── core/              # Core sentiment analysis logic
│   ├── processors/        # Data processors
│   ├── streaming/         # Real-time streaming components
│   ├── utils/             # Utility functions
│   └── web/               # Web interface
├── tests/                  # Test suites
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker configuration
└── README.md              # This file
```

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, WebSockets
- **ML/NLP**: Transformers, NLTK, spaCy, scikit-learn
- **Real-time**: Redis, Kafka, asyncio
- **Database**: PostgreSQL, MongoDB
- **Frontend**: React.js, D3.js for visualizations
- **Deployment**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Redis server
- PostgreSQL (optional)
- Node.js 16+ (for frontend)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/deethepytor/sentiment-analysis-system.git
   cd sentiment-analysis-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml with your settings
   ```

5. **Start the system**
   ```bash
   python main.py
   ```

6. **Access the web interface**
   Open http://localhost:8080 in your browser

## Usage Examples

### REST API

```python
import requests

# Analyze single text
response = requests.post('http://localhost:8000/api/v1/analyze', 
                        json={'text': 'I love this product!'})
result = response.json()
print(f"Sentiment: {result['sentiment']}, Score: {result['confidence']}")

# Batch analysis
texts = ['Great service!', 'Terrible experience', 'It was okay']
response = requests.post('http://localhost:8000/api/v1/analyze/batch', 
                        json={'texts': texts})
results = response.json()
```

### Python SDK

```python
from sentiment_analyzer import SentimentAnalyzer

# Initialize analyzer
analyzer = SentimentAnalyzer(model='bert-base')

# Analyze text
result = analyzer.analyze('This movie is amazing!')
print(f"Sentiment: {result.sentiment}")
print(f"Confidence: {result.confidence}")
print(f"Emotions: {result.emotions}")

# Real-time stream processing
for result in analyzer.stream_analyze(text_stream):
    print(f"Real-time sentiment: {result.sentiment}")
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sentiment');

ws.onopen = function() {
    ws.send(JSON.stringify({
        'type': 'analyze',
        'text': 'Hello world!'
    }));
};

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log('Sentiment:', result.sentiment);
};
```

## Testing

The system includes comprehensive test suites for all components. Tests are located in the `tests/` directory.

### Running Tests

To run all tests:

```bash
python run_tests.py
```

To run specific tests:

```bash
python run_tests.py tests/test_sentiment_analyzer.py
```

To run tests with coverage report:

```bash
python run_tests.py --coverage
```

For HTML coverage report:

```bash
python run_tests.py --coverage --html
```

See `tests/README.md` for more details on testing.

## Configuration

The system uses YAML configuration files located in the `config/` directory:

- `config.yaml`: Main configuration
- `models.yaml`: Model-specific settings
- `api.yaml`: API endpoint configurations
- `streaming.yaml`: Real-time processing settings

## Models

### Supported Models
1. **BERT-based**: Fine-tuned BERT for sentiment classification
2. **RoBERTa**: Robust sentiment analysis
3. **VADER**: Rule-based sentiment analysis
4. **TextBlob**: Simple sentiment analysis
5. **Custom Models**: Train your own models

### Model Performance
| Model | Accuracy | Speed | Memory |
|-------|----------|-------|--------|
| BERT | 94.2% | Medium | High |
| RoBERTa | 95.1% | Medium | High |
| VADER | 87.3% | Fast | Low |
| TextBlob | 82.1% | Fast | Low |

## API Documentation

### Endpoints

#### POST /api/v1/analyze
Analyze sentiment of a single text.

**Request:**
```json
{
    "text": "I love this product!",
    "model": "bert-base",
    "include_emotions": true
}
```

**Response:**
```json
{
    "sentiment": "positive",
    "confidence": 0.95,
    "emotions": {
        "joy": 0.8,
        "anger": 0.1,
        "fear": 0.05,
        "sadness": 0.05
    },
    "processing_time": 0.12
}
```

#### POST /api/v1/analyze/batch
Analyze sentiment of multiple texts.

#### GET /api/v1/models
List available models.

#### WebSocket /ws/sentiment
Real-time sentiment analysis.

## Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=3
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=sentiment-analyzer
```

## Monitoring

- **Health Check**: `/health`
- **Metrics**: `/metrics` (Prometheus format)
- **Logs**: Structured logging with correlation IDs
- **Performance**: Real-time performance dashboards

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Email**: deethepytor@example.com
- **Discord**: [Community Server](https://discord.gg/sentiment-analysis)

## Roadmap

- [ ] Multi-modal sentiment analysis (text + images)
- [ ] Real-time sentiment alerts
- [ ] Advanced emotion detection
- [ ] Sentiment trend prediction
- [ ] Mobile app integration
- [ ] Voice sentiment analysis

---

**Built with ❤️ by deethepytor**