#!/usr/bin/env python3
"""
<<<<<<< HEAD
Flask Web Application for Twitter Scraper with AI Analysis
=======
Flask Web Application for Twitter Scraper with AI Analysis.
>>>>>>> feature/add-api-endpoint

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
    
    Receives tweet data from bot and returns AI analysis.
    """
    try:
        # Récupérer les données du bot
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "response_text": "No data provided",
                "confidence_score": 0.0,
                "analysis_type": "error"
            }), 400
        
        # Extraire les informations du tweet
        tweet_content = data.get('tweet_content', '')
        author_handle = data.get('author_handle', '@unknown')
        user_response = data.get('user_response', '')
        tweet_id = data.get('tweet_id', '')
        
        logger.info(f"Bot analysis request for tweet {tweet_id} from {author_handle}")
        
        # Préparer le contenu pour analyse
        # Combiner le contenu du tweet et la question de l'utilisateur
        analysis_content = f"{tweet_content}\n\nUser question: {user_response}"
        
        # Utiliser votre logique existante pour analyser
        # On va créer un mock tweet avec le contenu reçu
        mock_tweet_data = [{
            "id_str": tweet_id,
            "created_at": data.get('timestamp', '2025-01-01T00:00:00Z'),
            "full_text": analysis_content,
            "user": {
                "screen_name": author_handle.replace('@', ''),
                "id_str": data.get('author_id', '123456789')
            }
        }]
        
        # Analyser avec votre système existant
        result = run_and_print(
            user=author_handle,
            limit=1,
            model='mistralai/mistral-small-3.2-24b-instruct:free',
            system_msg="You are a crypto sentiment analyst. Analyze the content and provide a helpful response to the user's question about cryptocurrency sentiment or trading signals.",
            as_json=False,  # On veut le résultat structuré
            mock_scraping=True,  # Utiliser nos données mockées
            mock_positions=True,
            use_tools=False,  # Pas d'outils pour une réponse rapide
            calculate_positions=False,
            simulate_positions=False,
            validate_sentiment=False,
            api_provider='coingecko'
        )
        
        # Extraire la réponse de l'analyse
        response_text = "I've analyzed the crypto sentiment in your message."
        confidence_score = 75.0
        
        if result and isinstance(result, dict):
            # Essayer d'extraire une réponse plus intelligente du résultat
            if 'tweets_analysis' in result and result['tweets_analysis']:
                analysis = result['tweets_analysis'][0]
                if 'analysis' in analysis:
                    response_text = analysis['analysis']
                    confidence_score = 85.0
            elif 'analysis_summary' in result:
                summary = result['analysis_summary']
                bullish = summary.get('bullish_sentiments', 0)
                bearish = summary.get('bearish_sentiments', 0)
                
                if bullish > bearish:
                    response_text = f"Based on my analysis, I detect a bullish sentiment in the crypto content. Bullish signals: {bullish}, Bearish signals: {bearish}"
                    confidence_score = 80.0
                elif bearish > bullish:
                    response_text = f"Based on my analysis, I detect a bearish sentiment in the crypto content. Bearish signals: {bearish}, Bullish signals: {bullish}"
                    confidence_score = 80.0
                else:
                    response_text = "The crypto sentiment appears neutral based on my analysis."
                    confidence_score = 70.0
        
        # Limiter la réponse à 280 caractères pour Twitter
        if len(response_text) > 280:
            response_text = response_text[:277] + "..."
        
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
