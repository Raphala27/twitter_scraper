"""
Migration wrapper to gradually move from old to new architecture
This allows us to test the new architecture while keeping the old one functional
"""

from src.models.analysis_result import AnalysisResult
from src.models.crypto_data import CryptoSentiment
from src.core.crypto_analyzer import CryptoAnalyzer
from src.services.openrouter_service import OpenRouterService
from src.services.coingecko_service import CoinGeckoService
from src.utils.config import Config


def quick_crypto_analysis_clean(
    tweet_content: str,
    user: str = "@test",
    model: str = "x-ai/grok-4-fast:free",
    tweet_timestamp: str = None
) -> str:
    """
    Clean version of quick_crypto_analysis using new architecture
    
    Args:
        tweet_content: Le contenu du tweet à analyser
        user: Twitter username de l'auteur (default: @test)
        model: Modèle OpenRouter à utiliser
        tweet_timestamp: Timestamp du tweet (format ISO) pour la validation CoinGecko
        
    Returns:
        str: Réponse finale du modèle OpenRouter uniquement
    """
    try:
        # Load environment variables using modern approach
        import os
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Fallback: load .env manually if python-dotenv not available
            env_path = '.env'
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
        
        # Load configuration
        config = Config.from_env()
        
        # Initialize services
        openrouter_service = OpenRouterService(
            api_key=config.openrouter_api_key,
            default_model=model
        )
        
        coingecko_service = CoinGeckoService(
            api_key=config.coingecko_api_key,
            mock_mode=config.mock_mode
        )
        
        # Initialize analyzer
        analyzer = CryptoAnalyzer(openrouter_service, coingecko_service)
        
        # Perform analysis
        result = analyzer.analyze_tweet(
            tweet_content=tweet_content,
            author=user,
            timestamp=tweet_timestamp or "2025-09-27T12:00:00Z",
            tweet_id=""
        )
        
        return result.response_text
        
    except Exception as e:
        return f"Error during analysis: {str(e)}"


def test_clean_analysis():
    """Test de la fonction clean"""
    print("🚀 Testing clean architecture...")
    
    # Test avec un tweet Bitcoin et un timestamp dans le passé
    test_tweet = "Bitcoin is looking strong today! The fundamentals are solid and adoption is growing. 🚀 #BTC"
    
    # Utiliser un timestamp dans le passé pour avoir les données CoinGecko
    from datetime import datetime, timedelta
    past_timestamp = (datetime.now() - timedelta(days=2)).isoformat() + "Z"
    
    result = quick_crypto_analysis_clean(
        tweet_content=test_tweet,
        user="@elonmusk",
        model="x-ai/grok-4-fast:free",
        tweet_timestamp=past_timestamp
    )
    
    print("✅ Clean Architecture Result:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    test_clean_analysis()
