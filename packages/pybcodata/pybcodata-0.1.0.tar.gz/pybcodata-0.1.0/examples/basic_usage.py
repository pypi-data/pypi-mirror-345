"""
Basic usage example of pybcodata.

This example shows how to:
1. Connect to Business Central
2. Fetch data from a single endpoint
3. Use basic filtering and field selection
"""

import asyncio

from pybcodata import connect

# Configuration
BASE_URL = "http://erp.konspec.in:8148/bc-user/odatav4/Company('KSPPL')/"
USERNAME = "your_username"
PASSWORD = "your_password"


async def main():
    # Create a session
    session = connect(BASE_URL, USERNAME, PASSWORD)

    async with session:
        # Verify credentials
        await session.check_credentials()

        # Basic fetch - get all customers
        customers = await session.source("customers").fetch()
        print(f"Found {len(customers)} customers")

        # Fetch with filtering and field selection
        active_customers = (
            await session.source("customers")
            .filter("status eq 'Active'")
            .select(["number", "name", "email"])
            .fetch()
        )
        print(f"Found {len(active_customers)} active customers")

        # Fetch as DataFrame (requires polars)
        try:
            customers_df = (
                await session.source("customers")
                .filter("status eq 'Active'")
                .select(["number", "name", "email"])
                .fetch(as_df=True)
            )
            print("\nDataFrame preview:")
            print(customers_df.head())
        except ImportError:
            print("\nPolars not installed. Install with: pip install polars")


if __name__ == "__main__":
    asyncio.run(main())
