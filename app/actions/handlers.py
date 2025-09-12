from __future__ import annotations
from typing import Dict, Any


def tag_crypto_action(post: Dict[str, Any]) -> Dict[str, Any]:
    """Example action executed when a crypto ticker is detected."""
    return {
        "id": post.get("id_str"),
        "created_at": post.get("created_at"),
        "flag": "crypto_ticker_detected",
    }
