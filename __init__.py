"""
Twitter Scraper with AI Analysis

A comprehensive tool for scraping Twitter data and analyzing cryptocurrency 
trading signals using Ollama AI with optional position simulation.
"""

from .utils_scraper import UtilsScraper
from .models_logic import (
    process_tweets_with_ollama,
    generate_with_ollama,
    Tools
)

__version__ = "1.0.0"
__author__ = "Twitter Scraper Team"

__all__ = [
    'UtilsScraper',
    'process_tweets_with_ollama',
    'generate_with_ollama', 
    'Tools'
]
