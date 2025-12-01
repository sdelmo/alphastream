import logging
import os
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor, execute_batch

load_dotenv()

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Handles PostgreSQL connections and operations"""

    # 1. Connection management
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize db connection.

        Args:
            connection_string: PostgreSQL connection string. If None, reacs from DATABSE_URL env var.
        Raises:
            ValueError: If connection string not provided and database url not set.
        """

        self.connection_string = connection_string or os.getenv("DATABASE_URL")

        if not self.connection_string:
            raise ValueError(
                "DATABASE_URL not found. " "Set it in .env or pass connection_string"
            )

        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish connection to db and cursor."""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
            logger.info("DB Connection established")
        except psycopg2.Error as e:
            logger.error(f"Connection to db failed: {e}")
            raise

    def close(self):
        """Closes db connection and cursor"""

        if self.cursor:
            try:
                self.cursor.close()
                logger.info("Cursor closed successfully.")
            except psycopg2.Error as e:
                logger.error(f"Error closing cursor: {e}")
        if self.conn:
            try:
                self.conn.close()
                logger.info("Connection closed successfully.")
            except psycopg2.Error as e:
                logger.error(f"Error closing connection: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit

        Args:
            exc_type: Type of exception if one ocurred, otherwise None
            exc_val: Exception instance, otherwise None
            exc_tb: Exception traceback, otherwise None
        """

        if exc_type is None:
            if self.conn:
                self.conn.commit()  # commit changes, success
        else:
            if self.conn:
                self.conn.rollback()  # Error, rollback changes
                logger.error(
                    "An error ocurred, details below\n"
                    f"Exc type/value: {exc_type.__name__}/{exc_val}\n"
                )
        self.close()

    # 2. Write operations
    def insert_quote(self, quote: dict) -> bool:
        """
        Inserts a single quote into the db.
        Uses UPSERT.

        Args:
            quote: Dictionary with keys: symbol, price, volume, change_percent, timestamp, fetched_at

        Returns:
            True if transaction is successful, False otherwise.
        """

        sql = """
            INSERT INTO stock_quotes
            (symbol, price, volume, change_percent, trading_day, fetched_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, fetched_at)
            DO UPDATE SET
                price = EXCLUDED.price,
                volume = EXCLUDED.volume,
                change_percent = EXCLUDED.change_percent,
                trading_day = EXCLUDED.trading_day
        """
        try:
            values = (
                quote["symbol"],
                quote["price"],
                quote["volume"],
                quote["change_percent"],
                quote["timestamp"],
                quote["fetched_at"],
            )

            self.cursor.execute(INSERT_INTO, values)
            logger.debug(f"Successfully inserted/updated quote for {quote['symbol']}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error while writing data: {e}")
            return False
        except KeyError as e:
            logger.error(f"Missing required field in quote: {e}")
            return False

    def insert_quotes_batch(self, quotes: list[dict]) -> int:
        """
        Insert multiple quotes in a single transation.
        Uses execute_batch

        Returns:
            Number of quotes successfully inserted.
        """
        sql = """
            INSERT INTO stock_quotes
            (symbol, price, volume, change_percent, trading_day, fetched_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, fetched_at)
            DO UPDATE SET
                price = EXCLUDED.price,
                volume = EXCLUDED.volume,
                change_percent = EXCLUDED.change_percent,
                trading_day = EXCLUDED.trading_day
        """

        if not quotes:
            logger.warning("No quotes to insert")
            return 0
        try:
            data = [
                (
                    quote["symbol"],
                    quote["price"],
                    quote["volume"],
                    quote["change_percent"],
                    quote["timestamp"],
                    quote["fetched_at"],
                )
                for quote in quotes
            ]
            execute_batch(self.cursor, sql, data, page_size=100)
            logger.info(f"Batch inserted {len(quotes)} quotes")
            return len(quotes)
        except psycopg2.Error as e:
            logger.error(f"Error while writing batch: {e}")
            raise
        except KeyError as e:
            logger.error(f"Error while parsing quotes: {e}")
            raise

    def _convert_quote_types(self, quote_dict: dict) -> dict:
        """
        Convert db types to JSON-friendly types.

        Args:
            quote_dict: Dictionary from DictCursor
        Returns:
            Dictionary with converted types
        """

        quote = dict(quote_dict)

        if "price" in quote:
            quote["price"] = float(quote["price"])

        if quote.get("trading_day"):
            quote["trading_day"] = quote["trading_day"].isoformat()

        if quote.get("fetched_at"):
            quote["fetched_at"] = quote["fetched_at"].isoformat()

        return quote

    # 3. Read operations
    def get_latest_quote(self, symbol: str) -> dict | None:
        """
        Get most recent quote for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g, 'PLTR')
        Returns:
            Dictionary with quote data, or None if not found
        """
        sql = "SELECT id, symbol, price, volume, change_percent, trading_day, fetched_at FROM stock_quotes WHERE symbol = %s ORDER BY fetched_at DESC LIMIT 1;"

        if not symbol:
            raise ValueError(f"Symbol must be provided")

        try:
            self.cursor.execute(sql, (symbol,))
            row = self.cursor.fetchone()

            if not row:
                logger.warning(f"No quote found for {symbol}")
                return None

            logger.debug(f"Retrieved latest quote for {symbol}")
            return self._convert_quote_types(row)
        except psycopg2.Error as e:
            logger.error(f"Db error while fetching quote for {symbol}: {e}")
            raise

    def get_quotes_by_date_range(
        self, symbol: str, start_date, end_date
    ) -> list | None:

        if not symbol:
            raise ValueError("Symbol must be provided")
        if not start_date and not end_date:
            raise ValueError(
                "Both Start and End dates must be provided to this method."
            )

        sql = "SELECT id, symbol, price, volume, change_percent, trading_day, fetched_at FROM stock_quotes WHERE symbol = %s AND trading_day BETWEEN %s AND %s ORDER BY trading_day ASC, fetched_at ASC"

        try:
            self.cursor.execute(sql, (symbol, start_date, end_date))
            rows = self.cursor.fetchall()

            if not rows:
                logger.warning(
                    f"No quotes found for timeframe starting {start_date}, and ending at {end_date}"
                )
                return None

            # convert each dictRow to regular dicts, convert types
            quotes = [self._convert_quote_types(row) for row in rows]
            logger.info(f"Retrieved {len(quotes)} quotes for {symbol}")
            return quotes
        except psycopg2.Error as e:
            logger.error(f"Db error: {e}")
            raise

    def get_all_symbols(self) -> list:
        """
        Get litst of all unique tickers in the db.

        Returns:
            List of unique ticker symbols, sorted alphabetically
        """

        sql = "SELECT DISTINCT symbol FROM stock_quotes ORDER BY symbol ASC;"

        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            # dunno what object type is returned
            if not rows:
                logger.info("No symbols were found in the database")
                return []
            symbols = [row["symbol"] for row in rows]
            logger.info(f"Retrieved {len(symbols)} unique symbols from database")
            return symbols
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            raise
