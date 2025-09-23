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
        
        # Track simulation
        current_capital = initial_capital
        max_capital = initial_capital
        min_capital = initial_capital
        exit_price = None
        exit_reason = None
        exit_time = None
        
        # Simulate through price data
        for price_point in price_data:
            current_price = price_point["price"]
            current_time = price_point["timestamp"]
            
            # Calculate current P&L
            if sentiment == "long":
                pnl = (current_price - effective_entry_price) * position_size
            else:  # short
                pnl = (effective_entry_price - current_price) * position_size
            
            current_capital = initial_capital + pnl
            
            # Update max/min capital
            max_capital = max(max_capital, current_capital)
            min_capital = min(min_capital, current_capital)
            
            # Check stop loss
            if stop_loss:
                if sentiment == "long" and current_price <= stop_loss:
                    exit_price = stop_loss
                    exit_reason = "Stop Loss"
                    exit_time = current_time
                    break
                elif sentiment == "short" and current_price >= stop_loss:
                    exit_price = stop_loss
                    exit_reason = "Stop Loss"
                    exit_time = current_time
                    break
            
            # Check take profits
            if take_profits:
                for tp in take_profits:
                    if sentiment == "long" and current_price >= tp:
                        exit_price = tp
                        exit_reason = f"Take Profit ${tp}"
                        exit_time = current_time
                        break
                    elif sentiment == "short" and current_price <= tp:
                        exit_price = tp
                        exit_reason = f"Take Profit ${tp}"
                        exit_time = current_time
                        break
                
                if exit_price:
                    break
        
        # Calculate final results
        if not exit_price:
            exit_price = price_data[-1]["price"]
            exit_reason = "Simulation End"
            exit_time = price_data[-1]["timestamp"]
        
        # Final P&L calculation
        if sentiment == "long":
            final_pnl = (exit_price - effective_entry_price) * position_size
        else:
            final_pnl = (effective_entry_price - exit_price) * position_size
        
        final_capital = initial_capital + final_pnl
        roi_percent = (final_pnl / initial_capital) * 100
        
        # Calculate maximum drawdown
        max_drawdown_percent = ((max_capital - min_capital) / max_capital) * 100 if max_capital > 0 else 0
        
        return {
            "ticker": ticker,
            "sentiment": sentiment,
            "leverage": leverage_multiplier,
            "entry_price": effective_entry_price,
            "exit_price": exit_price,
            "exit_reason": exit_reason,
            "exit_time": exit_time,
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "pnl": final_pnl,
            "roi_percent": roi_percent,
            "max_capital": max_capital,
            "min_capital": min_capital,
            "max_drawdown_percent": max_drawdown_percent,
            "simulation_hours": simulation_hours,
            "price_points": len(price_data)
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
            
            result = self.simulate_position(position_data, simulation_hours)
            
            if "error" not in result:
                simulation_results.append(result)
                total_capital += result["initial_capital"]
                total_pnl += result["pnl"]
                
                print(f"   ✅ {result['exit_reason']}: {result['pnl']:+.2f}$ ({result['roi_percent']:+.2f}%)")
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
        profitable_positions = len([r for r in simulation_results if r["pnl"] > 0])
        losing_positions = len([r for r in simulation_results if r["pnl"] < 0])
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
