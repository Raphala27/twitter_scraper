#!/usr/bin/env python3
"""
Flask Web Application for Twitter Scraper with AI Analysis.

Web interface for the Twitter Scraper with AI Analysis tool.
Provides REST API endpoints and a simple web interface.
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the main scraper functionality
try:
    from scraper import run_and_print, load_env_file
except ImportError:
    logger.error("Could not import scraper module")
    raise

app = Flask(__name__)
CORS(app)

# Configure Flask to preserve JSON order and handle Unicode properly
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

# Load environment variables
load_env_file()

@app.route('/')
def index():
    """API Documentation."""
    return jsonify({
        "service": "Twitter Scraper API Backend",
        "version": "2.0.0",
        "endpoints": {
            "/health": "Health check",
            "/api/bot/analyze": "POST - Main endpoint for Twitter bot",
            "/api/scraper": "GET - CLI equivalent endpoint",
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

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "twitter_scraper"})

@app.route('/api/bot/analyze', methods=['POST'])
def bot_analyze():
    """
    Main endpoint for Twitter bot integration.
    
    Receives tweet data and returns AI analysis using direct model + CoinGecko API.
    """
    try:
        # Récupérer les données du bot (format exact demandé)
        data = request.get_json()
        
        if not data:
            error_response = {
                "status": "error",
                "response_text": "No data provided",
                "confidence_score": 0.0,
                "analysis_type": "error"
            }
            return Response(
                json.dumps(error_response, ensure_ascii=False),
                mimetype='application/json'
            ), 400
        
        # Extraire les informations du tweet selon le format demandé
        tweet_id = data.get('tweet_id', '')
        author_handle = data.get('author_handle', '@unknown')
        author_id = data.get('author_id', '')
        tweet_content = data.get('tweet_content', '')
        timestamp = data.get('timestamp', '')
        is_reply = data.get('is_reply', False)
        parent_tweet_id = data.get('parent_tweet_id', None)
        mentioned_bot = data.get('mentioned_bot', '')
        user_response = data.get('user_response', '')
        
        logger.info(f"Bot analysis request for tweet {tweet_id} from {author_handle}")
        logger.info(f"Tweet content: {tweet_content}")
        logger.info(f"User response: {user_response}")
        
        # UTILISER LA NOUVELLE FONCTION quick_crypto_analysis
        from quick_analysis import quick_crypto_analysis
        
        # Combiner le contenu du tweet et la question de l'utilisateur
        full_content = f"{tweet_content}\n\nUser question: {user_response}"
        
        # Appeler la fonction qui fait toute l'analyse (extraction + validation + IA finale)
        ai_analysis = quick_crypto_analysis(
            tweet_content=full_content,
            user=author_handle,
            model='x-ai/grok-4-fast:free',
            tweet_timestamp=timestamp  # Passer le timestamp du tweet pour la validation CoinGecko
        )
        
        # La fonction retourne déjà l'analyse finale formatée
        response_text = ai_analysis
        confidence_score = 85.0  # Score élevé car on utilise validation CoinGecko
        
        # Detect sentiment based on keywords to adjust score
        ai_lower = ai_analysis.lower()
        if "0%" in ai_analysis or "weak" in ai_lower or "no crypto" in ai_lower:
            confidence_score = 25.0
        elif any(word in ai_lower for word in ['excellent', 'good', 'accurate', 'moon', 'nailed']):
            confidence_score = 90.0
        elif any(word in ai_lower for word in ['average', 'moderate', 'cautious', 'mixed']):
            confidence_score = 60.0
        
        # Limit to 280 characters for Twitter (safety net)
        if len(response_text) > 280:
            response_text = response_text[:277] + "..."
        
        # Format de réponse exact demandé
        from flask import Response
        import json
        
        response_data = {
            "status": "success",
            "response_text": response_text,
            "confidence_score": confidence_score,
            "analysis_type": "crypto_sentiment"
        }
        
        return Response(
            json.dumps(response_data, ensure_ascii=False, indent=None),
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error in bot_analyze: {str(e)}")
        error_response = {
            "status": "error",
            "response_text": f"Analysis failed: {str(e)[:100]}...",
            "confidence_score": 0.0,
            "analysis_type": "error"
        }
        return Response(
            json.dumps(error_response, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.route('/api/models')
def get_models():
    """Get available models."""
    models = [
        "x-ai/grok-4-fast:free",
        "microsoft/wizardlm-2-8x22b",
        "anthropic/claude-3-haiku",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3-8b-instruct:free"
    ]
    return jsonify({"models": models})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Twitter Scraper API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
