import pytest
from unittest.mock import patch, Mock
from src.ingestion.fetch_data import fetch_one_quote, fetch_many, _get_api_key

class TestGetApiKey:
    """Test API key retrieval"""

    def test_api_key_exists(self, monkeypatch):
        """Test api key retrieval"""
        monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "very-secret")
        assert _get_api_key() == "very-secret"
    
    def test_api_key_missing(self, monkeypatch):
        """Test error raising if key does not exist"""
        monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)

        with pytest.raises(ValueError):
            _get_api_key()

class TestFetchOneQuote:
    """Test single quote fetching."""
    
    @patch('src.ingestion.fetch_data.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful quote fetch."""
        # TODO: Mock the API response
        # TODO: Call fetch_one_quote()
        # TODO: Assert correct data structure returned
        pass
    
    @patch('src.ingestion.fetch_data.requests.get')
    def test_api_error_response(self, mock_get):
        """Test handling of API error message."""
        # TODO: Mock API returning {"Error Message": "Invalid symbol"}
        # TODO: Assert ValueError is raised
        pass
    
    @patch('src.ingestion.fetch_data.requests.get')
    def test_rate_limit_response(self, mock_get):
        """Test handling of rate limit."""
        # TODO: Mock API returning rate limit message
        # TODO: Assert ValueError is raised with correct message
        pass


class TestFetchMany:
    """Test multiple quote fetching."""
    
    @patch('src.ingestion.fetch_data.fetch_one_quote')
    def test_all_succeed(self, mock_fetch):
        """Test when all fetches succeed."""
        # TODO: Mock fetch_one_quote to return valid data
        # TODO: Call fetch_many with 3 tickers
        # TODO: Assert 3 results returned
        pass
    
    @patch('src.ingestion.fetch_data.fetch_one_quote')
    def test_partial_failure(self, mock_fetch):
        """Test when some fetches fail."""
        # TODO: Mock fetch_one_quote to fail on second ticker
        # TODO: Assert results only contain successful fetches
        pass