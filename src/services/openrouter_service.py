"""
OpenRouter service for AI model interactions
"""

import json
import re
import requests
from typing import List, Optional
from src.models.crypto_data import CryptoSentiment


class OpenRouterService:
    """Service for interacting with OpenRouter AI models"""
    
    def __init__(self, api_key: str, default_model: str):
        """
        Initialize OpenRouter service
        
        Args:
            api_key: OpenRouter API key
            default_model: Default model to use
        """
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _generate_with_openrouter(self, model: str, prompt: str) -> str:
        """
        Generate response using OpenRouter API
        
        Args:
            model: Model to use
            prompt: Prompt to send
            
        Returns:
            Generated response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.RequestException as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected API response format: {str(e)}")

    def extract_crypto_sentiment(self, tweet_content: str, model: Optional[str] = None) -> List[CryptoSentiment]:
        """
        Extract cryptocurrency mentions and sentiment from tweet content
        
        Args:
            tweet_content: Content of the tweet to analyze
            model: AI model to use (optional, uses default if not provided)
            
        Returns:
            List of detected crypto sentiments
        """
        prompt = self._build_extraction_prompt(tweet_content)
        model_to_use = model or self.default_model
        
        try:
            raw_response = self._generate_with_openrouter(
                model=model_to_use,
                prompt=prompt
            )
            
            return self._parse_crypto_response(raw_response)
            
        except Exception as e:
            print(f"Error extracting crypto sentiment: {e}")
            return []
    
    def generate_analysis(self, price_data: str, user_info: dict, model: Optional[str] = None) -> str:
        """
        Generate final analysis using AI model
        
        Args:
            price_data: Price validation information
            user_info: User and tweet information
            model: AI model to use (optional)
            
        Returns:
            Generated analysis text
        """
        prompt = self._build_analysis_prompt(price_data, user_info)
        model_to_use = model or self.default_model
        
        try:
            return self._generate_with_openrouter(
                model=model_to_use,
                prompt=prompt
            )
        except Exception as e:
            return f"Analysis generation failed: {str(e)}"
    
    def _build_extraction_prompt(self, tweet_content: str) -> str:
        """Build prompt for crypto sentiment extraction"""
        return f"""
You are a crypto expert analyst. Analyze this tweet and extract cryptocurrency mentions and sentiment.

TWEET: "{tweet_content}"

Look for cryptocurrency mentions including:
- Tickers (BTC, ETH, SOL, etc.)
- Full names (Bitcoin, Ethereum, etc.)
- Context clues about crypto sentiment (bullish, bearish, neutral)

Return ONLY a JSON array with this exact structure:
[{{"ticker": "BTC", "sentiment": "bullish", "context": "reason for sentiment"}}]

Sentiment must be one of: "bullish", "bearish", "neutral"
If no crypto is mentioned, return: []
        """
    
    def _build_analysis_prompt(self, price_data: str, user_info: dict) -> str:
        """Build prompt for final analysis generation"""
        has_validation = bool(price_data and price_data != "No price validation data available")
        
        return f"""
You are an expert crypto analyst with a sense of humor who speaks to the crypto community.

You are a crypto analyst talking to crypto bros. Be EXTREMELY concise.

PRICE DATA:
{price_data}

USER INFO:
- Account: {user_info.get('account', '')}
- Tweet sentiment: {user_info.get('sentiment', 'unknown')}
- Crypto: {user_info.get('ticker', 'unknown')}

INSTRUCTIONS:
Give a VERY SHORT analysis (max 250 characters total) in this format:

🎯 THE DEAL: Who and what they predict (max 1 sentence)
🎯 SKILLS: {"Use the actual price moves above" if has_validation else "No validation data"} (max 1 sentence)
🎯 VERDICT: DYOR or trust? (max 1 sentence)

CRITICAL RULES:
- MAXIMUM 250 characters total for entire response
- Use the REAL price data above if available
- Be direct and punchy
- No extra words or fluff
        """
    
    def _parse_crypto_response(self, raw_response: str) -> List[CryptoSentiment]:
        """
        Parse AI response to extract crypto sentiments
        
        Args:
            raw_response: Raw response from AI model
            
        Returns:
            List of parsed crypto sentiments
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            if not json_match:
                return []
            
            crypto_data = json.loads(json_match.group())
            
            # Convert to CryptoSentiment objects
            sentiments = []
            for item in crypto_data:
                if isinstance(item, dict) and all(key in item for key in ['ticker', 'sentiment', 'context']):
                    sentiments.append(CryptoSentiment(
                        ticker=item['ticker'],
                        sentiment=item['sentiment'],
                        context=item['context']
                    ))
            
            return sentiments
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing crypto response: {e}")
            return []
