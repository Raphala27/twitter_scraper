from __future__ import annotations
import json
import subprocess
import requests
from typing import Optional


class OllamaClient:
    """Minimal wrapper for Ollama HTTP API."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def ensure_model(self) -> None:
        try:
            show = subprocess.run(["ollama", "show", self.model], capture_output=True)
            if show.returncode != 0:
                subprocess.run(["ollama", "pull", self.model], check=False)
        except FileNotFoundError:
            # CLI not available; assume server is running
            pass

    def generate(self, prompt: str, stream: bool = False) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": stream}
        resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
