#!/usr/bin/env python3
"""
Quick Analysis Function

Fonction qui reproduit exactement la commande:
python3 scraper.py @test --limit 2 --mock-scraping --validate-sentiment --api coingecko --no-tools

Et retourne uniquement la réponse finale du modèle OpenRouter.
"""

import json
import os
from typing import Optional

def quick_crypto_analysis(
    tweet_content: str,
    user: str = "@test",
    model: str = "x-ai/grok-4-fast:free",
    tweet_timestamp: str = None
) -> str:
    """
    Analyse le contenu d'un seul tweet et retourne l'analyse finale IA.
    
    Args:
        tweet_content: Le contenu du tweet à analyser
        user: Twitter username de l'auteur (default: @test)
        model: Modèle OpenRouter à utiliser
        tweet_timestamp: Timestamp du tweet (format ISO) pour la validation CoinGecko
        
    Returns:
        str: Réponse finale du modèle OpenRouter uniquement
    """
    try:
        # Load environment variables
        from scraper import load_env_file
        load_env_file()
        
        # Import required modules
        from models_logic.openrouter_logic import generate_with_openrouter
        from coingecko_api.sentiment_validator import SentimentValidator
        
        # 1. Analyser directement le contenu du tweet avec OpenRouter
        # Create a prompt to extract cryptos and sentiments from the tweet
        extraction_prompt = f"""
You are a crypto expert analyst. Analyze this tweet and extract cryptocurrency mentions and sentiment.

TWEET: "{tweet_content}"

Look for cryptocurrency mentions including:
- Tickers
- Full names
- Context clues about crypto sentiment (bullish, bearish, neutral)

Return ONLY a JSON array with this exact structure:
[{{"ticker": "Crypto_ticker", "sentiment": "bullish", "context": "reason for sentiment"}}]

Sentiment must be one of: "bullish", "bearish", "neutral"
If no crypto is mentioned, return: []
        """
        
        # Extraire les cryptos du tweet
        crypto_analysis_raw = generate_with_openrouter(
            model=model,
            prompt=extraction_prompt
        )
        
        # Parser la réponse JSON
        try:
            # Nettoyer la réponse pour extraire le JSON
            import re
            json_match = re.search(r'\[.*\]', crypto_analysis_raw, re.DOTALL)
            if json_match:
                crypto_analysis = json.loads(json_match.group())
            else:
                crypto_analysis = []
        except:
            crypto_analysis = []
        
        if not crypto_analysis:
            return "No crypto detected in this tweet."
        
        # 2. Créer les données consolidées simulant le format original
        from datetime import datetime, timedelta
        
        # Use the provided tweet timestamp, or a past timestamp as fallback
        if tweet_timestamp:
            # Use the timestamp from the bot's tweet
            current_time = tweet_timestamp
        else:
            # Fallback: use a past timestamp (like in CLI command)
            past_time = datetime.now() - timedelta(days=3)  # 3 days ago
            current_time = past_time.isoformat() + "Z"
        
        consolidated_data = {
            "account": user,
            "total_tweets": 1,
            "analysis_summary": {
                "total_sentiments": len(crypto_analysis),
                "bullish_sentiments": sum(1 for c in crypto_analysis if c.get("sentiment") == "bullish"),
                "bearish_sentiments": sum(1 for c in crypto_analysis if c.get("sentiment") == "bearish"),
                "neutral_sentiments": sum(1 for c in crypto_analysis if c.get("sentiment") == "neutral")
            },
            "tweets_analysis": [
                {
                    "tweet_number": 1,
                    "timestamp": current_time,
                    "ticker": crypto.get("ticker", ""),
                    "sentiment": crypto.get("sentiment", "neutral"),
                    "context": crypto.get("context", "")
                }
                for crypto in crypto_analysis
            ]
        }
        
        # 3. Validation temporelle avec CoinGecko (avec fallback en cas d'erreur)
        try:
            validator = SentimentValidator(mock_mode=False)
            
            # Extract sentiment data for validation
            sentiment_data_list = []
            for analysis in consolidated_data["tweets_analysis"]:
                sentiment_data = {
                    "ticker": analysis.get("ticker", ""),
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "context": analysis.get("context", ""),
                    "timestamp": analysis.get("timestamp", current_time)
                }
                sentiment_data_list.append(sentiment_data)
            
            if sentiment_data_list:
                # Validate sentiments
                validation_results = validator.validate_all_sentiments(sentiment_data_list)
                
                # Add validation to consolidated data
                consolidated_data["sentiment_validation"] = {
                    "validation_status": "success",
                    "global_stats": validation_results["global_stats"],
                    "validation_results": validation_results["validation_results"],
                    "summary": {
                        "total_predictions": validation_results["global_stats"]["total_predictions"],
                        "accuracy_1h_percent": validation_results["global_stats"]["correct_1h"]/validation_results["global_stats"]["total_predictions"]*100 if validation_results["global_stats"]["total_predictions"] > 0 else 0,
                        "accuracy_24h_percent": validation_results["global_stats"]["correct_24h"]/validation_results["global_stats"]["total_predictions"]*100 if validation_results["global_stats"]["total_predictions"] > 0 else 0,
                        "accuracy_7d_percent": validation_results["global_stats"]["correct_7d"]/validation_results["global_stats"]["total_predictions"]*100 if validation_results["global_stats"]["total_predictions"] > 0 else 0,
                        "avg_score_1h": validation_results["global_stats"]["avg_accuracy_1h"],
                        "avg_score_24h": validation_results["global_stats"]["avg_accuracy_24h"],
                        "avg_score_7d": validation_results["global_stats"]["avg_accuracy_7d"]
                    }
                }
                
        except Exception as validation_error:
            # Fallback in case of CoinGecko validation error
            consolidated_data["sentiment_validation"] = {
                "validation_status": "error",
                "error_message": f"Temporal validation unavailable: {str(validation_error)}",
                "summary": {
                    "total_predictions": len(consolidated_data["tweets_analysis"]),
                    "accuracy_1h_percent": 0,
                    "accuracy_24h_percent": 0, 
                    "accuracy_7d_percent": 0,
                    "avg_score_1h": 0,
                    "avg_score_24h": 0,
                    "avg_score_7d": 0
                }
            }
        
        # 4. Generate final analysis with OpenRouter
        system_msg = "You are an expert crypto analyst with a sense of humor who speaks to the crypto community."
        
        # Check if we have validation data
        has_validation = consolidated_data.get("sentiment_validation", {}).get("validation_status") == "success"
        
        analysis_prompt = f"""
{system_msg}

You are a crypto analyst talking to crypto bros. Be concise, direct and slightly sarcastic.

ANALYSIS DATA:
{json.dumps(consolidated_data, indent=2, ensure_ascii=False)}

INSTRUCTIONS:
Analyze this data and give a SHORT report (max 200 words) with:

🎯 **THE DEAL**: Who is this and what they predict
🎯 **THEIR SKILLS**: {"Did they nail it or get rekt? (accuracy %)" if has_validation else "Sentiment analysis without temporal validation"}
🎯 **FINAL VERDICT**: DYOR or "trust me bro"?

Style: Crypto Twitter tone, slightly mocking but informative. 
Stay factual but entertaining. No more than 3-4 sentences per section.

NOTE: {"Temporal validation data is available" if has_validation else "Temporal validation data is not available - base your analysis on detected sentiment only"}
        """
        
        # Get final analysis from OpenRouter (THIS IS WHAT WE WANT TO RETURN)
        final_analysis = generate_with_openrouter(
            model=model,
            prompt=analysis_prompt
        )
        
        return final_analysis
        
    except Exception as e:
        return f"Error during analysis: {str(e)}"


# Fonction de test pour vérifier que ça marche
def test_quick_analysis():
    """Test the quick_crypto_analysis function"""
    print("🚀 Testing quick_crypto_analysis function...")
    
    # Test with a Bitcoin tweet and a past timestamp
    test_tweet = "Bitcoin is looking strong today! The fundamentals are solid and adoption is growing. 🚀 #BTC"
    
    # Use a past timestamp to have CoinGecko data
    from datetime import datetime, timedelta
    past_timestamp = (datetime.now() - timedelta(days=2)).isoformat() + "Z"
    
    result = quick_crypto_analysis(
        tweet_content=test_tweet,
        user="@elonmusk",
        model="x-ai/grok-4-fast:free",
        tweet_timestamp=past_timestamp
    )
    
    print("✅ Result obtained:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    # If we run this file directly, run a test
    test_quick_analysis()
