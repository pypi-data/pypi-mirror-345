import pandas as pd
from typing import Dict, Any, List, Optional

class Cleaner:
    """Cleans data by handling missing values, duplicates, etc."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def drop_duplicates(self, subset: List[str] = None) -> 'Cleaner':
        """Drop duplicate rows"""
        self.df = self.df.drop_duplicates(subset=subset)
        return self
    
    def fill_missing(self, strategy: str = 'mean', columns: List[str] = None, value: Any = None) -> 'Cleaner':
        
        """Fill missing values"""
        if columns is None:
            columns = self.df.columns
            
        fill_values = {}
        for col in columns:
            if strategy == 'mean':
                fill_values[col] = self.df[col].mean()
            elif strategy == 'median':
                fill_values[col] = self.df[col].median()
            elif strategy == 'mode':
                fill_values[col] = self.df[col].mode()[0]
            elif strategy == 'value' and value is not None:
                fill_values[col] = value
            else:
                self.df[col] = self.df[col].ffill()
                continue
                
            self.df = self.df.fillna(fill_values)
        return self
    
    def drop_columns(self, columns: List[str]) -> 'Cleaner':
        """Drop specified columns"""
        self.df = self.df.drop(columns=columns)
        return self
    
    def get_data(self) -> pd.DataFrame:
        """Get cleaned data"""
        return self.df