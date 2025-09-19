import os
from typing import List, Dict, Any
from .fetch_prices import fetch_prices_for_cryptos

def load_env_file():
    """Charge manuellement le fichier .env"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def calculate_positions(consolidated_analysis: Dict[str, Any], capital_per_position: float = 100.0, api_key: str = None) -> Dict[str, Any]:
    """
    Calcule les positions de trading basées sur l'analyse consolidée
    
    Args:
        consolidated_analysis: Le dictionnaire consolidé avec les tweets_analysis
        capital_per_position: Capital à investir par position (défaut: 100$)
        api_key: Clé API CoinCap (optionnel, utilise .env par défaut)
    
    Returns:
        Dict avec les positions calculées et les métriques
    """
    # Charger le fichier .env si pas de clé API fournie
    if api_key is None:
        load_env_file()
        api_key = os.environ.get("COINCAP_API_KEY", "")
    
    if not api_key:
        raise ValueError("Clé API CoinCap manquante. Renseignez COINCAP_API_KEY dans le fichier .env")
    
    tweets_analysis = consolidated_analysis.get("tweets_analysis", [])
    
    if not tweets_analysis:
        return {
            "positions": [],
            "total_capital_allocated": 0,
            "total_positions": 0,
            "summary": {"long_positions": 0, "short_positions": 0}
        }
    
    print(f"🔍 Récupération des prix historiques...")
    
    # Récupérer les prix historiques pour tous les tweets
    historical_prices = fetch_prices_for_cryptos(tweets_analysis, api_key)
    
    positions = []
    total_capital = 0
    long_count = 0
    short_count = 0
    
    for entry in tweets_analysis:
        ticker = entry.get("ticker", "")
        sentiment = entry.get("sentiment", "")
        leverage = entry.get("leverage", "1")
        timestamp = entry.get("timestamp", "")
        tweet_number = entry.get("tweet_number", 0)
        
        # Trouver le prix historique correspondant
        price_key = f"{ticker.upper()}_{tweet_number}"
        price_data = historical_prices.get(price_key)
        
        if price_data is None:
            print(f"⚠️ Prix non disponible pour {ticker} (tweet #{tweet_number})")
            continue
        
        price = price_data["price"]
        asset_id = price_data["asset_id"]
        
        # Convertir le leverage en nombre
        try:
            leverage_multiplier = float(leverage) if leverage != "none" else 1.0
        except (ValueError, TypeError):
            leverage_multiplier = 1.0
        
        # Calculer la position
        if sentiment == "long":
            position_type = "LONG"
            long_count += 1
        elif sentiment == "short":
            position_type = "SHORT"
            short_count += 1
        else:
            continue  # Ignorer les positions neutres
        
        # Capital effectif avec leverage
        effective_capital = capital_per_position * leverage_multiplier
        
        # Quantité de crypto achetée/vendue
        quantity = capital_per_position / price
        
        # Calcul de la valeur notionnelle
        notional_value = quantity * price * leverage_multiplier
        
        position = {
            "tweet_number": tweet_number,
            "timestamp": timestamp,
            "ticker": ticker,
            "position_type": position_type,
            "sentiment": sentiment,
            "leverage": leverage_multiplier,
            "entry_price": price,
            "asset_id": asset_id,  # ID CoinCap au lieu du block_number
            "capital_invested": capital_per_position,
            "effective_capital": effective_capital,
            "quantity": quantity,
            "notional_value": notional_value,
            "margin_required": capital_per_position,  # Marge requise = capital investi
            "potential_pnl": {
                "breakeven_price": price,
                "liquidation_price": calculate_liquidation_price(price, position_type, leverage_multiplier),
                "roi_per_1_percent_move": leverage_multiplier  # ROI pour 1% de mouvement
            }
        }
        
        positions.append(position)
        total_capital += capital_per_position
    
    return {
        "positions": positions,
        "total_capital_allocated": total_capital,
        "total_positions": len(positions),
        "summary": {
            "long_positions": long_count,
            "short_positions": short_count,
            "average_leverage": sum(pos["leverage"] for pos in positions) / len(positions) if positions else 0,
            "total_notional_value": sum(pos["notional_value"] for pos in positions),
            "total_margin_required": total_capital
        },
        "risk_metrics": {
            "max_loss_per_position": capital_per_position,
            "total_max_loss": total_capital,
            "leverage_distribution": get_leverage_distribution(positions)
        }
    }

def calculate_liquidation_price(entry_price: float, position_type: str, leverage: float) -> float:
    """
    Calcule le prix de liquidation approximatif
    
    Args:
        entry_price: Prix d'entrée
        position_type: "LONG" ou "SHORT"
        leverage: Multiplicateur de levier
    
    Returns:
        Prix de liquidation estimé
    """
    # Approximation simple : liquidation à ~90% de perte du capital
    liquidation_threshold = 0.9 / leverage
    
    if position_type == "LONG":
        # Pour un long, liquidation si le prix baisse de liquidation_threshold
        return entry_price * (1 - liquidation_threshold)
    else:  # SHORT
        # Pour un short, liquidation si le prix monte de liquidation_threshold
        return entry_price * (1 + liquidation_threshold)

def get_leverage_distribution(positions: List[Dict]) -> Dict[str, int]:
    """
    Retourne la distribution des leverages utilisés
    """
    distribution = {}
    for pos in positions:
        leverage = str(int(pos["leverage"]))
        distribution[leverage] = distribution.get(leverage, 0) + 1
    return distribution

def display_positions_summary(positions_result: Dict[str, Any]) -> None:
    """
    Affiche un résumé formaté des positions calculées
    """
    positions = positions_result["positions"]
    summary = positions_result["summary"]
    risk_metrics = positions_result["risk_metrics"]
    
    print("\n" + "💰" * 25 + " CALCUL DES POSITIONS " + "💰" * 25)
    print(f"📊 Résumé général:")
    print(f"   💵 Capital total alloué: ${positions_result['total_capital_allocated']:.2f}")
    print(f"   📈 Positions LONG: {summary['long_positions']}")
    print(f"   📉 Positions SHORT: {summary['short_positions']}")
    print(f"   ⚖️ Levier moyen: {summary['average_leverage']:.1f}x")
    print(f"   💎 Valeur notionnelle totale: ${summary['total_notional_value']:.2f}")
    
    print(f"\n🎯 Détail des positions:")
    for i, pos in enumerate(positions, 1):
        emoji = "📈" if pos["position_type"] == "LONG" else "📉"
        print(f"   {emoji} #{i}: {pos['ticker']} {pos['position_type']} {pos['leverage']:.1f}x")
        print(f"      💰 ${pos['capital_invested']:.0f} | Prix: ${pos['entry_price']:.2f}")
        print(f"      📦 Quantité: {pos['quantity']:.6f}")
    
    print(f"\n⚠️ Métriques de risque:")
    print(f"   💥 Perte max par position: ${risk_metrics['max_loss_per_position']:.2f}")
    print(f"   🔥 Perte max totale: ${risk_metrics['total_max_loss']:.2f}")
    print(f"   📊 Distribution des leviers: {risk_metrics['leverage_distribution']}")
