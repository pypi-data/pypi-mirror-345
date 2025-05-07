# pybcodata

A Python client library for interacting with Business Central's OData API. This library provides a simple, async interface for fetching and querying data from Business Central, with support for rate limiting, concurrent requests, and automatic retries.

## Features

- 🔄 **Async Support**: Built with `asyncio` for efficient concurrent operations
- 🚀 **Parallel Fetching**: Fetch multiple endpoints simultaneously
- 📊 **DataFrame Support**: Optional integration with Polars for data analysis
- ⚡ **Rate Limiting**: Built-in rate limiting to prevent API overload
- 🔁 **Automatic Retries**: Configurable retry mechanism with exponential backoff
- 🔒 **Authentication**: Simple username/password authentication
- 📝 **Query Builder**: Fluent interface for building OData queries
- 🛠️ **Error Handling**: Comprehensive error handling and logging

## Installation

```bash
pip install pybcodata
```

For DataFrame support, install with polars:

```bash
pip install pybcodata polars
```

## Quick Start

```python
import asyncio
from pybcodata import connect

async def main():
    # Create a session
    session = connect(
        base_url="https://api.businesscentral.com/v2.0/",
        username="your_username",
        password="your_password"
    )

    async with session:
        # Verify credentials
        await session.check_credentials()

        # Fetch data
        customers = await session.source("customers") \
            .filter("status eq 'Active'") \
            .select(["number", "name", "email"]) \
            .fetch()

        # Or as DataFrame
        customers_df = await session.source("customers") \
            .filter("status eq 'Active'") \
            .select(["number", "name", "email"]) \
            .fetch(as_df=True)

# Run the async code
asyncio.run(main())
```

## Parallel Fetching

Use the `fetch_all` shortcut to fetch multiple endpoints in parallel:

```python
from pybcodata.shortcuts import fetch_all

async def main():
    session = connect(...)
    async with session:
        # Create queries
        customers_query = session.source("customers").filter("status eq 'Active'")
        items_query = session.source("items").filter("type eq 'Inventory'")

        # Fetch both in parallel
        customers, items = await fetch_all(customers_query, items_query)

        # Or as DataFrames
        customers_df, items_df = await fetch_all(
            customers_query,
            items_query,
            as_df=True
        )
```

## Configuration

The `connect()` function accepts several configuration options:

```python
session = connect(
    base_url="https://api.businesscentral.com/v2.0/",
    username="your_username",
    password="your_password",
    limit=9,              # Maximum requests per period
    period=1,             # Time period in seconds
    max_concurrency=5,    # Maximum concurrent requests
    max_retries=3,        # Maximum retry attempts
    base_backoff=5.0      # Base backoff time in seconds
)
```

## Query Builder

The library provides a fluent interface for building OData queries:

```python
# Create a query
query = session.source("customers")

# Add filters
query = query.filter("status eq 'Active'")

# Select fields
query = query.select(["number", "name", "email"])

# Limit results
query = query.top(100)

# Skip results
query = query.skip(50)

# Order results
query = query.order_by("name asc")

# Execute the query
results = await query.fetch()
```

## Error Handling

The library includes comprehensive error handling:

```python
try:
    await session.check_credentials()
except ValueError as e:
    print("Invalid credentials:", e)
except ConnectionError as e:
    print("Connection error:", e)
except Exception as e:
    print("Unexpected error:", e)
```

## Examples

Check out the [examples](examples/) directory for more detailed usage examples:

- [Basic Usage](examples/basic_usage.py)
- [Parallel Fetching](examples/parallel_fetching.py)

## Development

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pybcodata.git
cd pybcodata
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for async HTTP requests
- Optional integration with [Polars](https://pola.rs/) for data analysis
- Inspired by the simplicity of Django's ORM
