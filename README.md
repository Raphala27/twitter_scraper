# Twitter Scraper with AI Analysis

A Python application that scrapes Twitter data and analyzes cryptocurrency trading signals using AI (Ollama) with position simulation capabilities.

## 🚀 Features

- **Twitter Scraping**: Fetch tweets from any Twitter account
- **AI Analysis**: Extract cryptocurrency trading signals using Ollama
- **Position Simulation**: Simulate trading positions with historical price data
- **Mock Mode**: Test without API calls
- **Multiple Output Formats**: JSON or formatted text output
- **Comprehensive Testing**: Full test suite included

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Raphala27/twitter_scraper.git
   cd twitter_scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Install Ollama** (if not already installed):
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

5. **Start Ollama and pull a model**:
   ```bash
   ollama serve
   ollama pull qwen3:14b
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required for real Twitter data (optional in mock mode)
TWITSCOUT_API_KEY=your_twitscout_api_key

# Required for sentiment validation (optional in mock mode)
COINGECKO_API_KEY=your_coingecko_api_key

# Required for position simulation (optional in mock mode)
COINCAP_API_KEY=your_coincap_api_key

# Optional: Ollama configuration
OLLAMA_HOST=http://localhost:11434
```

## 🎯 Quick Start

### Basic Usage

```bash
# Analyze tweets with AI (mock mode)
python scraper.py @trader --limit 5 --mock-scraping --mock-positions

# Analyze and validate sentiment predictions over time
python scraper.py @influencer --limit 3 --mock-scraping --validate-sentiment --api coingecko

# Analyze and simulate trading positions
python scraper.py @trader --limit 3 --mock --simulate --sim-hours 2

# Real data analysis (requires API keys)
python scraper.py @trader --limit 5 --simulate
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `user` | Twitter handle or user ID | `@trader` |
| `--limit` | Number of tweets to analyze | `2` |
| `--model` | Ollama model to use | `qwen3:14b` |
| `--mock-scraping` | Use mock tweets (no Twitter API) | `False` |
| `--mock-positions` | Use mock prices (no CoinCap API) | `False` |
| `--mock` | Enable both mock modes | `False` |
| `--simulate` | Simulate trading positions | `False` |
| `--sim-hours` | Hours to simulate | `24` |
| `--validate-sentiment` | Validate sentiment predictions over time | `False` |
| `--api` | Cryptocurrency API (coincap/coingecko) | `coincap` |
| `--json` | Output in JSON format | `False` |
| `--no-tools` | Disable AI tools (legacy mode) | `False` |

## 📊 Examples

### Example 1: Sentiment Validation Analysis
```bash
python scraper.py @crypto_influencer --limit 3 --mock-scraping --validate-sentiment --api coingecko
```

**Output:**
```
🐦 CONTENU DES TWEETS 
📝 TWEET #1: TRX is cheap and fast. Bullish on Tron...

📊 ANALYSE CONSOLIDÉE 
{
  "account": "@crypto_influencer",
  "total_tweets": 3,
  "analysis_summary": {
    "total_sentiments": 3,
    "bullish_sentiments": 2,
    "bearish_sentiments": 1,
    "neutral_sentiments": 0
  },
  "tweets_analysis": [...]
}

⏰ VALIDATION TEMPORELLE 
🎯 Validation des sentiments d'influenceur...
🔍 Validation sentiment pour TRX (bullish)
    1h: ✅ +2.34% (Prédit: bullish, Réel: bullish)
   24h: ❌ -1.78% (Prédit: bullish, Réel: neutral)
    7d: ✅ +5.21% (Prédit: bullish, Réel: bullish)

🎯 ANALYSE FINALE DES PRÉDICTIONS 
👤 Influenceur analysé: @crypto_influencer
📊 Évaluation globale (24h): 👍 Bonne (66.7%)
📈 Score moyen de précision: 73.5/100

💡 Recommandations:
   ✨ Cet influenceur montre de bonnes capacités prédictives
   ✨ Ses analyses peuvent être considérées comme fiables

📄 DICTIONNAIRE FINAL COMPLET 
🔧 Dictionnaire structuré pour utilisation programmatique:
{
  "account": "@crypto_influencer",
  "sentiment_validation": {
    "validation_status": "success",
    "summary": {
      "accuracy_24h_percent": 66.7,
      "avg_score_24h": 73.5
    }
  }
}
```

### Example 2: Mock Trading Analysis
```bash
python scraper.py @crypto_trader --limit 3 --mock --simulate --sim-hours 1
```

**Output:**
```
🐦 CONTENU DES TWEETS 
📝 TWEET #1: #BTC/USDT LONG Signal type: LONG...

📊 ANALYSE CONSOLIDÉE 
{
  "account": "@crypto_trader",
  "total_tweets": 3,
  "analysis_summary": {
    "total_positions": 3,
    "long_positions": 2,
    "short_positions": 1
  },
  "tweets_analysis": [...]
}

🎯 RÉSULTATS PERFORMANCES 
💰 Capital total: $300.00
📈 P&L total: +24.33$
📊 ROI: +8.11%
```

### Example 2: Real Data with Position Simulation
```bash
python scraper.py @actual_trader --limit 5 --simulate --sim-hours 6
```

## 🎯 New Features

### 🔍 Sentiment Validation
Validate influencer predictions over time with temporal analysis:

```bash
# Validate sentiment predictions with CoinGecko API
python scraper.py @influencer --validate-sentiment --api coingecko --mock-scraping

# Real-time validation (requires COINGECKO_API_KEY)
python scraper.py @real_influencer --validate-sentiment --api coingecko --limit 10
```

**Features:**
- ⏰ **Multi-timeframe validation**: 1h, 24h, 7d accuracy tracking
- 📊 **Performance scoring**: Detailed accuracy metrics per prediction
- 🎯 **Influencer assessment**: Global performance evaluation with recommendations
- 📄 **Structured output**: Complete JSON dictionary with validation results
- 🔬 **Detailed analysis**: Per-tweet breakdown with price movements and accuracy scores

## 🏗️ Architecture

```
twitter_scraper/
├── scraper.py              # Main entry point
├── utils_scraper.py        # Twitter scraping utilities
├── models_logic/           # AI analysis
│   ├── ollama_logic.py     # Ollama integration
│   └── tools.py            # AI tools for crypto analysis
├── coincap_api/            # Price data and simulation
│   ├── fetch_prices.py     # Price fetching
│   ├── position_calculator.py
│   └── position_simulator.py
├── tests/                  # Test suite
├── docs/                   # Documentation
└── examples/               # Usage examples
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python tests/test_ollama_tools.py
python tests/test_tools.py
```

## 📚 Documentation

- [Usage Guide](docs/USAGE.md) - Detailed usage examples
- [API Reference](docs/API.md) - API documentation
- [Architecture](docs/ARCHITECTURE.md) - Technical details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🛠️ Troubleshooting

### Common Issues

**"Ollama connection error"**
- Ensure Ollama is running: `ollama serve`
- Check if the model exists: `ollama list`

**"API key not found"**
- Verify `.env` file exists and contains valid keys
- For testing, use mock modes: `--mock`

**"No cryptocurrency data found"**
- Check if the Twitter account posts trading signals
- Verify the AI model can extract trading data
- Use `--no-tools` for legacy mode

For more help, see our [troubleshooting guide](docs/TROUBLESHOOTING.md).

