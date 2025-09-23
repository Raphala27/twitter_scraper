#!/usr/bin/env python3
"""
Exemple d'utilisation des APIs CoinCap et CoinGecko

Ce script démontre comment utiliser les deux intégrations API pour
obtenir des données de prix de cryptomonnaies et effectuer des simulations.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from coincap_api import get_current_asset_price as coincap_price
    from coingecko_api import get_current_asset_price as coingecko_price
    from coincap_api import PositionSimulator as CoinCapSimulator
    from coingecko_api import PositionSimulator as CoinGeckoSimulator
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)


def compare_apis_pricing():
    """Compare les prix entre CoinCap et CoinGecko"""
    print("🔍 COMPARAISON DES PRIX ENTRE COINCAP ET COINGECKO")
    print("=" * 60)
    
    cryptos = ["BTC", "ETH", "BNB", "SOL", "ADA"]
    
    for crypto in cryptos:
        print(f"\n💰 {crypto}:")
        
        # Prix CoinCap
        try:
            coincap_data = coincap_price(crypto, api_key="")
            if coincap_data and "price" in coincap_data:
                coincap_price_val = float(coincap_data["price"])
                print(f"  📊 CoinCap:   ${coincap_price_val:,.2f}")
            else:
                print("  📊 CoinCap:   Données non disponibles")
                coincap_price_val = None
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"  📊 CoinCap:   Erreur - {e}")
            coincap_price_val = None
        
        # Prix CoinGecko  
        try:
            coingecko_data = coingecko_price(crypto)
            if coingecko_data and "price" in coingecko_data:
                coingecko_price_val = float(coingecko_data["price"])
                print(f"  🦎 CoinGecko: ${coingecko_price_val:,.2f}")
            else:
                print("  🦎 CoinGecko: Données non disponibles")
                coingecko_price_val = None
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"  🦎 CoinGecko: Erreur - {e}")
            coingecko_price_val = None
        
        # Calcul de la différence
        if coincap_price_val and coingecko_price_val:
            diff_percent = ((coingecko_price_val - coincap_price_val) / coincap_price_val) * 100
            print(f"  📈 Différence: {diff_percent:+.2f}%")


def simulate_trading_position():
    """Simulation d'une position de trading avec les deux APIs"""
    print("\n\n🎯 SIMULATION DE POSITION DE TRADING")
    print("=" * 60)
    
    # Position d'exemple
    position_data = {
        "ticker": "BTC",
        "sentiment": "long",
        "leverage": "2",
        "entry_price": 45000,
        "take_profits": [50000, 55000],
        "stop_loss": 42000,
        "timestamp": (datetime.now() - timedelta(hours=24)).isoformat()
    }
    
    print(f"📊 Position: {position_data['sentiment'].upper()} {position_data['ticker']}")
    print(f"💰 Prix d'entrée: ${position_data['entry_price']:,}")
    print(f"🎯 Take Profits: {position_data['take_profits']}")
    print(f"🛑 Stop Loss: ${position_data['stop_loss']:,}")
    print(f"⚡ Leverage: {position_data['leverage']}x")
    
    # Simulation avec CoinCap
    print("\n📊 SIMULATION COINCAP:")
    try:
        coincap_sim = CoinCapSimulator(mock_mode=True)
        coincap_result = coincap_sim.simulate_position(position_data, simulation_hours=24)
        
        if "error" not in coincap_result:
            print(f"  💰 Capital initial: ${coincap_result['initial_capital']:.2f}")
            print(f"  📈 Capital final: ${coincap_result['final_capital']:.2f}")
            print(f"  💸 P&L: {coincap_result['pnl']:+.2f}$")
            print(f"  📊 ROI: {coincap_result['roi_percent']:+.2f}%")
            print(f"  🚪 Sortie: {coincap_result['exit_reason']} à ${coincap_result['exit_price']:.2f}")
        else:
            print(f"  ❌ Erreur: {coincap_result['error']}")
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"  ❌ Erreur CoinCap: {e}")
    
    # Simulation avec CoinGecko
    print("\n🦎 SIMULATION COINGECKO:")
    try:
        coingecko_sim = CoinGeckoSimulator(mock_mode=True)
        coingecko_result = coingecko_sim.simulate_position(position_data, simulation_hours=24)
        
        if "error" not in coingecko_result:
            print(f"  💰 Capital initial: ${coingecko_result['initial_capital']:.2f}")
            print(f"  📈 Capital final: ${coingecko_result['final_capital']:.2f}")
            print(f"  💸 P&L: {coingecko_result['pnl']:+.2f}$")
            print(f"  📊 ROI: {coingecko_result['roi_percent']:+.2f}%")
            print(f"  🚪 Sortie: {coingecko_result['exit_reason']} à ${coingecko_result['exit_price']:.2f}")
        else:
            print(f"  ❌ Erreur: {coingecko_result['error']}")
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"  ❌ Erreur CoinGecko: {e}")


def demo_api_selection():
    """Démontre comment choisir entre les APIs"""
    print("\n\n⚙️ SÉLECTION D'API DYNAMIQUE")
    print("=" * 60)
    
    def get_price_with_fallback(symbol: str):
        """Tente CoinCap d'abord, puis CoinGecko en fallback"""
        print(f"\n🔍 Recherche du prix pour {symbol}...")
        
        # Essayer CoinCap d'abord
        try:
            print("  📊 Tentative CoinCap...")
            price_data = coincap_price(symbol, api_key="")
            if price_data and "price" in price_data:
                price = float(price_data["price"])
                print(f"  ✅ CoinCap réussi: ${price:,.2f}")
                return {"price": price, "source": "CoinCap"}
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"  ❌ CoinCap échoué: {e}")
        
        # Fallback vers CoinGecko
        try:
            print("  🦎 Tentative CoinGecko...")
            price_data = coingecko_price(symbol)
            if price_data and "price" in price_data:
                price = float(price_data["price"])
                print(f"  ✅ CoinGecko réussi: ${price:,.2f}")
                return {"price": price, "source": "CoinGecko"}
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"  ❌ CoinGecko échoué: {e}")
        
        print(f"  💥 Aucune API n'a pu récupérer le prix pour {symbol}")
        return None
    
    # Test avec différentes cryptomonnaies
    test_cryptos = ["BTC", "ETH", "INVALID_SYMBOL"]
    
    for crypto in test_cryptos:
        result = get_price_with_fallback(crypto)
        if result:
            print(f"📈 {crypto}: ${result['price']:,.2f} (via {result['source']})")


def main():
    """Fonction principale"""
    print("🚀 DÉMONSTRATION DES APIS COINCAP ET COINGECKO")
    print("=" * 60)
    print("Ce script compare les deux intégrations API et démontre leur utilisation.")
    
    try:
        # Comparaison des prix
        compare_apis_pricing()
        
        # Simulation de trading
        simulate_trading_position()
        
        # Sélection d'API dynamique
        demo_api_selection()
        
        print("\n\n✅ DÉMONSTRATION TERMINÉE")
        print("=" * 60)
        print("Les deux APIs sont maintenant disponibles pour votre projet!")
        print("📊 CoinCap: Bon pour les données en temps réel")
        print("🦎 CoinGecko: Excellent pour les données historiques")
        print("💡 Recommandation: Utilisez CoinCap en premier, CoinGecko en fallback")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Démonstration interrompue par l'utilisateur")
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"\n\n❌ Erreur durant la démonstration: {e}")


if __name__ == "__main__":
    main()
