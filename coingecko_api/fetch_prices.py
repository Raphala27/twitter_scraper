#!/usr/bin/env python3
"""
CoinGecko API Price Fetching

This module handles cryptocurrency price data fetching from the CoinGecko API,
including asset search, current prices, and historical data retrieval.
"""

# Standard library imports
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
import requests

# Global configuration
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")


def convert_twitter_timestamp_to_iso(timestamp: str) -> str:
    """
    Convert Twitter timestamp format to ISO format
    
    Args:
        timestamp: Twitter timestamp (e.g., 'Mon Sep 22 13:52:57 +0000 2025')
    
    Returns:
        ISO formatted timestamp string
    """
    try:
        # Handle Twitter format: 'Mon Sep 22 13:52:57 +0000 2025'
        if '+0000' in timestamp and len(timestamp.split()) == 6:
            # Parse Twitter format
            dt = datetime.strptime(timestamp, '%a %b %d %H:%M:%S %z %Y')
            return dt.isoformat()
        
        # Handle already ISO format or other standard formats
        if 'T' in timestamp:
            # Already ISO-like, just clean it up
            return timestamp.replace('Z', '+00:00')
        
        # Default: try to parse as-is
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.isoformat()
        
    except (ValueError, TypeError) as e:
        print(f"⚠️ Erreur conversion timestamp '{timestamp}': {e}")
        # Fallback to current time
        return datetime.now().isoformat()


def search_asset_by_symbol(symbol: str, api_key: str = None) -> Optional[str]:
    """
    Search for an asset by its symbol via CoinGecko API
    Returns the asset ID or None if not found
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        api_key: CoinGecko API key (optional for basic tier)
    
    Returns:
        Asset ID string or None if not found
    """
    url = "https://api.coingecko.com/api/v3/coins/list"
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        coins = response.json()
        for coin in coins:
            if coin.get("symbol", "").upper() == symbol.upper():
                return coin.get("id")
        
        return None
        
    except requests.RequestException as e:
        print(f"Erreur lors de la recherche de {symbol}: {e}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        print(f"Erreur lors du traitement des données pour {symbol}: {e}")
        return None


def get_asset_history(asset_id: str, timestamp: str, api_key: str = None) -> Optional[float]:
    """
    Get historical price for an asset at a specific timestamp via CoinGecko API
    
    Args:
        asset_id: CoinGecko asset ID
        timestamp: ISO timestamp string
        api_key: CoinGecko API key (optional)
    
    Returns:
        Price in USD or None if not found
    """
    try:
        # Convert Twitter timestamp to ISO format first
        iso_timestamp = convert_twitter_timestamp_to_iso(timestamp)
        
        # Convert timestamp to date format (DD-MM-YYYY) required by CoinGecko
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        date_str = dt.strftime("%d-%m-%Y")
        
        url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/history"
        params = {
            "date": date_str,
            "localization": "false"
        }
        headers = {}
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        price = data.get("market_data", {}).get("current_price", {}).get("usd")
        
        return float(price) if price is not None else None
        
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de l'historique pour {asset_id}: {e}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        print(f"Erreur lors du traitement de l'historique pour {asset_id}: {e}")
        return None


def get_current_asset_price(symbol: str, api_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Get current price for a cryptocurrency symbol via CoinGecko API
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        api_key: CoinGecko API key (optional)
    
    Returns:
        Dictionary with price data or None if not found
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "symbols": symbol.lower(),
        "vs_currencies": "usd"
    }
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        symbol_lower = symbol.lower()
        price = data.get(symbol_lower, {}).get("usd")
        
        if price is not None:
            return {
                "price": float(price),
                "symbol": symbol.upper(),
                "timestamp": datetime.now().isoformat()
            }
        
        return None
        
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du prix actuel pour {symbol}: {e}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        print(f"Erreur lors du traitement du prix pour {symbol}: {e}")
        return None


def get_crypto_price_at_time(ticker: str, timestamp: str, api_key: str = None) -> Optional[float]:
    """
    Get cryptocurrency price at a specific time using CoinGecko API
    
    Args:
        ticker: Cryptocurrency ticker (e.g., 'BTC', 'ETH')
        timestamp: ISO timestamp string
        api_key: CoinGecko API key (optional)
    
    Returns:
        Price in USD or None if not found
    """
    # First, get the asset ID from the ticker
    asset_id = search_asset_by_symbol(ticker, api_key)
    if not asset_id:
        print(f"Asset ID non trouvé pour le ticker {ticker}")
        return None
    
    # Then get the historical price
    return get_asset_history(asset_id, timestamp, api_key)


def fetch_prices_for_cryptos(cryptos_list: List[Dict], api_key: str = None) -> Dict[str, Dict]:
    """
    Fetch current and historical prices for a list of cryptocurrencies using CoinGecko API
    
    Args:
        cryptos_list: List of crypto dictionaries with ticker and timestamp info
        api_key: CoinGecko API key (optional)
    
    Returns:
        Dictionary with ticker as key and price info as value
    """
    if api_key is None:
        api_key = COINGECKO_API_KEY
    
    print("🔍 Récupération des prix historiques...")
    
    results = {}
    
    for crypto in cryptos_list:
        ticker = crypto.get("ticker", "").upper()
        timestamp = crypto.get("timestamp", "")
        
        if not ticker:
            continue
            
        print(f"📊 Traitement de {ticker}...")
        
        try:
            # Get asset ID
            asset_id = search_asset_by_symbol(ticker, api_key)
            if not asset_id:
                print(f"❌ Asset ID non trouvé pour {ticker}")
                continue
            
            # Get current price
            current_price = get_current_asset_price(asset_id, api_key)
            
            # Get historical price if timestamp is provided
            historical_price = None
            if timestamp:
                historical_price = get_asset_history(asset_id, timestamp, api_key)
            
            results[ticker] = {
                "asset_id": asset_id,
                "current_price": current_price,
                "historical_price": historical_price,
                "timestamp": timestamp
            }
            
            print(f"✅ {ticker}: Prix actuel=${current_price}, Prix historique=${historical_price}")
            
            # Rate limiting - CoinGecko allows 30 calls/minute for free tier
            time.sleep(2)
            
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"❌ Erreur lors du traitement de {ticker}: {e}")
            continue
    
    return results
