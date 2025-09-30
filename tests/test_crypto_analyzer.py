"""
Tests for the CryptoAnalyzer core component
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core.crypto_analyzer import CryptoAnalyzer
from src.models.crypto_data import CryptoSentiment, PriceValidation
from src.models.analysis_result import AnalysisResult
from src.services.openrouter_service import OpenRouterService
from src.services.coingecko_service import CoinGeckoService


class TestCryptoAnalyzer:
    """Test suite for CryptoAnalyzer"""
    
    @pytest.fixture
    def mock_openrouter_service(self):
        """Create mock OpenRouter service"""
        return Mock(spec=OpenRouterService)
    
    @pytest.fixture
    def mock_coingecko_service(self):
        """Create mock CoinGecko service"""
        return Mock(spec=CoinGeckoService)
    
    @pytest.fixture
    def analyzer(self, mock_openrouter_service, mock_coingecko_service):
        """Create CryptoAnalyzer with mocked services"""
        return CryptoAnalyzer(mock_openrouter_service, mock_coingecko_service)
    
    def test_analyze_tweet_success(self, analyzer, mock_openrouter_service, mock_coingecko_service):
        """Test successful tweet analysis"""
        # Setup mocks
        crypto_sentiment = CryptoSentiment(
            ticker="BTC",
            sentiment="bullish",
            context="positive news"
        )
        mock_openrouter_service.extract_crypto_sentiment.return_value = [crypto_sentiment]
        
        price_validation = PriceValidation(
            period="1h",
            base_price=50000.0,
            target_price=50500.0,
            price_change_pct=1.0,
            is_correct=True,
            accuracy_score=85.0
        )
        mock_coingecko_service.validate_multiple_sentiments.return_value = {
            "BTC": {"1h": price_validation}
        }
        mock_coingecko_service.get_price_summary.return_value = "BTC: 1h: ✅ +1.0%"
        mock_openrouter_service.generate_analysis.return_value = "Great prediction!"
        
        # Execute
        result = analyzer.analyze_tweet(
            tweet_content="Bitcoin to the moon! 🚀",
            author="@testuser",
            timestamp="2025-09-27T12:00:00Z",
            tweet_id="123"
        )
        
        # Assert
        assert result.is_success()
        assert result.response_text == "Great prediction!"
        assert result.confidence_score > 0
        assert result.analysis_type == "crypto_sentiment"
    
    def test_analyze_tweet_no_crypto(self, analyzer, mock_openrouter_service):
        """Test tweet with no crypto mentions"""
        # Setup mocks
        mock_openrouter_service.extract_crypto_sentiment.return_value = []
        
        # Execute
        result = analyzer.analyze_tweet(
            tweet_content="Just had a great lunch!",
            author="@testuser",
            timestamp="2025-09-27T12:00:00Z"
        )
        
        # Assert
        assert result.is_success()
        assert "No crypto detected" in result.response_text
        assert result.confidence_score == 25.0
    
    def test_analyze_tweet_api_error(self, analyzer, mock_openrouter_service):
        """Test handling of API errors"""
        # Setup mocks
        mock_openrouter_service.extract_crypto_sentiment.side_effect = Exception("API Error")
        
        # Execute
        result = analyzer.analyze_tweet(
            tweet_content="Bitcoin test",
            author="@testuser",
            timestamp="2025-09-27T12:00:00Z"
        )
        
        # Assert
        assert result.is_error()
        assert "Analysis failed" in result.response_text
        assert result.confidence_score == 0.0
    
    def test_calculate_confidence_high_accuracy(self, analyzer):
        """Test confidence calculation with high accuracy"""
        # This would test the private method through a public interface
        # Implementation would depend on exposing confidence calculation logic
        pass
    
    def test_parse_timestamp_valid(self, analyzer):
        """Test timestamp parsing with valid input"""
        timestamp = "2025-09-27T12:00:00Z"
        result = analyzer._parse_timestamp(timestamp)
        assert isinstance(result, datetime)
    
    def test_parse_timestamp_invalid(self, analyzer):
        """Test timestamp parsing with invalid input"""
        timestamp = "invalid-timestamp"
        result = analyzer._parse_timestamp(timestamp)
        assert isinstance(result, datetime)  # Should fallback to current time
