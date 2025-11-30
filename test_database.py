"""
Testing db insertions
"""

from src.storage.database import DatabaseConnection
from src.ingestion.fetch_data import fetch_one_quote, fetch_many

def test_insert():
    print("Fetching TSM quote...")
    quote = fetch_one_quote("TSM")
    print(f"Fetched: {quote}")

    # insert

    with DatabaseConnection() as db:
        success = db.insert_quote(quote)
        print(f"Insert successfull: {success}")

    # check if it wrote
    with DatabaseConnection() as db:
        db.cursor.execute(
            "SELECT symbol, price, volume, fetched_at FROM stock_quotes WHERE symbol = 'TSM' ORDER BY fetched_at DESC LIMIT 1;"
        )
        result = db.cursor.fetchone()
        if result:
            print(f"Found in DB: symbol={result[0]}, price={result[1]}, volume={result[2]}, fetched_at={result[3]}")
        else:
            print("Not found in db")

def test_batch_insert():
    symbols = ["AAPL", "NVDA", "CATL", "LGLD", "AMD", "AMZN", "PLTR", "MSFT"]
    print(f"Fetching these bad boys: {symbols}")
    quotes = fetch_many(symbols)

    with DatabaseConnection() as db:
        success = db.insert_quotes_batch(quotes)
        print(f"Successfully inserted {success} records.")
    
    with DatabaseConnection() as db:
        db.cursor.execute(
            "SELECT symbol, price, volume, fetched_at FROM stock_quotes WHERE symbol IN ('AAPL', 'NVDA', 'CATL', 'LGLD', 'AMD', 'AMZN', 'PLTR', 'MSFT') ORDER BY SYMBOL;"
        )
        results = db.cursor.fetchall()
        print(f"\nFound {len(results)} quotes in db:")
        for symbol, price, volume, fetched_at in results:
            print(f"    {symbol}: ${price}")
            print(f"vol {volume}: td>{fetched_at}")



if __name__ == "__main__":
    # test_insert()
    test_batch_insert()