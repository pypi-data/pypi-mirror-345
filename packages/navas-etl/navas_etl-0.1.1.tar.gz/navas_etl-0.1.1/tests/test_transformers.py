import pytest
import pandas as pd
from navas_etl.transformers import Cleaner, Aggregator, Formatter

class TestCleaner:
    def test_drop_duplicates(self):
        df = pd.DataFrame([{"id": 1}, {"id": 1}, {"id": 2}])
        cleaner = Cleaner(df)
        result = cleaner.drop_duplicates().get_data()
        
        assert len(result) == 2

    def test_fill_missing(self):
        df = pd.DataFrame([{"id": 1, "value": None}, {"id": 2, "value": 5}])
        cleaner = Cleaner(df)
        result = cleaner.fill_missing(strategy='value', value=0).get_data()
        
        assert result.iloc[0]['value'] == 0

# Similar tests for Aggregator and Formatter