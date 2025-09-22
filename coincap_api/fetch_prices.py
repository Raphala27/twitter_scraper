#!/usr/bin/env python3
"""
CoinCap API Price Fetching

This module handles cryptocurrency price data fetching from the CoinCap API,
including asset search, current prices, and historical data retrieval.
"""

# Standard library imports
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
import requests

# Global configuration
COINCAP_API_KEY = os.environ.get("COINCAP_API_KEY", "")

def search_asset_by_symbol(symbol: str, api_key: str) -> Optional[str]:
    """
    Recherche un asset par son symbole via l'API CoinCap
    Retourne l'ID de l'asset ou None si non trouvé
    """
    url = "https://rest.coincap.io/v3/assets"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "search": symbol.upper(),
        "limit": 20
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            assets = data.get("data", [])
            
            # Chercher une correspondance exacte avec le symbole
            for asset in assets:
                if asset.get("symbol", "").upper() == symbol.upper():
                    return asset.get("id")
            
            # Si pas de correspondance exacte, retourner le premier résultat
            if assets:
                return assets[0].get("id")
            
            print(f"⚠️ Asset {symbol} non trouvé")
            return None
        else:
            print(f"❌ Erreur API pour {symbol}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur recherche {symbol}: {e}")
        return None

def get_asset_history(asset_id: str, timestamp: str, api_key: str) -> Optional[float]:
    """
    Récupère le prix historique d'un asset à un moment donné
    timestamp: format '2024-04-16T23:35:00Z'
    """
    # Convertir timestamp en millisecondes
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    start_timestamp = int(dt.timestamp() * 1000)
    end_timestamp = start_timestamp + (60 * 1000)  # +1 minute pour avoir des données
    
    url = f"https://rest.coincap.io/v3/assets/{asset_id}/history"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "interval": "m1",  # Intervalles de 1 minute
        "start": start_timestamp,
        "end": end_timestamp
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            history = data.get("data", [])
            
            if history:
                # Prendre le prix le plus proche du timestamp demandé
                closest_price = history[0].get("priceUsd")
                if closest_price:
                    return float(closest_price)
            
            # Si pas d'historique, essayer le prix actuel
            return get_current_asset_price(asset_id, api_key)
        else:
            print(f"❌ Erreur API historique pour {asset_id}: {response.status_code}")
            return get_current_asset_price(asset_id, api_key)
            
    except Exception as e:
        print(f"❌ Erreur historique {asset_id}: {e}")
        return get_current_asset_price(asset_id, api_key)

def get_current_asset_price(asset_id: str, api_key: str) -> Optional[float]:
    """
    Récupère le prix actuel d'un asset comme fallback
    """
    url = f"https://rest.coincap.io/v3/assets/{asset_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            asset_data = data.get("data", {})
            price = asset_data.get("priceUsd")
            if price:
                return float(price)
        
        print(f"❌ Impossible de récupérer le prix pour {asset_id}")
        return None
        
    except Exception as e:
        print(f"❌ Erreur prix actuel {asset_id}: {e}")
        return None

def get_crypto_price_at_time(ticker: str, timestamp: str, api_key: str) -> Optional[float]:
    """
    Récupère le prix d'une crypto à un moment donné
    ticker: ex 'BTC', 'ETH'
    timestamp: format '2024-04-16T23:35:00Z'
    """
    # Étape 1: Rechercher l'asset ID
    asset_id = search_asset_by_symbol(ticker, api_key)
    if not asset_id:
        return None
    
    # Étape 2: Obtenir le prix historique
    price = get_asset_history(asset_id, timestamp, api_key)
    if price:
        print(f"💰 {ticker}: ${price:.8f}")
    
    return price

def fetch_prices_for_cryptos(cryptos_list: List[Dict], api_key: str = None) -> Dict[str, Dict]:
    """
    Prend une liste plate de cryptos (format du résumé consolidé)
    et retourne un dict {f"{ticker}_{timestamp}": {"price": prix, "asset_id": asset_id}}
    """
    if api_key is None:
        api_key = COINCAP_API_KEY
    if not api_key:
        raise ValueError("Clé API CoinCap manquante. Renseignez-la dans .env via COINCAP_API_KEY.")

    prices_data = {}
    
    # Traiter chaque entrée individuellement pour avoir le prix historique
    for entry in cryptos_list:
        ticker = entry.get("ticker", "").upper()
        timestamp = entry.get("timestamp", "")
        tweet_number = entry.get("tweet_number", 0)
        
        if not ticker or not timestamp:
            continue
        
        print(f"📅 Tweet #{tweet_number}: {ticker}")
        
        # Récupérer le prix historique
        price = get_crypto_price_at_time(ticker, timestamp, api_key)
        
        if price is not None:
            # Récupérer aussi l'asset_id pour la cohérence
            asset_id = search_asset_by_symbol(ticker, api_key)
            
            key = f"{ticker}_{tweet_number}"
            prices_data[key] = {
                "ticker": ticker,
                "price": price,
                "asset_id": asset_id,
                "timestamp": timestamp,
                "tweet_number": tweet_number
            }
        
        # Petite pause pour éviter de surcharger l'API
        time.sleep(0.3)
    
    print(f"\n✅ {len(prices_data)} prix historiques récupérés")
    return prices_data
