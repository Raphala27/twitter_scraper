# Contributing to Twitter Scraper

Thank you for your interest in contributing to the Twitter Scraper project! This guide will help you get started.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/twitter_scraper.git
   cd twitter_scraper
   ```

2. **Set up development environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest pylint black isort
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with test API keys (optional for mock mode)
   ```

4. **Install Ollama** (for AI functionality):
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama and pull model
   ollama serve
   ollama pull qwen3:14b
   ```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python tests/test_ollama_tools.py
python tests/test_tools.py

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 📋 Development Guidelines

### Code Style

We use the following tools for code quality:

1. **Black** for code formatting:
   ```bash
   black . --line-length 88
   ```

2. **isort** for import sorting:
   ```bash
   isort . --profile black
   ```

3. **Pylint** for code analysis:
   ```bash
   pylint *.py models_logic/ coincap_api/
   ```

### Code Standards

- **Line length**: Maximum 88 characters
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Add type hints for function parameters and returns
- **Error handling**: Use appropriate exception handling
- **Logging**: Use print statements for user output, consider logging for debug

### Example Code Style

```python
from typing import List, Dict, Optional
import requests

def process_tweets(
    user_handle: str, 
    limit: int = 10, 
    mock_mode: bool = False
) -> List[Dict[str, Any]]:
    """
    Process tweets from a given user handle.
    
    Args:
        user_handle: Twitter username (with or without @)
        limit: Maximum number of tweets to process
        mock_mode: Use mock data instead of API calls
        
    Returns:
        List of processed tweet data dictionaries
        
    Raises:
        ValueError: If user_handle is empty
        requests.RequestException: If API call fails
    """
    if not user_handle:
        raise ValueError("User handle cannot be empty")
        
    # Implementation here
    pass
```

## 🔧 Project Structure

### Core Components

- `scraper.py` - Main entry point and CLI
- `models_logic/` - AI integration and tools
- `coincap_api/` - Price data and position simulation
- `utils_scraper.py` - Twitter scraping utilities
- `tests/` - Test suite
- `docs/` - Documentation
- `examples/` - Usage examples

### Adding New Features

1. **New AI Tools**: Add to `models_logic/tools.py`
2. **New API Integrations**: Create new module in appropriate package
3. **New Analysis Types**: Extend `models_logic/ollama_logic.py`
4. **New Simulation Features**: Extend `coincap_api/position_simulator.py`

## 🧪 Testing

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **Mock Tests**: Test with mock data
4. **End-to-End Tests**: Test complete workflows

### Writing Tests

```python
import unittest
from unittest.mock import patch, MagicMock

class TestPositionSimulator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.simulator = PositionSimulator(mock_mode=True)
    
    def test_simulate_position_basic(self):
        """Test basic position simulation."""
        position_data = {
            "ticker": "BTC",
            "sentiment": "long",
            "leverage": "10",
            "entry_price": 63000,
            "stop_loss": 60000,
            "take_profits": [65000, 67000],
            "timestamp": "2024-04-16T23:35:00Z"
        }
        
        result = self.simulator.simulate_position(position_data, capital=100.0)
        
        self.assertIn("results", result)
        self.assertIsInstance(result["results"]["final_pnl_dollar"], float)
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling."""
        mock_get.side_effect = requests.RequestException("API Error")
        
        with self.assertRaises(requests.RequestException):
            # Test code that should raise exception
            pass
```

### Test Data

Use realistic test data that matches actual API responses:

```python
MOCK_TWEET_DATA = {
    "full_text": "#BTC/USDT LONG\nLeverage: 10x\nEntry: 63000\nTP: 65000, 67000\nSL: 60000",
    "created_at": "2024-04-16T23:35:00Z",
    "id_str": "1234567890"
}

MOCK_POSITION_DATA = {
    "ticker": "BTC",
    "sentiment": "long", 
    "leverage": "10",
    "entry_price": 63000,
    "take_profits": [65000, 67000],
    "stop_loss": 60000,
    "timestamp": "2024-04-16T23:35:00Z"
}
```

## 📝 Documentation

### Documentation Standards

- **README**: Keep main README concise and focused
- **API Docs**: Document all public functions and classes
- **Usage Examples**: Provide practical examples
- **Architecture**: Explain design decisions

### Writing Documentation

- Use clear, simple language
- Include code examples
- Add screenshots for CLI tools
- Keep examples up-to-date with code changes

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Test with latest version
3. Try in mock mode to isolate API issues
4. Check logs and error messages

### Bug Report Template

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Run command: `python scraper.py ...`
2. Expected behavior: ...
3. Actual behavior: ...

**Environment**
- Python version: 3.x
- OS: macOS/Linux/Windows
- Ollama version: x.x.x
- Mock mode: Yes/No

**Error Output**
```
Paste error output here
```

**Additional Context**
Add any other context about the problem.
```

## 🚀 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the requested feature.

**Use Case**
Explain why this feature would be useful.

**Proposed Implementation**
If you have ideas about how to implement this.

**Alternatives Considered**
Other approaches you considered.
```

## 📦 Pull Requests

### PR Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** the test suite: `python -m pytest`
6. **Run** linting: `pylint *.py models_logic/ coincap_api/`
7. **Update** documentation if needed
8. **Submit** a pull request

### PR Guidelines

- **Small, focused changes**: One feature or fix per PR
- **Clear description**: Explain what and why
- **Tests included**: Add tests for new functionality
- **Documentation updated**: Update docs if needed
- **Backwards compatible**: Don't break existing APIs

### PR Template

```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

**Testing**
- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release notes
6. Tag release: `git tag v1.2.3`
7. Push to repository

## 💬 Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: For security issues or private matters

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and improve
- Follow community guidelines

Thank you for contributing to Twitter Scraper! 🎉
