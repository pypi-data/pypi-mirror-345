import pandas as pd
from typing import Union, List

class CsvExtractor:
    """Extracts data from CSV files"""
    
    def extract(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Extract data from CSV file"""
        return pd.read_csv(file_path, **kwargs)
    
    def extract_multiple(self, file_paths: List[str], **kwargs) -> List[pd.DataFrame]:
        """Extract data from multiple CSV files"""
        return [self.extract(file_path, **kwargs) for file_path in file_paths]