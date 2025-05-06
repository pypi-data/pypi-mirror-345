import pandas as pd
from typing import List, Dict, Any

class Aggregator:
    """Aggregates data using groupby operations"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def groupby(self, group_columns: List[str], agg_config: Dict[str, Any]) -> pd.DataFrame:
        """Group by specified columns and apply aggregations"""
        return self.df.groupby(group_columns).agg(agg_config).reset_index()
    
    def pivot(self, index: str, columns: str, values: str) -> pd.DataFrame:
        """Create pivot table"""
        return self.df.pivot(index=index, columns=columns, values=values)