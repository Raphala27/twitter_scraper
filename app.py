"""
Application factory for the Twitter Scraper Flask app
"""

from flask import Flask
from flask_cors import CORS
import logging
import os

from src.api.endpoints import api_bp, init_endpoints
from src.core.crypto_analyzer import CryptoAnalyzer
from src.services.openrouter_service import OpenRouterService
from src.services.coingecko_service import CoinGeckoService
from src.utils.config import Config


def create_app(config: Config = None) -> Flask:
    """
    Application factory pattern for Flask app
    
    Args:
        config: Configuration object (uses environment if not provided)
        
    Returns:
        Configured Flask application
    """
    # Load configuration
    if config is None:
        config = Config.from_env()
    
    # Validate configuration
    config.validate()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app)
    
    # Configure Flask
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSON_AS_ASCII'] = False
    
    # Configure logging
    _configure_logging(app, config)
    
    # Initialize services
    openrouter_service = OpenRouterService(
        api_key=config.openrouter_api_key,
        default_model=config.default_ai_model
    )
    
    coingecko_service = CoinGeckoService(
        api_key=config.coingecko_api_key,
        mock_mode=config.mock_mode
    )
    
    # Initialize core analyzer
    crypto_analyzer = CryptoAnalyzer(openrouter_service, coingecko_service)
    
    # Initialize API endpoints with dependencies
    init_endpoints(crypto_analyzer)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Store config in app for access
    app.config['APP_CONFIG'] = config
    
    return app


def _configure_logging(app: Flask, config: Config):
    """
    Configure application logging
    
    Args:
        app: Flask application
        config: Application configuration
    """
    log_level = logging.DEBUG if config.flask_debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set Flask logger level
    app.logger.setLevel(log_level)


def load_env_file():
    """Load environment variables from .env file (for backward compatibility)"""
    try:
        # Import the original function for compatibility
        from scraper import load_env_file as original_load_env
        original_load_env()
    except ImportError:
        # Fallback: load .env manually
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value


if __name__ == '__main__':
    # Load environment variables
    load_env_file()
    
    # Create app
    app = create_app()
    config = app.config['APP_CONFIG']
    
    # Run app
    app.logger.info(f"Starting Twitter Scraper API on port {config.flask_port}")
    app.run(
        host=config.flask_host,
        port=config.flask_port,
        debug=config.flask_debug
    )
