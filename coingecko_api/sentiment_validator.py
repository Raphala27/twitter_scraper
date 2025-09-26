#!/usr/bin/env python3
"""
Sentiment Validator for Cryptocurrency Analysis

Ce module valide les sentiments crypto des influenceurs en comparant
les prédictions avec les performances réelles sur 1h, 24h et 7j.
"""

# Standard library imports
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Third-party imports
import requests

# Local imports
try:
    from .fetch_prices import search_asset_by_symbol, convert_twitter_timestamp_to_iso
except ImportError:
    from fetch_prices import search_asset_by_symbol, convert_twitter_timestamp_to_iso


class SentimentValidator:
    """
    Classe pour valider les sentiments crypto des influenceurs
    en analysant les performances sur différentes périodes
    """
    
    def __init__(self, api_key: str = None, mock_mode: bool = False):
        """
        Initialise le validateur de sentiment
        
        Args:
            api_key: Clé API CoinGecko (optionnelle)
            mock_mode: Utilise des prix mock pour les tests
        """
        self.api_key = api_key or os.environ.get("COINGECKO_API_KEY", "")
        self.mock_mode = mock_mode
        self.validation_periods = {
            "1h": 1,
            "24h": 24, 
            "7d": 168  # 7 jours = 168 heures
        }
    
    def get_price_at_multiple_times(self, ticker: str, base_timestamp: str) -> Dict[str, Optional[float]]:
        """
        Récupère le prix d'une crypto à différents moments
        
        Args:
            ticker: Symbole de la crypto (ex: 'BTC')
            base_timestamp: Timestamp de base (moment du tweet)
            
        Returns:
            Dict avec les prix à différents moments
        """
        if self.mock_mode:
            return self._get_mock_prices(ticker)
        
        prices = {}
        
        try:
            # Convertir le timestamp de base
            base_dt = datetime.fromisoformat(convert_twitter_timestamp_to_iso(base_timestamp).replace('Z', '+00:00'))
            
            # Récupérer l'asset ID
            asset_id = search_asset_by_symbol(ticker, self.api_key)
            if not asset_id:
                print(f"❌ Asset ID non trouvé pour {ticker}")
                return {period: None for period in ["base", "1h", "24h", "7d"]}
            
            # Prix au moment du tweet (base)
            prices["base"] = self._get_historical_price(asset_id, base_dt)
            
            # Prix après différentes périodes
            for period, hours in self.validation_periods.items():
                target_dt = base_dt + timedelta(hours=hours)
                # Ne pas aller dans le futur
                if target_dt <= datetime.now(base_dt.tzinfo):
                    prices[period] = self._get_historical_price(asset_id, target_dt)
                else:
                    prices[period] = None
                    
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des prix pour {ticker}: {e}")
            return {period: None for period in ["base", "1h", "24h", "7d"]}
        
        return prices
    
    def _get_mock_prices(self, ticker: str) -> Dict[str, Optional[float]]:
        """
        Génère des prix mock pour les tests
        
        Args:
            ticker: Symbole de la crypto
            
        Returns:
            Dict avec des prix mock simulant différents scénarios
        """
        # Prix de base déterministes basés sur le ticker
        base_prices = {
            "BTC": 50000.0,
            "ETH": 3000.0,
            "SOL": 150.0,
            "ADA": 0.5,
            "XRP": 1.0,
            "BNB": 400.0,
            "DOGE": 0.1,
            "MATIC": 0.8,
            "AVAX": 25.0,
            "DOT": 6.0,
            "LTC": 80.0,
            "TRX": 0.08,
            "LINK": 15.0,
            "UNI": 8.0
        }
        
        base_price = base_prices.get(ticker.upper(), 100.0)
        
        # Simuler des variations réalistes
        # Pour un test cohérent, simulons différents scénarios par crypto
        variations = {
            "BTC": {"1h": 0.5, "24h": -2.0, "7d": 5.0},  # Scenario: court terme volatile, long terme positif
            "ETH": {"1h": -0.8, "24h": -3.5, "7d": -1.0},  # Scenario: baisse générale
            "SOL": {"1h": 0.2, "24h": 1.0, "7d": 8.0},  # Scenario: croissance progressive
            "ADA": {"1h": -1.2, "24h": -5.0, "7d": -8.0},  # Scenario: baisse continue
            "XRP": {"1h": 2.0, "24h": 8.0, "7d": 15.0},  # Scenario: forte hausse
        }
        
        default_variations = {"1h": 0.1, "24h": 0.5, "7d": 2.0}
        ticker_variations = variations.get(ticker.upper(), default_variations)
        
        prices = {"base": base_price}
        
        for period, variation_pct in ticker_variations.items():
            prices[period] = base_price * (1 + variation_pct / 100)
        
        return prices
    
    def _get_historical_price(self, asset_id: str, dt: datetime) -> Optional[float]:
        """
        Récupère le prix historique pour une date/heure spécifique
        
        Args:
            asset_id: ID CoinGecko de la crypto
            dt: DateTime pour lequel récupérer le prix
            
        Returns:
            Prix en USD ou None si non trouvé
        """
        try:
            # CoinGecko API pour prix historique par date
            date_str = dt.strftime("%d-%m-%Y")
            
            url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/history"
            params = {
                "date": date_str,
                "localization": "false"
            }
            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            price = data.get("market_data", {}).get("current_price", {}).get("usd")
            
            return float(price) if price is not None else None
            
        except Exception as e:
            print(f"⚠️ Erreur récupération prix historique: {e}")
            return None
    
    def calculate_performance(self, base_price: float, target_price: float) -> Tuple[float, float]:
        """
        Calcule la performance entre deux prix
        
        Args:
            base_price: Prix de départ
            target_price: Prix d'arrivée
            
        Returns:
            Tuple (variation_absolue, variation_pourcentage)
        """
        if not base_price or not target_price:
            return 0.0, 0.0
            
        variation_abs = target_price - base_price
        variation_pct = (variation_abs / base_price) * 100
        
        return variation_abs, variation_pct
    
    def validate_sentiment(self, sentiment: str, price_change_pct: float) -> Dict[str, Any]:
        """
        Valide si un sentiment était correct basé sur la performance prix
        
        Args:
            sentiment: Sentiment prédit ('bullish', 'bearish', 'neutral')
            price_change_pct: Variation de prix en pourcentage
            
        Returns:
            Dict avec résultats de validation
        """
        # Seuils pour déterminer si la prédiction était correcte
        NEUTRAL_THRESHOLD = 2.0  # +/- 2% considéré comme neutre
        
        actual_direction = "neutral"
        if price_change_pct > NEUTRAL_THRESHOLD:
            actual_direction = "bullish"
        elif price_change_pct < -NEUTRAL_THRESHOLD:
            actual_direction = "bearish"
        
        # Vérifier si la prédiction était correcte
        correct = False
        if sentiment == actual_direction:
            correct = True
        elif sentiment == "neutral" and abs(price_change_pct) <= NEUTRAL_THRESHOLD:
            correct = True
        
        # Calculer le score de précision
        accuracy_score = 0.0
        if correct:
            if sentiment == "neutral":
                # Score basé sur la proximité à 0
                accuracy_score = max(0, 100 - abs(price_change_pct) * 10)
            else:
                # Score basé sur l'amplitude du mouvement
                accuracy_score = min(100, abs(price_change_pct) * 5)
        
        return {
            "predicted_sentiment": sentiment,
            "actual_direction": actual_direction,
            "price_change_pct": price_change_pct,
            "correct": correct,
            "accuracy_score": accuracy_score
        }
    
    def analyze_sentiment_accuracy(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la précision d'un sentiment sur toutes les périodes
        
        Args:
            sentiment_data: Données de sentiment avec ticker, sentiment, timestamp
            
        Returns:
            Dict avec analyse complète de la précision
        """
        ticker = sentiment_data.get("ticker", "")
        sentiment = sentiment_data.get("sentiment", "neutral")
        timestamp = sentiment_data.get("timestamp", "")
        context = sentiment_data.get("context", "")
        
        print(f"🔍 Validation sentiment pour {ticker} ({sentiment})")
        
        # Récupérer les prix à différents moments
        prices = self.get_price_at_multiple_times(ticker, timestamp)
        
        if not prices.get("base"):
            return {
                "ticker": ticker,
                "sentiment": sentiment,
                "context": context,
                "error": "Prix de base non trouvé",
                "validations": {}
            }
        
        base_price = prices["base"]
        validations = {}
        
        # Analyser chaque période
        for period in ["1h", "24h", "7d"]:
            target_price = prices.get(period)
            if target_price:
                _, price_change_pct = self.calculate_performance(base_price, target_price)
                validation = self.validate_sentiment(sentiment, price_change_pct)
                
                validations[period] = {
                    "base_price": base_price,
                    "target_price": target_price,
                    "price_change_pct": price_change_pct,
                    **validation
                }
                
                # Affichage des résultats
                status = "✅" if validation["correct"] else "❌"
                print(f"   {period:>3}: {status} {price_change_pct:+.2f}% (Prédit: {sentiment}, Réel: {validation['actual_direction']})")
            else:
                validations[period] = {
                    "base_price": base_price,
                    "target_price": None,
                    "price_change_pct": 0.0,
                    "error": "Prix cible non disponible"
                }
                print(f"   {period:>3}: ⚠️  Prix non disponible")
        
        return {
            "ticker": ticker,
            "sentiment": sentiment,
            "context": context,
            "timestamp": timestamp,
            "base_price": base_price,
            "validations": validations
        }
    
    def validate_all_sentiments(self, tweets_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valide tous les sentiments d'une analyse consolidée
        
        Args:
            tweets_analysis: Liste des analyses de tweets
            
        Returns:
            Dict avec résultats de validation globaux
        """
        print("🎯 Validation des sentiments d'influenceur...")
        
        validation_results = []
        global_stats = {
            "total_predictions": 0,
            "correct_1h": 0,
            "correct_24h": 0,
            "correct_7d": 0,
            "avg_accuracy_1h": 0.0,
            "avg_accuracy_24h": 0.0,
            "avg_accuracy_7d": 0.0
        }
        
        for sentiment_data in tweets_analysis:
            result = self.analyze_sentiment_accuracy(sentiment_data)
            validation_results.append(result)
            
            # Mettre à jour les statistiques globales
            global_stats["total_predictions"] += 1
            
            for period in ["1h", "24h", "7d"]:
                validation = result.get("validations", {}).get(period, {})
                if validation.get("correct"):
                    global_stats[f"correct_{period}"] += 1
                
                accuracy = validation.get("accuracy_score", 0)
                global_stats[f"avg_accuracy_{period}"] += accuracy
        
        # Calculer les moyennes
        if global_stats["total_predictions"] > 0:
            for period in ["1h", "24h", "7d"]:
                global_stats[f"avg_accuracy_{period}"] /= global_stats["total_predictions"]
        
        return {
            "validation_results": validation_results,
            "global_stats": global_stats
        }
