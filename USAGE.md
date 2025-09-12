# Usage Guide for `process_with_ollama.py`

This script analyzes tweets using the Ollama model. Below are the different ways you can run the script and the arguments you can use.

## Basic Command
```bash
python process_with_ollama.py
```

## Arguments

### Positional Arguments
- `user` (optional): The Twitter numeric user ID or handle. Example: `44196397` or `@elonmusk`. Defaults to `swissborg`.

### Optional Arguments
- `--limit`: Number of tweets to fetch. Defaults to `2`.
  ```bash
  python process_with_ollama.py --limit 5
  ```

- `--model`: The Ollama model name/tag. Defaults to `koesn/mistral-7b-instruct:latest`.
  ```bash
  python process_with_ollama.py --model llama3.1:8b
  ```

- `--system`: Optional system instruction to prepend to the prompt. Defaults to:
  ```
  Recover the crypto and thickers. give me back only a list of it in python only a list. like following: ['BTC', 'ETH'] but do not add them if they are not present in the post.
  ```
  Example:
  ```bash
  python process_with_ollama.py --system "Extract hashtags from the tweets."
  ```

- `--json`: Output the results in JSON format. Defaults to pretty text output.
  ```bash
  python process_with_ollama.py --json
  ```

- `--mock`: Fetch posts in mock mode (no API calls).
  ```bash
  python process_with_ollama.py --mock
  ```

- `--menu`: Launch the interactive menu.
  ```bash
  python process_with_ollama.py --menu
  ```

## Examples

### Fetch and Analyze Tweets for a Specific User
```bash
python process_with_ollama.py @elonmusk --limit 10 --model llama3.1:8b
```

### Use Mock Mode
```bash
python process_with_ollama.py --mock
```

### Output Results in JSON Format
```bash
python process_with_ollama.py @elonmusk --json
```

### Launch Interactive Menu
```bash
python process_with_ollama.py --menu
```

### Use a Custom System Instruction
```bash
python process_with_ollama.py @elonmusk --system "Extract hashtags from the tweets."
```
