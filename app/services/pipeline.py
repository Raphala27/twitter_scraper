from __future__ import annotations
from typing import Dict, Any, List

from app.config import load_config
from app.api.twitter_client import TwitterClient
from app.ai.ollama_client import OllamaClient
from app.rules.detector import RulesDetector, DetectionRule
from app.actions.handlers import tag_crypto_action
from app.storage.jsonl_store import JSONLStore


def build_detector() -> RulesDetector:
    detector = RulesDetector()
    # Simple crypto ticker pattern example: $BTC, BTC, ETH, $SOL
    detector.register(DetectionRule(
        name="crypto_ticker",
        pattern=r"\b(?:\$?[A-Z]{2,6}|bitcoin|ethereum|solana)\b",
        action=tag_crypto_action,
    ))
    return detector


def run_pipeline(user: str, limit: int) -> Dict[str, Any]:
    cfg = load_config()
    tw = TwitterClient(api_key=cfg.tweetscout_api_key, mock=True)
    ollama = OllamaClient(model=cfg.ollama_model)
    ollama.ensure_model()
    store = JSONLStore(cfg.storage_path)
    detector = build_detector()

    # Fetch posts (mocked)
    resolved = tw.handle_to_id(user)
    if not resolved:
        return {"error": "cannot resolve user"}

    # Gather N posts (may require pagination)
    collected: List[Dict[str, Any]] = []
    cursor = None
    while len(collected) < limit:
        batch = tw.user_tweets(resolved, limit=limit - len(collected), cursor=cursor)
        posts = batch.get("tweets", [])
        if not posts:
            break
        collected.extend(posts)
        cursor = batch.get("next_cursor")
        if not cursor:
            break

    # Analyze + detect rules; persist findings
    events: List[Dict[str, Any]] = []
    for p in collected[:limit]:
        text = p.get("full_text", "")
        prompt = f"Analyze the following post and extract potential crypto tickers or flags.\n\nPost:\n{text}\n\nReturn a concise list."
        analysis = ollama.generate(prompt=prompt, stream=False)
        matches = detector.detect(p)
        for m in matches:
            record = {
                "user": user,
                "post_id": p.get("id_str"),
                "created_at": p.get("created_at"),
                "analysis": analysis,
                "rule": m["rule"],
                "result": m["result"],
            }
            store.append(record)
            events.append(record)

    return {"processed": len(collected[:limit]), "events": events}
