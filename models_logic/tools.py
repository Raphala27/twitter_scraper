#!/usr/bin/env python3
"""
AI Tools for Cryptocurrency Analysis

This module provides tools for cryptocurrency ticker extraction and analysis
that can be used by AI models to process trading signals from social media.
"""

import re
from typing import List


class Tools:
    """Tools for cryptocurrency analysis and ticker extraction."""
    
    @staticmethod
    def get_crypto_names_from_tickers(tickers: List[str]) -> List[str]:
        """
        Convert cryptocurrency tickers to their full names.

        Args:
            tickers: List of cryptocurrency tickers (e.g., ["BTC", "ETH"])

        Returns:
            List of corresponding cryptocurrency names (e.g., ["Bitcoin", "Ethereum"])
        """
        # Dictionnaire de correspondance ticker -> nom de crypto-monnaie
        ticker_to_name = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "BNB": "Binance Coin",
            "SOL": "Solana",
            "XRP": "XRP",
            "ADA": "Cardano",
            "DOGE": "Dogecoin",
            "DOT": "Polkadot",
            "TRX": "Tron",
            "AVAX": "Avalanche",
            "MATIC": "Polygon",
            "LTC": "Litecoin",
            "LINK": "Chainlink",
            "ATOM": "Cosmos",
            "XLM": "Stellar",
            "UNI": "Uniswap",
            "BCH": "Bitcoin Cash",
            "APT": "Aptos",
            "OP": "Optimism",
            "ARB": "Arbitrum",
            "USDT": "Tether",
            "USDC": "USD Coin",
            "SUI": "Sui",
            "NEAR": "Near Protocol",
            "FTM": "Fantom",
            "ALGO": "Algorand",
            "VET": "VeChain",
            "ICP": "Internet Computer",
            "FIL": "Filecoin",
            "SAND": "The Sandbox",
            "MANA": "Decentraland",
            "CRO": "Cronos",
            "LDO": "Lido DAO",
            "QNT": "Quant"
        }

        crypto_names = []
        for ticker in tickers:
            name = ticker_to_name.get(ticker.upper())
            if name:
                crypto_names.append(name)
        return crypto_names
