"""
Models and AI logic package for Ollama integration and cryptocurrency analysis.
"""

from .ollama_logic import (
    ensure_model_present,
    generate_with_ollama,
    generate_with_ollama_tools,
    process_tweets_with_ollama,
    get_available_tools,
    execute_tool
)
from .tools import Tools

__all__ = [
    'ensure_model_present',
    'generate_with_ollama', 
    'generate_with_ollama_tools',
    'process_tweets_with_ollama',
    'get_available_tools',
    'execute_tool',
    'Tools'
]
