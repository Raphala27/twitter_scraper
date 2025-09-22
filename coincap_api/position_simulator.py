import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import time

class PositionSimulator:
    """
    Simulateur de positions de trading basé sur les données extraites des tweets
    et les prix historiques de CoinCap API
    """
    
    def __init__(self, api_key: str = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        
        if not mock_mode:
            if api_key is None:
                load_dotenv()
                self.api_key = os.getenv('COINCAP_API_KEY')
            else:
                self.api_key = api_key
                
            if not self.api_key:
                print("⚠️ COINCAP_API_KEY manquante, passage en mode mock")
                self.mock_mode = True
        
        # Données mock pour les prix
        self.mock_prices = {
            "BTC": {"current": 63500, "volatility": 0.02},
            "ETH": {"current": 3150, "volatility": 0.03}, 
            "SOL": {"current": 185, "volatility": 0.04},
            "ADA": {"current": 0.48, "volatility": 0.05},
            "XRP": {"current": 0.52, "volatility": 0.03},
            "DOGE": {"current": 0.08, "volatility": 0.06},
            "MATIC": {"current": 0.95, "volatility": 0.04},
            "DOT": {"current": 8.50, "volatility": 0.04},
            "UNI": {"current": 7.00, "volatility": 0.05},
            "LTC": {"current": 85.00, "volatility": 0.03},
            "LINK": {"current": 14.50, "volatility": 0.04},
            "AVAX": {"current": 35.00, "volatility": 0.05},
            "ATOM": {"current": 8.20, "volatility": 0.04},
            "BNB": {"current": 320.00, "volatility": 0.03},
            "NEAR": {"current": 5.50, "volatility": 0.06},
            "FTM": {"current": 0.75, "volatility": 0.07},
            "ALGO": {"current": 0.25, "volatility": 0.06},
            "ICP": {"current": 12.50, "volatility": 0.05},
            "APT": {"current": 8.80, "volatility": 0.06},
            "ARB": {"current": 1.20, "volatility": 0.05}
        }
    
    def get_headers(self):
        """Retourne les headers avec l'authentification Bearer token"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def search_asset_id(self, ticker: str) -> Optional[str]:
        """Recherche l'ID d'un asset par son symbole"""
        if self.mock_mode:
            # En mode mock, retourner directement le ticker en lowercase
            ticker_upper = ticker.upper()
            if ticker_upper in self.mock_prices:
                return ticker_upper.lower()
            print(f"⚠️ Mock: Asset {ticker} non supporté")
            return None
        
        url = "https://rest.coincap.io/v3/assets"
        params = {"search": ticker.upper(), "limit": 10}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                assets = data.get("data", [])
                
                # Chercher correspondance exacte
                for asset in assets:
                    if asset.get("symbol", "").upper() == ticker.upper():
                        return asset.get("id")
                
                # Si pas de correspondance exacte, prendre le premier
                if assets:
                    return assets[0].get("id")
            
            print(f"⚠️ Asset {ticker} non trouvé")
            return None
        except Exception as e:
            print(f"❌ Erreur recherche {ticker}: {e}")
            return None
    
    def get_price_historical(self, asset_id: str, timestamp_start: int, timestamp_end: int = None) -> Optional[float]:
        """
        Récupère le prix historique d'un asset à un timestamp donné
        timestamp_start: timestamp Unix en millisecondes
        timestamp_end: timestamp Unix en millisecondes (optionnel)
        """
        if self.mock_mode:
            return self._generate_mock_price(asset_id, timestamp_start)
        
        url = f'https://rest.coincap.io/v3/assets/{asset_id}/history'
        params = {
            'interval': 'm1',  # Intervalle de 1 minute
            'start': timestamp_start
        }
        
        if timestamp_end:
            params['end'] = timestamp_end
        
        try:
            response = requests.get(url, params=params, headers=self.get_headers(), timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data['data'] and len(data['data']) > 0:
                    price = float(data['data'][0]['priceUsd'])
                    return price
                else:
                    print(f'⚠️ Aucune donnée historique trouvée pour {asset_id} à {timestamp_start}')
                    return None
            else:
                print(f'❌ Erreur API historique pour {asset_id}: {response.status_code}')
                return None
        except Exception as e:
            print(f'❌ Erreur récupération prix historique: {e}')
            return None
    
    def get_price_history_interval(self, asset_id: str, start_date_str: str, 
                                 interval_minutes: int = 1, total_intervals: int = 60) -> Dict[str, Any]:
        """
        Récupère une série de prix historiques à intervalles réguliers
        """
        # Convertir la date de début en timestamp Unix
        dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        
        prices = []
        price_list_chronological = []
        
        for i in range(total_intervals):
            # Calculer le timestamp pour ce point
            current_dt = dt + timedelta(minutes=i * interval_minutes)
            timestamp_ms = int(current_dt.timestamp() * 1000)
            
            # Calculer le timestamp de fin (1 minute après)
            end_timestamp_ms = timestamp_ms + 60000
            
            # Récupérer le prix à ce moment
            price = self.get_price_historical(asset_id, timestamp_ms, end_timestamp_ms)
            
            if price:
                time_str = current_dt.strftime('%Y-%m-%d %H:%M:%S')
                
                prices.append({
                    'timestamp': timestamp_ms,
                    'datetime': time_str,
                    'price': price,
                    'interval': i
                })
                
                price_list_chronological.append(price)
            
            # Petite pause pour éviter de surcharger l'API
            if not self.mock_mode:
                time.sleep(0.1)
        
        return {
            'detailed_data': prices,
            'price_list': price_list_chronological
        }
    
    def _generate_mock_price(self, asset_id: str, timestamp_ms: int) -> Optional[float]:
        """Génère un prix mock basé sur le ticker et le timestamp"""
        ticker = asset_id.upper()
        
        if ticker not in self.mock_prices:
            return None
        
        base_price = self.mock_prices[ticker]["current"]
        volatility = self.mock_prices[ticker]["volatility"]
        
        # Utiliser le timestamp pour créer une variation déterministe
        import random
        seed = timestamp_ms % 1000000  # Utiliser les derniers 6 chiffres
        rnd = random.Random(seed)
        
        # Variation entre -volatility et +volatility
        variation = rnd.uniform(-volatility, volatility)
        mock_price = base_price * (1 + variation)
        
        return round(mock_price, 6)
    
    def simulate_position(self, position_data: Dict[str, Any], capital: float = 100.0, 
                        simulation_hours: int = 24, verbose: bool = True) -> Dict[str, Any]:
        """
        Simule une position de trading avec les données fournies
        """
        # Extraire les données
        ticker = position_data.get("ticker", "")
        sentiment = position_data.get("sentiment", "")
        leverage_str = position_data.get("leverage", "1")
        take_profits = position_data.get("take_profits", [])
        stop_loss = position_data.get("stop_loss")
        entry_price = position_data.get("entry_price")
        timestamp = position_data.get("timestamp", "")
        
        # Validation
        if not all([ticker, sentiment, entry_price]):
            return {"error": "Données manquantes (ticker, sentiment, entry_price)"}
        
        # Conversion du leverage
        try:
            leverage = float(leverage_str)
        except (ValueError, TypeError):
            leverage = 1.0
        
        if verbose:
            print(f"\n🎯 SIMULATION DE POSITION: {ticker} {sentiment.upper()}")
            print(f"📅 Timestamp: {timestamp}")
            print(f"💰 Capital: ${capital}")
            print(f"⚖️ Leverage: {leverage}x")
            print(f"🎯 Entry Price: ${entry_price}")
            print(f"📈 Take Profits: {take_profits}")
            print(f"⛔ Stop Loss: ${stop_loss}")
            print(f"🔧 Mode: {'MOCK' if self.mock_mode else 'API'}")
            print("-" * 60)
        
        # Rechercher l'asset ID
        asset_id = self.search_asset_id(ticker)
        if not asset_id:
            return {"error": f"Asset {ticker} non trouvé"}
        
        # Récupérer l'historique des prix
        total_intervals = simulation_hours * 60  # 1 point par minute
        price_history = self.get_price_history_interval(
            asset_id, timestamp, interval_minutes=1, total_intervals=total_intervals
        )
        
        if not price_history['detailed_data']:
            return {"error": "Aucun prix historique disponible"}
        
        # Simulation de la position
        results = self._simulate_trading_logic(
            price_history['detailed_data'], 
            entry_price, sentiment, leverage, take_profits, stop_loss, capital
        )
        
        return {
            "ticker": ticker,
            "sentiment": sentiment,
            "capital": capital,
            "leverage": leverage,
            "entry_price": entry_price,
            "take_profits": take_profits,
            "stop_loss": stop_loss,
            "simulation_hours": simulation_hours,
            "results": results,
            "price_history": price_history['detailed_data'][:10]  # Premiers 10 points pour référence
        }
    
    def _simulate_trading_logic(self, price_data: List[Dict], entry_price: float, 
                              sentiment: str, leverage: float, take_profits: List[float], 
                              stop_loss: float, capital: float) -> Dict[str, Any]:
        """
        Logique de simulation du trading
        """
        if not entry_price:
            # Si pas de prix d'entrée spécifié, utiliser le premier prix disponible
            entry_price = price_data[0]['price']
        
        # Calculer la quantité achetée/vendue
        effective_capital = capital * leverage
        quantity = capital / entry_price  # Quantité basée sur le capital sans leverage
        
        position_active = True
        exit_reason = None
        exit_price = None
        exit_time = None
        tp_hits = []  # Take profits atteints
        max_gain = 0
        max_loss = 0
        
        for i, price_point in enumerate(price_data):
            current_price = price_point['price']
            current_time = price_point['datetime']
            
            if not position_active:
                break
            
            # Calculer le P&L actuel
            if sentiment == "long":
                price_diff = current_price - entry_price
            else:  # short
                price_diff = entry_price - current_price
            
            # P&L avec leverage
            pnl_percent = (price_diff / entry_price) * leverage
            pnl_dollar = capital * pnl_percent
            
            # Suivre les gains/pertes max
            if pnl_dollar > max_gain:
                max_gain = pnl_dollar
            if pnl_dollar < max_loss:
                max_loss = pnl_dollar
            
            # Vérifier Stop Loss
            if stop_loss:
                if sentiment == "long" and current_price <= stop_loss:
                    position_active = False
                    exit_reason = "Stop Loss"
                    exit_price = stop_loss
                    exit_time = current_time
                    continue
                elif sentiment == "short" and current_price >= stop_loss:
                    position_active = False
                    exit_reason = "Stop Loss"
                    exit_price = stop_loss
                    exit_time = current_time
                    continue
            
            # Vérifier Take Profits
            for tp_price in take_profits:
                if tp_price not in [tp['price'] for tp in tp_hits]:  # Pas déjà atteint
                    if sentiment == "long" and current_price >= tp_price:
                        tp_hits.append({
                            'price': tp_price,
                            'time': current_time,
                            'interval': i
                        })
                    elif sentiment == "short" and current_price <= tp_price:
                        tp_hits.append({
                            'price': tp_price,
                            'time': current_time,
                            'interval': i
                        })
        
        # Calculer le résultat final
        final_price = price_data[-1]['price'] if not exit_price else exit_price
        
        if sentiment == "long":
            final_price_diff = final_price - entry_price
        else:
            final_price_diff = entry_price - final_price
        
        final_pnl_percent = (final_price_diff / entry_price) * leverage
        final_pnl_dollar = capital * final_pnl_percent
        
        return {
            "position_closed": not position_active,
            "exit_reason": exit_reason,
            "exit_price": exit_price,
            "exit_time": exit_time,
            "final_price": final_price,
            "final_pnl_dollar": final_pnl_dollar,
            "final_pnl_percent": final_pnl_percent * 100,
            "max_gain": max_gain,
            "max_loss": max_loss,
            "take_profits_hit": tp_hits,
            "quantity": quantity,
            "effective_capital": effective_capital
        }
    
    def simulate_all_positions(self, consolidated_analysis: Dict[str, Any], 
                             capital_per_position: float = 100.0) -> Dict[str, Any]:
        """
        Simule toutes les positions d'une analyse consolidée
        """
        tweets_analysis = consolidated_analysis.get("tweets_analysis", [])
        
        if not tweets_analysis:
            return {"error": "Aucune position à simuler"}
        
        print(f"\n🎮 SIMULATION DE {len(tweets_analysis)} POSITIONS")
        print(f"💰 Capital par position: ${capital_per_position}")
        print("=" * 50)
        
        simulation_results = []
        total_pnl = 0
        total_capital = 0
        
        for i, position in enumerate(tweets_analysis, 1):
            print(f"\n📍 Position #{i}/{len(tweets_analysis)}: {position.get('ticker', 'N/A')} {position.get('sentiment', 'N/A').upper()}")
            
            result = self.simulate_position(position, capital_per_position, verbose=False)
            
            if "error" not in result:
                pnl = result["results"]["final_pnl_dollar"]
                total_pnl += pnl
                total_capital += capital_per_position
                
                # Affichage du résultat
                emoji = "✅" if pnl >= 0 else "❌"
                print(f"{emoji} Résultat: {pnl:+.2f}$ ({result['results']['final_pnl_percent']:+.2f}%)")
                
                if result["results"]["take_profits_hit"]:
                    print(f"🎯 Take Profits atteints: {len(result['results']['take_profits_hit'])}")
                
                if result["results"]["position_closed"]:
                    print(f"🚪 Position fermée: {result['results']['exit_reason']}")
            else:
                print(f"❌ Erreur: {result['error']}")
            
            simulation_results.append(result)
            
            # Pause entre les simulations
            time.sleep(0.5)
        
        # Résumé global
        print(f"\n{'='*50}")
        print(f"📊 RÉSUMÉ GLOBAL")
        print(f"💰 Capital total investi: ${total_capital:.2f}")
        print(f"📈 P&L total: {total_pnl:+.2f}$")
        
        # Éviter la division par zéro
        if total_capital > 0:
            roi_percent = (total_pnl/total_capital)*100
            print(f"📊 ROI global: {roi_percent:+.2f}%")
        else:
            roi_percent = 0
            print(f"📊 ROI global: N/A (aucune position simulée avec succès)")
        
        return {
            "total_capital": total_capital,
            "total_pnl": total_pnl,
            "roi_percent": roi_percent,
            "positions_simulated": len(simulation_results),
            "individual_results": simulation_results
        }
