import argparse
import json
import sys
import os
from models_logic.ollama_logic import process_tweets_with_ollama

# Charger les variables d'environnement
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_env_file():
    """Charge manuellement le fichier .env"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def run_and_print(u: str, lim: int, mdl: str, sysmsg: str | None, as_json: bool, mock_scraping: bool, mock_positions: bool, use_tools: bool = True, calculate_positions: bool = False, simulate_positions: bool = False, simulation_hours: int = 24) -> None:
    # Charger les variables d'environnement
    load_env_file()
    
    results = process_tweets_with_ollama(u, lim, mdl, system_instruction=sysmsg, mock=mock_scraping, use_tools=use_tools)
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("\n" + "🐦" * 20 + " CONTENU DES TWEETS " + "🐦" * 20)
        
        # Séparer les tweets individuels de l'analyse consolidée
        tweet_results = [r for r in results if "consolidated_analysis" not in r]
        consolidated = next((r for r in results if "consolidated_analysis" in r), None)
        
        # Afficher uniquement le contenu des tweets
        for i, r in enumerate(tweet_results, start=1):
            tweet_text = r.get('full_text', '')
            if len(tweet_text) > 300:
                tweet_text = tweet_text[:300] + "..."
            print(f"\n� TWEET #{i}: {tweet_text}")
        
        # Afficher l'analyse consolidée
        if consolidated:
            print("\n" + "📊" * 20 + " ANALYSE CONSOLIDÉE " + "📊" * 20)
            cons_data = consolidated["consolidated_analysis"]
            print(json.dumps(cons_data, indent=2, ensure_ascii=False))
            
            # Calcul des positions si demandé
            if calculate_positions and consolidated:
                try:
                    from coincap_api.position_calculator import calculate_positions, display_positions_summary
                    positions_result = calculate_positions(cons_data)
                    display_positions_summary(positions_result)
                except Exception as e:
                    print(f"⚠️ Erreur lors du calcul des positions: {e}")
                    print(f"💡 Assurez-vous d'avoir installé 'requests' et configuré COINCAP_API_KEY dans .env")
            
            # Simulation des positions si demandée
            if simulate_positions and consolidated:
                try:
                    from coincap_api.position_simulator import PositionSimulator
                    simulator = PositionSimulator(mock_mode=mock_positions)
                    simulation_result = simulator.simulate_all_positions(cons_data)
                    
                    if "error" not in simulation_result:
                        print(f"\n" + "�" * 20 + " RÉSULTATS PERFORMANCES " + "🎯" * 20)
                        print(f"💰 Capital total: ${simulation_result['total_capital']:.2f}")
                        print(f"📈 P&L total: {simulation_result['total_pnl']:+.2f}$")
                        print(f"📊 ROI: {simulation_result['roi_percent']:+.2f}%")
                    else:
                        print(f"❌ Erreur simulation: {simulation_result['error']}")
                        
                except Exception as e:
                    print(f"⚠️ Erreur lors de la simulation: {e}")
                    if not mock_positions:
                        print(f"💡 Assurez-vous d'avoir configuré COINCAP_API_KEY dans .env")
                    else:
                        print(f"💡 Erreur en mode mock positions")
        
        print("\n" + "🏁" * 10 + " FIN DE L'ANALYSE " + "🏁" * 10)


if __name__ == "__main__":

    prompt = "You are a crypto analyst. Extract cryptocurrency information from social media posts."

    parser = argparse.ArgumentParser(description="Analyze latest posts with an Ollama model and crypto ticker extraction.")
    parser.add_argument("user", nargs="?",default="swissborg", help="Twitter numeric user_id or handle (e.g., 44196397 or @elonmusk)")
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
                run_and_print(user, limit, model, system_msg, as_json=False, mock_scraping=True, mock_positions=False, use_tools=not args.no_tools if 'args' in locals() else True, calculate_positions=False, simulate_positions=False, simulation_hours=24)
            elif choice == "6":
                if not user:
                    print("Please set a user/handle first.")
                    continue
                run_and_print(user, limit, model, system_msg, as_json=True, mock_scraping=True, mock_positions=False, use_tools=not args.no_tools if 'args' in locals() else True, calculate_positions=False, simulate_positions=False, simulation_hours=24)
            elif choice == "7":
                sys.exit(0)
            else:
                print("Unknown option")
    else:
        # Direct CLI mode
        # Gérer les options mock
        mock_scraping = args.mock_scraping or args.mock
        mock_positions = args.mock_positions or args.mock
        
        run_and_print(args.user, args.limit, args.model, args.system, as_json=args.json, mock_scraping=mock_scraping, mock_positions=mock_positions, use_tools=not args.no_tools, calculate_positions=args.positions, simulate_positions=args.simulate, simulation_hours=args.sim_hours)
