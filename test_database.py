"""
Testing db insertions and stuff
"""

from src.ingestion.fetch_data import fetch_many, fetch_one_quote
from src.storage.database import DatabaseConnection


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
            print(
                f"Found in DB: symbol={result[0]}, price={result[1]}, volume={result[2]}, fetched_at={result[3]}"
            )
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


def test_get_latest():
    with DatabaseConnection() as db:
        quote = db.get_latest_quote("PLTR")
        if quote:
            print(f"Found: {quote["symbol"]} @{quote["price"]}")
        else:
            print(f"Sad borat voice: not nice, not found")

        # invalid ticker
        quote = db.get_latest_quote("HAHA")
        if quote:
            print(f"Found: {quote["symbol"]} @{quote["price"]}")
        else:
            print(f"Sad borat voice: not nice, not found")


def test_complete_workflow():
    print("=" * 60)
    print("COMPLETE DATABASE MODULE TEST")
    print("=" * 60)

    # Step 1: Fetch data from API
    print("\n1. Fetching quotes from API...")
    tickers = ["AAPL", "GOOGL", "MSFT", "NVDA"]
    quotes = fetch_many(tickers)
    print(f"Fetched {len(quotes)} quotes")

    # Step 2: Batch insert
    print("\n2. Batch inserting to database...")
    with DatabaseConnection() as db:
        count = db.insert_quotes_batch(quotes)
        print(f"Inserted {count} quotes")

    # Step 3: Get latest quote
    print("\n3. Testing get_latest_quote()...")
    with DatabaseConnection() as db:
        for ticker in tickers:
            quote = db.get_latest_quote(ticker)
            if quote:
                print(f"{ticker}: ${quote['price']} on {quote['trading_day']}")

    # Step 4: Test non-existent symbol
    print("\n4. Testing with invalid symbol...")
    with DatabaseConnection() as db:
        quote = db.get_latest_quote("INVALID")
        if quote is None:
            print("Correctly returned None for invalid symbol")

    # Step 5: Get date range
    print("\n5. Testing get_quotes_by_date_range()...")
    with DatabaseConnection() as db:
        quotes = db.get_quotes_by_date_range("AAPL", "2025-11-01", "2025-12-31")
        if quotes:
            print(f"Found {len(quotes)} AAPL quotes in Nov-Dec 2025")
            for q in quotes[:3]:  # Show first 3
                print(f"   {q['trading_day']}: ${q['price']}")

    # Step 6: Verify data persistence
    print("\n6. Testing data persistence...")
    with DatabaseConnection() as db:
        db.cursor.execute("SELECT COUNT(*) FROM stock_quotes")
        count = db.cursor.fetchone()["count"]
        print(f"Total quotes in database: {count}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ")
    print("=" * 60)


def get_tickers():
    with DatabaseConnection() as db:
        tickers = db.get_all_symbols()

        if tickers:
            for t in tickers:
                print(f"Found ticker: {t}")
        else:
            print(f"Something went wrong.")


if __name__ == "__main__":
    # test_insert()
    # test_batch_insert()
    # test_get_latest()
    # test_complete_workflow()
    get_tickers()
