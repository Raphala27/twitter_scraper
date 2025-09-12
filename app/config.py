import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    tweetscout_api_key: str | None
    ollama_model: str
    storage_path: Path
    mock_mode: bool


def load_config() -> AppConfig:
    tweetscout_api_key = os.getenv("TWITSCOUT_API_KEY")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    storage_path = Path(os.getenv("STORAGE_PATH", "data/events.jsonl")).resolve()
    mock_mode = os.getenv("MOCK_MODE", "true").lower() in {"1", "true", "yes"}
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    return AppConfig(
        tweetscout_api_key=tweetscout_api_key,
        ollama_model=ollama_model,
        storage_path=storage_path,
        mock_mode=mock_mode,
    )
