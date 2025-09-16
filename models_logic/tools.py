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
    
    @staticmethod
    def analyze_crypto_sentiment(text: str, tickers: list[str]) -> list[dict]:
        """
        Analyse le sentiment (long/short) pour chaque ticker crypto mentionné dans le texte.
        
        Args:
            text (str): Texte du tweet à analyser
            tickers (list[str]): Liste des tickers trouvés
            
        Returns:
            list[dict]: Liste de dictionnaires avec ticker et sentiment
                       ex: [{"ticker": "BTC", "sentiment": "long"}, {"ticker": "ETH", "sentiment": "short"}]
        """
        text_lower = text.lower()
        
        # Mots-clés pour sentiment positif (long)
        positive_keywords = [
            'bullish', 'bull', 'pump', 'pumping', 'moon', 'rocket', 'buy', 'buying',
            'long', 'hodl', 'hold', 'accumulate', 'accumulating', 'up', 'rise', 'rising',
            'green', 'profit', 'gains', 'winning', 'success', 'breakthrough', 'surge',
            'rally', 'breakout', 'momentum', 'strong', 'positive', 'optimistic'
        ]
        
        # Mots-clés pour sentiment négatif (short)
        negative_keywords = [
            'bearish', 'bear', 'dump', 'dumping', 'crash', 'sell', 'selling',
            'short', 'down', 'drop', 'dropping', 'fall', 'falling', 'red',
            'loss', 'losses', 'losing', 'weak', 'negative', 'pessimistic',
            'correction', 'decline', 'dip', 'resistance', 'rejection'
        ]
        
        results = []
        for ticker in tickers:
            # Compter les mots positifs et négatifs
            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)
            
            # Déterminer le sentiment
            if positive_count > negative_count:
                sentiment = "long"
            elif negative_count > positive_count:
                sentiment = "short"
            else:
                sentiment = "neutral"
            
            results.append({
                "ticker": ticker.upper(),
                "sentiment": sentiment
            })
        
        return results
