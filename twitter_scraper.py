import requests
import json
import argparse
import os
from dotenv import load_dotenv
from pathlib import Path


def get_user_tweets(user_id: str, limit: int = 10, as_json: bool = False, link: str = None, start_cursor: str = None) -> str:
    """
    Récupère les N derniers tweets d'un compte Twitter en utilisant l'API TwitScoot.
    """
    # Charger les variables d'environnement depuis le fichier .env
    env_path = Path('.') / '.env'
    if not env_path.exists():
        return "Erreur: Le fichier .env n'existe pas dans le répertoire courant."

    load_dotenv(dotenv_path=env_path)

    # Récupérer la clé API
    api_key = os.getenv("TWITSCOUT_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return """Erreur: La clé API TwitScoot n'est pas définie ou est encore le placeholder.
        
Pour corriger cela:
1. Obtenez votre clé API depuis https://tweetscout.io
2. Ouvrez le fichier .env dans ce répertoire
3. Remplacez 'YOUR_API_KEY_HERE' par votre vraie clé API
4. Sauvegardez le fichier et relancez le script"""

    # Vérifier que la limite est valide
    if limit < 1 or limit > 100:
        limit = min(max(limit, 1), 100)

    # URL de l'API TwitScoot (corrigée selon la documentation)
    url = "https://api.tweetscout.io/v2/user-tweets"

    # En-têtes selon la documentation TwitScoot
    headers = {
        "Accept": "application/json",
        "ApiKey": api_key,
        "Content-Type": "application/json"
    }

    # Pagination: récupérer jusqu'à 'limit' éléments en suivant next_cursor
    collected = []
    next_cursor = start_cursor
    try:
        while len(collected) < limit:
            payload = {
                "link": link or f"https://x.com/{user_id}",
                "user_id": user_id
            }
            if next_cursor:
                payload["cursor"] = next_cursor

            # Utilisation de POST au lieu de GET
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                return f"Erreur API: {response.status_code} - {response.text}"

            response_data = response.json()
            batch = response_data.get("tweets", [])
            if not batch:
                break
            collected.extend(batch)
            next_cursor = response_data.get("next_cursor")
            if not next_cursor:
                break

        tweets = collected[:limit]

        if as_json:
            # Retourner les données collectées et le prochain curseur pour un appel ultérieur
            return json.dumps({
                "tweets": tweets,
                "next_cursor": next_cursor
            }, indent=4, ensure_ascii=False)
        else:
            # Extraire le texte des tweets (full_text selon la documentation)
            tweets_text = [tweet.get("full_text", "") for tweet in tweets]
            return "\n\n".join(tweets_text)

    except Exception as e:
        return f"Erreur lors de la récupération des tweets: {str(e)}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Récupérer les N derniers tweets d'un utilisateur via Tweetscout (par user_id numérique).")
    parser.add_argument("user_id", help="ID numérique Twitter (ex: 44196397)")
    parser.add_argument("--limit", type=int, default=10, help="Nombre de tweets à récupérer (max 100)")
    parser.add_argument("--json", action="store_true", help="Afficher les données complètes en JSON")
    parser.add_argument("--link", type=str, default=None, help="URL du profil (ex: https://x.com/elonmusk)")
    parser.add_argument("--cursor", type=str, default=None, help="Cursor de départ pour la pagination")
    args = parser.parse_args()

    result = get_user_tweets(args.user_id, args.limit, args.json, link=args.link, start_cursor=args.cursor)
    print(result)
