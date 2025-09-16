# Tweetscout / Ollama App

## Modules
- app/config.py: load env, defaults, paths
- app/api/twitter_client.py: Tweetscout client (mockable)
- app/ai/ollama_client.py: Ollama HTTP client
- app/rules/detector.py: extensible rule engine
- app/actions/handlers.py: example action for crypto tickers
- app/storage/jsonl_store.py: append-only JSONL storage
- app/services/pipeline.py: orchestrates fetch -> AI -> detect -> store
- app/cli.py: CLI entry point

## Setup
1) pip install -r requirements.txt
2) Create .env (optional):
   - TWITSCOUT_API_KEY=... (ignored in mock)
   - OLLAMA_MODEL=qwen3:4b
   - STORAGE_PATH=./data/events.jsonl
   - MOCK_MODE=true

## Run (mocked)
python -m app.cli @elonmusk --limit 10 --json
