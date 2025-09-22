"""
CoinCap API integration package for cryptocurrency price data and position simulation.
"""

from .fetch_prices import (
    search_asset_by_symbol,
    get_asset_history,
    get_current_asset_price,
    get_crypto_price_at_time,
    fetch_prices_for_cryptos
)
from .position_calculator import (
    calculate_positions,
    display_positions_summary
)
from .position_simulator import PositionSimulator

__all__ = [
    'search_asset_by_symbol',
    'get_asset_history',
    'get_current_asset_price', 
    'get_crypto_price_at_time',
    'fetch_prices_for_cryptos',
    'calculate_positions',
    'display_positions_summary',
    'PositionSimulator'
]
