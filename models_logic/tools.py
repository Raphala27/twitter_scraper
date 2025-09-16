import re
from typing import List

class Tools:
    
    @staticmethod
    def get_crypto_names_from_tickers(tickers: list[str]) -> list[str]:
        """
        Prend une liste de tickers crypto et retourne les noms de crypto-monnaies correspondants.

        Args:
            tickers (list[str]): Liste de tickers (ex: ["BTC", "ETH"])

        Returns:
            list[str]: Liste des noms de crypto-monnaies correspondants (ex: ["Bitcoin", "Ethereum"])
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
        }

        crypto_names = []
        for ticker in tickers:
            name = ticker_to_name.get(ticker.upper())
            if name:
                crypto_names.append(name)
        return crypto_names
