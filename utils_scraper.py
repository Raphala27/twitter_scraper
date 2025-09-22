#!/usr/bin/env python3
"""
Utilities for Twitter Scraping

This module provides utility functions for Twitter data scraping using the TwitScoot API,
including user ID resolution, tweet fetching, and mock data generation for testing.
"""

# Standard library imports
import hashlib
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
import requests
from dotenv import load_dotenv


class UtilsScraper:
    """Utility class for Twitter scraping operations."""
    
    @staticmethod
    def resolve_user_id(user_or_handle: str, headers: Dict[str, str], mock: bool = False) -> Optional[str]:
        """
        Resolve a Twitter handle to a numeric user ID.
        
        Args:
            user_or_handle: Twitter handle (@username) or numeric user ID
            headers: HTTP headers including API authentication
            mock: Use mock mode for testing (no API calls)
        
        Returns:
            Numeric user ID as string, or None if resolution fails
        """
        candidate = user_or_handle.strip()
        if candidate.startswith("@"):
            candidate = candidate[1:]
        if candidate.isdigit():
            return candidate

        if mock:
            # Generate stable ID based on MD5 hash of handle
            hash_obj = hashlib.md5(candidate.encode("utf-8"))
            return str(int(hash_obj.hexdigest()[:12], 16) % 10_000_000_000)
        
        url = f"https://api.tweetscout.io/v2/handle-to-id/{candidate}"
        try:
            resp = requests.get(url, headers={"Accept": "application/json", **headers}, timeout=30)
            if resp.status_code != 200:
                return None
            data = resp.json()
            # Handle both 'id' and 'id_str' fields
            user_id = data.get("id") or data.get("id_str")
            return str(user_id) if user_id else None
        except Exception:
            return None

    @staticmethod
    def get_user_tweets(
        user_or_handle: str, 
        limit: int = 10, 
        as_json: bool = False, 
        link: Optional[str] = None, 
        start_cursor: Optional[str] = None, 
        mock: bool = False
    ) -> str:
        """
        Fetch the latest tweets from a Twitter account using TwitScoot API.
        
        Args:
            user_or_handle: Twitter handle (@username) or numeric user ID
            limit: Maximum number of tweets to fetch (1-100)
            as_json: Return raw JSON response instead of formatted string
            link: Optional specific link parameter for API
            start_cursor: Pagination cursor for continuing from specific point
            mock: Use mock mode for testing (no API calls)
        
        Returns:
            JSON string of tweets or formatted text output
        """
        # Charger les variables d'environnement depuis le fichier .env
        env_path = Path('.') / '.env'
        if not env_path.exists():
            return "Erreur: Le fichier .env n'existe pas dans le répertoire courant."

        load_dotenv(dotenv_path=env_path)

        # Récupérer la clé API (optionnel en mode mock)
        api_key = os.getenv("TWITSCOUT_API_KEY")
        if not mock:
            if not api_key:
                return "Erreur: La clé API TwitScoot n'est pas définie."
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
        user_id = UtilsScraper.resolve_user_id(user_or_handle, {"ApiKey": api_key or "mock-key"}, mock=mock)
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
                        """[MOCK] #BTC/USDT
Signal type: SHORT
Leverage: 25x
Entry : 64200
Take Profit Targets:
➖ 63000
➖ 62000
➖ 61000
➖ 60000
➖ 59000
⚠️SL: 66000""",

                        """#ETH/USDT LONG
👉Leverage : Cross 25×
Entry : 3150 - 3100
Take Profit
1) 3250
2) 3350
3) 3450
⭕Stoploss : 3000""",

                        """[MOCK] #SOL/USDT
Signal type: LONG
Leverage: 20x
Entry : 185.50
Take Profit Targets:
➖ 190.00
➖ 195.00
➖ 200.00
➖ 205.00
➖ 210.00
⚠️SL: 180.00""",

                        """[MOCK] #ADA/USDT
Signal type: SHORT
Leverage: 15x
Entry : 0.4850
Take Profit Targets:
➖ 0.4750
➖ 0.4650
➖ 0.4550
➖ 0.4450
➖ 0.4350
⚠️SL: 0.5000""",

                        """[MOCK] #XRP/USDT LONG
Signal type: LONG
Leverage: 10x
Entry : 0.5250
Take Profit Targets:
➖ 0.5400
➖ 0.5550
➖ 0.5700
➖ 0.5850
⚠️SL: 0.5000""",

                        """[MOCK] #BNB/USDT SHORT
Signal type: SHORT
Leverage: 8x
Entry : 590.00
Take Profit Targets:
➖ 580.00
➖ 570.00
➖ 560.00
➖ 550.00
⚠️SL: 610.00""",

                        """[MOCK] #DOGE/USDT LONG
Signal type: LONG
Leverage: 12x
Entry : 0.1500
Take Profit Targets:
➖ 0.1550
➖ 0.1600
➖ 0.1650
➖ 0.1700
⚠️SL: 0.1400""",

                        """[MOCK] #MATIC/USDT SHORT
Signal type: SHORT
Leverage: 20x
Entry : 0.7000
Take Profit Targets:
➖ 0.6900
➖ 0.6800
➖ 0.6700
➖ 0.6600
⚠️SL: 0.7200""",

                        """[MOCK] #AVAX/USDT LONG
Signal type: LONG
Leverage: 18x
Entry : 32.00
Take Profit Targets:
➖ 33.00
➖ 34.00
➖ 35.00
➖ 36.00
⚠️SL: 30.00""",

                        """[MOCK] #DOT/USDT SHORT
Signal type: SHORT
Leverage: 14x
Entry : 6.50
Take Profit Targets:
➖ 6.40
➖ 6.30
➖ 6.20
➖ 6.10
⚠️SL: 6.70""",

                        """[MOCK] #LTC/USDT LONG
Signal type: LONG
Leverage: 16x
Entry : 85.00
Take Profit Targets:
➖ 87.00
➖ 89.00
➖ 91.00
➖ 93.00
⚠️SL: 82.00""",

                        """[MOCK] #TRX/USDT SHORT
Signal type: SHORT
Leverage: 10x
Entry : 0.1200
Take Profit Targets:
➖ 0.1180
➖ 0.1160
➖ 0.1140
➖ 0.1120
⚠️SL: 0.1240""",

                        """[MOCK] #LINK/USDT LONG
Signal type: LONG
Leverage: 22x
Entry : 14.00
Take Profit Targets:
➖ 14.50
➖ 15.00
➖ 15.50
➖ 16.00
⚠️SL: 13.50""",

                        """[MOCK] #UNI/USDT SHORT
Signal type: SHORT
Leverage: 9x
Entry : 7.00
Take Profit Targets:
➖ 6.90
➖ 6.80
➖ 6.70
➖ 6.60
⚠️SL: 7.20""",
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
                    response = requests.post(url, headers=headers, json=payload, timeout=30)

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
