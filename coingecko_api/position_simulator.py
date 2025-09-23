#!/usr/bin/env python3
"""
Position Simulator for Cryptocurrency Trading using CoinGecko API

This module simulates cryptocurrency trading positions using historical price data
from CoinGecko API to evaluate the performance of AI-generated trading signals.
"""

# Standard library imports
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Third-party imports
import requests
from dotenv import load_dotenv

# Local imports
try:
    from .fetch_prices import convert_twitter_timestamp_to_iso
except ImportError:
    from fetch_prices import convert_twitter_timestamp_to_iso


class PositionSimulator:
    """
    Trading position simulator using CoinGecko API for historical price data
    """
    
    def __init__(self, api_key: str = None, mock_mode: bool = False):
        self.mock_mode = mock_mode
        
        if not mock_mode:
            if api_key:
                self.api_key = api_key
            else:
                load_dotenv()
                self.api_key = os.environ.get("COINGECKO_API_KEY", "")
                if not self.api_key:
                    print("⚠️ COINGECKO_API_KEY non trouvée, utilisation du mode mock")
                    self.mock_mode = True
        
        self.base_url = "https://api.coingecko.com/api/v3"


    def get_coin_id_from_symbol(self, symbol: str) -> Optional[str]:
        """
        Get CoinGecko coin ID from symbol
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        
        Returns:
            CoinGecko coin ID or None if not found
        """
        if self.mock_mode:
            # Mock data for common cryptocurrencies
            mock_mapping = {
                "BTC": "bitcoin",
                "ETH": "ethereum", 
                "BNB": "binancecoin",
                "SOL": "solana",
                "ADA": "cardano",
                "DOT": "polkadot",
                "DOGE": "dogecoin",
                "MATIC": "matic-network",
                "LTC": "litecoin",
                "LINK": "chainlink"
            }
            return mock_mapping.get(symbol.upper())
        
        try:
            url = f"{self.base_url}/coins/list"
            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key
                
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


    def get_historical_price_range(self, coin_id: str, start_timestamp: str, end_timestamp: str) -> List[Dict]:
        """
        Get historical price data for a coin over a time range using CoinGecko API
        
        Args:
            coin_id: CoinGecko coin ID
            start_timestamp: Start timestamp in ISO format
            end_timestamp: End timestamp in ISO format
        
        Returns:
            List of price data points
        """
        if self.mock_mode:
            # Generate mock price data
            import random
            
            start_dt = datetime.fromisoformat(convert_twitter_timestamp_to_iso(start_timestamp).replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(convert_twitter_timestamp_to_iso(end_timestamp).replace('Z', '+00:00'))
            
            # Mock base prices for different coins
            base_prices = {
                "bitcoin": 45000,
                "ethereum": 3000,
                "binancecoin": 400,
                "solana": 100,
                "cardano": 0.5,
                "polkadot": 25,
                "dogecoin": 0.08,
                "matic-network": 1.2,
                "litecoin": 150,
                "chainlink": 15
            }
            
            base_price = base_prices.get(coin_id, 100)
            
            # Generate hourly price data with some volatility
            prices = []
            current_dt = start_dt
            current_price = base_price
            
            while current_dt <= end_dt:
                # Add some random volatility
                change_percent = random.uniform(-0.05, 0.05)  # ±5% per hour
                current_price *= (1 + change_percent)
                
                prices.append({
                    "timestamp": current_dt.isoformat(),
                    "price": round(current_price, 6)
                })
                
                current_dt += timedelta(hours=1)
            
            return prices
        
        try:
            # Convert timestamps to Unix timestamps
            start_dt = datetime.fromisoformat(convert_twitter_timestamp_to_iso(start_timestamp).replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(convert_twitter_timestamp_to_iso(end_timestamp).replace('Z', '+00:00'))
            
            start_unix = int(start_dt.timestamp())
            end_unix = int(end_dt.timestamp())
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart/range"
            params = {
                "vs_currency": "usd",
                "from": start_unix,
                "to": end_unix
            }
            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            prices_raw = data.get("prices", [])
            
            # Convert to our format
            prices = []
            for price_point in prices_raw:
                timestamp_ms, price = price_point
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                prices.append({
                    "timestamp": dt.isoformat(),
                    "price": price
                })
            
            return prices
            
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération des prix historiques pour {coin_id}: {e}")
            return []
        except (ValueError, KeyError, TypeError) as e:
            print(f"Erreur lors du traitement des données de prix pour {coin_id}: {e}")
            return []


    def simulate_position(self, position_data: Dict[str, Any], simulation_hours: int = 24) -> Dict[str, Any]:
        """
        Simulate a single trading position
        
        Args:
            position_data: Position information from tweet analysis
            simulation_hours: Number of hours to simulate
        
        Returns:
            Dictionary with simulation results
        """
        ticker = position_data.get("ticker", "").upper()
        sentiment = position_data.get("sentiment", "neutral")
        leverage = position_data.get("leverage", "none")
        entry_price = position_data.get("entry_price")
        take_profits = position_data.get("take_profits", [])
        stop_loss = position_data.get("stop_loss")
        timestamp = position_data.get("timestamp", "")
        
        if sentiment not in ["long", "short"]:
            return {
                "error": f"Sentiment invalide: {sentiment}",
                "ticker": ticker
            }
        
        # Get coin ID
        coin_id = self.get_coin_id_from_symbol(ticker)
        if not coin_id:
            return {
                "error": f"Coin ID non trouvé pour {ticker}",
                "ticker": ticker
            }
        
        # Calculate simulation time range
        if timestamp:
            # Convert Twitter timestamp format to ISO
            iso_timestamp = convert_twitter_timestamp_to_iso(timestamp)
            start_dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        else:
            start_dt = datetime.now()
        
        end_dt = start_dt + timedelta(hours=simulation_hours)
        
        # Get historical price data
        price_data = self.get_historical_price_range(
            coin_id, 
            start_dt.isoformat(), 
            end_dt.isoformat()
        )
        
        if not price_data:
            return {
                "error": f"Données de prix non disponibles pour {ticker}",
                "ticker": ticker
            }
        
        # Use entry price or first available price
        if entry_price:
            effective_entry_price = entry_price
        else:
            effective_entry_price = price_data[0]["price"]
        
        # Convert leverage to numeric
        try:
            leverage_multiplier = float(leverage) if leverage != "none" else 1.0
        except (ValueError, TypeError):
            leverage_multiplier = 1.0
        
        # Simulation parameters
        initial_capital = 100.0  # $100 per position
        position_size = (initial_capital * leverage_multiplier) / effective_entry_price
        
        # Track simulation with partial exits
        max_capital = initial_capital
        min_capital = initial_capital
        remaining_position_size = position_size  # Position restante
        realized_pnl = 0.0  # P&L réalisé (profits pris)
        unrealized_pnl = 0.0  # P&L non réalisé (position en cours)
        
        # Take profit tracking
        take_profits_hit = []  # TPs déjà atteints
        tp_percentages = []  # Pourcentages pour chaque TP
        
        # Calculer les pourcentages pour chaque Take Profit
        if take_profits:
            num_tps = len(take_profits)
            tp_percentages = [1.0 / num_tps] * num_tps  # Répartition égale
        
        exit_info = {
            "fully_closed": False,
            "exit_price": None,
            "exit_reason": None,
            "exit_time": None,
            "partial_exits": []
        }
        
        # Display historical price data for debugging
        print(f"   📈 Données historiques pour {ticker} (Entry: ${effective_entry_price}):")
        if leverage_multiplier > 1.0:
            print(f"   🔥 Levier {leverage_multiplier:.0f}x appliqué - Taille position: {position_size:.6f} {ticker}")
            print(f"      💰 Capital: ${initial_capital} → Exposition: ${initial_capital * leverage_multiplier:.0f}")
        for i, price_point in enumerate(price_data[:10]):  # Show first 10 points
            price = price_point["price"]
            timestamp = price_point["timestamp"]
            pnl_preview = (price - effective_entry_price) * position_size if sentiment == "long" else (effective_entry_price - price) * position_size
            print(f"      {i+1:2d}. ${price:,.2f} à {timestamp} (P&L: {pnl_preview:+.2f}$)")
        
        if len(price_data) > 10:
            print(f"      ... et {len(price_data) - 10} autres points de données")
        print()
        
        # Simulate through price data
        for price_point in price_data:
            current_price = price_point["price"]
            current_time = price_point["timestamp"]
            
            # Check stop loss first (fermeture complète)
            if stop_loss and remaining_position_size > 0:
                if sentiment == "long" and current_price <= stop_loss:
                    # Fermeture complète au stop loss
                    if sentiment == "long":
                        final_pnl = (stop_loss - effective_entry_price) * remaining_position_size
                    else:
                        final_pnl = (effective_entry_price - stop_loss) * remaining_position_size
                    
                    realized_pnl += final_pnl
                    remaining_position_size = 0
                    exit_info.update({
                        "fully_closed": True,
                        "exit_price": stop_loss,
                        "exit_reason": "Stop Loss",
                        "exit_time": current_time
                    })
                    print(f"   🛑 Stop Loss déclenché à ${stop_loss}")
                    print(f"      ⏰ Prix marché: ${current_price:,.2f} à {current_time}")
                    print(f"      💸 P&L final: ${final_pnl:+.2f}")
                    print()
                    break
                elif sentiment == "short" and current_price >= stop_loss:
                    # Fermeture complète au stop loss
                    if sentiment == "long":
                        final_pnl = (stop_loss - effective_entry_price) * remaining_position_size
                    else:
                        final_pnl = (effective_entry_price - stop_loss) * remaining_position_size
                    
                    realized_pnl += final_pnl
                    remaining_position_size = 0
                    exit_info.update({
                        "fully_closed": True,
                        "exit_price": stop_loss,
                        "exit_reason": "Stop Loss",
                        "exit_time": current_time
                    })
                    print(f"   🛑 Stop Loss déclenché à ${stop_loss}")
                    print(f"      ⏰ Prix marché: ${current_price:,.2f} à {current_time}")
                    print(f"      💸 P&L final: ${final_pnl:+.2f}")
                    print()
                    break
            
            # Check take profits (sorties partielles)
            if take_profits and remaining_position_size > 0:
                for i, tp in enumerate(take_profits):
                    # Skip si ce TP a déjà été atteint
                    if tp in take_profits_hit:
                        continue
                    
                    tp_hit = False
                    if sentiment == "long" and current_price >= tp:
                        tp_hit = True
                    elif sentiment == "short" and current_price <= tp:
                        tp_hit = True
                    
                    if tp_hit:
                        # Calculer la taille de la sortie partielle
                        exit_percentage = tp_percentages[i]
                        exit_size = position_size * exit_percentage
                        
                        # S'assurer qu'on ne vend pas plus que ce qui reste
                        exit_size = min(exit_size, remaining_position_size)
                        
                        # Calculer le P&L pour cette sortie partielle
                        if sentiment == "long":
                            partial_pnl = (tp - effective_entry_price) * exit_size
                        else:
                            partial_pnl = (effective_entry_price - tp) * exit_size
                        
                        # Mettre à jour les totaux
                        realized_pnl += partial_pnl
                        remaining_position_size -= exit_size
                        take_profits_hit.append(tp)
                        
                        # Enregistrer cette sortie partielle
                        exit_info["partial_exits"].append({
                            "tp_level": tp,
                            "exit_price": tp,
                            "exit_percentage": exit_percentage,
                            "exit_size": exit_size,
                            "pnl": partial_pnl,
                            "time": current_time,
                            "market_price": current_price
                        })
                        
                        print(f"   🎯 Take Profit ${tp}: -{exit_percentage*100:.1f}% position (+${partial_pnl:.2f})")
                        print(f"      ⏰ Prix marché: ${current_price:,.2f} à {current_time}")
                        print(f"      📊 Taille sortie: {exit_size:.6f} {ticker} ({exit_percentage*100:.1f}% de la position)")
                        print(f"      💰 P&L de cette sortie: ${partial_pnl:+.2f}")
                        print(f"      📈 Position restante: {remaining_position_size:.6f} {ticker}")
                        print()
                        
                        # Si toute la position est fermée
                        if remaining_position_size <= 0.001:  # Seuil de tolérance
                            exit_info.update({
                                "fully_closed": True,
                                "exit_reason": "All Take Profits Hit",
                                "exit_time": current_time
                            })
                            remaining_position_size = 0
                            break
            
            # Calculer le P&L non réalisé de la position restante
            if remaining_position_size > 0:
                if sentiment == "long":
                    unrealized_pnl = (current_price - effective_entry_price) * remaining_position_size
                else:
                    unrealized_pnl = (effective_entry_price - current_price) * remaining_position_size
                
                current_total_capital = initial_capital + realized_pnl + unrealized_pnl
                max_capital = max(max_capital, current_total_capital)
                min_capital = min(min_capital, current_total_capital)
                
                # Affichage périodique de l'évolution (tous les 10 points pour éviter le spam)
                if len(price_data) > 50 and (len([p for p in price_data if p["timestamp"] <= current_time]) % (len(price_data) // 5) == 0):
                    print(f"   📊 ${current_price:,.2f} | P&L non réalisé: ${unrealized_pnl:+.2f} | Capital total: ${current_total_capital:.2f}")
            
            # Si la position est complètement fermée, arrêter la simulation
            if exit_info["fully_closed"]:
                break
        
        # Résultats finaux
        if not exit_info["fully_closed"]:
            # Position encore ouverte à la fin
            final_price = price_data[-1]["price"]
            if remaining_position_size > 0:
                if sentiment == "long":
                    unrealized_pnl = (final_price - effective_entry_price) * remaining_position_size
                else:
                    unrealized_pnl = (effective_entry_price - final_price) * remaining_position_size
            
            exit_info.update({
                "exit_price": final_price,
                "exit_reason": "Position Still Open",
                "exit_time": price_data[-1]["timestamp"]
            })
        
        # Calculs finaux
        total_pnl = realized_pnl + unrealized_pnl
        final_capital = initial_capital + total_pnl
        roi_percent = (total_pnl / initial_capital) * 100
        
        # Calculate maximum drawdown
        max_drawdown_percent = ((max_capital - min_capital) / max_capital) * 100 if max_capital > 0 else 0
        
        return {
            "ticker": ticker,
            "sentiment": sentiment,
            "leverage": leverage_multiplier,
            "entry_price": effective_entry_price,
            "exit_price": exit_info["exit_price"],
            "exit_reason": exit_info["exit_reason"],
            "exit_time": exit_info["exit_time"],
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": total_pnl,
            "roi_percent": roi_percent,
            "max_capital": max_capital,
            "min_capital": min_capital,
            "max_drawdown_percent": max_drawdown_percent,
            "simulation_hours": simulation_hours,
            "price_points": len(price_data),
            "position_status": {
                "fully_closed": exit_info["fully_closed"],
                "remaining_position_size": remaining_position_size,
                "position_closed_percent": ((position_size - remaining_position_size) / position_size) * 100,
                "partial_exits": exit_info["partial_exits"]
            }
        }


    def simulate_all_positions(self, consolidated_analysis: Dict[str, Any], simulation_hours: int = 24) -> Dict[str, Any]:
        """
        Simulate all positions from consolidated analysis
        
        Args:
            consolidated_analysis: Consolidated analysis from tweet processing
            simulation_hours: Number of hours to simulate each position
        
        Returns:
            Dictionary with overall simulation results
        """
        tweets_analysis = consolidated_analysis.get("tweets_analysis", [])
        
        if not tweets_analysis:
            return {
                "error": "Aucune analyse de tweets trouvée pour la simulation"
            }
        
        simulation_results = []
        total_capital = 0
        total_pnl = 0
        
        print(f"🎯 Simulation de {len(tweets_analysis)} positions sur {simulation_hours}h...")
        
        for i, position_data in enumerate(tweets_analysis, 1):
            ticker = position_data.get("ticker", "")
            sentiment = position_data.get("sentiment", "")
            
            print(f"📊 {i}/{len(tweets_analysis)}: Simulation {sentiment} {ticker}...")
            leverage_info = position_data.get("leverage", "none")
            if leverage_info != "none":
                print(f"   📈 Levier: {leverage_info}x (Capital effectif: ${100 * float(leverage_info):.0f})")
            
            result = self.simulate_position(position_data, simulation_hours)
            
            if "error" not in result:
                simulation_results.append(result)
                total_capital += result["initial_capital"]
                total_pnl += result["total_pnl"]
                
                print(f"   ✅ {result['exit_reason']}: {result['total_pnl']:+.2f}$ ({result['roi_percent']:+.2f}%)")
                
                # Affichage détaillé des paliers atteints
                if result['position_status']['partial_exits']:
                    print(f"   🎯 Paliers atteints: {len(result['position_status']['partial_exits'])}/{len(position_data.get('take_profits', []))}")
                    for idx, exit_data in enumerate(result['position_status']['partial_exits'], 1):
                        print(f"      TP{idx}: ${exit_data['tp_level']} → -{exit_data['exit_percentage']*100:.1f}% position (+${exit_data['pnl']:.2f})")
                else:
                    total_tps = len(position_data.get('take_profits', []))
                    if total_tps > 0:
                        print(f"   🎯 Paliers atteints: 0/{total_tps} (aucun TP touché)")
                
                # Informations sur la position restante
                if not result['position_status']['fully_closed']:
                    print(f"   📊 Position restante: {100 - result['position_status']['position_closed_percent']:.1f}%")
                    print(f"      💰 P&L réalisé: ${result['realized_pnl']:+.2f} | Non réalisé: ${result['unrealized_pnl']:+.2f}")
                else:
                    print("   ✅ Position complètement fermée")
                
                if result['position_status']['partial_exits']:
                    print(f"      💰 Realized P&L: ${result['realized_pnl']:+.2f}")
                    if result['unrealized_pnl'] != 0:
                        print(f"      📊 Unrealized P&L: ${result['unrealized_pnl']:+.2f}")
                    print(f"      📈 Position closed: {result['position_status']['position_closed_percent']:.1f}%")
            else:
                print(f"   ❌ {result['error']}")
            
            # Rate limiting for API calls
            if not self.mock_mode:
                time.sleep(1)
        
        if not simulation_results:
            return {
                "error": "Aucune position simulée avec succès"
            }
        
        # Calculate overall metrics
        successful_positions = len(simulation_results)
        profitable_positions = len([r for r in simulation_results if r["total_pnl"] > 0])
        losing_positions = len([r for r in simulation_results if r["total_pnl"] < 0])
        win_rate = (profitable_positions / successful_positions * 100) if successful_positions > 0 else 0
        roi_percent = (total_pnl / total_capital * 100) if total_capital > 0 else 0
        
        # Find best and worst trades
        best_trade = max(simulation_results, key=lambda x: x["roi_percent"]) if simulation_results else None
        worst_trade = min(simulation_results, key=lambda x: x["roi_percent"]) if simulation_results else None
        
        # Calculate average metrics
        avg_roi = sum(r["roi_percent"] for r in simulation_results) / len(simulation_results) if simulation_results else 0
        avg_drawdown = sum(r["max_drawdown_percent"] for r in simulation_results) / len(simulation_results) if simulation_results else 0
        
        summary_result = {
            "total_positions": successful_positions,
            "total_capital": total_capital,
            "total_pnl": total_pnl,
            "roi_percent": roi_percent,
            "profitable_positions": profitable_positions,
            "losing_positions": losing_positions,
            "win_rate": win_rate,
            "average_roi": avg_roi,
            "average_drawdown": avg_drawdown,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "simulation_hours": simulation_hours,
            "positions": simulation_results
        }
        
        # Display summary
        self._display_simulation_summary(summary_result)
        
        return summary_result


    def _display_simulation_summary(self, results: Dict[str, Any]) -> None:
        """Display simulation summary"""
        print("📊 RÉSUMÉ GLOBAL")
        print(f"💰 Capital total: ${results['total_capital']:.2f}")
        print(f"📈 P&L total: {results['total_pnl']:+.2f}$")
        print(f"📊 ROI global: {results['roi_percent']:+.2f}%")
        print(f"🎯 Positions: {results['total_positions']} simulées")
        print(f"✅ Gagnantes: {results['profitable_positions']}")
        print(f"❌ Perdantes: {results['losing_positions']}")
        print(f"🎲 Taux de réussite: {results['win_rate']:.1f}%")
        print(f"📊 ROI moyen: {results['average_roi']:+.2f}%")
        print(f"📉 Drawdown moyen: {results['average_drawdown']:.2f}%")
        
        if results.get('best_trade'):
            best = results['best_trade']
            print(f"🏆 Meilleur trade: {best['ticker']} {best['sentiment']} (+{best['roi_percent']:.2f}%)")
        
        if results.get('worst_trade'):
            worst = results['worst_trade']
            print(f"😞 Pire trade: {worst['ticker']} {worst['sentiment']} ({worst['roi_percent']:+.2f}%)")
        
        if results['total_positions'] == 0:
            print("📊 ROI global: N/A (aucune position simulée avec succès)")
