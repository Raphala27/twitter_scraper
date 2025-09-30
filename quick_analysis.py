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
    user: str = "@test",
    limit: int = 2,
    model: str = "mistralai/mistral-small-3.2-24b-instruct:free"
) -> str:
    """
    Fonction qui reproduit exactement la commande CLI et retourne uniquement l'analyse finale IA.
    
    Args:
        user: Twitter username (default: @test)
        limit: Nombre de tweets à analyser (default: 2)
        model: Modèle OpenRouter à utiliser
        
    Returns:
        str: Réponse finale du modèle OpenRouter uniquement
    """
    try:
        # Load environment variables
        from scraper import load_env_file
        load_env_file()
        
        # Import required modules
        from models_logic import process_tweets_with_openrouter
        from models_logic.openrouter_logic import generate_with_openrouter
        from coingecko_api.sentiment_validator import SentimentValidator
        
        # 1. Process tweets with AI analysis (équivalent à la partie scraping + analyse)
        results = process_tweets_with_openrouter(
            user, 
            limit, 
            model, 
            system_instruction=None, 
            mock=True,  # --mock-scraping
            use_tools=False  # --no-tools
        )
        
        # 2. Extract consolidated data (équivalent à _display_results mais sans affichage)
        tweet_results = [r for r in results if "consolidated_analysis" not in r]
        consolidated = next((r for r in results if "consolidated_analysis" in r), None)
        
        if not consolidated:
            return "Erreur: Aucune analyse consolidée trouvée"
        
        consolidated_data = consolidated["consolidated_analysis"]
        
        # 3. Validation temporelle (équivalent à --validate-sentiment --api coingecko)
        validator = SentimentValidator(mock_mode=False)  # Utilise vraies données CoinGecko
        
        # Extract sentiment data for validation
        sentiment_data_list = []
        tweets_analysis = consolidated_data.get("tweets_analysis", [])
        
        for analysis in tweets_analysis:
            if isinstance(analysis, dict):
                sentiment_data = {
                    "ticker": analysis.get("ticker", ""),
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "context": analysis.get("context", ""),
                    "timestamp": analysis.get("timestamp", "2025-01-01T00:00:00Z")
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
        
        # 4. Génération de l'analyse finale par OpenRouter (équivalent à _handle_final_ai_analysis)
        system_msg = "Tu es un expert analyste crypto avec un sens de l'humour qui s'adresse à la communauté crypto."
        
        analysis_prompt = f"""
{system_msg}

Tu es un analyste crypto qui parle à des crypto-bros. Sois concis, direct et un peu sarcastique.

DONNÉES D'ANALYSE:
{json.dumps(consolidated_data, indent=2, ensure_ascii=False)}

INSTRUCTIONS:
Analyse ces données et donne un compte-rendu COURT (max 200 mots) avec:

🎯 **LE DEAL**: Qui c'est et qu'est-ce qu'il predict
🎯 **SES SKILLS**: Il a visé juste ou il s'est planté ? (précision %)  
🎯 **VERDICT FINAL**: DYOR ou "trust me bro" ?

Style: Ton de la crypto Twitter, un peu moqueur mais informatif. 
Utilise le jargon crypto (moon, dump, ape, diamond hands, etc.).
Reste factuel mais amusant. Pas plus de 3-4 phrases par section.
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
    
    result = quick_crypto_analysis(
        user="@test",
        limit=2,
        model="mistralai/mistral-small-3.2-24b-instruct:free"
    )
    
    print("✅ Résultat obtenu:")
    print("=" * 60)
    print(result)
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    # Si on exécute ce fichier directement, on fait un test
    test_quick_analysis()
