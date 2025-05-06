import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Any

class DbExtractor:
    """Extracts data from databases"""
    
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
    
    def extract(self, query: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """Extract data using SQL query"""
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params=params)
    
    def extract_table(self, table_name: str, limit: int = None) -> pd.DataFrame:
        """Extract data from entire table"""
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        return self.extract(query)