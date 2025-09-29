"""
Models and AI logic package for OpenRouter integration and cryptocurrency analysis.
"""

# Import OpenRouter logic as primary
from .openrouter_logic import (
    generate_with_openrouter,
    generate_with_openrouter_tools,
    process_tweets_with_openrouter,
    get_available_tools,
    execute_tool
)
from .tools import Tools

__all__ = [
    'generate_with_openrouter',
    'generate_with_openrouter_tools',
    'process_tweets_with_openrouter',
    'get_available_tools',
    'execute_tool',
    'Tools'
]
