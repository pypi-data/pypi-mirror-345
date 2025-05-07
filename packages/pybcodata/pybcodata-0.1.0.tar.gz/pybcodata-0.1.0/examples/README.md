# pybcodata Examples

This directory contains examples demonstrating how to use the `pybcodata` library to interact with Business Central's OData API.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates:

- Connecting to Business Central
- Basic data fetching
- Using filters and field selection
- Working with DataFrames

Run it with:

```bash
python basic_usage.py
```

### 2. Parallel Fetching (`parallel_fetching.py`)

Demonstrates:

- Fetching multiple endpoints in parallel
- Using the `fetch_all` shortcut
- Working with multiple DataFrames

Run it with:

```bash
python parallel_fetching.py
```

## Configuration

Before running the examples:

1. Update the configuration variables in each example:

   ```python
   BASE_URL = "your_business_central_url"
   USERNAME = "your_username"
   PASSWORD = "your_password"
   ```

2. Install required dependencies:
   ```bash
   pip install pybcodata polars  # for DataFrame support
   ```

## Notes

- The examples use async/await syntax, so they must be run with Python 3.7+
- DataFrame support requires the `polars` package to be installed
- Make sure you have the correct permissions to access the Business Central API
- The examples use dummy data and endpoints - adjust them according to your Business Central setup
