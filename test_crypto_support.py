#!/usr/bin/env python3
"""
Test de validation des cryptomonnaies supportées en mode mock
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coincap_api.position_simulator import PositionSimulator

def test_supported_cryptos():
    """Test toutes les cryptomonnaies supportées en mode mock"""
    
    print("🧪 TEST DES CRYPTOMONNAIES SUPPORTÉES EN MODE MOCK")
    print("=" * 60)
    
    simulator = PositionSimulator(mock_mode=True)
    
    # Liste de toutes les cryptos supportées
    supported_cryptos = list(simulator.mock_prices.keys())
    
    print(f"📋 Cryptomonnaies supportées ({len(supported_cryptos)}):")
    for i, crypto in enumerate(supported_cryptos, 1):
        price_info = simulator.mock_prices[crypto]
        print(f"  {i:2d}. {crypto:<6} - Prix: ${price_info['current']:>8.2f} - Volatilité: {price_info['volatility']:.1%}")
    
    print(f"\n🔍 TEST DE RECHERCHE D'ASSETS:")
    print("-" * 40)
    
    successful_searches = 0
    for crypto in supported_cryptos:
        asset_id = simulator.search_asset_id(crypto)
        if asset_id:
            print(f"✅ {crypto:<6} -> {asset_id}")
            successful_searches += 1
        else:
            print(f"❌ {crypto:<6} -> Échec")
    
    print(f"\n📊 RÉSULTATS:")
    print(f"✅ Succès: {successful_searches}/{len(supported_cryptos)}")
    print(f"📈 Taux de réussite: {(successful_searches/len(supported_cryptos))*100:.1f}%")
    
    # Test d'une simulation rapide avec différentes cryptos
    print(f"\n🎮 TEST DE SIMULATION RAPIDE:")
    print("-" * 40)
    
    test_positions = [
        {"ticker": "UNI", "sentiment": "short", "leverage": "5", "take_profits": [6.9], "stop_loss": 7.2, "entry_price": 7.0, "timestamp": "2024-01-01T00:00:00Z"},
        {"ticker": "LTC", "sentiment": "long", "leverage": "3", "take_profits": [87.0], "stop_loss": 82.0, "entry_price": 85.0, "timestamp": "2024-01-01T00:00:00Z"},
        {"ticker": "LINK", "sentiment": "long", "leverage": "2", "take_profits": [15.0], "stop_loss": 14.0, "entry_price": 14.5, "timestamp": "2024-01-01T00:00:00Z"},
        {"ticker": "AVAX", "sentiment": "short", "leverage": "4", "take_profits": [34.0], "stop_loss": 36.0, "entry_price": 35.0, "timestamp": "2024-01-01T00:00:00Z"}
    ]
    
    for i, position in enumerate(test_positions, 1):
        print(f"\n📍 Test {i}: {position['ticker']} {position['sentiment'].upper()}")
        result = simulator.simulate_position(position, capital=50.0, simulation_hours=1, verbose=False)
        
        if "error" not in result:
            res = result['results']
            status = "✅" if res['final_pnl_dollar'] >= 0 else "❌"
            print(f"{status} Résultat: {res['final_pnl_dollar']:+.2f}$ ({res['final_pnl_percent']:+.2f}%)")
        else:
            print(f"❌ Erreur: {result['error']}")

if __name__ == "__main__":
    test_supported_cryptos()
