#!/usr/bin/env python3
"""
Configuration manager for API selection and fallback

This module allows users to configure which cryptocurrency API to use
(CoinCap or CoinGecko) with automatic fallback options.
"""

# Standard library imports
import os
from enum import Enum
from typing import Any, Dict, Optional, Union

# Third-party imports
from dotenv import load_dotenv


class APIProvider(Enum):
    """Available API providers"""
    COINCAP = "coincap"
    COINGECKO = "coingecko"


class CryptoAPIManager:
    """
    Manager for cryptocurrency API selection with fallback support
    """
    
    def __init__(self, 
                 primary_api: Union[str, APIProvider] = APIProvider.COINCAP,
                 enable_fallback: bool = True,
                 mock_mode: bool = False):
        """
        Initialize the API manager
        
        Args:
            primary_api: Primary API to use (COINCAP or COINGECKO)
            enable_fallback: Whether to use fallback API if primary fails
            mock_mode: Use mock data instead of real API calls
        """
        load_dotenv()
        
        # Convert string to enum if needed
        if isinstance(primary_api, str):
            try:
                self.primary_api = APIProvider(primary_api.lower())
            except ValueError:
                print(f"⚠️ API inconnue '{primary_api}', utilisation de CoinCap par défaut")
                self.primary_api = APIProvider.COINCAP
        else:
            self.primary_api = primary_api
        
        self.enable_fallback = enable_fallback
        self.mock_mode = mock_mode
        
        # Setup API keys
        self.coincap_api_key = os.getenv("COINCAP_API_KEY", "")
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY", "")
        
        # Import APIs
        self._setup_apis()
        
        print("🔧 API Manager configuré:")
        print(f"   📊 API primaire: {self.primary_api.value.upper()}")
        print(f"   🔄 Fallback: {'Activé' if self.enable_fallback else 'Désactivé'}")
        print(f"   🎭 Mode mock: {'Activé' if self.mock_mode else 'Désactivé'}")


    def _setup_apis(self):
        """Setup API modules"""
        try:
            from coincap_api import (
                get_current_asset_price as coincap_price,
                PositionSimulator as CoinCapSimulator
            )
            from coingecko_api import (
                get_current_asset_price as coingecko_price,
                PositionSimulator as CoinGeckoSimulator
            )
            
            self.coincap_price = coincap_price
            self.coingecko_price = coingecko_price
            self.CoinCapSimulator = CoinCapSimulator
            self.CoinGeckoSimulator = CoinGeckoSimulator
            
        except ImportError as e:
            print(f"❌ Erreur d'import des APIs: {e}")
            raise


    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current price for a cryptocurrency symbol
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        
        Returns:
            Price data dictionary or None if failed
        """
        symbol = symbol.upper()
        
        # Try primary API first
        result = self._try_api(self.primary_api, symbol)
        if result:
            result["source"] = self.primary_api.value.upper()
            return result
        
        # Try fallback if enabled
        if self.enable_fallback:
            fallback_api = (APIProvider.COINGECKO 
                          if self.primary_api == APIProvider.COINCAP 
                          else APIProvider.COINCAP)
            
            print(f"   🔄 Tentative fallback vers {fallback_api.value.upper()}...")
            result = self._try_api(fallback_api, symbol)
            if result:
                result["source"] = fallback_api.value.upper()
                return result
        
        print(f"   💥 Aucune API n'a pu récupérer le prix pour {symbol}")
        return None


    def _try_api(self, api_provider: APIProvider, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Try to get price from specific API provider
        
        Args:
            api_provider: API provider to use
            symbol: Cryptocurrency symbol
        
        Returns:
            Price data or None if failed
        """
        try:
            if api_provider == APIProvider.COINCAP:
                data = self.coincap_price(symbol, api_key=self.coincap_api_key)
            else:  # COINGECKO
                data = self.coingecko_price(symbol, api_key=self.coingecko_api_key)
            
            if data and "price" in data:
                return data
                
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"   ❌ {api_provider.value.upper()} échoué: {e}")
        
        return None


    def create_simulator(self, api_provider: Optional[APIProvider] = None) -> Any:
        """
        Create a position simulator for the specified API
        
        Args:
            api_provider: API provider to use (uses primary if None)
        
        Returns:
            PositionSimulator instance
        """
        if api_provider is None:
            api_provider = self.primary_api
        
        if api_provider == APIProvider.COINCAP:
            return self.CoinCapSimulator(
                api_key=self.coincap_api_key,
                mock_mode=self.mock_mode
            )
        else:  # COINGECKO
            return self.CoinGeckoSimulator(
                api_key=self.coingecko_api_key,
                mock_mode=self.mock_mode
            )


    def simulate_position(self, 
                         position_data: Dict[str, Any], 
                         simulation_hours: int = 24,
                         api_provider: Optional[APIProvider] = None) -> Dict[str, Any]:
        """
        Simulate a trading position using specified API
        
        Args:
            position_data: Position information
            simulation_hours: Hours to simulate
            api_provider: API provider to use (uses primary if None)
        
        Returns:
            Simulation results
        """
        if api_provider is None:
            api_provider = self.primary_api
        
        simulator = self.create_simulator(api_provider)
        result = simulator.simulate_position(position_data, simulation_hours)
        
        # Add API source to result
        if "error" not in result:
            result["api_source"] = api_provider.value.upper()
        
        return result


    def get_api_status(self) -> Dict[str, Any]:
        """
        Get status of all available APIs
        
        Returns:
            Dictionary with API status information
        """
        status = {
            "primary_api": self.primary_api.value.upper(),
            "fallback_enabled": self.enable_fallback,
            "mock_mode": self.mock_mode,
            "apis": {}
        }
        
        # Test CoinCap
        try:
            test_result = self.coincap_price("BTC", api_key=self.coincap_api_key)
            status["apis"]["COINCAP"] = {
                "available": bool(test_result),
                "has_api_key": bool(self.coincap_api_key),
                "status": "✅ Disponible" if test_result else "❌ Indisponible"
            }
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            status["apis"]["COINCAP"] = {
                "available": False,
                "has_api_key": bool(self.coincap_api_key),
                "status": f"❌ Erreur: {e}"
            }
        
        # Test CoinGecko
        try:
            test_result = self.coingecko_price("BTC", api_key=self.coingecko_api_key)
            status["apis"]["COINGECKO"] = {
                "available": bool(test_result),
                "has_api_key": bool(self.coingecko_api_key),
                "status": "✅ Disponible" if test_result else "❌ Indisponible"
            }
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            status["apis"]["COINGECKO"] = {
                "available": False,
                "has_api_key": bool(self.coingecko_api_key),
                "status": f"❌ Erreur: {e}"
            }
        
        return status


    def display_status(self):
        """Display API status in a readable format"""
        status = self.get_api_status()
        
        print("🔧 STATUS DES APIS CRYPTO")
        print("=" * 50)
        print(f"📊 API primaire: {status['primary_api']}")
        print(f"🔄 Fallback: {'Activé' if status['fallback_enabled'] else 'Désactivé'}")
        print(f"🎭 Mode mock: {'Activé' if status['mock_mode'] else 'Désactivé'}")
        
        print("\n📋 APIs disponibles:")
        for api_name, api_info in status["apis"].items():
            print(f"  {api_name}: {api_info['status']}")
            if api_info["has_api_key"]:
                print("    🔑 Clé API configurée")
            else:
                print("    ⚠️ Pas de clé API")


def create_api_manager(config: Optional[Dict[str, Any]] = None) -> CryptoAPIManager:
    """
    Factory function to create API manager with configuration
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Configured CryptoAPIManager instance
    """
    if config is None:
        config = {}
    
    return CryptoAPIManager(
        primary_api=config.get("primary_api", APIProvider.COINCAP),
        enable_fallback=config.get("enable_fallback", True),
        mock_mode=config.get("mock_mode", False)
    )


# Configuration examples
CONFIG_COINCAP_FIRST = {
    "primary_api": APIProvider.COINCAP,
    "enable_fallback": True,
    "mock_mode": False
}

CONFIG_COINGECKO_FIRST = {
    "primary_api": APIProvider.COINGECKO,
    "enable_fallback": True,
    "mock_mode": False
}

CONFIG_MOCK_ONLY = {
    "primary_api": APIProvider.COINCAP,
    "enable_fallback": False,
    "mock_mode": True
}


if __name__ == "__main__":
    # Test de base
    print("🧪 TEST DU MANAGER D'API")
    
    # Test avec CoinCap en premier
    manager = create_api_manager(CONFIG_COINCAP_FIRST)
    manager.display_status()
    
    # Test d'un prix
    print("\n💰 Test de prix BTC:")
    btc_price = manager.get_current_price("BTC")
    if btc_price:
        print(f"   Prix: ${btc_price['price']:,.2f} (via {btc_price['source']})")
    else:
        print("   ❌ Prix non disponible")
