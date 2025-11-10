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

        with pytest.raises(ValueError, match="ALPHA_VANTAGE_API_KEY not found"):
            _get_api_key()

class TestFetchOneQuote:
    """Test single quote fetching."""
    
    @patch("src.ingestion.fetch_data.requests.get")
    @patch("src.ingestion.fetch_data._get_api_key")
    def test_successful_fetch(self, mock_get_key, mock_get):
        """Test successful quote fetch."""
        # Mock API key
        mock_get_key.return_value = "fake-api-key"

        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"Global Quote": {
                "01. symbol": "AAPL",
                "05. price": "268.47",
                "06. volume": "48227365",
                "07. latest trading day": "2025-11-07",
                "10. change percent": "-0.4819%"
            }}
        mock_response.raise_for_status = Mock() # shouldn't raise an error
        mock_get.return_value = mock_response
        result = fetch_one_quote("AAPL")
        # Assertions
        assert result["symbol"] == "AAPL"
        assert result["price"] == 268.47
        assert result["volume"] == 48227365
        assert result["timestamp"] == "2025-11-07"
        assert result["change_percent"] == "-0.4819%"
        assert "fetched_at" in result
        
        # Verify the mock was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["symbol"] == "AAPL"
        assert call_args[1]["timeout"] == 10

    @patch("src.ingestion.fetch_data.requests.get")
    @patch("src.ingestion.fetch_data._get_api_key")
    def test_api_error_response(self, mock_get_key, mock_get):
        """Test handling of API error message."""
        mock_get_key.return_value = "fake-api-key"
        mock_response = Mock()
        mock_response.json.return_value = {"Error Message": "Testing 123"}
        mock_response.raise_for_status = Mock() # Nothing to see here
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="API Error: Testing 123"):
            fetch_one_quote("invalid_ticker")
    
    @patch("src.ingestion.fetch_data.requests.get")
    @patch("src.ingestion.fetch_data._get_api_key")
    def test_rate_limit_response(self, mock_get_key, mock_get):
        """Test handling of rate limit."""
        mock_get_key.return_value = "fake-api-key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "Note": "Start using premium broke boy"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Rate limit exceeded: Start using premium broke boy"):
            fetch_one_quote("AAPL")

    @patch("src.ingestion.fetch_data.requests.get")
    @patch("src.ingestion.fetch_data._get_api_key")
    def test_network_failure_with_retry(self, mock_get_key, mock_get):
        """Test retry behavior"""
        mock_get_key.return_value = "fake-api-key"
        # Mock network failure
        import requests
        mock_get.side_effect = requests.RequestException("Connection error")

        with pytest.raises(requests.RequestException):
            fetch_one_quote("AAPL", max_retries=2)
        assert mock_get.call_count == 2



class TestFetchMany:
    """Test multiple quote fetching."""
    
    @patch("src.ingestion.fetch_data.fetch_one_quote")
    @patch("src.ingestion.fetch_data.time.sleep") # mock sleep so we don't have to wait 1000s to run test suite
    def test_all_succeed(self, mock_sleep, mock_fetch):
        """Test when all fetches succeed."""
        mock_fetch.side_effect = [
            {"symbol": "AAPL", "price": 150.0, "volume": 1000000, "timestamp": "2025-11-07", "change_percent": "+1.5%", "fetched_at": "2025-11-10T12:00:00+00:00"},
            {"symbol": "GOOGL", "price": 2800.0, "volume": 500000, "timestamp": "2025-11-07", "change_percent": "+0.5%", "fetched_at": "2025-11-10T12:00:01+00:00"},
            {"symbol": "MSFT", "price": 380.0, "volume": 800000, "timestamp": "2025-11-07", "change_percent": "-0.3%", "fetched_at": "2025-11-10T12:00:02+00:00"},
        ]

        tickers = ["AAPL", "GOOGL", "MSFT"]
        results = fetch_many(tickers)

        # Assert 3 results returned
        assert len(results) == 3
        assert results[0]["symbol"] == "AAPL"
        assert results[1]["symbol"] == "GOOGL"
        assert results[2]["symbol"] == "MSFT"
        
        # Verify fetch_one_quote was called 3 times
        assert mock_fetch.call_count == 3
        
        # Verify sleep was called between requests (2 times for 3 tickers)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(12)

    
    @patch("src.ingestion.fetch_data.fetch_one_quote")
    @patch("src.ingestion.fetch_data.time.sleep")
    def test_partial_failure(self, mock_sleep, mock_fetch):
        """Test when some fetches fail."""
        import requests
        
        # Mock: first succeeds, second fails, third succeeds
        mock_fetch.side_effect = [
            {"symbol": "AAPL", "price": 150.0, "volume": 1000000, "timestamp": "2025-11-07", "change_percent": "+1.5%", "fetched_at": "2025-11-10T12:00:00+00:00"},
            requests.RequestException("Network error"),
            {"symbol": "MSFT", "price": 380.0, "volume": 800000, "timestamp": "2025-11-07", "change_percent": "-0.3%", "fetched_at": "2025-11-10T12:00:02+00:00"},
        ]
        
        tickers = ["AAPL", "GOOGL", "MSFT"]
        results = fetch_many(tickers)
        
        # Assert only 2 successful results
        assert len(results) == 2
        assert results[0]["symbol"] == "AAPL"
        assert results[1]["symbol"] == "MSFT"
        
        # GOOGL should not be in results
        symbols = [r["symbol"] for r in results]
        assert "GOOGL" not in symbols