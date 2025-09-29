#!/usr/bin/env python3
"""
Twitter Scraper with AI Analysis

Main entry point for scraping Twitter data and analyzing cryptocurrency 
trading signals using Ollama AI with optional position simulation.
"""

# Standard library imports
import argparse
import json
import os
import sys
from typing import Optional

# Local application imports
try:
    # Try relative imports when run as module
    from .models_logic import process_tweets_with_ollama
except ImportError:
    # Fallback for direct execution
    from models_logic import process_tweets_with_ollama


def load_env_file() -> None:
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def run_and_print(
    user: str,
    limit: int,
    model: str,
    system_msg: Optional[str],
    as_json: bool,
    mock_scraping: bool,
    mock_positions: bool,
    use_tools: bool = True,
    calculate_positions: bool = False,
    simulate_positions: bool = False,
    simulation_hours: int = 24,
    api_provider: str = "coincap",
    validate_sentiment: bool = False
) -> Optional[dict]:
    """
    Main function to run tweet analysis and optionally simulate positions.
    
    Args:
        user: Twitter username or handle
        limit: Number of tweets to analyze
        model: Ollama model name
        system_msg: Custom system instruction
        as_json: Output in JSON format
        mock_scraping: Use mock tweets
        mock_positions: Use mock prices for simulation
        use_tools: Enable AI tools
        calculate_positions: Calculate trading positions
        simulate_positions: Simulate position performance
        simulation_hours: Hours to simulate
        
    Returns:
        dict: Consolidated analysis with validation results (if available)
    """
    # Load environment variables
    load_env_file()
    
    # Process tweets with AI analysis
    results = process_tweets_with_ollama(
        user, limit, model, 
        system_instruction=system_msg, 
        mock=mock_scraping, 
        use_tools=use_tools
    )
    
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return None
    
    # Format output for console display and get structured result
    structured_result = _display_results(results, calculate_positions, simulate_positions, mock_positions, api_provider, validate_sentiment, model, system_msg)
    
    return structured_result


def _display_results(
    results: list,
    calculate_positions: bool,
    simulate_positions: bool,
    mock_positions: bool,
    api_provider: str = "coincap",
    validate_sentiment: bool = False,
    model: str = "qwen3:14b",
    system_msg: Optional[str] = None
) -> Optional[dict]:
    """Display results in formatted console output and return structured data."""
    print("\n" + "🐦" * 20 + " CONTENU DES TWEETS " + "🐦" * 20)
    
    # Separate individual tweets from consolidated analysis
    tweet_results = [r for r in results if "consolidated_analysis" not in r]
    consolidated = next((r for r in results if "consolidated_analysis" in r), None)
    
    # Display tweet content only
    for i, tweet_result in enumerate(tweet_results, start=1):
        tweet_text = tweet_result.get('full_text', '')
        if len(tweet_text) > 300:
            tweet_text = tweet_text[:300] + "..."
        print(f"\n📝 TWEET #{i}: {tweet_text}")
    
    # Display consolidated analysis
    if consolidated:
        print("\n" + "📊" * 20 + " ANALYSE CONSOLIDÉE " + "📊" * 20)
        cons_data = consolidated["consolidated_analysis"]
        print(json.dumps(cons_data, indent=2, ensure_ascii=False))
        
        # Calculate positions if requested
        if calculate_positions:
            _handle_position_calculation(cons_data)
        
        # Simulate positions if requested
        if simulate_positions:
            _handle_position_simulation(cons_data, mock_positions, api_provider)
        
        # Validate sentiment predictions if requested
        if validate_sentiment:
            validation_data = _handle_sentiment_validation(cons_data, mock_positions)
            # Add validation results to consolidated data
            cons_data["sentiment_validation"] = validation_data
            
            # Display final analysis summary
            _display_final_analysis_summary(cons_data)
        
        # Final Ollama analysis of all collected data
        _handle_final_ollama_analysis(cons_data, model, system_msg)
        
        print("\n" + "🏁" * 10 + " FIN DE L'ANALYSE " + "🏁" * 10)
        
        # Return the consolidated data with all results
        return cons_data
    
    print("\n" + "🏁" * 10 + " FIN DE L'ANALYSE " + "🏁" * 10)
    return None


def _handle_position_calculation(consolidated_data: dict) -> None:
    """Handle position calculation."""
    try:
        try:
            from .coincap_api import calculate_positions, display_positions_summary
        except ImportError:
            from coincap_api import calculate_positions, display_positions_summary
        positions_result = calculate_positions(consolidated_data)
        display_positions_summary(positions_result)
    except Exception as e:
        print(f"⚠️ Erreur lors du calcul des positions: {e}")
        print("💡 Assurez-vous d'avoir configuré COINCAP_API_KEY dans .env")


def _handle_position_simulation(consolidated_data: dict, mock_positions: bool, api_provider: str = "coincap") -> None:
    """Handle position simulation."""
    try:
        # Configure API based on provider choice
        if api_provider == "coingecko":
            try:
                from .api_manager import create_api_manager, APIProvider
            except ImportError:
                from api_manager import create_api_manager, APIProvider
            
            # Use CoinGecko with CoinCap fallback
            api_manager = create_api_manager({
                "primary_api": APIProvider.COINGECKO,
                "enable_fallback": True,
                "mock_mode": mock_positions
            })
            simulator = api_manager.create_simulator()
            print("🦎 Utilisation de CoinGecko API pour la simulation")
        else:
            # Default CoinCap
            try:
                from .coincap_api import PositionSimulator
            except ImportError:
                from coincap_api import PositionSimulator
            simulator = PositionSimulator(mock_mode=mock_positions)
            print("📊 Utilisation de CoinCap API pour la simulation")
        
        simulation_result = simulator.simulate_all_positions(consolidated_data)
        
        if "error" not in simulation_result:
            print("\n" + "🎯" * 20 + " RÉSULTATS PERFORMANCES " + "🎯" * 20)
            print(f"💰 Capital total: ${simulation_result['total_capital']:.2f}")
            print(f"📈 P&L total: {simulation_result['total_pnl']:+.2f}$")
            print(f"📊 ROI: {simulation_result['roi_percent']:+.2f}%")
        else:
            print(f"❌ Erreur simulation: {simulation_result['error']}")
            
    except (ImportError, ValueError, TypeError) as e:
        print(f"⚠️ Erreur lors de la simulation: {e}")
        if not mock_positions:
            api_key_name = "COINGECKO_API_KEY" if api_provider == "coingecko" else "COINCAP_API_KEY"
            print(f"💡 Assurez-vous d'avoir configuré {api_key_name} dans .env")
        else:
            print("💡 Erreur en mode mock positions")


def _handle_sentiment_validation(consolidated_data: dict, mock_mode: bool = False) -> dict:
    """Handle sentiment validation over time and return results."""
    print("\n" + "⏰" * 20 + " VALIDATION TEMPORELLE " + "⏰" * 20)
    
    try:
        try:
            from .coingecko_api.sentiment_validator import SentimentValidator
        except ImportError:
            from coingecko_api.sentiment_validator import SentimentValidator
        
        # Initialize validator with mock mode option
        validator = SentimentValidator(mock_mode=mock_mode)
        
        # Extract sentiment data with timestamps from consolidated analysis
        sentiment_data_list = []
        
        # Convert consolidated analysis to format expected by validator
        tweets_analysis = consolidated_data.get("tweets_analysis", [])
        if not tweets_analysis:
            # Fallback: try to extract from consolidated_data if it's a list
            if isinstance(consolidated_data, list):
                for analysis in consolidated_data:
                    if isinstance(analysis, dict):
                        sentiment_data = {
                            "ticker": analysis.get("ticker", ""),
                            "sentiment": analysis.get("sentiment", "neutral"),
                            "context": analysis.get("context", ""),
                            "timestamp": analysis.get("timestamp", "2025-01-01T00:00:00Z")
                        }
                        sentiment_data_list.append(sentiment_data)
        else:
            # Standard format from consolidated analysis
            for analysis in tweets_analysis:
                if isinstance(analysis, dict):
                    sentiment_data = {
                        "ticker": analysis.get("ticker", ""),
                        "sentiment": analysis.get("sentiment", "neutral"),
                        "context": analysis.get("context", ""),
                        "timestamp": analysis.get("timestamp", "2025-01-01T00:00:00Z")
                    }
                    sentiment_data_list.append(sentiment_data)
        
        if not sentiment_data_list:
            print("❌ Aucune donnée de sentiment trouvée pour la validation")
            return {
                "validation_status": "error",
                "error_message": "Aucune donnée de sentiment trouvée",
                "results": {}
            }
        
        # Validate all sentiments
        validation_results = validator.validate_all_sentiments(sentiment_data_list)
        
        # Display results
        print(f"\n📊 Statistiques globales:")
        stats = validation_results["global_stats"]
        total = stats["total_predictions"]
        
        if total > 0:
            print(f"   Total prédictions: {total}")
            print(f"   Précision 1h:  {stats['correct_1h']}/{total} ({stats['correct_1h']/total*100:.1f}%)")
            print(f"   Précision 24h: {stats['correct_24h']}/{total} ({stats['correct_24h']/total*100:.1f}%)")
            print(f"   Précision 7j:  {stats['correct_7d']}/{total} ({stats['correct_7d']/total*100:.1f}%)")
            print(f"   Score moyen 1h:  {stats['avg_accuracy_1h']:.1f}/100")
            print(f"   Score moyen 24h: {stats['avg_accuracy_24h']:.1f}/100")
            print(f"   Score moyen 7j:  {stats['avg_accuracy_7d']:.1f}/100")
        
        # Also display detailed results for each prediction
        print(f"\n🔍 Détails par prédiction:")
        for result in validation_results["validation_results"]:
            ticker = result["ticker"]
            sentiment = result["sentiment"]
            base_price = result.get("base_price", 0)
            
            print(f"\n🪙 {ticker} ({sentiment}) - Base: ${base_price:.2f}")
            validations = result.get("validations", {})
            for period, validation in validations.items():
                if "error" in validation:
                    print(f"   {period:>3}: ⚠️  {validation['error']}")
                else:
                    correct = "✅" if validation.get("correct", False) else "❌"
                    price_change = validation.get("price_change_pct", 0)
                    actual = validation.get("actual_direction", "unknown")
                    score = validation.get("accuracy_score", 0)
                    print(f"   {period:>3}: {correct} {price_change:+.2f}% (Score: {score:.0f})")
        
        # Return structured results
        return {
            "validation_status": "success",
            "global_stats": validation_results["global_stats"],
            "validation_results": validation_results["validation_results"],
            "summary": {
                "total_predictions": total,
                "accuracy_1h_percent": stats['correct_1h']/total*100 if total > 0 else 0,
                "accuracy_24h_percent": stats['correct_24h']/total*100 if total > 0 else 0,
                "accuracy_7d_percent": stats['correct_7d']/total*100 if total > 0 else 0,
                "avg_score_1h": stats['avg_accuracy_1h'],
                "avg_score_24h": stats['avg_accuracy_24h'],
                "avg_score_7d": stats['avg_accuracy_7d']
            }
        }
        
    except (ImportError, ValueError, TypeError) as e:
        print(f"⚠️ Erreur lors de la validation de sentiment: {e}")
        if not mock_mode:
            print("💡 Assurez-vous d'avoir configuré COINGECKO_API_KEY dans .env pour l'historique des prix")
        else:
            print("💡 Erreur en mode mock de validation")
        
        return {
            "validation_status": "error",
            "error_message": str(e),
            "results": {}
        }


def _display_final_analysis_summary(consolidated_data: dict) -> None:
    """Display a comprehensive final analysis of influencer predictions and their validation."""
    print("\n" + "🎯" * 20 + " ANALYSE FINALE DES PRÉDICTIONS " + "🎯" * 20)
    
    account = consolidated_data.get("account", "Compte inconnu")
    total_tweets = consolidated_data.get("total_tweets", 0)
    
    print(f"👤 Influenceur analysé: {account}")
    print(f"📊 Nombre de tweets analysés: {total_tweets}")
    
    # Analysis summary
    analysis_summary = consolidated_data.get("analysis_summary", {})
    print(f"\n📈 Résumé des sentiments détectés:")
    print(f"   🟢 Bullish: {analysis_summary.get('bullish_sentiments', 0)}")
    print(f"   🔴 Bearish: {analysis_summary.get('bearish_sentiments', 0)}")
    print(f"   ⚪ Neutral: {analysis_summary.get('neutral_sentiments', 0)}")
    
    # Validation results
    sentiment_validation = consolidated_data.get("sentiment_validation", {})
    if sentiment_validation and sentiment_validation.get("validation_status") == "success":
        print(f"\n🔍 Validation temporelle des prédictions:")
        
        summary = sentiment_validation.get("summary", {})
        total_predictions = summary.get("total_predictions", 0)
        
        if total_predictions > 0:
            print(f"   ⏰ Précision à 1h:  {summary.get('accuracy_1h_percent', 0):.1f}%")
            print(f"   ⏰ Précision à 24h: {summary.get('accuracy_24h_percent', 0):.1f}%")
            print(f"   ⏰ Précision à 7j:  {summary.get('accuracy_7d_percent', 0):.1f}%")
            
            # Detailed analysis for each prediction
            validation_results = sentiment_validation.get("validation_results", [])
            
            print(f"\n🔬 Analyse détaillée par annonce:")
            for i, result in enumerate(validation_results, 1):
                ticker = result.get("ticker", "N/A")
                sentiment = result.get("sentiment", "neutral")
                context = result.get("context", "Aucun contexte")
                timestamp = result.get("timestamp", "")
                base_price = result.get("base_price", 0)
                
                # Format timestamp
                formatted_time = ""
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime("%d/%m/%Y à %H:%M")
                    except:
                        formatted_time = timestamp[:16]
                
                print(f"\n   📝 Tweet #{i} - {ticker}")
                print(f"      🕐 Date: {formatted_time}")
                print(f"      💭 Sentiment prédit: {sentiment}")
                print(f"      💡 Contexte: {context}")
                print(f"      💰 Prix de base: ${base_price:.4f}")
                
                # Validation details
                validations = result.get("validations", {})
                for period in ["1h", "24h", "7d"]:
                    if period in validations:
                        validation = validations[period]
                        if "error" not in validation:
                            price_change = validation.get("price_change_pct", 0)
                            actual_direction = validation.get("actual_direction", "unknown")
                            correct = validation.get("correct", False)
                            accuracy_score = validation.get("accuracy_score", 0)
                            
                            status_emoji = "✅" if correct else "❌"
                            direction_emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(actual_direction, "❓")
                            
                            print(f"      {period:>3}: {status_emoji} {price_change:+.2f}% {direction_emoji} (Score: {accuracy_score:.0f}/100)")
                        else:
                            print(f"      {period:>3}: ⚠️ {validation.get('error', 'Erreur inconnue')}")
            
            # Overall performance assessment
            avg_accuracy_24h = summary.get("accuracy_24h_percent", 0)
            avg_score_24h = summary.get("avg_score_24h", 0)
            
            print(f"\n📊 Évaluation globale de l'influenceur:")
            if avg_accuracy_24h >= 70:
                performance = "🌟 Excellente"
            elif avg_accuracy_24h >= 50:
                performance = "👍 Bonne"
            elif avg_accuracy_24h >= 30:
                performance = "⚠️ Moyenne"
            else:
                performance = "👎 Faible"
            
            print(f"   🎯 Performance globale (24h): {performance} ({avg_accuracy_24h:.1f}%)")
            print(f"   📈 Score moyen de précision: {avg_score_24h:.1f}/100")
            
            # Recommendations
            print(f"\n💡 Recommandations:")
            if avg_accuracy_24h >= 60:
                print(f"   ✨ Cet influenceur montre de bonnes capacités prédictives")
                print(f"   ✨ Ses analyses peuvent être considérées comme fiables")
            elif avg_accuracy_24h >= 40:
                print(f"   ⚖️ Performance modérée, à utiliser avec prudence")
                print(f"   ⚖️ Croiser avec d'autres sources d'analyse")
            else:
                print(f"   ⚠️ Faible performance prédictive observée")
                print(f"   ⚠️ Recommandé d'être très prudent avec ces signaux")
        
        else:
            print("   ❌ Aucune prédiction à valider")
    
    else:
        print(f"\n❌ Validation des sentiments non disponible ou échouée")
    
    print("\n" + "🎯" * 60)
    
    # Don't display the dictionary again here - it will be shown after Ollama analysis


def _handle_final_ollama_analysis(consolidated_data: dict, model: str = "qwen3:14b", system_msg: Optional[str] = None) -> None:
    """Send the complete analysis to Ollama for final interpretation and insights."""
    print("\n" + "🤖" * 20 + " ANALYSE FINALE PAR OLLAMA " + "🤖" * 20)
    
    try:
        # Import Ollama functions
        try:
            from .models_logic.ollama_logic import generate_with_ollama
        except ImportError:
            from models_logic.ollama_logic import generate_with_ollama
        
        # Create analysis prompt
        analysis_prompt = f"""
{system_msg or 'Tu es un expert analyste crypto avec un sens de l\'humour qui s\'adresse à la communauté crypto.'}

Tu es un analyste crypto qui parle à des crypto-bros. Sois concis, direct et un peu sarcastique.

DONNÉES D'ANALYSE:
{json.dumps(consolidated_data, indent=2, ensure_ascii=False)}

INSTRUCTIONS:
Analyse ces données et donne un compte-rendu COURT (max 200 mots) avec:

� **LE DEAL**: Qui c'est et qu'est-ce qu'il predict
🎯 **SES SKILLS**: Il a visé juste ou il s'est planté ? (précision %)  
� **VERDICT FINAL**: DYOR ou "trust me bro" ?

Style: Ton de la crypto Twitter, un peu moqueur mais informatif. 
Utilise le jargon crypto (moon, dump, ape, diamond hands, etc.).
Reste factuel mais amusant. Pas plus de 3-4 phrases par section.
        """
        
        print("🧠 Génération de l'analyse finale par Ollama...")
        print("📊 Traitement des données collectées...")
        
        # Get final analysis from Ollama
        final_analysis = generate_with_ollama(
            model=model,
            prompt=analysis_prompt
        )
        
        print("\n" + "💬" * 60)
        print("🤖 ANALYSE FINALE D'OLLAMA:")
        print("💬" * 60)
        print(final_analysis)
        print("💬" * 60)
        
        # Display the complete dictionary after Ollama analysis
        print("\n" + "📄" * 15 + " DICTIONNAIRE FINAL COMPLET " + "📄" * 15)
        print("🔧 Données complètes utilisées pour l'analyse:")
        print(json.dumps(consolidated_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'analyse finale par Ollama: {e}")
        print("🔄 Affichage du dictionnaire sans analyse Ollama:")
        
        # Fallback: just display the dictionary
        print("\n" + "📄" * 15 + " DICTIONNAIRE FINAL COMPLET " + "📄" * 15)
        print("🔧 Dictionnaire structuré pour utilisation programmatique:")
        print(json.dumps(consolidated_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    prompt = "You are a crypto sentiment analyst. Analyze cryptocurrency sentiment from social media posts and detect if influencers are bullish, bearish, or neutral on specific cryptocurrencies."

    parser = argparse.ArgumentParser(description="Analyze crypto sentiment in posts and validate influencer predictions over time.")
    parser.add_argument("user", nargs="?", default="swissborg", help="Twitter numeric user_id or handle (e.g., 44196397 or @elonmusk)")
    parser.add_argument("--limit", type=int, default=2, help="Number of posts to fetch")
    parser.add_argument("--model", type=str, default="qwen3:14b", help="Ollama model name/tag")
    parser.add_argument("--system", type=str, default=prompt, help="Optional system instruction to prepend")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of pretty text")
    parser.add_argument("--mock-scraping", action="store_true", help="Fetch posts in mock mode (no API calls)")
    parser.add_argument("--mock-positions", action="store_true", help="Use mock mode for position simulation (no CoinCap API calls)")
    parser.add_argument("--mock", action="store_true", help="Enable both mock scraping and mock positions")
    parser.add_argument("--no-tools", action="store_true", help="Disable tools usage (legacy mode)")
    parser.add_argument("--positions", action="store_true", help="Calculate trading positions with CoinCap API")
    parser.add_argument("--simulate", action="store_true", help="Simulate trading positions with historical prices")
    parser.add_argument("--validate-sentiment", action="store_true", help="Validate sentiment predictions over time (1h, 24h, 7d)")
    parser.add_argument("--sim-hours", type=int, default=24, help="Hours to simulate (default: 24)")
    parser.add_argument("--api", type=str, choices=["coincap", "coingecko"], default="coincap", help="Cryptocurrency API to use (default: coincap)")
    parser.add_argument("--menu", action="store_true", help="Launch interactive menu")
    args = parser.parse_args()

    if args.menu or not args.user:
        # Interactive menu mode
        user = args.user or ""
        limit = args.limit
        model = args.model
        system_msg = args.system
        
        while True:
            print("\n=== Ollama Tweet Analyzer ===")
            print(f"1) Set user/handle          : {user or '(not set)'}")
            print(f"2) Set limit                : {limit}")
            print(f"3) Set model                : {model}")
            print(f"4) Set system instruction   : {system_msg or '(none)'}")
            print("5) Run analysis (pretty)")
            print("6) Run analysis (JSON)")
            print("7) Quit")
            
            choice = input("> ").strip()
            
            if choice == "1":
                user = input("Enter user_id or handle (@handle): ").strip()
            elif choice == "2":
                try:
                    limit = int(input("Enter limit (e.g., 10): ").strip())
                except ValueError:
                    print("Invalid number")
            elif choice == "3":
                model = input("Enter Ollama model (e.g., llama3.1:8b): ").strip() or model
            elif choice == "4":
                system_msg = input("Enter system instruction (optional): ").strip() or None
            elif choice == "5":
                if not user:
                    print("Please set a user/handle first.")
                    continue
                run_and_print(
                    user, limit, model, system_msg, 
                    as_json=False, mock_scraping=True, mock_positions=False, 
                    use_tools=not args.no_tools, calculate_positions=False, 
                    simulate_positions=False, simulation_hours=24
                )
            elif choice == "6":
                if not user:
                    print("Please set a user/handle first.")
                    continue
                run_and_print(
                    user, limit, model, system_msg, 
                    as_json=True, mock_scraping=True, mock_positions=False, 
                    use_tools=not args.no_tools, calculate_positions=False, 
                    simulate_positions=False, simulation_hours=24
                )
            elif choice == "7":
                sys.exit(0)
            else:
                print("Unknown option")
    else:
        # Direct CLI mode
        mock_scraping = args.mock_scraping or args.mock
        mock_positions = args.mock_positions or args.mock
        
        run_and_print(
            args.user, args.limit, args.model, args.system, 
            as_json=args.json, mock_scraping=mock_scraping, 
            mock_positions=mock_positions, use_tools=not args.no_tools, 
            calculate_positions=args.positions, simulate_positions=args.simulate, 
            simulation_hours=args.sim_hours, api_provider=args.api, 
            validate_sentiment=args.validate_sentiment
        )
