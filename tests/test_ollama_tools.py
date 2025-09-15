#!/usr/bin/env python3
"""
Script de test pour les tools Ollama avec extraction de tickers crypto.
"""

from process_with_ollama import test_tools_with_ollama, process_tweets_with_ollama

def test_direct_tool_call():
    """Test direct de la fonctionnalité des tools."""
    print("=== Test Direct des Tools ===")
    
    test_cases = [
        "I'm investing in Bitcoin and Ethereum this week.",
        "BTC is pumping! Also watching SOL and ADA closely.",
        "The market is crazy today. DOGE to the moon! 🚀",
        "Just bought some Polygon (MATIC) and Cardano tokens.",
        "No crypto content here, just talking about stocks."
    ]
    
    model = "qwen3:14b"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case}")
        result = test_tools_with_ollama(model, test_case)
        print(f"Result: {result}")
        print("-" * 50)

def test_tweet_processing():
    """Test du traitement des tweets avec les tools."""
    print("\n=== Test Traitement des Tweets avec Tools ===")
    
    # Test avec des données mock
    results = process_tweets_with_ollama(
        user_or_handle="testuser",
        limit=2,
        model="qwen3:14b",
        system_instruction="You are a crypto analyst. Extract cryptocurrency tickers from social media posts.",
        mock=True,
        use_tools=True
    )
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Tweet {i} ---")
        print(f"Text: {result['full_text']}")
        print(f"Analysis: {result['analysis']}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        test_direct_tool_call()
        test_tweet_processing()
    except Exception as e:
        print(f"Erreur lors du test: {e}")
