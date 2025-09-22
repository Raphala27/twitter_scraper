# Options Mock du Scraper

Ce document explique les nouvelles options mock disponibles dans le scraper.

## Options disponibles

### 1. `--mock-scraping`
- **Usage** : Active uniquement le mode mock pour le scraping de tweets
- **Effet** : Utilise des tweets générés automatiquement au lieu d'appeler l'API Twitter
- **Exemple** : `python3 scraper.py @trader --limit 3 --mock-scraping`

### 2. `--mock-positions`
- **Usage** : Active uniquement le mode mock pour les simulations de positions
- **Effet** : Utilise des prix générés automatiquement au lieu d'appeler l'API CoinCap
- **Exemple** : `python3 scraper.py @trader --simulate --mock-positions`

### 3. `--mock`
- **Usage** : Active les deux modes mock (scraping + positions)
- **Effet** : Équivalent à `--mock-scraping --mock-positions`
- **Exemple** : `python3 scraper.py @trader --simulate --mock`

## Cas d'usage

### Test du scraping seulement
```bash
python3 scraper.py @trader --limit 5 --mock-scraping
```
- Tweets mock
- API CoinCap réelle (si simulation activée)

### Test de la simulation seulement
```bash
python3 scraper.py @trader --simulate --mock-positions
```
- Tweets réels depuis l'API
- Simulation avec prix mock

### Test complet mock
```bash
python3 scraper.py @trader --simulate --mock
```
- Tweets mock
- Simulation avec prix mock

### Production avec données réelles
```bash
python3 scraper.py @trader --simulate
```
- Tweets réels depuis l'API
- Simulation avec prix réels CoinCap

## Avantages

1. **Développement rapide** : Pas de limite d'API pendant les tests
2. **Tests isolés** : Tester chaque composant indépendamment
3. **Données cohérentes** : Résultats reproductibles pour les tests
4. **Économie d'API** : Éviter les coûts pendant le développement
