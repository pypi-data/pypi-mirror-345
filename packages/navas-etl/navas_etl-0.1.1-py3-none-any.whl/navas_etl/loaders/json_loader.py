import pandas as pd
import json
from typing import Union, Dict, List

class JsonLoader:
    """Loads data into JSON files"""
    
    def load(self, data: Union[Dict, List, pd.DataFrame], file_path: str, orient: str = 'records', **kwargs) -> None:
        """Load data into JSON file"""
        if isinstance(data, pd.DataFrame):
            data.to_json(file_path, orient=orient, **kwargs)
        else:
            with open(file_path, 'w') as f:
                json.dump(data, f, **kwargs)