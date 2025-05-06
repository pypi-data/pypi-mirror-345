import pandas as pd
from typing import Optional, Dict

class CsvLoader:
    """Loads data into CSV files"""
    
    def load(self, df: pd.DataFrame, file_path: str, **kwargs) -> None:
        """Load DataFrame into CSV file"""
        df.to_csv(file_path, index=True, **kwargs)
    
    def load_multiple(self, dfs: Dict[str, pd.DataFrame], file_prefix: str, **kwargs) -> None:
        """Load multiple DataFrames into separate CSV files"""
        for name, df in dfs.items():
            self.load(df, f"{file_prefix}_{name}.csv", **kwargs)