#!/usr/bin/env python3
"""
Basic scraping example - analyze tweets without position simulation.
"""
from twitter_scraper.models_logic import process_tweets_with_ollama

import sys
import os

# Add parent directory to Python path so we can import directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


def basic_analysis_example():
    """
    Example 1: Basic tweet analysis without position simulation
    """
    print("🚀 Example 1: Basic Tweet Analysis")
    print("=" * 50)
    
    # Analyze tweets from a crypto trader account
    results = process_tweets_with_ollama(
        user_or_handle="@trader",
        limit=3,
        model="qwen3:14b",
        system_instruction="Extract cryptocurrency trading signals from tweets.",
        mock=True,  # Use mock data for this example
        use_tools=True
    )
    
    # Print results
    for result in results:
        if "consolidated_analysis" in result:
            print("\n📊 Consolidated Analysis:")
            analysis = result["consolidated_analysis"]
            print(f"Account: {analysis['account']}")
            print(f"Total tweets: {analysis['total_tweets']}")
            print(f"Positions found: {analysis['analysis_summary']['total_positions']}")
            print(f"Long positions: {analysis['analysis_summary']['long_positions']}")
            print(f"Short positions: {analysis['analysis_summary']['short_positions']}")
        else:
            print(f"\n📝 Tweet Analysis:")
            analysis = result.get('analysis', {})
            if isinstance(analysis, dict) and 'cryptos' in analysis:
                for crypto in analysis['cryptos']:
                    print(f"  • {crypto['ticker']}: {crypto['sentiment']} (leverage: {crypto['leverage']})")

if __name__ == "__main__":
    basic_analysis_example()
