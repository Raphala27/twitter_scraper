class Tools:
    
    @staticmethod
    def extract_unique_tickers(cryptos: list[str]) -> list[str]:
        # Dictionnaire de mapping noms → tickers
        mapping = {
            # Top cryptos
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "solana": "SOL",
            "cardano": "ADA",
            "ripple": "XRP",
            "dogecoin": "DOGE",
            "polygon": "MATIC",
            "polkadot": "DOT",
            "litecoin": "LTC",
            "avalanche": "AVAX",
            "tron": "TRX",
            "chainlink": "LINK",
            "uniswap": "UNI",
            "cosmos": "ATOM",
            # Stablecoins
            "tether": "USDT",
            "usdt": "USDT",
            "usd coin": "USDC",
            "usdc": "USDC",
            "dai": "DAI",
        }
        
        # Tous les tickers connus (en majuscule)
        valid_tickers = set(mapping.values())
        
        tickers = []
        for item in cryptos:
            lower_item = item.lower()
            upper_item = item.upper()
            
            if lower_item in mapping:  # Si c'est un nom de crypto
                tickers.append(mapping[lower_item])
            elif upper_item in valid_tickers:  # Si c'est déjà un ticker
                tickers.append(upper_item)
        
        # Supprimer doublons en conservant l'ordre
        seen = set()
        unique_tickers = []
        for t in tickers:
            if t not in seen:
                seen.add(t)
                unique_tickers.append(t)
        
        return unique_tickers
