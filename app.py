#!/usr/bin/env python3
"""
Flask Web Application for Twitter Scraper with AI Analysis

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
    """Main page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "twitter_scraper"})

@app.route('/api/analyze', methods=['POST'])
def analyze_tweets():
    """Analyze tweets via API."""
    try:
        data = request.get_json()
        
        # Extract parameters with defaults
        user = data.get('user', '@trader')
        limit = int(data.get('limit', 2))
        model = data.get('model', 'mistralai/mistral-small-3.2-24b-instruct:free')
        system_msg = data.get('system_msg', None)
        mock_scraping = data.get('mock_scraping', True)
        mock_positions = data.get('mock_positions', True)
        use_tools = data.get('use_tools', True)
        simulate_positions = data.get('simulate_positions', False)
        validate_sentiment = data.get('validate_sentiment', False)
        api_provider = data.get('api_provider', 'coincap')
        
        logger.info(f"Analyzing tweets for user: {user}")
        
        # Run analysis
        result = run_and_print(
            user=user,
            limit=limit,
            model=model,
            system_msg=system_msg,
            as_json=True,
            mock_scraping=mock_scraping,
            mock_positions=mock_positions,
            use_tools=use_tools,
            simulate_positions=simulate_positions,
            validate_sentiment=validate_sentiment,
            api_provider=api_provider
        )
        
        if result:
            return jsonify({
                "status": "success",
                "data": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No results returned"
            }), 400
            
    except Exception as e:
        logger.error(f"Error in analyze_tweets: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/analyze/simple', methods=['GET'])
def analyze_simple():
    """Simple GET endpoint for quick testing."""
    try:
        user = request.args.get('user', '@trader')
        limit = int(request.args.get('limit', 2))
        
        logger.info(f"Simple analysis for user: {user}")
        
        # Run in mock mode for safety
        result = run_and_print(
            user=user,
            limit=limit,
            model='mistralai/mistral-small-3.2-24b-instruct:free',
            system_msg=None,
            as_json=True,
            mock_scraping=True,
            mock_positions=True,
            use_tools=True,
            simulate_positions=False,
            validate_sentiment=False
        )
        
        return jsonify({
            "status": "success",
            "data": result,
            "params": {
                "user": user,
                "limit": limit,
                "mode": "mock"
            }
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_simple: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
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

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create static directory if it doesn't exist  
if not os.path.exists('static'):
    os.makedirs('static')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Twitter Scraper API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
