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
            return jsonify({
                "status": "error",
                "response_text": "No data provided",
                "confidence_score": 0.0,
                "analysis_type": "error"
            }), 400
        
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
        
        # UTILISER DIRECTEMENT VOS MODULES D'ANALYSE
        from models_logic.openrouter_logic import generate_with_openrouter
        from coingecko_api.sentiment_validator import SentimentValidator
        
        # Préparer le contenu à analyser
        content_to_analyze = f"""
        Tweet from {author_handle}: {tweet_content}
        
        User question: {user_response}
        
        Please provide a crypto sentiment analysis focusing on any cryptocurrencies mentioned.
        """
        
        # Utiliser votre système d'analyse directement
        ai_analysis = generate_with_openrouter(
            model='mistralai/mistral-small-3.2-24b-instruct:free',
            prompt=content_to_analyze
        )
        
        # Récupérer l'analyse du modèle
        confidence_score = 75.0
        
        if ai_analysis:
            # Pour l'instant, formatons directement l'analyse sans validation complexe
            # Vous pourrez ajouter la validation CoinGecko plus tard si nécessaire
            
            # Formatter la réponse directement avec l'analyse IA
            response_text = f"🔍 Crypto Analysis:\n{ai_analysis[:200]}"
            
            # Détecter le sentiment basé sur des mots-clés
            ai_lower = ai_analysis.lower()
            if any(word in ai_lower for word in ['bullish', 'buy', 'pump', 'moon', 'rise', 'up']):
                response_text += "\n📈 Bullish sentiment detected"
                confidence_score = 80.0
            elif any(word in ai_lower for word in ['bearish', 'sell', 'dump', 'crash', 'fall', 'down']):
                response_text += "\n📉 Bearish sentiment detected"
                confidence_score = 80.0
            else:
                response_text += "\n➡️ Neutral sentiment"
                confidence_score = 70.0
                
        else:
            response_text = "Unable to complete analysis at this time"
            confidence_score = 0.0
        
        # Limiter à 280 caractères pour Twitter
        if len(response_text) > 280:
            response_text = response_text[:277] + "..."
        
        # Format de réponse exact demandé
        return jsonify({
            "status": "success",
            "response_text": response_text,
            "confidence_score": confidence_score,
            "analysis_type": "crypto_sentiment"
        })
        
    except Exception as e:
        logger.error(f"Error in bot_analyze: {str(e)}")
        return jsonify({
            "status": "error",
            "response_text": f"Analysis failed: {str(e)[:100]}...",
            "confidence_score": 0.0,
            "analysis_type": "error"
        }), 500

@app.route('/api/models')
def get_models():
    """Get available models."""
    models = [
        "mistralai/mistral-small-3.2-24b-instruct:free",
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
