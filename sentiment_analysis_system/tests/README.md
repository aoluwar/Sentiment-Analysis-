# Sentiment Analysis System Tests

This directory contains unit tests for the Sentiment Analysis System. The tests are organized by component and use Python's built-in `unittest` framework.

## Test Structure

The tests are organized as follows:

- `test_sentiment_analyzer.py`: Tests for the sentiment analysis functionality
- `test_emotion_detector.py`: Tests for the emotion detection functionality
- `test_text_processor.py`: Tests for the text processing functionality
- `test_stream_manager.py`: Tests for the streaming functionality
- `test_db_manager.py`: Tests for the database management functionality
- `test_cache_manager.py`: Tests for the caching functionality
- `test_api.py`: Tests for the API endpoints
- `test_web_server.py`: Tests for the web server
- `test_main.py`: Tests for the main application entry point
- `test_logger.py`: Tests for the logging utility

## Running Tests

### Running All Tests

To run all tests, navigate to the project root directory and run:

```bash
python -m unittest discover tests
```

### Running Specific Tests

To run a specific test file, use:

```bash
python -m unittest tests/test_sentiment_analyzer.py
```

To run a specific test case or method, use:

```bash
python -m unittest tests.test_sentiment_analyzer.TestSentimentAnalyzer
python -m unittest tests.test_sentiment_analyzer.TestSentimentAnalyzer.test_analyze_text_vader
```

## Test Dependencies

The tests require the following dependencies:

- `unittest`: Python's built-in testing framework
- `unittest.mock`: For mocking dependencies
- `fastapi.testclient`: For testing FastAPI endpoints

Most of these are included with Python or will be installed with the project requirements.

## Writing New Tests

When adding new functionality to the system, please also add corresponding tests. Follow these guidelines:

1. Create a new test file if testing a new component, or add to an existing file if extending functionality
2. Use descriptive test method names that explain what is being tested
3. Include docstrings for test classes and methods
4. Use setUp and tearDown methods for common test fixtures
5. Mock external dependencies to isolate the component being tested
6. Test both success and failure cases

## Test Coverage

To check test coverage, install the `coverage` package and run:

```bash
coverage run -m unittest discover tests
coverage report
```

For a more detailed HTML report:

```bash
coverage html
```

Then open `htmlcov/index.html` in a web browser.