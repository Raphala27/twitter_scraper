"""
CoinGecko service for price validation
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from src.models.crypto_data import CryptoSentiment, PriceValidation


class CoinGeckoService:
    """Service for CoinGecko price validation"""
    
    def __init__(self, api_key: Optional[str] = None, mock_mode: bool = False):
        """
        Initialize CoinGecko service
        
        Args:
            api_key: CoinGecko API key (optional)
            mock_mode: Use mock data for testing
        """
        self.api_key = api_key
        self.mock_mode = mock_mode
    
    def validate_sentiment(self, crypto_sentiment: CryptoSentiment, timestamp: str) -> Dict[str, PriceValidation]:
        """
        Validate sentiment against actual price movements
        
        Args:
            crypto_sentiment: Crypto sentiment to validate
            timestamp: Timestamp of the original tweet
            
        Returns:
            Dictionary of price validations by period
        """
        # Import here to avoid circular imports
        from coingecko_api.sentiment_validator import SentimentValidator
        
        try:
            validator = SentimentValidator(api_key=self.api_key, mock_mode=self.mock_mode)
            
            # Prepare sentiment data for validation
            sentiment_data = {
                "ticker": crypto_sentiment.ticker,
                "sentiment": crypto_sentiment.sentiment,
                "context": crypto_sentiment.context,
                "timestamp": timestamp
            }
            
            # Perform validation
            result = validator.analyze_sentiment_accuracy(sentiment_data)
            
            # Convert to PriceValidation objects
            validations = {}
            for period, validation_data in result.get("validations", {}).items():
                if "error" not in validation_data:
                    validations[period] = PriceValidation(
                        period=period,
                        base_price=validation_data.get("base_price", 0.0),
                        target_price=validation_data.get("target_price"),
                        price_change_pct=validation_data.get("price_change_pct", 0.0),
                        is_correct=validation_data.get("correct", False),
                        accuracy_score=validation_data.get("accuracy_score", 0.0)
                    )
            
            return validations
            
        except Exception as e:
            print(f"Error validating sentiment for {crypto_sentiment.ticker}: {e}")
            return {}
    
    def validate_multiple_sentiments(self, crypto_sentiments: List[CryptoSentiment], timestamp: str) -> Dict[str, Dict[str, PriceValidation]]:
        """
        Validate multiple crypto sentiments
        
        Args:
            crypto_sentiments: List of crypto sentiments to validate
            timestamp: Timestamp of the original tweet
            
        Returns:
            Dictionary mapping ticker to price validations
        """
        results = {}
        
        for crypto_sentiment in crypto_sentiments:
            validations = self.validate_sentiment(crypto_sentiment, timestamp)
            if validations:
                results[crypto_sentiment.ticker] = validations
        
        return results
    
    def get_price_summary(self, validations: Dict[str, PriceValidation], ticker: str, sentiment: str) -> str:
        """
        Generate a price summary string from validations
        
        Args:
            validations: Price validations by period
            ticker: Cryptocurrency ticker
            sentiment: Original sentiment prediction
            
        Returns:
            Formatted price summary string
        """
        if not validations:
            return "No price validation data available"
        
        price_moves = []
        for period in ["1h", "24h", "7d"]:
            if period in validations:
                validation = validations[period]
                if validation.target_price is not None:
                    status = "✅" if validation.is_correct else "❌"
                    change_pct = validation.price_change_pct
                    price_moves.append(f"{period}: {status} {change_pct:+.1f}%")
                else:
                    price_moves.append(f"{period}: ⚠️ N/A")
            else:
                price_moves.append(f"{period}: ⚠️ N/A")
        
        return f"Price moves for {ticker} (predicted {sentiment}): {', '.join(price_moves)}"
