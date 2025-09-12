import argparse
import json
import sys
from models_logic.ollama_logic import process_tweets_with_ollama


def run_and_print(u: str, lim: int, mdl: str, sysmsg: str | None, as_json: bool, mock: bool) -> None:
    results = process_tweets_with_ollama(u, lim, mdl, system_instruction=sysmsg, mock=mock)
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        sep = "\n" + ("=" * 80) + "\n"
        blocks = []
        for i, r in enumerate(results, start=1):
            header = f"[{i}] {r.get('created_at','')} (id: {r.get('id_str','')})"
            blocks.append(f"{header}\nPost:\n{r.get('full_text','')}\n\nAnalysis:\n{r.get('analysis','')}")
        print(sep.join(blocks))


if __name__ == "__main__":

    prompt = "Recover the crypto and thickers. give me back only a list of it in python only a list. like following: ['BTC', 'ETH'] but do not add them if they are not present in the post."

    parser = argparse.ArgumentParser(description="Analyze latest posts with an Ollama model.")
    parser.add_argument("user", nargs="?",default="swissborg", help="Twitter numeric user_id or handle (e.g., 44196397 or @elonmusk)")
    parser.add_argument("--limit", type=int, default=2, help="Number of posts to fetch")
    parser.add_argument("--model", type=str, default="koesn/mistral-7b-instruct:latest", help="Ollama model name/tag")
    parser.add_argument("--system", type=str, default=prompt, help="Optional system instruction to prepend")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of pretty text")
    parser.add_argument("--mock", action="store_true", help="Fetch posts in mock mode (no API calls)")
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
                run_and_print(user, limit, model, system_msg, as_json=False, mock=True)
            elif choice == "6":
                if not user:
                    print("Please set a user/handle first.")
                    continue
                run_and_print(user, limit, model, system_msg, as_json=True, mock=True)
            elif choice == "7":
                sys.exit(0)
            else:
                print("Unknown option")
    else:
        # Direct CLI mode
        run_and_print(args.user, args.limit, args.model, args.system, as_json=args.json, mock=args.mock)
