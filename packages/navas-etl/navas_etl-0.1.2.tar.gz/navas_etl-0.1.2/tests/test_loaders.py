import pytest
import pandas as pd
from navas_etl.loaders import CsvLoader, JsonLoader, DbLoader
from unittest.mock import patch, MagicMock

class TestCsvLoader:
    @patch('pandas.DataFrame.to_csv')
    def test_load(self, mock_to_csv):
        df = pd.DataFrame([{"id": 1}])
        loader = CsvLoader()
        loader.load(df, "test.csv")
        
        mock_to_csv.assert_called_once_with("test.csv", index=True)  # 

class TestDbLoader:
    @patch('pandas.DataFrame.to_sql')
    @patch('sqlalchemy.create_engine')
    def test_load(self, mock_engine, mock_to_sql):
        df = pd.DataFrame([{"id": 1}])
        loader = DbLoader("sqlite://")
        loader.load(df, "test_table")
        
        mock_to_sql.assert_called_once_with(
            "test_table",
            loader.engine,
            if_exists='append',
            index=False
        )

# Similar tests for JsonLoader