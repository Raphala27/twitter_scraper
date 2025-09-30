"""
Configuration management for the Twitter Scraper application
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration"""
    # API Keys
    openrouter_api_key: Optional[str]
    coingecko_api_key: Optional[str]
    
    # Model settings
    default_ai_model: str
    response_max_length: int
    
    # App settings
    flask_debug: bool
    flask_port: int
    flask_host: str
    
    # Validation settings
    price_validation_enabled: bool
    mock_mode: bool

    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        return cls(
            # API Keys
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY'),
            coingecko_api_key=os.getenv('COINGECKO_API_KEY'),
            
            # Model settings
            default_ai_model=os.getenv('DEFAULT_AI_MODEL', 'x-ai/grok-4-fast:free'),
            response_max_length=int(os.getenv('RESPONSE_MAX_LENGTH', '280')),
            
            # App settings
            flask_debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            flask_port=int(os.getenv('PORT', '5000')),
            flask_host=os.getenv('FLASK_HOST', '0.0.0.0'),
            
            # Validation settings
            price_validation_enabled=os.getenv('PRICE_VALIDATION', 'True').lower() == 'true',
            mock_mode=os.getenv('MOCK_MODE', 'False').lower() == 'true'
        )
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        if self.response_max_length <= 0:
            raise ValueError("RESPONSE_MAX_LENGTH must be positive")
        
        if self.flask_port <= 0 or self.flask_port > 65535:
            raise ValueError("PORT must be between 1 and 65535")
