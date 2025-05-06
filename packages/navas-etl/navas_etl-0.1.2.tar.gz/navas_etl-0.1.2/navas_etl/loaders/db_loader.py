import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Any

class DbLoader:
    """Loads data into databases"""
    
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
    
    def load(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append', **kwargs) -> None:
        """Load DataFrame into database table"""
        df.to_sql(
            table_name, 
            self.engine, 
            if_exists=if_exists, 
            index=False,
            **kwargs
        )
    
    def execute_query(self, query: str) -> None:
        """Execute raw SQL query"""
        with self.engine.connect() as conn:
            conn.execute(query)