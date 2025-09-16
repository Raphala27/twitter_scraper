import requests
import json
import argparse
import os
from dotenv import load_dotenv
from pathlib import Path
import hashlib
from datetime import datetime, timedelta
import random


def resolve_user_id(user_or_handle: str, headers: dict, mock: bool = False) -> str | None:
    """
    Retourne l'ID numérique à partir d'un handle si nécessaire.
    - Si `user_or_handle` est déjà un ID numérique, le retourne tel quel.
    - Sinon, appelle GET /handle-to-id/{user_handle}.
    """
    candidate = user_or_handle.strip()
    if candidate.startswith("@"):
        candidate = candidate[1:]
    if candidate.isdigit():
        return candidate

    if mock:
        # ID stable basé sur MD5 du handle
        h = hashlib.md5(candidate.encode("utf-8")).hexdigest()
        return str(int(h[:12], 16) % 10_000_000_000)
    url = f"https://api.tweetscout.io/v2/handle-to-id/{candidate}"
    # headers doivent contenir ApiKey et Accept
    try:
        resp = requests.get(url, headers={"Accept": "application/json", **headers})
        if resp.status_code != 200:
            return None
        data = resp.json()
        # On s'attend à un champ id ou id_str selon l'API; couvrir les deux
        return str(data.get("id") or data.get("id_str")) if (data.get("id") or data.get("id_str")) else None
    except Exception:
        return None


def get_user_tweets(user_or_handle: str, limit: int = 10, as_json: bool = False, link: str = None, start_cursor: str = None, mock: bool = False) -> str:
    """
    Récupère les N derniers tweets d'un compte Twitter en utilisant l'API TwitScoot.
    """
    # Charger les variables d'environnement depuis le fichier .env
    env_path = Path('.') / '.env'
    if not env_path.exists():
        return "Erreur: Le fichier .env n'existe pas dans le répertoire courant."

    load_dotenv(dotenv_path=env_path)

    # Récupérer la clé API (optionnel en mode mock)
    api_key = os.getenv("TWITSCOUT_API_KEY")
    if not mock:
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
        "ApiKey": api_key or "mock-key",
        "Content-Type": "application/json"
    }

    # Résoudre le user_id si un handle a été fourni
    user_id = resolve_user_id(user_or_handle, {"ApiKey": api_key or "mock-key"}, mock=mock)
    if not user_id:
        return "Erreur: impossible de résoudre l'user_id depuis le handle fourni."

    # Pagination: récupérer jusqu'à 'limit' éléments en suivant next_cursor
    collected = []
    next_cursor = start_cursor
    try:
        while len(collected) < limit:
            if mock:
                # Génération déterministe et stable (mêmes sorties pour mêmes paramètres)
                page_size = 20
                remaining = limit - len(collected)
                gen_n = min(page_size, remaining)
                start_idx = len(collected) + 1
                seed_input = f"{user_id}:{next_cursor or '0'}"
                seed = int(hashlib.md5(seed_input.encode("utf-8")).hexdigest()[:12], 16)
                rnd = random.Random(seed)
                # Base de date déterministe
                base_shift_days = int(hashlib.md5(user_id.encode("utf-8")).hexdigest()[:6], 16) % 365
                base_dt = datetime(2025, 1, 1) - timedelta(days=base_shift_days)
                templates = [
                    "[MOCK] Update #{idx} for user {user_id}: shipping new feature today.",
                    "[MOCK] Thoughts #{idx}: markets, tech, and a bit of fun.",
                    "[MOCK] Quick note #{idx} — remember to stay hydrated.",
                    "[MOCK] Dev log #{idx}: performance improved by 23% on latest build.",
                    "[MOCK] AMA #{idx}: answering top 3 questions from the community.",
                ]
                batch = []
                for i in range(gen_n):
                    idx = start_idx + i
                    # ID stable basé sur MD5 de (user_id, idx)
                    h = hashlib.md5(f"{user_id}:{idx}".encode("utf-8")).hexdigest()
                    tid = h[:16]
                    # Texte stable: choix de template déterministe
                    t_idx = int(hashlib.md5(f"template:{user_id}:{idx}".encode("utf-8")).hexdigest()[:6], 16) % len(templates)
                    text = templates[t_idx].format(idx=idx, user_id=user_id)
                    # Date stable: quelques minutes d'écart par idx
                    created_at = (base_dt - timedelta(minutes=idx * (5 + rnd.randint(0, 3)))).isoformat() + "Z"
                    batch.append({
                        "id_str": tid,
                        "created_at": created_at,
                        "full_text": text,
                        "favorite_count": 0,
                        "retweet_count": 0,
                        "reply_count": 0,
                        "quote_count": 0,
                        "bookmark_count": 0,
                        "view_count": 0,
                        "entities": []
                    })
                collected.extend(batch)
                next_cursor = None if len(collected) >= limit else f"mock_cursor_{len(collected)}"
                if not next_cursor:
                    break
            else:
                payload = {
                    "user_id": user_id
                }
                if link:
                    payload["link"] = link
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
            # Affichage lisible: un séparateur clair entre chaque post
            blocks = []
            for i, tweet in enumerate(tweets, start=1):
                created = tweet.get("created_at", "")
                text = tweet.get("full_text", "")
                header = f"[{i}] {created}".strip()
                blocks.append(f"{header}\n{text}".strip())
            separator = "\n" + ("-" * 80) + "\n"
            return separator.join(blocks)

    except Exception as e:
        return f"Erreur lors de la récupération des tweets: {str(e)}"


if __name__ == "__main__":
    # Unique point d'entrée: on appelle le modèle pour chaque post via process_with_ollama,
    # mais la logique d'analyse reste dans le fichier séparé.
    from process_with_ollama import process_tweets_with_ollama

    parser = argparse.ArgumentParser(description="Entrée unique: récupère des posts (mock) et appelle un modèle Ollama pour chaque post.")
    parser.add_argument("user_id", help="ID numérique Twitter ou handle (ex: 44196397 ou @elonmusk)")
    parser.add_argument("--limit", type=int, default=10, help="Nombre de posts à récupérer")
    parser.add_argument("--model", type=str, default="qwen3:4b", help="Modèle Ollama")
    parser.add_argument("--system", type=str, default=None, help="Instruction système optionnelle")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    args = parser.parse_args()

    # Toujours mocker la récupération (pas d'appels payants)
    results = process_tweets_with_ollama(args.user_id, args.limit, args.model, system_instruction=args.system, mock=True)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        sep = "\n" + ("=" * 80) + "\n"
        blocks = []
        for i, r in enumerate(results, start=1):
            header = f"[{i}] {r.get('created_at','')} (id: {r.get('id_str','')})"
            blocks.append(f"{header}\nPost:\n{r.get('full_text','')}\n\nAnalysis:\n{r.get('analysis','')}")
        print(sep.join(blocks))
