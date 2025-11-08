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
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )


def _get_api_key() -> str:
    """Get API key"""
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not API_KEY:
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY not found. "
            "Please set it in your .env file"
        )
    return API_KEY

def fetch_one_quote(ticker: str = "AAPL", max_retries: int = 3) -> dict:
    """
    Fetch real-time quote for a ticker using Alpha Vantage API.

    Args:
        ticker: Stock ticker symbol, defaults to AAPL
    Returns:
        Dictionary with data about the stock
    """

    API_KEY = _get_api_key()

    base_url = f"https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol" : ticker,
        "apikey" : API_KEY,
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "Error Message" in data:
                raise ValueError(f"API Error: {data["Error Message"]}")
            
            if "Note" in data: #rate limit
                raise ValueError(f"Rate limit exceeded: {data["Note"]}")
            
            quote = data.get("Global Quote")

            if not quote:
                raise ValueError(f"No quote data returned for {ticker}")

            return {
                "symbol": quote.get("01. symbol"),
                "price": float(quote.get("05. price", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "timestamp": quote.get("07. latest trading day"),
                "change_percent": quote.get("10. change percent"),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
        
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt # exponential backoff
                logging.warning(f"Attempt {attempt + 1} failed for {ticker}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"All {max_retries} attempts failed for ticker {ticker}")
                raise


def fetch_many(tickers: list[str]) -> list[dict]:
    """Fetch quotes for multiple tickers, rate limiting based on 5req/min for free alpha vantage sub"""
    results = []
    failed_tickers = []

    for i, ticker in enumerate(tickers):
        try:
            data = fetch_one_quote(ticker)
            results.append(data)
            logging.info(f"Fetched {ticker}: ${data.get("price")}")

            # primitive Rate limit, wait 12s between requests (60s/5req)
            if i < len(tickers) - 1:
                logging.debug("Rate limiting: waiting 12s...")
                time.sleep(12)

        except requests.RequestException as e:
            logging.error(f"Failed to fetch {ticker}: {e}")
            failed_tickers.append(ticker)
        except (KeyError, ValueError) as e:
            logging.error(f"Invalid data format for {ticker}: {e}")
            failed_tickers.append(ticker)
    
    if failed_tickers:
        logging.warning(f"Failed to fetch {len(failed_tickers)} tickers: {failed_tickers}")

    return results

if __name__ == "__main__":
    test_tickers = ["AAPL", "GOOG", "PLTR", "NVDA", "AMZN"]

    logging.info("=" * 50)
    logging.info("Testing API connection")
    logging.info("=" * 50)
    quotes = fetch_many(test_tickers)
    output_file = "sample_data.json"

    with open(output_file, "w") as f:
        json.dump(quotes, f, indent=2)
    
    logging.info(f"Saved {len(quotes)} quotes to {output_file}")
    if quotes:
        logging.info("Sample data structure:")
        print(f"{json.dumps(quotes[0], indent=2)}")
