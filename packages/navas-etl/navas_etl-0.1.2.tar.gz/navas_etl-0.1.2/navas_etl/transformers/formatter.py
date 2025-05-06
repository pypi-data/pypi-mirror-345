import pandas as pd
from typing import Dict, List

class Formatter:
    """Formats data (column renaming, type conversion, etc.)"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def rename_columns(self, column_map: Dict[str, str]) -> 'Formatter':
        """Rename columns"""
        self.df = self.df.rename(columns=column_map)
        return self
    
    def convert_types(self, type_map: Dict[str, str]) -> 'Formatter':
        """Convert column data types"""
        for col, dtype in type_map.items():
            self.df[col] = self.df[col].astype(dtype)
        return self
    
    def format_dates(self, date_columns: List[str], format_str: str = '%Y-%m-%d') -> 'Formatter':
        """Format date columns"""
        for col in date_columns:
            self.df[col] = pd.to_datetime(self.df[col]).dt.strftime(format_str)
        return self
    
    def get_data(self) -> pd.DataFrame:
        """Get formatted data"""
        return self.df