import os
import requests
from typing import List, Dict
from datetime import datetime
import time

MORALIS_API_KEY = os.environ.get("MORALIS_API_KEY", "")

def get_block_from_date(date_str: str, api_key: str) -> int:
    """
    Convertit une date en numéro de bloc
    date_str: format '2024-04-16T23:35:00Z'
    """
    # Convertir la date ISO en timestamp Unix
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    unix_timestamp = int(dt.timestamp())
    
    url = 'https://deep-index.moralis.io/api/v2/dateToBlock'
    params = {
        'chain': 'eth',
        'date': unix_timestamp
    }
    headers = {
        'X-API-Key': api_key
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        block_number = data.get('block')
        return block_number
    else:
        print(f"❌ Erreur conversion timestamp pour {date_str}")
        return None

def get_token_price_at_block(token_address: str, block_number: int, api_key: str) -> float:
    """
    Récupère le prix d'un token à un bloc spécifique
    """
    url = f'https://deep-index.moralis.io/api/v2/erc20/{token_address}/price'
    
    params = {
        'chain': 'eth',
        'to_block': str(block_number)
    }
    
    headers = {
        'X-API-Key': api_key
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=15)
    if response.status_code == 200:
        data = response.json()
        price = data.get('usdPrice')
        if price is not None:
            return float(price)
    else:
        print(f"❌ Erreur API prix")
    return None

def search_token_address(ticker: str, api_key: str) -> str:
    """
    Recherche l'adresse du contrat d'un token via l'API Moralis
    Retourne directement l'adresse ou None
    """
    url = "https://deep-index.moralis.io/api/v2/erc20/metadata/symbols"
    params = {
        'symbols': [ticker.upper()],
        'chain': 'eth'
    }
    headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                # Chercher le token qui correspond exactement au symbol
                for token_info in data:
                    symbol = token_info.get('symbol', '').upper()
                    if symbol == ticker.upper():
                        return token_info.get('address')
                
                # Si pas de correspondance exacte, prendre le premier
                return data[0].get('address')
            
            print(f"⚠️ Token {ticker} non trouvé")
            return None
        else:
            print(f"❌ Erreur API pour {ticker}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur recherche {ticker}: {e}")
        return None

def get_crypto_price_at_time(ticker: str, timestamp: str, api_key: str) -> float:
    """
    Récupère le prix d'une crypto à un moment donné
    ticker: ex 'BTC', 'ETH'
    timestamp: format '2024-04-16T23:35:00Z'
    """
    # Étape 1: Rechercher l'adresse du token
    token_address = search_token_address(ticker, api_key)
    if not token_address:
        return None
    
    # Étape 2: Convertir la date en numéro de bloc
    block_number = get_block_from_date(timestamp, api_key)
    if not block_number:
        return None
    
    # Étape 3: Obtenir le prix à ce bloc
    price = get_token_price_at_block(token_address, block_number, api_key)
    if price:
        print(f"💰 {ticker}: ${price:.8f}")
    
    return price

def fetch_prices_for_cryptos(cryptos_list: List[Dict], api_key: str = None) -> Dict[str, Dict]:
    """
    Prend une liste plate de cryptos (format du résumé consolidé)
    et retourne un dict {f"{ticker}_{timestamp}": {"price": prix, "block": bloc}}
    """
    if api_key is None:
        api_key = MORALIS_API_KEY
    if not api_key:
        raise ValueError("Clé API Moralis manquante. Renseignez-la dans .env via MORALIS_API_KEY.")

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
            # Récupérer aussi le bloc pour la cohérence
            block_number = get_block_from_date(timestamp, api_key)
            
            key = f"{ticker}_{tweet_number}"
            prices_data[key] = {
                "ticker": ticker,
                "price": price,
                "block": block_number,
                "timestamp": timestamp,
                "tweet_number": tweet_number
            }
        
        # Petite pause pour éviter de surcharger l'API
        time.sleep(0.3)
    
    print(f"\n✅ {len(prices_data)} prix historiques récupérés")
    return prices_data
