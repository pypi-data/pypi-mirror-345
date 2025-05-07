"""
Shortcuts for common Business Central operations.
"""

import asyncio
from typing import Any

from pybcodata.query import QueryBuilder


async def fetch_all(*queries: QueryBuilder, as_df: bool = False) -> list[Any]:
    """
    Fetch data from multiple queries in parallel.

    Args:
        *queries: QueryBuilder instances to execute
        as_df: If True, return results as Polars DataFrames

    Returns:
        list[Any]: Results in the same order as the queries

    Example:
        ```python
        # Create queries
        cmp_query = session.source("ksppl_cmp")
        sales_query = session.source("ksppl_sales_people")

        # Fetch both in parallel
        cmp_data, sales_data = await fetch_all(cmp_query, sales_query)

        # Or as DataFrames
        cmp_df, sales_df = await fetch_all(cmp_query, sales_query, as_df=True)
        ```
    """

    async def fetch_query(query: QueryBuilder) -> Any:
        return await query.fetch(as_df=as_df)

    return await asyncio.gather(*(fetch_query(query) for query in queries))
