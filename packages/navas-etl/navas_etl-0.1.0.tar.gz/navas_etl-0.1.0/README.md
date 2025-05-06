# navas-etl

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![PyPI Version](https://img.shields.io/pypi/v/pipelinex.svg)](https://pypi.org/project/pipelinex/)

A flexible ELT (Extract, Load, Transform) pipeline implementation in Python with support for multiple data sources and destinations.

## Features

- **Extract** from multiple sources:
  - REST APIs
  - CSV files
  - Databases (via SQLAlchemy)
  
- **Transform** data with:
  - Cleaning operations
  - Aggregations
  - Formatting
  
- **Load** to various targets:
  - Databases
  - CSV files
  - JSON files

## Installation

```bash
pip install navas-etl
```

## Quick Start

```python
from navas-etl import ApiExtractor, Cleaner, DbLoader

# 1. Extract data from API
extractor = ApiExtractor("https://api.example.com")
data = extractor.extract_to_dataframe("users")

# 2. Transform/Clean the data
cleaner = Cleaner(data)
cleaned_data = (cleaner
               .drop_duplicates()
               .fill_missing(strategy='mean')
               .get_data())

# 3. Load to database
loader = DbLoader("postgresql://user:password@localhost:5432/mydb")
loader.load(cleaned_data, "users_table")
```

## Documentation

### Extractors

#### API Extractor
```python
from navas-etl import ApiExtractor

extractor = ApiExtractor(base_url="https://api.example.com", auth=("user", "pass"))
data = extractor.extract("endpoint", params={"param": "value"})
```

#### CSV Extractor
```python
from navas-etl import CsvExtractor

extractor = CsvExtractor()
df = extractor.extract("data.csv")
```

#### Database Extractor
```python
from navas-etl import DbExtractor

extractor = DbExtractor("postgresql://user:pass@localhost:5432/db")
df = extractor.extract("SELECT * FROM table")
```

### Transformers

See [full documentation](https://github.com/Navashub/navas_pipeline) for more examples.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.