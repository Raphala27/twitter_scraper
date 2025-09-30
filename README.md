# 🚀 Twitter Scraper API with Clean Architecture

A production-ready Twitter sentiment analysis API using OpenRouter AI models and CoinGecko price validation.

## 🏗️ Architecture

This project follows clean architecture principles with clear separation of concerns:

```
src/
├── api/              # API layer (Flask endpoints, response formatting)
├── core/             # Business logic (crypto analysis)
├── services/         # External services (OpenRouter, CoinGecko)
├── models/           # Data models and structures
└── utils/            # Configuration and validation utilities
```

## ⚡ Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

## 🌐 API Endpoints

### Main Endpoint: `/api/bot/analyze`

**Request:**
```json
{
  "tweet_id": "1234567890",
  "author_handle": "@username",
  "tweet_content": "Bitcoin to the moon! 🚀",
  "timestamp": "2025-09-27T12:00:00Z",
  "user_response": "What do you think?"
}
```

**Response:**
```json
{
  "status": "success",
  "response_text": "🎯 THE DEAL: @username predicts BTC moonshot...",
  "confidence_score": 85.0,
  "analysis_type": "crypto_sentiment"
}
```

### Other Endpoints

- `GET /` - API documentation
- `GET /health` - Health check
- `GET /api/models` - Available AI models

## 🔧 Configuration

Environment variables:

- `OPENROUTER_API_KEY` - Required: OpenRouter API key
- `COINGECKO_API_KEY` - Optional: CoinGecko API key for price validation
- `DEFAULT_AI_MODEL` - Default: "x-ai/grok-4-fast:free"
- `PORT` - Default: 5000
- `FLASK_DEBUG` - Default: False

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/
```

Run quick analysis test:
```bash
python quick_analysis.py
```

## 🚀 Deployment

The application is ready for deployment on platforms like Render, Heroku, or any cloud provider:

1. **Procfile** is configured for gunicorn
2. **requirements.txt** includes all dependencies
3. **Environment variables** are properly configured

## 📊 Features

- **Clean Architecture**: Modular, testable, maintainable code
- **AI-Powered Analysis**: OpenRouter integration with multiple models
- **Price Validation**: Real-time crypto price validation via CoinGecko
- **Twitter-Ready**: Responses optimized for Twitter's 280 character limit
- **Error Handling**: Robust error handling and fallbacks
- **Unicode Support**: Proper emoji and Unicode handling
- **Logging**: Structured logging for debugging and monitoring

## 🔄 Migration from Legacy

Legacy files are preserved with `_legacy` suffix:
- `app_legacy.py` - Original Flask application
- `quick_analysis_legacy.py` - Original analysis function

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing architecture patterns
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.
