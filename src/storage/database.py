import psycopg2
from dotenv import load_dotenv
import os
import logging
from typing import Optional
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
    def __init__(self, connection_string: Optional[str]=None):
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
                "DATABASE_URL not found. "
                "Set it in .env or pass connection_string"
            )

        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish connection to db and cursor."""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor()
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
        
    def __enter__(self):  # Context manager
        pass
    def __exit__(self):   # Context manager
        pass
    
    # 2. Write operations
    def insert_quote(self, quote: dict) -> bool:
        pass
    def insert_quotes_batch(self, quotes: list) -> int:
        pass
    
    # 3. Read operations
    def get_latest_quote(self, symbol: str) -> dict:
        pass
    def get_quotes_by_date_range(self, symbol: str, start_date, end_date) -> list:
        pass
    def get_all_symbols(self) -> list:
        pass