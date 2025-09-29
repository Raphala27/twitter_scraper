#!/usr/bin/env python3
"""
Flask API Backend for Twitter Scraper with AI Analysis

Pure API backend for the Twitter Scraper with AI Analysis tool.
Provides REST API endpoints only.
"""

import os
import json
from flask import Flask, request, jsonify
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
    """API information."""
    return jsonify({
        "service": "Twitter Scraper AI - API Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/analyze",
            "analyze_simple": "/api/analyze/simple"
        },
        "status": "running"
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "twitter_scraper"})

@app.route('/api/analyze', methods=['POST'])
def analyze_tweets():
    """
    Analyze tweets via API.
    
    Expected JSON payload:
    {
        "user": "@username or user_id",
        "limit": 2,
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "system_msg": "optional system message",
        "mock_scraping": true,
        "mock_positions": true,
        "use_tools": true,
        "simulate_positions": false,
        "validate_sentiment": false,
        "api_provider": "coincap"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
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
        
        logger.info(f"Analyzing tweets for user: {user}, limit: {limit}")
        
        # Run analysis and return structured result
        result = run_and_print(
            user=user,
            limit=limit,
            model=model,
            system_msg=system_msg,
            as_json=False,  # We want the structured result, not JSON output
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
                "message": "No analysis results returned"
            }), 500
            
    except Exception as e:
        logger.error(f"Error in analyze_tweets: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/analyze/simple', methods=['GET'])
def analyze_simple():
    """
    Simple GET endpoint for quick testing.
    
    Query parameters:
    - user: Twitter username (default: @trader)
    - limit: Number of tweets (default: 2)
    - mock_scraping: Use mock data (default: true)
    - mock_positions: Use mock prices (default: true)
    - validate_sentiment: Validate sentiment (default: false)
    - api: API provider (default: coincap)
    - no_tools: Disable tools (default: false)
    
    Example: /api/analyze/simple?user=@test&limit=2&validate_sentiment=true&api=coingecko&no_tools=true
    """
    try:
        user = request.args.get('user', '@trader')
        limit = int(request.args.get('limit', 2))
        mock_scraping = request.args.get('mock_scraping', 'true').lower() == 'true'
        mock_positions = request.args.get('mock_positions', 'true').lower() == 'true'
        validate_sentiment = request.args.get('validate_sentiment', 'false').lower() == 'true'
        api_provider = request.args.get('api', 'coincap')
        no_tools = request.args.get('no_tools', 'false').lower() == 'true'
        
        logger.info(f"Simple analysis for user: {user}, limit: {limit}, validate_sentiment: {validate_sentiment}, api: {api_provider}, no_tools: {no_tools}")
        
        # Run in the same way as your CLI command
        result = run_and_print(
            user=user,
            limit=limit,
            model='mistralai/mistral-small-3.2-24b-instruct:free',
            system_msg=None,
            as_json=False,  # We want the structured result
            mock_scraping=mock_scraping,
            mock_positions=mock_positions,
            use_tools=not no_tools,  # Invert no_tools to get use_tools
            simulate_positions=False,
            validate_sentiment=validate_sentiment,
            api_provider=api_provider
        )
        
        return jsonify({
            "status": "success",
            "data": result,
            "params": {
                "user": user,
                "limit": limit,
                "mock_scraping": mock_scraping,
                "mock_positions": mock_positions,
                "validate_sentiment": validate_sentiment,
                "api_provider": api_provider,
                "no_tools": no_tools
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
    """Get available AI models."""
    models = [
        "mistralai/mistral-small-3.2-24b-instruct:free",
        "microsoft/wizardlm-2-8x22b",
        "anthropic/claude-3-haiku",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3-8b-instruct:free"
    ]
    return jsonify({"models": models})

@app.route('/api/cli', methods=['GET', 'POST'])
def cli_endpoint():
    """
    CLI-compatible endpoint that reproduces your exact command:
    python3 scraper.py @test --limit 2 --mock-scraping --validate-sentiment --api coingecko --no-tools
    
    GET example: /api/cli?user=@test&limit=2&mock-scraping&validate-sentiment&api=coingecko&no-tools
    
    POST example:
    {
        "user": "@test",
        "limit": 2,
        "mock_scraping": true,
        "validate_sentiment": true,
        "api": "coingecko", 
        "no_tools": true
    }
    """
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            user = data.get('user', '@test')
            limit = int(data.get('limit', 2))
            mock_scraping = data.get('mock_scraping', True)
            validate_sentiment = data.get('validate_sentiment', False)
            api_provider = data.get('api', 'coingecko')
            no_tools = data.get('no_tools', False)
        else:  # GET
            user = request.args.get('user', '@test')
            limit = int(request.args.get('limit', 2))
            mock_scraping = 'mock-scraping' in request.args or request.args.get('mock_scraping', '').lower() == 'true'
            validate_sentiment = 'validate-sentiment' in request.args or request.args.get('validate_sentiment', '').lower() == 'true'
            api_provider = request.args.get('api', 'coingecko')
            no_tools = 'no-tools' in request.args or request.args.get('no_tools', '').lower() == 'true'
        
        logger.info(f"CLI endpoint - user: {user}, limit: {limit}, mock_scraping: {mock_scraping}, validate_sentiment: {validate_sentiment}, api: {api_provider}, no_tools: {no_tools}")
        
        # Run exactly like your CLI command
        result = run_and_print(
            user=user,
            limit=limit,
            model='mistralai/mistral-small-3.2-24b-instruct:free',
            system_msg=None,
            as_json=False,  # Get structured result
            mock_scraping=mock_scraping,
            mock_positions=True,  # Always use mock positions for safety
            use_tools=not no_tools,  # Convert no_tools to use_tools
            calculate_positions=False,
            simulate_positions=False,
            validate_sentiment=validate_sentiment,
            api_provider=api_provider
        )
        
        return jsonify({
            "status": "success",
            "command_equivalent": f"python3 scraper.py {user} --limit {limit}" + 
                                (f" --mock-scraping" if mock_scraping else "") +
                                (f" --validate-sentiment" if validate_sentiment else "") +
                                (f" --api {api_provider}" if api_provider != 'coincap' else "") +
                                (f" --no-tools" if no_tools else ""),
            "params": {
                "user": user,
                "limit": limit,
                "mock_scraping": mock_scraping,
                "validate_sentiment": validate_sentiment,
                "api_provider": api_provider,
                "no_tools": no_tools
            },
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error in CLI endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Remove template and static routes since we don't need frontend
# @app.route('/static/<path:filename>')
# def serve_static(filename):
#     """Serve static files."""
#     return send_from_directory('static', filename)

# Don't create template/static directories since we don't need them

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Twitter Scraper API Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
