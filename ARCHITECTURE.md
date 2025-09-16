# Architecture du Code - Post Refactoring

## Structure actuelle

```
twitter_scraper/
├── scraper.py                    # 🎯 POINT D'ENTRÉE PRINCIPAL
├── models_logic/
│   ├── __init__.py              # Package marker
│   ├── ollama_logic.py          # 🧠 LOGIQUE OLLAMA COMPLÈTE
│   ├── tools.py                 # 🔧 TOOLS DISPONIBLES
│   └── test_refactoring.py      # ✅ Tests de validation
├── utils_scraper.py             # 📡 Utilitaires de scraping
├── test_ollama_tools.py         # 🧪 Tests des tools
└── process_with_ollama.py       # ⚠️  OBSOLÈTE (à supprimer après validation)
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

### 🧠 Logique Ollama : `models_logic/ollama_logic.py`
- **Fonction principale** : `process_tweets_with_ollama()`
- **Support des tools** : `generate_with_ollama_tools()`
- **Fonction legacy** : `generate_with_ollama()`

### 🔧 Tools disponibles : `models_logic/tools.py`
- **`Tools.extract_unique_tickers()`** : Extraction de tickers crypto

## Flux de données

```
scraper.py 
    ↓ import
models_logic.ollama_logic.process_tweets_with_ollama()
    ↓ utilise
models_logic.tools.Tools.extract_unique_tickers()
    ↓ appelle
utils_scraper.UtilsScraper.get_user_tweets()
```

## Paramètres principaux

### `process_tweets_with_ollama()`
- `user_or_handle`: Utilisateur Twitter à analyser
- `limit`: Nombre de tweets à traiter
- `model`: Modèle Ollama à utiliser
- `system_instruction`: Instructions système
- `mock`: Mode mock (pas d'API calls)
- `use_tools`: **NOUVEAU** - Active/désactive les tools

## Migration depuis l'ancienne version

### ❌ Avant (obsolète)
```python
from process_with_ollama import process_tweets_with_ollama
```

### ✅ Maintenant
```python
from models_logic.ollama_logic import process_tweets_with_ollama
```

## Tests

### Validation du refactoring
```bash
cd models_logic
python test_refactoring.py
```

### Tests complets des tools
```bash
python test_ollama_tools.py
```

## Prochaines étapes

1. ✅ Valider que tout fonctionne avec les tests
2. ⚠️ Supprimer `process_with_ollama.py` après validation
3. 🔧 Ajouter d'autres tools si nécessaire
4. 📚 Mettre à jour la documentation utilisateur

## Avantages de cette architecture

- **Séparation claire** : Logique Ollama isolée dans `models_logic/`
- **Extensibilité** : Facile d'ajouter de nouveaux tools
- **Compatibilité** : Support des modes avec et sans tools
- **Point d'entrée unique** : `scraper.py` pour toutes les utilisations
- **Testabilité** : Tests séparés et modulaires
