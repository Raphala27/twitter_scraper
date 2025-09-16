import os
import json
import argparse
import subprocess
import requests
from typing import List, Dict, Any
import sys

# We reuse the scraper module by importing the function
from twitter_scraper import get_user_tweets


def ensure_model_present(model: str) -> None:
    """Pull the Ollama model if not present locally."""
    try:
        # 'ollama show' returns non-zero if model not present
        show = subprocess.run(["ollama", "show", model], capture_output=True)
        if show.returncode != 0:
            pull = subprocess.run(["ollama", "pull", model], check=False)
            if pull.returncode != 0:
                print(f"Warn: unable to pull model '{model}'. Ensure Ollama is running and the model name is correct.")
    except FileNotFoundError:
        print("Warn: 'ollama' CLI not found. Assuming Ollama API is reachable at http://localhost:11434.")


def generate_with_ollama(model: str, prompt: str, url: str = "http://localhost:11434/api/generate") -> str:
    """Call Ollama generate API with a simple prompt and return the full response text."""
    payload = {"model": model, "prompt": prompt, "stream": False}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    resp.raise_for_status()
    data = resp.json()
    # standard response has key 'response'
    return data.get("response", "")


def process_tweets_with_ollama(user_or_handle: str, limit: int, model: str, system_instruction: str | None = None, mock: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch tweets and process each with an Ollama model.
    Returns a list of { created_at, id_str, full_text, analysis }.
    """
    # get_user_tweets returns either pretty-printed JSON (when as_json=True) or text; we need JSON
    raw = get_user_tweets(user_or_handle, limit=limit, as_json=True, mock=mock)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: wrap raw text as one pseudo tweet
        data = {"tweets": [{"full_text": raw}]}

    tweets = data.get("tweets", [])
    ensure_model_present(model)

    results: List[Dict[str, Any]] = []
    for idx, tw in enumerate(tweets, start=1):
        text = tw.get("full_text", "").strip()
        created = tw.get("created_at", "")
        tid = tw.get("id_str", "")
        if not text:
            continue

        prompt_parts = []
        if system_instruction:
            prompt_parts.append(system_instruction.strip())
        prompt_parts.append("Post:\n" + text)
        prompt_parts.append("\nTask: Provide a concise analysis (3-5 bullet points).")
        prompt = "\n\n".join(prompt_parts)

        try:
            analysis = generate_with_ollama(model=model, prompt=prompt)
        except Exception as e:
            analysis = f"<ollama_error: {e}>"

        results.append({
            "created_at": created,
            "id_str": tid,
            "full_text": text,
            "analysis": analysis,
        })

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze latest posts with an Ollama model.")
    parser.add_argument("user", nargs="?", help="Twitter numeric user_id or handle (e.g., 44196397 or @elonmusk)")
    parser.add_argument("--limit", type=int, default=10, help="Number of posts to fetch")
    parser.add_argument("--model", type=str, default="llama3.1:8b", help="Ollama model name/tag")
    parser.add_argument("--system", type=str, default=None, help="Optional system instruction to prepend")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of pretty text")
    parser.add_argument("--mock", action="store_true", help="Fetch posts in mock mode (no API calls)")
    parser.add_argument("--menu", action="store_true", help="Launch interactive menu")
    args = parser.parse_args()

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
