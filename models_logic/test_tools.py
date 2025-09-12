from tools import Tools

def test_extract_unique_tickers():
    """
    Test the extract_crypto_tickers function from the Tools class.
    """
    test_cases = [
        {
            "input": ["Bitcoin", "Ethereum", "Dogecoin"],
            "expected": ["BTC", "ETH", "DOGE"]
        },
        {
            "input": ["Solana", "SOL", "Cardano", "ADA"],
            "expected": ["SOL", "ADA"]
        },
        {
            "input": ["XRP", "LTC"],
            "expected": ["XRP", "LTC"]
        },
        {
            "input": ["Unknown", "Random"],
            "expected": []
        }
    ]

    for i, case in enumerate(test_cases, start=1):
        result = Tools.extract_unique_tickers(case["input"])
        assert result == case["expected"], f"Test case {i} failed: expected {case['expected']}, got {result}"
        print(f"Test case {i} passed.")

if __name__ == "__main__":
    test_extract_unique_tickers()
