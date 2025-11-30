"""
Testing db insertions
"""

from src.storage.database import DatabaseConnection
from src.ingestion.fetch_data import fetch_one_quote

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

if __name__ == "__main__":
    test_insert()