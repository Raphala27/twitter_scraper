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
    simulation_hours: int = 24
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
    _display_results(results, calculate_positions, simulate_positions, mock_positions)


def _display_results(
    results: list,
    calculate_positions: bool,
    simulate_positions: bool,
    mock_positions: bool
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
            _handle_position_simulation(cons_data, mock_positions)
    
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


def _handle_position_simulation(consolidated_data: dict, mock_positions: bool) -> None:
    """Handle position simulation."""
    try:
        try:
            from .coincap_api import PositionSimulator
        except ImportError:
            from coincap_api import PositionSimulator
        simulator = PositionSimulator(mock_mode=mock_positions)
        simulation_result = simulator.simulate_all_positions(consolidated_data)
        
        if "error" not in simulation_result:
            print("\n" + "🎯" * 20 + " RÉSULTATS PERFORMANCES " + "🎯" * 20)
            print(f"💰 Capital total: ${simulation_result['total_capital']:.2f}")
            print(f"📈 P&L total: {simulation_result['total_pnl']:+.2f}$")
            print(f"📊 ROI: {simulation_result['roi_percent']:+.2f}%")
        else:
            print(f"❌ Erreur simulation: {simulation_result['error']}")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la simulation: {e}")
        if not mock_positions:
            print("💡 Assurez-vous d'avoir configuré COINCAP_API_KEY dans .env")
        else:
            print("💡 Erreur en mode mock positions")


if __name__ == "__main__":
    prompt = "You are a crypto analyst. Extract cryptocurrency information from social media posts."

    parser = argparse.ArgumentParser(description="Analyze latest posts with an Ollama model and crypto ticker extraction.")
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
    parser.add_argument("--sim-hours", type=int, default=24, help="Hours to simulate (default: 24)")
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
            simulation_hours=args.sim_hours
        )
