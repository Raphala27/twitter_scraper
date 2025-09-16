import argparse
import json
import sys
from models_logic.ollama_logic import process_tweets_with_ollama


def run_and_print(u: str, lim: int, mdl: str, sysmsg: str | None, as_json: bool, mock: bool, use_tools: bool = True) -> None:
    results = process_tweets_with_ollama(u, lim, mdl, system_instruction=sysmsg, mock=mock, use_tools=use_tools)
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("\n" + "🐦" * 30 + " ANALYSE DES TWEETS " + "🐦" * 30)
        for i, r in enumerate(results, start=1):
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
                # Nouveau format structuré
                tickers = analysis.get('tickers', [])
                sentiments = analysis.get('sentiments', [])
                timestamp = analysis.get('timestamp', '')
                tweet_id = analysis.get('tweet_id', '')
                
                if tickers:
                    print(f"🔍 Cryptos analysées:")
                    for sentiment_data in sentiments:
                        ticker = sentiment_data.get('ticker', 'N/A')
                        sentiment = sentiment_data.get('sentiment', 'neutral')
                        emoji = "📈" if sentiment == "long" else "📉" if sentiment == "short" else "➡️"
                        print(f"   {emoji} {ticker}: {sentiment.upper()}")
                else:
                    print("🔍 Aucune crypto détectée")
                
                # Affichage de la date/heure précise
                if timestamp:
                    print(f"🕐 Timestamp: {timestamp}")
                if tweet_id:
                    print(f"🆔 Tweet ID: {tweet_id}")
                    
            elif isinstance(analysis, list):
                # Format ancien (liste de noms)
                if analysis:
                    print(f"🔍 Cryptos détectées: {', '.join(analysis)}")
                else:
                    print("🔍 Aucune crypto détectée")
            else:
                # Format texte brut
                print(f"🔍 Analyse: {analysis}")
            
            # Métadonnées (optionnel, plus discret)
            if not isinstance(analysis, dict):  # Éviter la duplication si déjà affiché
                if r.get('created_at') or r.get('id_str'):
                    print(f"📅 {r.get('created_at', 'N/A')} | ID: {r.get('id_str', 'N/A')}")
        
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
                run_and_print(user, limit, model, system_msg, as_json=False, mock=True, use_tools=not args.no_tools if 'args' in locals() else True)
            elif choice == "6":
                if not user:
                    print("Please set a user/handle first.")
                    continue
                run_and_print(user, limit, model, system_msg, as_json=True, mock=True, use_tools=not args.no_tools if 'args' in locals() else True)
            elif choice == "7":
                sys.exit(0)
            else:
                print("Unknown option")
    else:
        # Direct CLI mode
        run_and_print(args.user, args.limit, args.model, args.system, as_json=args.json, mock=args.mock, use_tools=not args.no_tools)
