"""
Data models for cryptocurrency analysis
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class CryptoSentiment:
    """Represents a cryptocurrency sentiment analysis"""
    ticker: str
    sentiment: str  # bullish, bearish, neutral
    context: str
    confidence: float = 0.0

    def __post_init__(self):
        """Validate sentiment value"""
        valid_sentiments = {'bullish', 'bearish', 'neutral'}
        if self.sentiment not in valid_sentiments:
            raise ValueError(f"Invalid sentiment: {self.sentiment}. Must be one of {valid_sentiments}")


@dataclass
class PriceValidation:
    """Represents price validation data for a specific period"""
    period: str  # 1h, 24h, 7d
    base_price: float
    target_price: Optional[float]
    price_change_pct: float
    is_correct: bool
    accuracy_score: float

    def __post_init__(self):
        """Validate period value"""
        valid_periods = {'1h', '24h', '7d'}
        if self.period not in valid_periods:
            raise ValueError(f"Invalid period: {self.period}. Must be one of {valid_periods}")


@dataclass
class TweetAnalysis:
    """Represents a complete tweet analysis"""
    tweet_id: str
    author_handle: str
    content: str
    timestamp: datetime
    detected_cryptos: List[CryptoSentiment]
    price_validations: Dict[str, PriceValidation]

    def get_primary_crypto(self) -> Optional[CryptoSentiment]:
        """Get the first detected crypto"""
        return self.detected_cryptos[0] if self.detected_cryptos else None
    
    def has_validations(self) -> bool:
        """Check if price validations are available"""
        return bool(self.price_validations)
