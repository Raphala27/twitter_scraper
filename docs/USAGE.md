# Usage Guide for Twitter Scraper with OpenRouter Tools

This script analyzes tweets using the OpenRouter.ai models with integrated tools for crypto ticker extraction. Below are the different ways you can run the script and the arguments you can use.

## Basic Command
```bash
python scraper.py
```

## Arguments

### Positional Arguments
- `user` (optional): The Twitter numeric user ID or handle. Example: `44196397` or `@elonmusk`. Defaults to `swissborg`.

### Optional Arguments
- `--limit`: Number of tweets to fetch. Defaults to `2`.
  ```bash
  python scraper.py --limit 5
  ```

- `--model`: The OpenRouter model name/tag. Defaults to `x-ai/grok-4-fast:free`.
  ```bash
  python scraper.py --model llama3.1:8b
  ```

- `--system`: Optional system instruction to prepend to the prompt. Defaults to:
  ```
  You are a crypto analyst. Extract cryptocurrency information from social media posts.
  ```
  Example:
  ```bash
  python scraper.py --system "Extract hashtags from the tweets."
  ```

- `--json`: Output the results in JSON format. Defaults to pretty text output.
  ```bash
  python scraper.py --json
  ```

- `--mock`: Fetch posts in mock mode (no API calls).
  ```bash
  python scraper.py --mock
  ```

- `--no-tools`: Disable tools usage and use legacy mode.
  ```bash
  python scraper.py --no-tools
  ```

- `--menu`: Launch the interactive menu.
  ```bash
  python scraper.py --menu
  ```

## Examples

### Fetch and Analyze Tweets with Tools (Default)
```bash
python scraper.py @elonmusk --limit 10 --model llama3.1:8b
```

### Use Mock Mode with Tools
```bash
python scraper.py --mock --limit 5
```

### Output Results in JSON Format
```bash
python scraper.py @elonmusk --json --mock
```

### Launch Interactive Menu
```bash
python scraper.py --menu
```

### Use Legacy Mode (No Tools)
```bash
python scraper.py @elonmusk --no-tools --mock
```

### Use a Custom System Instruction
```bash
python scraper.py @elonmusk --system "Focus on technical analysis and price predictions."
```

## Tools Integration

The script now includes integrated tools for:
- **Crypto Ticker Extraction**: Automatically extracts cryptocurrency tickers from text using the `extract_crypto_tickers` tool

When tools are enabled (default), the model can automatically call these tools when analyzing tweets, providing more accurate and structured extraction of cryptocurrency information.

## Testing Tools

To test the tools functionality directly:
```bash
python test_openrouter_tools.py
```
