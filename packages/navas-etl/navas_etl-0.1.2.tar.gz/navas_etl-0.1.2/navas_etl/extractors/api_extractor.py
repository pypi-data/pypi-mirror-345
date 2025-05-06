import requests
import pandas as pd
from typing import Dict, Any, Union

class ApiExtractor:
    """Extracts data from REST APIs"""
    
    def __init__(self, base_url: str, auth: tuple = None, headers: dict = None):
        self.base_url = base_url
        self.auth = auth
        self.headers = headers
    
    def extract(self, endpoint: str, params: Dict[str, Any] = None) -> Union[dict, list]:
        """Extract data from API endpoint"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(
            url, 
            params=params, 
            auth=self.auth, 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def extract_to_dataframe(self, endpoint: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """Extract data from API and convert to pandas DataFrame"""
        data = self.extract(endpoint, params)
        return pd.DataFrame(data)