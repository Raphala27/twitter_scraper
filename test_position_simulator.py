#!/usr/bin/env python3
"""
Test du simulateur de positions avec des données réalistes
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coincap_api.position_simulator import PositionSimulator

def test_realistic_position():
    """Test avec une position réaliste"""
    
    # Données de position réalistes
    position_data = {
        "ticker": "BTC",
        "sentiment": "long",
        "leverage": "10",
        "take_profits": [65000, 67000, 70000],  # Prix réalistes pour BTC
        "stop_loss": 60000,
        "entry_price": 63000,
        "timestamp": "2024-04-16T23:35:00Z"  # Date dans le passé
    }
    
    try:
        print("🧪 Test du simulateur de positions")
        print("=" * 50)
        
        simulator = PositionSimulator()
        result = simulator.simulate_position(position_data, capital=100.0, simulation_hours=6)
        
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
        else:
            print(f"✅ Simulation réussie!")
            print(f"📊 Résultat final: {result['results']['final_pnl_dollar']:+.2f}$")
            print(f"📈 ROI: {result['results']['final_pnl_percent']:+.2f}%")
            print(f"🎯 Take Profits atteints: {len(result['results']['take_profits_hit'])}")
            
            if result['results']['position_closed']:
                print(f"🚪 Position fermée: {result['results']['exit_reason']}")
    
    except Exception as e:
        print(f"❌ Erreur du test: {e}")
        import traceback
        traceback.print_exc()

def test_eth_realistic():
    """Test avec ETH à des prix réalistes"""
    
    position_data = {
        "ticker": "ETH", 
        "sentiment": "long",
        "leverage": "20",
        "take_profits": [3200, 3300, 3400],  # Prix réalistes pour ETH
        "stop_loss": 3000,
        "entry_price": 3100,
        "timestamp": "2024-04-16T23:35:00Z"
    }
    
    try:
        print("\n🧪 Test ETH réaliste")
        print("=" * 50)
        
        simulator = PositionSimulator()
        result = simulator.simulate_position(position_data, capital=100.0, simulation_hours=4)
        
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
        else:
            print(f"✅ Simulation ETH réussie!")
            print(f"📊 Résultat final: {result['results']['final_pnl_dollar']:+.2f}$")
            print(f"📈 ROI: {result['results']['final_pnl_percent']:+.2f}%")
            
    except Exception as e:
        print(f"❌ Erreur test ETH: {e}")

if __name__ == "__main__":
    test_realistic_position()
    test_eth_realistic()
