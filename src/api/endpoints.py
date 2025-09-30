"""
Flask API endpoints with clean separation of concerns
"""

from flask import Blueprint, request
from src.core.crypto_analyzer import CryptoAnalyzer
from src.api.response_formatter import ResponseFormatter
from src.utils.validators import RequestValidator
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)


class BotAnalysisEndpoint:
    """Handler for bot analysis endpoint"""
    
    def __init__(self, crypto_analyzer: CryptoAnalyzer):
        """
        Initialize endpoint handler
        
        Args:
            crypto_analyzer: Configured crypto analyzer instance
        """
        self.analyzer = crypto_analyzer
        self.formatter = ResponseFormatter()
        self.validator = RequestValidator()
    
    def analyze(self):
        """
        POST /api/bot/analyze endpoint handler
        
        Returns:
            Flask Response with analysis results
        """
        try:
            # 1. Get and validate request data
            request_data = request.get_json()
            validated_data = self.validator.validate_bot_request(request_data)
            
            logger.info(f"Bot analysis request for tweet {validated_data.get('tweet_id')} from {validated_data.get('author_handle')}")
            
            # 2. Combine tweet content with user response
            tweet_content = validated_data['tweet_content']
            user_response = validated_data.get('user_response', '')
            
            if user_response:
                full_content = f"{tweet_content}\n\nUser question: {user_response}"
            else:
                full_content = tweet_content
            
            # 3. Perform analysis
            result = self.analyzer.analyze_tweet(
                tweet_content=full_content,
                author=validated_data['author_handle'],
                timestamp=validated_data['timestamp'],
                tweet_id=validated_data['tweet_id']
            )
            
            # 4. Apply length limit for Twitter
            if len(result.response_text) > 280:
                result.response_text = result.response_text[:277] + "..."
            
            # 5. Format and return response
            return self.formatter.format_response(result)
            
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return self.formatter.format_error(str(e), 400)
        except Exception as e:
            logger.error(f"Unexpected error in bot_analyze: {e}", exc_info=True)
            return self.formatter.format_error("Internal server error", 500)


# Global endpoint handler (will be initialized in app factory)
_bot_endpoint_handler = None


def init_endpoints(crypto_analyzer: CryptoAnalyzer):
    """
    Initialize endpoint handlers with dependencies
    
    Args:
        crypto_analyzer: Configured crypto analyzer instance
    """
    global _bot_endpoint_handler
    _bot_endpoint_handler = BotAnalysisEndpoint(crypto_analyzer)


@api_bp.route('/api/bot/analyze', methods=['POST'])
def bot_analyze():
    """POST /api/bot/analyze - Main endpoint for Twitter bot integration"""
    if _bot_endpoint_handler is None:
        return ResponseFormatter.format_error("Service not initialized", 500)
    
    return _bot_endpoint_handler.analyze()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """GET /health - Health check endpoint"""
    from flask import jsonify
    return jsonify({"status": "healthy", "service": "twitter_scraper"})


@api_bp.route('/', methods=['GET'])
def api_documentation():
    """GET / - API documentation"""
    from flask import jsonify
    return jsonify({
        "service": "Twitter Scraper API Backend",
        "version": "2.0.0",
        "endpoints": {
            "/health": "Health check",
            "/api/bot/analyze": "POST - Main endpoint for Twitter bot",
            "/api/models": "GET - Available models"
        },
        "main_endpoint": {
            "url": "/api/bot/analyze",
            "method": "POST",
            "description": "Main endpoint for Twitter bot integration",
            "request_format": {
                "tweet_id": "string",
                "author_handle": "@username",
                "author_id": "string",
                "tweet_content": "string",
                "timestamp": "ISO datetime",
                "is_reply": "boolean",
                "parent_tweet_id": "string or null",
                "mentioned_bot": "@botname",
                "user_response": "string"
            },
            "response_format": {
                "status": "success/error",
                "response_text": "AI generated analysis",
                "confidence_score": "float 0-100",
                "analysis_type": "crypto_sentiment"
            }
        }
    })


@api_bp.route('/api/models', methods=['GET'])
def get_models():
    """GET /api/models - Get available AI models"""
    from flask import jsonify
    models = [
        "x-ai/grok-4-fast:free",
        "mistralai/mistral-small-3.2-24b-instruct:free",
        "microsoft/wizardlm-2-8x22b",
        "anthropic/claude-3-haiku",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3-8b-instruct:free"
    ]
    return jsonify({"models": models})
