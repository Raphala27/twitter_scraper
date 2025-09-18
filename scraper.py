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


def run_and_print(u: str, lim: int, mdl: str, sysmsg: str | None, as_json: bool, mock: bool, use_tools: bool = True, calculate_positions: bool = False) -> None:
    # Charger les variables d'environnement
    load_env_file()
    
    results = process_tweets_with_ollama(u, lim, mdl, system_instruction=sysmsg, mock=mock, use_tools=use_tools)
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("\n" + "🐦" * 30 + " ANALYSE DES TWEETS " + "🐦" * 30)
        
        # Séparer les tweets individuels de l'analyse consolidée
        tweet_results = [r for r in results if "consolidated_analysis" not in r]
        consolidated = next((r for r in results if "consolidated_analysis" in r), None)
        
        # Afficher les tweets individuels
        for i, r in enumerate(tweet_results, start=1):
            print(f"\n📝 TWEET #{i}")
            print("─" * 60)
            
            # Affichage du contenu du tweet
            tweet_text = r.get('full_text', '')
            if len(tweet_text) > 200:
                tweet_text = tweet_text[:200] + "..."
            print(f"💬 Contenu: {tweet_text}")
            
            # Affichage de l'analyse
            analysis = r.get('analysis', '')
            if isinstance(analysis, dict):
                # Afficher le dictionnaire brut pour debug
                print(f"🔧 Dictionnaire brut: {analysis}")
                
                # Format structuré avec cryptos
                cryptos = analysis.get('cryptos', [])
                timestamp = analysis.get('timestamp', '')
                tweet_id = analysis.get('tweet_id', '')
                
                if cryptos:
                    print(f"🔍 Cryptos analysées:")
                    for crypto_data in cryptos:
                        if isinstance(crypto_data, dict):
                            ticker = crypto_data.get('ticker', 'N/A')
                            sentiment = crypto_data.get('sentiment', 'neutral')
                            leverage = crypto_data.get('leverage', 'none')
                            emoji = "📈" if sentiment == "long" else "📉" if sentiment == "short" else "➡️"
                            lever_display = f" ({leverage})" if leverage and leverage != 'none' else ""
                            print(f"   {emoji} {ticker}: {sentiment.upper()}{lever_display}")
                        else:
                            print(f"   💰 {crypto_data}")
                else:
                    print("🔍 Aucune crypto détectée")
                
                # Affichage de la date/heure précise
                if timestamp:
                    print(f"🕐 Timestamp: {timestamp}")
                if tweet_id:
                    print(f"🆔 Tweet ID: {tweet_id}")
                    
            elif isinstance(analysis, list):
                # Format ancien (liste)
                print(f"🔧 Liste brute: {analysis}")
                if analysis:
                    print(f"🔍 Cryptos détectées: {', '.join(str(x) for x in analysis)}")
                else:
                    print("🔍 Aucune crypto détectée")
            else:
                # Format texte brut
                print(f"🔧 Texte brut: {analysis}")
                print(f"🔍 Analyse: {analysis}")
            
            # Métadonnées (optionnel, plus discret)
            if not isinstance(analysis, dict):  # Éviter la duplication si déjà affiché
                if r.get('created_at') or r.get('id_str'):
                    print(f"📅 {r.get('created_at', 'N/A')} | ID: {r.get('id_str', 'N/A')}")
        
        # Afficher l'analyse consolidée
        if consolidated:
            print("\n" + "📊" * 25 + " ANALYSE CONSOLIDÉE " + "📊" * 25)
            cons_data = consolidated["consolidated_analysis"]
            print(f"🔧 Dictionnaire consolidé complet:")
            print(json.dumps(cons_data, indent=2, ensure_ascii=False))
            
            summary = cons_data["analysis_summary"]
            print(f"\n📈 RÉSUMÉ GLOBAL:")
            print(f"   🏢 Compte: {cons_data['account']}")
            print(f"   📝 Total tweets analysés: {cons_data['total_tweets']}")
            print(f"   💰 Total positions: {summary['total_positions']}")
            print(f"   📈 Positions long: {summary['long_positions']}")
            print(f"   📉 Positions short: {summary['short_positions']}")
            
            # Calcul des positions si demandé
            if calculate_positions and consolidated:
                try:
                    from moralis_api.position_calculator import calculate_positions, display_positions_summary
                    positions_result = calculate_positions(cons_data)
                    display_positions_summary(positions_result)
                except Exception as e:
                    print(f"⚠️ Erreur lors du calcul des positions: {e}")
                    print(f"💡 Assurez-vous d'avoir installé 'requests' et configuré MORALIS_API_KEY dans .env")
        
        print("\n" + "🏁" * 20 + " FIN DE L'ANALYSE " + "🏁" * 20)


if __name__ == "__main__":

    prompt = "You are a crypto analyst. Extract cryptocurrency information from social media posts."

    parser = argparse.ArgumentParser(description="Analyze latest posts with an Ollama model and crypto ticker extraction.")
    parser.add_argument("user", nargs="?",default="swissborg", help="Twitter numeric user_id or handle (e.g., 44196397 or @elonmusk)")
    parser.add_argument("--limit", type=int, default=2, help="Number of posts to fetch")
    parser.add_argument("--model", type=str, default="qwen3:14b", help="Ollama model name/tag")
    parser.add_argument("--system", type=str, default=prompt, help="Optional system instruction to prepend")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of pretty text")
    parser.add_argument("--mock", action="store_true", help="Fetch posts in mock mode (no API calls)")
    parser.add_argument("--no-tools", action="store_true", help="Disable tools usage (legacy mode)")
    parser.add_argument("--positions", action="store_true", help="Calculate trading positions with Moralis API")
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
                run_and_print(user, limit, model, system_msg, as_json=False, mock=True, use_tools=not args.no_tools if 'args' in locals() else True, calculate_positions=False)
            elif choice == "6":
                if not user:
                    print("Please set a user/handle first.")
                    continue
                run_and_print(user, limit, model, system_msg, as_json=True, mock=True, use_tools=not args.no_tools if 'args' in locals() else True, calculate_positions=False)
            elif choice == "7":
                sys.exit(0)
            else:
                print("Unknown option")
    else:
        # Direct CLI mode
        run_and_print(args.user, args.limit, args.model, args.system, as_json=args.json, mock=args.mock, use_tools=not args.no_tools, calculate_positions=args.positions)
