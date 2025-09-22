#!/usr/bin/env python3
"""
Test rapide du simulateur en mode mock
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coincap_api.position_simulator import PositionSimulator

def test_mock_simulator():
    """Test rapide avec le mode mock"""
    
    print("🧪 Test du simulateur en mode MOCK")
    print("=" * 50)
    
    # Créer le simulateur en mode mock
    simulator = PositionSimulator(mock_mode=True)
    
    # Données de test
    position_data = {
        "ticker": "BTC",
        "sentiment": "long",
        "leverage": "10",
        "take_profits": [65000, 67000, 70000],
        "stop_loss": 60000,
        "entry_price": 63000,
        "timestamp": "2024-04-16T23:35:00Z"
    }
    
    try:
        result = simulator.simulate_position(position_data, capital=100.0, simulation_hours=2)
        
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
        else:
            print(f"✅ Simulation mock réussie!")
            res = result['results']
            print(f"📊 P&L final: {res['final_pnl_dollar']:+.2f}$")
            print(f"📈 ROI: {res['final_pnl_percent']:+.2f}%")
            print(f"🎯 TP atteints: {len(res['take_profits_hit'])}")
            
            if res['position_closed']:
                print(f"🚪 Position fermée: {res['exit_reason']}")
            
            print(f"📈 Gain max: ${res['max_gain']:+.2f}")
            print(f"📉 Perte max: ${res['max_loss']:+.2f}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_multiple_positions_mock():
    """Test avec plusieurs positions en mode mock"""
    
    print(f"\n🧪 Test positions multiples (MOCK)")
    print("=" * 50)
    
    consolidated_analysis = {
        "account": "@test_mock",
        "total_tweets": 2,
        "analysis_summary": {
            "total_positions": 2,
            "long_positions": 1,
            "short_positions": 1
        },
        "tweets_analysis": [
            {
                "tweet_number": 1,
                "timestamp": "2024-04-16T23:35:00Z",
                "ticker": "BTC",
                "sentiment": "long",
                "leverage": "5",
                "take_profits": [65000, 67000],
                "stop_loss": 60000,
                "entry_price": 63000
            },
            {
                "tweet_number": 2,
                "timestamp": "2024-04-16T23:40:00Z",
                "ticker": "ETH",
                "sentiment": "short",
                "leverage": "10",
                "take_profits": [3000, 2900],
                "stop_loss": 3300,
                "entry_price": 3150
            }
        ]
    }
    
    try:
        simulator = PositionSimulator(mock_mode=True)
        result = simulator.simulate_all_positions(consolidated_analysis, capital_per_position=100.0)
        
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
        else:
            print(f"\n🎯 RÉSULTATS MOCK:")
            print(f"💰 Capital total: ${result['total_capital']:.2f}")
            print(f"📈 P&L total: {result['total_pnl']:+.2f}$")
            print(f"📊 ROI: {result['roi_percent']:+.2f}%")
            
    except Exception as e:
        print(f"❌ Erreur test multiple: {e}")

if __name__ == "__main__":
    test_mock_simulator()
    test_multiple_positions_mock()
