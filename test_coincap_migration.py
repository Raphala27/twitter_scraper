#!/usr/bin/env python3
"""
Script de test pour valider la migration vers CoinCap API
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_coincap_import():
    """Test d'import des modules CoinCap"""
    try:
        from coincap_api.fetch_prices import get_crypto_price_at_time, search_asset_by_symbol
        from coincap_api.position_calculator import calculate_positions
        print("✅ Imports CoinCap réussis")
        return True
    except Exception as e:
        print(f"❌ Erreur import CoinCap: {e}")
        return False

def test_env_config():
    """Test de la configuration environnement"""
    from dotenv import load_dotenv
    load_dotenv()
    
    coincap_key = os.environ.get("COINCAP_API_KEY", "")
    if coincap_key and coincap_key != "your_coincap_api_key_here":
        print("✅ Clé API CoinCap configurée")
        return True
    else:
        print("⚠️ Clé API CoinCap non configurée (utilisera le mode test)")
        return False

def test_mock_data():
    """Test avec des données mock"""
    try:
        mock_cryptos = [
            {
                "ticker": "BTC",
                "timestamp": "2024-04-16T23:35:00Z",
                "tweet_number": 1,
                "sentiment": "long",
                "leverage": "10"
            }
        ]
        
        mock_analysis = {
            "tweets_analysis": mock_cryptos,
            "analysis_summary": {
                "total_positions": 1,
                "long_positions": 1,
                "short_positions": 0
            }
        }
        
        # Test sans API (structure seulement)
        from coincap_api.position_calculator import calculate_liquidation_price
        liq_price = calculate_liquidation_price(50000.0, "LONG", 10.0)
        print(f"✅ Calcul de liquidation: ${liq_price:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test mock: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test de migration CoinCap API")
    print("=" * 50)
    
    tests = [
        ("Import des modules", test_coincap_import),
        ("Configuration environnement", test_env_config),
        ("Données mock", test_mock_data),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name}...")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {sum(results)}/{len(results)} tests réussis")
    
    if all(results):
        print("🎉 Migration CoinCap prête !")
        print("\n💡 Prochaines étapes:")
        print("   1. Configurer COINCAP_API_KEY dans .env")
        print("   2. Tester: python3 scraper.py @trader --limit 3 --positions --mock")
    else:
        print("⚠️ Certains tests ont échoué")
        print("💡 Vérifiez la configuration et les dépendances")

if __name__ == "__main__":
    main()
