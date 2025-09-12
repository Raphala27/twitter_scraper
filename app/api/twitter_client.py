from __future__ import annotations
import hashlib
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import requests


class TwitterClient:
    """Tweetscout-backed client (mockable).

    Methods:
      - handle_to_id(handle) -> str
      - user_tweets(user_id, limit) -> { tweets: [...], next_cursor: str | None }
    """

    def __init__(self, api_key: Optional[str], mock: bool = True) -> None:
        self.api_key = api_key
        self.mock = mock
        self.base = "https://api.tweetscout.io/v2"

    def _headers(self) -> Dict[str, str]:
        return {"Accept": "application/json", "ApiKey": self.api_key or "mock-key", "Content-Type": "application/json"}

    def handle_to_id(self, handle: str) -> Optional[str]:
        h = handle.lstrip("@")
        if h.isdigit():
            return h
        if self.mock:
            m = hashlib.md5(h.encode("utf-8")).hexdigest()
            return str(int(m[:12], 16) % 10_000_000_000)
        url = f"{self.base}/handle-to-id/{h}"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        if resp.status_code != 200:
            return None
        data = resp.json()
        return str(data.get("id") or data.get("id_str")) if (data.get("id") or data.get("id_str")) else None

    def user_tweets(self, user_id: str, limit: int = 2, cursor: Optional[str] = None, link: Optional[str] = None) -> Dict[str, Any]:
        if self.mock:
            # deterministic stable mock batch
            collected: List[Dict[str, Any]] = []
            page_size = min(20, max(1, limit))
            seed_input = f"{user_id}:{cursor or '0'}"
            seed = int(hashlib.md5(seed_input.encode("utf-8")).hexdigest()[:12], 16)
            rnd = random.Random(seed)
            base_shift_days = int(hashlib.md5(user_id.encode("utf-8")).hexdigest()[:6], 16) % 365
            base_dt = datetime(2025, 1, 1) - timedelta(days=base_shift_days)
            templates = [
                "[MOCK] Update #{idx} for user {user_id}: shipping new feature today.",
                "[MOCK] Thoughts #{idx}: markets, tech, and a bit of fun.",
                "[MOCK] Quick note #{idx} — remember to stay hydrated.",
                "[MOCK] Dev log #{idx}: performance improved by 23% on latest build.",
                "[MOCK] AMA #{idx}: answering top 3 questions from the community.",
            ]
            for i in range(page_size):
                idx = (int(cursor.split('_')[-1]) if cursor else 0) + i + 1
                tid = hashlib.md5(f"{user_id}:{idx}".encode("utf-8")).hexdigest()[:16]
                t_idx = int(hashlib.md5(f"template:{user_id}:{idx}".encode("utf-8")).hexdigest()[:6], 16) % len(templates)
                text = templates[t_idx].format(idx=idx, user_id=user_id)
                created_at = (base_dt - timedelta(minutes=idx * (5 + rnd.randint(0, 3)))).isoformat() + "Z"
                collected.append({
                    "id_str": tid,
                    "created_at": created_at,
                    "full_text": text,
                })
            next_cursor = None if page_size >= limit else f"mock_cursor_{page_size}"
            return {"tweets": collected[:limit], "next_cursor": next_cursor}
        # real API
        import json as _json
        payload: Dict[str, Any] = {"user_id": user_id}
        if cursor:
            payload["cursor"] = cursor
        if link:
            payload["link"] = link
        url = f"{self.base}/user-tweets"
        resp = requests.post(url, headers=self._headers(), data=_json.dumps(payload), timeout=45)
        resp.raise_for_status()
        return resp.json()
