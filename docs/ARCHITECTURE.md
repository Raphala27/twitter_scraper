# Architecture du Code - Post Migration OpenRouter

## Structure actuelle

```
twitter_scraper/
├── scraper.py                    # 🎯 POINT D'ENTRÉE PRINCIPAL
├── models_logic/
│   ├── __init__.py              # Package marker
│   ├── openrouter_logic.py      # 🧠 LOGIQUE OPENROUTER COMPLÈTE
│   ├── tools.py                 # 🔧 TOOLS DISPONIBLES
│   └── test_refactoring.py      # ✅ Tests de validation
├── utils_scraper.py             # 📡 Utilitaires de scraping
├── tests/
│   └── test_openrouter_tools.py # 🧪 Tests des tools
```

## Points d'entrée

### 🎯 Script principal : `scraper.py`
```bash
# Utilisation normale avec tools
python scraper.py @elonmusk --limit 5 --mock

# Mode legacy sans tools
python scraper.py @elonmusk --limit 5 --mock --no-tools

# Menu interactif
python scraper.py --menu
```

### 🧠 Logique OpenRouter : `models_logic/openrouter_logic.py`
- **Fonction principale** : `process_tweets_with_openrouter()`
- **Support des tools** : `generate_with_openrouter_tools()`
- **Fonction de base** : `generate_with_openrouter()`

### 🔧 Tools disponibles : `models_logic/tools.py`
- **`Tools.extract_unique_tickers()`** : Extraction de tickers crypto

## Flux de données

```
scraper.py 
    ↓ import
models_logic.openrouter_logic.process_tweets_with_openrouter()
    ↓ utilise
models_logic.tools.Tools.extract_unique_tickers()
    ↓ appelle
utils_scraper.UtilsScraper.get_user_tweets()
```

## Paramètres principaux

### `process_tweets_with_openrouter()`
- `user_or_handle`: Utilisateur Twitter à analyser
- `limit`: Nombre de tweets à traiter
- `model`: Modèle OpenRouter à utiliser
- `system_instruction`: Instructions système
- `mock`: Mode mock (pas d'API calls)
- `use_tools`: Active/désactive les tools

## Migration depuis Ollama

### ❌ Avant (Ollama)
```python
from models_logic.ollama_logic import process_tweets_with_ollama
```

### ✅ Maintenant (OpenRouter)
```python
from models_logic.openrouter_logic import process_tweets_with_openrouter
```

## Tests

### Validation de la migration
```bash
cd models_logic
python test_refactoring.py
```

### Tests complets des tools
```bash
python tests/test_openrouter_tools.py
```

## Migration réalisée

1. ✅ Migration complète vers OpenRouter.ai
2. ✅ Suppression des références Ollama
3. ✅ Tests de la nouvelle architecture
4. ✅ Documentation mise à jour

## Avantages de cette architecture

- **Cloud-based** : Plus besoin d'installation locale
- **Scalabilité** : Compatible Cloudflare Workers
- **Extensibilité** : Facile d'ajouter de nouveaux tools
- **Compatibilité** : Support des modes avec et sans tools
- **Point d'entrée unique** : `scraper.py` pour toutes les utilisations
- **Testabilité** : Tests séparés et modulaires
