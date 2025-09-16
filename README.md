## Analyze posts with Ollama
## User info (Tweetscout)
# Twitter Scraper avec TwitScoot API

Ce script Python permet de récupérer les derniers tweets d'un compte Twitter en utilisant l'API TwitScoot.

## Installation

1. Assurez-vous d'avoir Python 3.7+ installé
2. Installez les dépendances:
```bash
pip install requests python-dotenv
```

## Configuration

1. Obtenez votre clé API depuis [TwitScoot](https://tweetscout.io)
2. Créez un fichier `.env` dans le répertoire du projet:
```bash
TWITSCOUT_API_KEY=votre_cle_api_ici
```

## Utilisation

### Script principal (corrigé selon la documentation TwitScoot)
```bash
python twitter_scraper.py username --limit 10 --json
```

### Script avec gestion d'erreurs améliorée
```bash
python twitter_scraper_final.py username --limit 10 --json
```

### Paramètres
- `username`: Le nom d'utilisateur Twitter (sans le '@')
- `--limit`: Nombre de tweets à récupérer (max 100, défaut: 10)
- `--json`: Afficher les données complètes en JSON

## Exemples

```bash
# Récupérer 5 tweets de @elonmusk
python twitter_scraper.py elonmusk --limit 5

# Récupérer 20 tweets en format JSON
python twitter_scraper.py elonmusk --limit 20 --json
```

## API TwitScoot - Format correct

Selon la documentation officielle TwitScoot, l'API utilise:

- **Méthode**: POST (pas GET)
- **URL**: `https://api.tweetscout.io/v2/user-tweets`
- **Headers**: 
  - `Accept: application/json`
  - `ApiKey: votre_cle_api`
  - `Content-Type: application/json`
- **Body**: JSON avec `link` et `user_id`

### Exemple de requête cURL:
```bash
curl --request POST \
  --url https://api.tweetscout.io/v2/user-tweets \
  --header 'Accept: application/json' \
  --header 'ApiKey: votre_cle_api' \
  --header 'Content-Type: application/json' \
  --data '{
    "link": "https://twitter.com/username",
    "user_id": "username"
  }'
```

## Résolution des problèmes

### Erreur "missing key in request header"
✅ **RÉSOLU** - Le script utilise maintenant le bon format d'en-tête `ApiKey` selon la documentation TwitScoot.

### Erreur 500 "Internal server error"
Cette erreur peut indiquer:
1. Le `user_id` doit être l'ID numérique Twitter au lieu du nom d'utilisateur
2. Le compte Twitter n'existe pas ou est privé
3. Problème temporaire avec l'API TwitScoot

### Erreur "La clé API n'est pas définie"
1. Vérifiez que le fichier `.env` existe
2. Vérifiez que la clé API est correctement définie dans le fichier `.env`
3. Assurez-vous que la clé API est valide et active

### Erreur 403 Forbidden
- Vérifiez que votre clé API est correcte
- Vérifiez que votre compte TwitScoot a les permissions nécessaires
- Contactez le support TwitScoot si le problème persiste

## Fichiers

- `twitter_scraper.py`: Script principal corrigé selon la documentation TwitScoot
- `twitter_scraper_corrected.py`: Version alternative avec le même format
- `twitter_scraper_final.py`: Script avec gestion d'erreurs améliorée (formats multiples)
- `twitter_scraper_old.py`: Sauvegarde de l'ancienne version
- `twitter_scraper_backup.py`: Sauvegarde du script original
- `.env`: Fichier de configuration (à créer)
- `README.md`: Ce fichier

## Notes importantes

- Le script utilise maintenant le format d'API correct selon la documentation TwitScoot
- Méthode POST avec headers `ApiKey` au lieu de `Authorization`
- URL corrigée: `/v2/user-tweets` au lieu de `/v2/user/tweets`
- Le champ `full_text` est utilisé au lieu de `text` pour extraire le contenu des tweets
- Si vous obtenez une erreur 500, vous devrez peut-être utiliser l'ID numérique Twitter au lieu du nom d'utilisateur

## Prochaines étapes

Si vous continuez à avoir des erreurs 500:
1. Essayez d'utiliser l'ID numérique Twitter au lieu du nom d'utilisateur
2. Vérifiez que le compte Twitter existe et est public
3. Contactez le support TwitScoot pour obtenir de l'aide

### Usage
```bash
python tweetscout_user_info.py 44196397
```

- Endpoint: GET /info/id/{user_id}
- Auth header: ApiKey: <your_key>
- Docs: https://api.tweetscout.io/v2/docs/#/paths/info-id-user_id/get


### Usage
```bash
# Analyze 20 latest posts from a handle with a specific model
python process_with_ollama.py @elonmusk --limit 20 --model llama3.1:8b

# Output JSON
python process_with_ollama.py 44196397 --limit 10 --json

# With a custom instruction
python process_with_ollama.py @elonmusk --limit 5 --system "Classify tone and extract main claims"
```

Assumes Ollama daemon is running at http://localhost:11434.
If not, start with: `ollama serve` and ensure the model is available (the script attempts to `ollama pull <model>` if needed).

