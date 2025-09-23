#!/usr/bin/env python3
"""
Position Calculator for Cryptocurrency Trading using CoinGecko API

This module calculates trading positions based on AI analysis results,
including position sizing, risk management, and performance metrics.
"""

# Standard library imports
import os
from typing import Any, Dict

# Local application imports
from .fetch_prices import fetch_prices_for_cryptos


def load_env_file():
    """Load environment variables manually from .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def calculate_positions(consolidated_analysis: Dict[str, Any], capital_per_position: float = 100.0, api_key: str = None) -> Dict[str, Any]:
    """
    Calculate trading positions based on consolidated analysis using CoinGecko API
    
    Args:
        consolidated_analysis: Consolidated analysis from tweet processing
        capital_per_position: Capital allocated per position in USD
        api_key: CoinGecko API key
    
    Returns:
        Dictionary with position calculations and metrics
    """
    if api_key is None:
        load_env_file()
        api_key = os.environ.get("COINGECKO_API_KEY", "")
    
    tweets_analysis = consolidated_analysis.get("tweets_analysis", [])
    
    if not tweets_analysis:
        return {
            "error": "Aucune analyse de tweets trouvée",
            "positions": [],
            "summary": {
                "total_capital": 0,
                "total_positions": 0,
                "risk_metrics": {}
            }
        }
    
    # Extract unique cryptos for price fetching
    unique_cryptos = []
    seen_tickers = set()
    
    for analysis in tweets_analysis:
        ticker = analysis.get("ticker", "").upper()
        timestamp = analysis.get("timestamp", "")
        
        if ticker and ticker not in seen_tickers:
            unique_cryptos.append({
                "ticker": ticker,
                "timestamp": timestamp
            })
            seen_tickers.add(ticker)
    
    print("🔍 Récupération des prix historiques...")
    
    # Fetch prices using CoinGecko API
    prices_data = fetch_prices_for_cryptos(unique_cryptos, api_key)
    
    if not prices_data:
        return {
            "error": "Impossible de récupérer les prix via CoinGecko API",
            "positions": [],
            "summary": {
                "total_capital": 0,
                "total_positions": 0,
                "risk_metrics": {}
            }
        }
    
    # Calculate positions
    positions = []
    total_capital = 0
    
    for analysis in tweets_analysis:
        ticker = analysis.get("ticker", "").upper()
        sentiment = analysis.get("sentiment", "neutral")
        leverage = analysis.get("leverage", "none")
        take_profits = analysis.get("take_profits", [])
        stop_loss = analysis.get("stop_loss")
        entry_price = analysis.get("entry_price")
        tweet_number = analysis.get("tweet_number", 0)
        
        # Skip neutral positions
        if sentiment not in ["long", "short"]:
            continue
        
        price_info = prices_data.get(ticker, {})
        current_price = price_info.get("current_price")
        historical_price = price_info.get("historical_price")
        
        if not current_price:
            print(f"⚠️ Prix non disponible pour {ticker}")
            continue
        
        # Use entry price if provided, otherwise use historical price or current price
        effective_entry_price = entry_price or historical_price or current_price
        
        # Convert leverage to numeric value
        try:
            leverage_multiplier = float(leverage) if leverage != "none" else 1.0
        except (ValueError, TypeError):
            leverage_multiplier = 1.0
        
        # Calculate position size
        position_size = capital_per_position * leverage_multiplier / effective_entry_price
        
        position = {
            "tweet_number": tweet_number,
            "ticker": ticker,
            "sentiment": sentiment,
            "entry_price": effective_entry_price,
            "current_price": current_price,
            "leverage": leverage_multiplier,
            "position_size": position_size,
            "capital_allocated": capital_per_position,
            "total_exposure": capital_per_position * leverage_multiplier,
            "take_profits": take_profits,
            "stop_loss": stop_loss,
            "unrealized_pnl": 0,
            "roi_percent": 0
        }
        
        # Calculate unrealized P&L
        if sentiment == "long":
            position["unrealized_pnl"] = (current_price - effective_entry_price) * position_size
        elif sentiment == "short":
            position["unrealized_pnl"] = (effective_entry_price - current_price) * position_size
        
        # Calculate ROI percentage
        if capital_per_position > 0:
            position["roi_percent"] = (position["unrealized_pnl"] / capital_per_position) * 100
        
        positions.append(position)
        total_capital += capital_per_position
    
    # Calculate summary metrics
    total_pnl = sum(pos["unrealized_pnl"] for pos in positions)
    total_roi = (total_pnl / total_capital * 100) if total_capital > 0 else 0
    
    long_positions = [p for p in positions if p["sentiment"] == "long"]
    short_positions = [p for p in positions if p["sentiment"] == "short"]
    
    profitable_positions = [p for p in positions if p["unrealized_pnl"] > 0]
    losing_positions = [p for p in positions if p["unrealized_pnl"] < 0]
    
    summary = {
        "total_capital": total_capital,
        "total_positions": len(positions),
        "total_pnl": total_pnl,
        "total_roi_percent": total_roi,
        "long_positions": len(long_positions),
        "short_positions": len(short_positions),
        "profitable_positions": len(profitable_positions),
        "losing_positions": len(losing_positions),
        "win_rate": len(profitable_positions) / len(positions) * 100 if positions else 0,
        "risk_metrics": {
            "max_leverage": max([p["leverage"] for p in positions], default=1),
            "total_exposure": sum(p["total_exposure"] for p in positions),
            "average_leverage": sum(p["leverage"] for p in positions) / len(positions) if positions else 0
        }
    }
    
    return {
        "positions": positions,
        "summary": summary,
        "prices_data": prices_data
    }


def display_positions_summary(positions_result: Dict[str, Any]) -> None:
    """
    Display a formatted summary of positions and performance
    
    Args:
        positions_result: Result from calculate_positions function
    """
    if "error" in positions_result:
        print(f"❌ Erreur: {positions_result['error']}")
        return
    
    positions = positions_result.get("positions", [])
    summary = positions_result.get("summary", {})
    
    if not positions:
        print("📊 Aucune position calculée")
        return
    
    print("📊 Résumé général:")
    print(f"💰 Capital total: ${summary.get('total_capital', 0):.2f}")
    print(f"📈 P&L total: {summary.get('total_pnl', 0):+.2f}$")
    print(f"📊 ROI: {summary.get('total_roi_percent', 0):+.2f}%")
    print(f"🎯 Positions: {summary.get('total_positions', 0)} "
          f"(🟢 {summary.get('long_positions', 0)} long, 🔴 {summary.get('short_positions', 0)} short)")
    print(f"✅ Gagnantes: {summary.get('profitable_positions', 0)}")
    print(f"❌ Perdantes: {summary.get('losing_positions', 0)}")
    print(f"🎲 Taux de réussite: {summary.get('win_rate', 0):.1f}%")
    
    print("\n🎯 Détail des positions:")
    for i, pos in enumerate(positions, 1):
        direction = "🟢 LONG" if pos["sentiment"] == "long" else "🔴 SHORT"
        pnl_color = "🟢" if pos["unrealized_pnl"] >= 0 else "🔴"
        
        print(f"  {i}. {direction} {pos['ticker']}")
        print(f"     💵 Entry: ${pos['entry_price']:.2f} | Current: ${pos['current_price']:.2f}")
        print(f"     📊 Size: {pos['position_size']:.4f} {pos['ticker']} | Leverage: {pos['leverage']:.1f}x")
        print(f"     {pnl_color} P&L: {pos['unrealized_pnl']:+.2f}$ ({pos['roi_percent']:+.2f}%)")
    
    print("\n⚠️ Métriques de risque:")
    risk_metrics = summary.get("risk_metrics", {})
    print(f"📊 Exposition totale: ${risk_metrics.get('total_exposure', 0):.2f}")
    print(f"📈 Levier maximum: {risk_metrics.get('max_leverage', 1):.1f}x")
    print(f"📊 Levier moyen: {risk_metrics.get('average_leverage', 1):.1f}x")
