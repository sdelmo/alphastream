"""
Data fetcher: gets market data, verifies API access
POC right now
"""
import os
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

def fetch_one_quote(ticker: str = "AAPL") -> dict:
    """
    Fetch real-time quote for a ticker using Alpha Vantage API.

    Args:
        ticker: Stock ticker symbol, defaults to AAPL
    Returns:
        Dictionary with data about the stock
    """

    if not API_KEY:
        raise ValueError("Please set ALPHA_VANTAGE_API_KEY in .env file")
    
    base_url = f"https://www.alphavantage.co/query"

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol" : ticker,
        "apikey" : API_KEY,
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()
    quote = data.get("Global Quote")

    # Parse through quote
    if quote:
        return {
            "symbol": quote.get("01. symbol"),
            "price": float(quote.get("05. price", 0)),
            "volume": int(quote.get("06. volume", 0)),
            "timestamp": quote.get("07. latest trading day"),
            "change_percent": quote.get("10. change percent"),
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }

    return data

def fetch_many(tickers: list[str]) -> list[dict]:
    """Fetch quotes for multiple tickers"""
    results = []
    for ticker in tickers:
        try:
            data = fetch_one_quote(ticker)
            results.append(data)
            logging.info(f"Fetched {ticker}: ${data.get("price")}")
        except Exception as e:
            logging.error(f"Error while fetching {ticker}: {e}")

    return results

if __name__ == "__main__":
    test_tickers = ["AAPL", "GOOG", "PLTR", "NVDA", "AMZN"]
    logging.info("Testing API connection")
    quotes = fetch_many(test_tickers)
    output_file = "sample_data.json"

    with open(output_file, "w") as f:
        json.dump(quotes, f, indent=2)
    
    logging.info(f"\nSaved {len(quotes)} quotes to {output_file}")
    logging.info("\nSample data structure:")
    logging.info(f"{json.dumps(quotes[0], indent=2)}")
