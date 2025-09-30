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
    model: str = "mistralai/mistral-small-3.2-24b-instruct:free",
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
        # Créer un prompt pour extraire les cryptos et sentiments du tweet
        extraction_prompt = f"""
Tu es un expert analyste crypto. Analyse ce tweet et extrais les informations suivantes au format JSON:

TWEET: "{tweet_content}"

Retourne UNIQUEMENT un JSON avec cette structure:
[{{"ticker": "BTC", "sentiment": "bullish|bearish|neutral", "context": "raison du sentiment"}}]

Si aucune crypto n'est mentionnée, retourne: []
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
            return "Aucune crypto détectée dans ce tweet."
        
        # 2. Créer les données consolidées simulant le format original
        from datetime import datetime, timedelta
        
        # Utiliser le timestamp du tweet fourni, ou un timestamp dans le passé par défaut
        if tweet_timestamp:
            # Utiliser le timestamp du tweet reçu du bot
            current_time = tweet_timestamp
        else:
            # Fallback : utiliser un timestamp dans le passé (comme dans la commande CLI)
            past_time = datetime.now() - timedelta(days=3)  # Il y a 3 jours
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
            # Fallback en cas d'erreur de validation CoinGecko
            consolidated_data["sentiment_validation"] = {
                "validation_status": "error",
                "error_message": f"Validation temporelle non disponible: {str(validation_error)}",
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
        
        # 4. Génération de l'analyse finale par OpenRouter
        system_msg = "Tu es un expert analyste crypto avec un sens de l'humour qui s'adresse à la communauté crypto."
        
        # Vérifier si on a des données de validation
        has_validation = consolidated_data.get("sentiment_validation", {}).get("validation_status") == "success"
        
        analysis_prompt = f"""
{system_msg}

Tu es un analyste crypto qui parle à des crypto-bros. Sois concis, direct et un peu sarcastique.

DONNÉES D'ANALYSE:
{json.dumps(consolidated_data, indent=2, ensure_ascii=False)}

INSTRUCTIONS:
Analyse ces données et donne un compte-rendu COURT (max 200 mots) avec:

🎯 **LE DEAL**: Qui c'est et qu'est-ce qu'il predict
🎯 **SES SKILLS**: {"Il a visé juste ou il s'est planté ? (précision %)" if has_validation else "Analyse du sentiment sans validation temporelle"}
🎯 **VERDICT FINAL**: DYOR ou "trust me bro" ?

Style: Ton de la crypto Twitter, un peu moqueur mais informatif. 
Reste factuel mais amusant. Pas plus de 3-4 phrases par section.

NOTE: {"Les données de validation temporelle sont disponibles" if has_validation else "Les données de validation temporelle ne sont pas disponibles - base ton analyse sur le sentiment détecté uniquement"}
        """
        
        # Get final analysis from OpenRouter (C'EST ÇA QU'ON VEUT RETOURNER)
        final_analysis = generate_with_openrouter(
            model=model,
            prompt=analysis_prompt
        )
        
        return final_analysis
        
    except Exception as e:
        return f"Erreur lors de l'analyse: {str(e)}"


# Fonction de test pour vérifier que ça marche
def test_quick_analysis():
    """Test de la fonction quick_crypto_analysis"""
    print("🚀 Test de la fonction quick_crypto_analysis...")
    
    # Test avec un tweet Bitcoin et un timestamp dans le passé
    test_tweet = "Bitcoin is looking strong today! The fundamentals are solid and adoption is growing. 🚀 #BTC"
    
    # Utiliser un timestamp dans le passé pour avoir les données CoinGecko
    from datetime import datetime, timedelta
    past_timestamp = (datetime.now() - timedelta(days=2)).isoformat() + "Z"
    
    result = quick_crypto_analysis(
        tweet_content=test_tweet,
        user="@elonmusk",
        model="mistralai/mistral-small-3.2-24b-instruct:free",
        tweet_timestamp=past_timestamp
    )
    
    print("✅ Résultat obtenu:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    # Si on exécute ce fichier directement, on fait un test
    test_quick_analysis()
