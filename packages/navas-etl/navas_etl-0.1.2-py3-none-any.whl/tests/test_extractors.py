import pytest
import pandas as pd
from navas_etl.extractors import ApiExtractor, CsvExtractor, DbExtractor
from unittest.mock import patch, MagicMock

class TestApiExtractor:
    @patch('requests.get')
    def test_extract(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1, "name": "test"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test extraction
        extractor = ApiExtractor("http://test.com")
        result = extractor.extract("endpoint")
        
        assert result == [{"id": 1, "name": "test"}]
        mock_get.assert_called_once_with(
            "http://test.com/endpoint",
            params=None,
            auth=None,
            headers=None
        )

class TestCsvExtractor:
    @patch('pandas.read_csv')
    def test_extract(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame([{"id": 1}])
        
        extractor = CsvExtractor()
        result = extractor.extract("test.csv")
        
        assert isinstance(result, pd.DataFrame)
        mock_read_csv.assert_called_once_with("test.csv")

# Similar tests for DbExtractor and other components