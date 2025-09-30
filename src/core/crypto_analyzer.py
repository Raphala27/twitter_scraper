"""
Main crypto analyzer - coordinates sentiment detection and price validation
"""

from typing import List, Dict, Any
from src.models.crypto_data import CryptoSentiment, TweetAnalysis, PriceValidation
from src.models.analysis_result import AnalysisResult
from src.services.openrouter_service import OpenRouterService
from src.services.coingecko_service import CoinGeckoService
from datetime import datetime


class CryptoAnalyzer:
    """Main analyzer that coordinates crypto sentiment analysis and price validation"""
    
    def __init__(self, openrouter_service: OpenRouterService, coingecko_service: CoinGeckoService):
        """
        Initialize the crypto analyzer
        
        Args:
            openrouter_service: Service for AI model interactions
            coingecko_service: Service for price validation
        """
        self.openrouter = openrouter_service
        self.coingecko = coingecko_service
    
    def analyze_tweet(self, tweet_content: str, author: str, timestamp: str, tweet_id: str = "") -> AnalysisResult:
        """
        Main analysis pipeline for a tweet
        
        Args:
            tweet_content: Content of the tweet
            author: Author handle (e.g., @username)
            timestamp: Tweet timestamp in ISO format
            tweet_id: Tweet ID (optional)
            
        Returns:
            Complete analysis result
        """
        try:
            # 1. Extract crypto sentiments from tweet
            crypto_sentiments = self.openrouter.extract_crypto_sentiment(tweet_content)
            
            if not crypto_sentiments:
                return AnalysisResult.success(
                    response_text="No crypto detected in this tweet.",
                    confidence_score=25.0
                )
            
            # 2. Validate sentiments with price data
            price_validations = self._validate_sentiments(crypto_sentiments, timestamp)
            
            # 3. Create tweet analysis object
            tweet_analysis = TweetAnalysis(
                tweet_id=tweet_id,
                author_handle=author,
                content=tweet_content,
                timestamp=self._parse_timestamp(timestamp),
                detected_cryptos=crypto_sentiments,
                price_validations=price_validations.get(crypto_sentiments[0].ticker, {}) if crypto_sentiments else {}
            )
            
            # 4. Generate final analysis
            final_analysis = self._generate_final_analysis(tweet_analysis)
            
            # 5. Calculate confidence score
            confidence = self._calculate_confidence(final_analysis, tweet_analysis)
            
            return AnalysisResult.success(
                response_text=final_analysis,
                confidence_score=confidence
            )
            
        except Exception as e:
            return AnalysisResult.error(f"Analysis failed: {str(e)}")
    
    def _validate_sentiments(self, crypto_sentiments: List[CryptoSentiment], timestamp: str) -> Dict[str, Dict[str, PriceValidation]]:
        """
        Validate crypto sentiments against price movements
        
        Args:
            crypto_sentiments: List of detected crypto sentiments
            timestamp: Tweet timestamp
            
        Returns:
            Dictionary mapping ticker to price validations
        """
        try:
            return self.coingecko.validate_multiple_sentiments(crypto_sentiments, timestamp)
        except Exception as e:
            print(f"Price validation error: {e}")
            return {}
    
    def _generate_final_analysis(self, tweet_analysis: TweetAnalysis) -> str:
        """
        Generate final AI analysis based on tweet analysis
        
        Args:
            tweet_analysis: Complete tweet analysis data
            
        Returns:
            Generated analysis text
        """
        primary_crypto = tweet_analysis.get_primary_crypto()
        if not primary_crypto:
            return "No crypto sentiment detected."
        
        # Prepare price data summary
        price_info = ""
        if tweet_analysis.has_validations():
            price_info = self.coingecko.get_price_summary(
                tweet_analysis.price_validations,
                primary_crypto.ticker,
                primary_crypto.sentiment
            )
        else:
            price_info = "No price validation data available"
        
        # Prepare user info
        user_info = {
            'account': tweet_analysis.author_handle,
            'sentiment': primary_crypto.sentiment,
            'ticker': primary_crypto.ticker
        }
        
        # Generate analysis using OpenRouter
        return self.openrouter.generate_analysis(price_info, user_info)
    
    def _calculate_confidence(self, analysis_text: str, tweet_analysis: TweetAnalysis) -> float:
        """
        Calculate confidence score based on analysis and validations
        
        Args:
            analysis_text: Generated analysis text
            tweet_analysis: Tweet analysis data
            
        Returns:
            Confidence score (0-100)
        """
        base_confidence = 85.0  # High confidence with CoinGecko validation
        
        # Adjust based on analysis content
        analysis_lower = analysis_text.lower()
        
        if "0%" in analysis_text or "no crypto" in analysis_lower:
            return 25.0
        elif any(word in analysis_lower for word in ['excellent', 'good', 'accurate', 'moon', 'nailed']):
            return 90.0
        elif any(word in analysis_lower for word in ['average', 'moderate', 'cautious', 'mixed']):
            return 60.0
        
        # Adjust based on price validation accuracy
        if tweet_analysis.has_validations():
            correct_validations = sum(1 for v in tweet_analysis.price_validations.values() if v.is_correct)
            total_validations = len(tweet_analysis.price_validations)
            
            if total_validations > 0:
                accuracy_ratio = correct_validations / total_validations
                if accuracy_ratio == 0:
                    return 25.0  # No correct predictions
                elif accuracy_ratio >= 0.5:
                    return min(90.0, base_confidence + (accuracy_ratio * 10))
        
        return base_confidence
    
    def _parse_timestamp(self, timestamp: str) -> datetime:
        """
        Parse timestamp string to datetime object
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Parsed datetime object
        """
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            # Fallback to current time
            return datetime.now()
