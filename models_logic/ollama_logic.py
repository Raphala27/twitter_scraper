import json
import subprocess
import requests
from typing import List, Dict, Any
from utils_scraper import UtilsScraper as us

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
    raw = us.get_user_tweets(user_or_handle, limit=limit, as_json=True, mock=mock)
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
        prompt_parts.append("\nRecover the crypto and thickers. give me back only a list of it in python only a list. like following: ['BTC', 'ETH'] but do not add them if they are not present in the post. Do not give any other explaination and don;t even write sentences. Be very precise and don't forget a crypto ticker in the post")
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
