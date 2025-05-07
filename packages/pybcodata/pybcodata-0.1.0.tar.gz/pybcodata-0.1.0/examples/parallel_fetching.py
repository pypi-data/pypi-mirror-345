"""
Parallel fetching example using pybcodata shortcuts.

This example demonstrates how to:
1. Fetch multiple endpoints in parallel
2. Use the fetch_all shortcut
3. Handle both regular data and DataFrames
"""

import asyncio

from pybcodata import connect
from pybcodata.shortcuts import fetch_all

# Configuration
BASE_URL = "http://erp.konspec.in:8148/bc-user/odatav4/Company('KSPPL')/"
USERNAME = "your_username"
PASSWORD = "your_password"


async def main():
    # Create a session
    session = connect(BASE_URL, USERNAME, PASSWORD)

    async with session:
        # Create multiple queries
        customers_query = (
            session.source("customers")
            .filter("status eq 'Active'")
            .select(["number", "name", "email"])
        )

        items_query = (
            session.source("items")
            .filter("type eq 'Inventory'")
            .select(["number", "description", "unitPrice"])
        )

        sales_query = (
            session.source("salesOrders")
            .filter("status eq 'Open'")
            .select(["number", "customerNumber", "orderDate"])
        )

        # Fetch all queries in parallel
        print("Fetching data in parallel...")
        customers, items, sales = await fetch_all(
            customers_query, items_query, sales_query
        )

        print("\nResults:")
        print(f"Found {len(customers)} active customers")
        print(f"Found {len(items)} inventory items")
        print(f"Found {len(sales)} open sales orders")

        # Fetch as DataFrames in parallel
        try:
            print("\nFetching as DataFrames in parallel...")
            customers_df, items_df, sales_df = await fetch_all(
                customers_query, items_query, sales_query, as_df=True
            )

            print("\nDataFrame previews:")
            print("\nCustomers:")
            print(customers_df.head())
            print("\nItems:")
            print(items_df.head())
            print("\nSales Orders:")
            print(sales_df.head())

        except ImportError:
            print("\nPolars not installed. Install with: pip install polars")


if __name__ == "__main__":
    asyncio.run(main())
