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
) -> None:
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
        return
    
    # Format output for console display
    _display_results(results, calculate_positions, simulate_positions, mock_positions, api_provider, validate_sentiment)


def _display_results(
    results: list,
    calculate_positions: bool,
    simulate_positions: bool,
    mock_positions: bool,
    api_provider: str = "coincap",
    validate_sentiment: bool = False
) -> None:
    """Display results in formatted console output."""
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
            _handle_sentiment_validation(cons_data, mock_positions)
    
    print("\n" + "🏁" * 10 + " FIN DE L'ANALYSE " + "🏁" * 10)


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


def _handle_sentiment_validation(consolidated_data: dict, mock_mode: bool = False) -> None:
    """Handle sentiment validation over time."""
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
            return
        
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
        
    except (ImportError, ValueError, TypeError) as e:
        print(f"⚠️ Erreur lors de la validation de sentiment: {e}")
        if not mock_mode:
            print("💡 Assurez-vous d'avoir configuré COINGECKO_API_KEY dans .env pour l'historique des prix")
        else:
            print("💡 Erreur en mode mock de validation")


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
