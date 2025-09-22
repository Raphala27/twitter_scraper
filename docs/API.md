# API Reference

This document provides detailed information about the Twitter Scraper API and its components.

## Core Functions

### `process_tweets_with_ollama()`

Main function for processing tweets with AI analysis.

**Location**: `models_logic/ollama_logic.py`

```python
def process_tweets_with_ollama(
    user_or_handle: str,
    limit: int = 2,
    model: str = "qwen3:14b",
    system_instruction: str = None,
    mock: bool = False,
    use_tools: bool = True
) -> List[Dict]
```

**Parameters:**
- `user_or_handle` (str): Twitter username or handle (e.g., "@trader" or "trader")
- `limit` (int): Number of tweets to process (default: 2)
- `model` (str): Ollama model name (default: "qwen3:14b")
- `system_instruction` (str): Custom system prompt for AI analysis
- `mock` (bool): Use mock data instead of real API calls (default: False)
- `use_tools` (bool): Enable AI tools for structured extraction (default: True)

**Returns:**
- `List[Dict]`: List of analysis results including consolidated analysis

**Example:**
```python
from models_logic.ollama_logic import process_tweets_with_ollama

results = process_tweets_with_ollama(
    user_or_handle="@trader",
    limit=5,
    mock=True,
    use_tools=True
)
```

## Position Simulation

### `PositionSimulator`

Class for simulating trading positions with historical price data.

**Location**: `coincap_api/position_simulator.py`

```python
class PositionSimulator:
    def __init__(self, api_key: str = None, mock_mode: bool = False)
```

**Methods:**

#### `simulate_position()`
```python
def simulate_position(
    self, 
    position_data: Dict[str, Any], 
    capital: float = 100.0, 
    simulation_hours: int = 24,
    verbose: bool = True
) -> Dict[str, Any]
```

Simulates a single trading position.

**Parameters:**
- `position_data` (Dict): Position details (ticker, sentiment, leverage, etc.)
- `capital` (float): Capital amount to invest (default: 100.0)
- `simulation_hours` (int): Hours to simulate (default: 24)
- `verbose` (bool): Print detailed output (default: True)

#### `simulate_all_positions()`
```python
def simulate_all_positions(
    self, 
    consolidated_analysis: Dict[str, Any], 
    capital_per_position: float = 100.0
) -> Dict[str, Any]
```

Simulates all positions from consolidated analysis.

## AI Tools

### `Tools` Class

**Location**: `models_logic/tools.py`

#### `extract_unique_tickers()`
```python
@staticmethod
def extract_unique_tickers(text: str) -> List[str]
```

Extracts cryptocurrency tickers from text using regex patterns.

**Parameters:**
- `text` (str): Input text to analyze

**Returns:**
- `List[str]`: List of unique cryptocurrency tickers found

## Data Structures

### Tweet Analysis Result

```python
{
    "analysis": {
        "cryptos": [
            {
                "ticker": "BTC",
                "sentiment": "long",
                "leverage": "10",
                "take_profits": [65000, 67000, 70000],
                "stop_loss": 60000,
                "entry_price": 63000
            }
        ],
        "timestamp": "2024-04-16T23:35:00Z",
        "tweet_id": "12345"
    },
    "full_text": "Tweet content...",
    "created_at": "2024-04-16T23:35:00Z",
    "id_str": "12345"
}
```

### Consolidated Analysis

```python
{
    "account": "@trader",
    "total_tweets": 5,
    "analysis_summary": {
        "total_positions": 5,
        "long_positions": 3,
        "short_positions": 2
    },
    "tweets_analysis": [
        {
            "tweet_number": 1,
            "timestamp": "2024-04-16T23:35:00Z",
            "ticker": "BTC",
            "sentiment": "long",
            "leverage": "10",
            "take_profits": [65000, 67000, 70000],
            "stop_loss": 60000,
            "entry_price": 63000
        }
    ]
}
```

### Simulation Result

```python
{
    "total_capital": 500.0,
    "total_pnl": 45.67,
    "roi_percent": 9.13,
    "successful_simulations": 4,
    "total_simulations": 5
}
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TWITSCOUT_API_KEY` | Twitter API key | No (if using mock) | None |
| `COINCAP_API_KEY` | CoinCap API key | No (if using mock) | None |
| `OLLAMA_HOST` | Ollama server URL | No | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default Ollama model | No | `qwen3:14b` |

### Supported Cryptocurrencies (Mock Mode)

The following cryptocurrencies are supported in mock mode:

- BTC, ETH, SOL, ADA, XRP, DOGE, MATIC, DOT
- UNI, LTC, LINK, AVAX, ATOM, BNB, NEAR, FTM
- ALGO, ICP, APT, ARB

## Error Handling

### Common Exceptions

- `requests.RequestException`: Network errors when calling APIs
- `json.JSONDecodeError`: Invalid JSON response from APIs
- `KeyError`: Missing required fields in data structures
- `ValueError`: Invalid parameter values

### Error Response Format

```python
{
    "error": "Description of the error",
    "details": "Additional error details",
    "timestamp": "2024-04-16T23:35:00Z"
}
```

## Rate Limits

- **TwitScout API**: Check your plan limits
- **CoinCap API**: 500 requests/minute for free tier
- **Ollama**: No limits (local installation)

## Testing

### Mock Mode

Use mock mode for testing without API calls:

```python
# Mock scraping only
results = process_tweets_with_ollama("@trader", mock=True)

# Mock position simulation
simulator = PositionSimulator(mock_mode=True)
```

### Integration Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_ollama_tools.py
```
