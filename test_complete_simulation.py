#!/usr/bin/env python3
"""
Test de simulation complète avec données consolidées
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coincap_api.position_simulator import PositionSimulator

def test_complete_simulation():
    """Test d'une simulation complète avec plusieurs positions"""
    
    # Données consolidées simulées avec prix réalistes
    consolidated_analysis = {
        "account": "@trader_test",
        "total_tweets": 3,
        "analysis_summary": {
            "total_positions": 3,
            "long_positions": 2,
            "short_positions": 1
        },
        "tweets_analysis": [
            {
                "tweet_number": 1,
                "timestamp": "2024-04-16T23:35:00Z",
                "ticker": "BTC",
                "sentiment": "long",
                "leverage": "10",
                "take_profits": [65000, 67000, 70000],
                "stop_loss": 60000,
                "entry_price": 63000
            },
            {
                "tweet_number": 2,
                "timestamp": "2024-04-16T23:40:00Z", 
                "ticker": "ETH",
                "sentiment": "long",
                "leverage": "20",
                "take_profits": [3200, 3300, 3400],
                "stop_loss": 3000,
                "entry_price": 3100
            },
            {
                "tweet_number": 3,
                "timestamp": "2024-04-16T23:45:00Z",
                "ticker": "BTC", 
                "sentiment": "short",
                "leverage": "15",
                "take_profits": [62000, 61000, 60000],
                "stop_loss": 65000,
                "entry_price": 63500
            }
        ]
    }
    
    try:
        print("🧪 Test de simulation complète")
        print("=" * 70)
        
        simulator = PositionSimulator()
        result = simulator.simulate_all_positions(consolidated_analysis, capital_per_position=100.0)
        
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
        else:
            print(f"\n🎯 RÉSULTATS FINAUX:")
            print(f"💰 Capital total investi: ${result['total_capital']:.2f}")
            print(f"📈 P&L total: {result['total_pnl']:+.2f}$")
            print(f"📊 ROI global: {result['roi_percent']:+.2f}%")
            print(f"🔢 Positions simulées: {result['positions_simulated']}")
            
            # Détail par position
            print(f"\n📋 DÉTAIL PAR POSITION:")
            for i, pos_result in enumerate(result['individual_results'], 1):
                if "error" not in pos_result:
                    res = pos_result['results']
                    ticker = pos_result['ticker']
                    sentiment = pos_result['sentiment']
                    pnl = res['final_pnl_dollar']
                    roi = res['final_pnl_percent']
                    
                    emoji = "✅" if pnl >= 0 else "❌"
                    print(f"{emoji} Position #{i}: {ticker} {sentiment.upper()} → {pnl:+.2f}$ ({roi:+.2f}%)")
                    
                    if res['take_profits_hit']:
                        print(f"   🎯 TP atteints: {len(res['take_profits_hit'])}/{len(pos_result['take_profits'])}")
                    
                    if res['position_closed']:
                        print(f"   🚪 Fermée: {res['exit_reason']} à ${res['exit_price']}")
                else:
                    print(f"❌ Position #{i}: Erreur - {pos_result['error']}")
    
    except Exception as e:
        print(f"❌ Erreur du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_simulation()
