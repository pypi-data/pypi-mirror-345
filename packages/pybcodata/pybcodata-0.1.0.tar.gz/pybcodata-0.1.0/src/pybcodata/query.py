"""
Query builder for Business Central OData API.

This module provides a fluent interface for building OData queries with support for
filtering, sorting, field selection, and pagination. It also includes optional
integration with Polars for data analysis.

Example:
    ```python
    query = session.source("customers") \
        .filter("status eq 'Active'") \
        .select(["number", "name", "email"]) \
        .top(100) \
        .fetch()
    ```
"""

from typing import TYPE_CHECKING, Any

from loguru import logger

try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

if TYPE_CHECKING:
    from pybcodata.session import BusinessCentralSession

    if POLARS_AVAILABLE and pl:
        PolarsDataFrame = pl.DataFrame
    else:
        PolarsDataFrame = Any


class QueryBuilder:
    """
    Builder class for constructing OData queries.

    This class provides a fluent interface for building OData queries with support for:
    - Filtering data using OData filter expressions
    - Sorting results using OData orderby expressions
    - Selecting specific fields
    - Limiting the number of results
    - Skipping results for pagination

    The query is executed when fetch() is called, which returns either a list of
    dictionaries or a Polars DataFrame (if polars is installed and as_df=True).

    Args:
        session: The BusinessCentralSession instance to use for requests
        endpoint: The API endpoint for this query (e.g., "customers", "items")

    Attributes:
        session: The BusinessCentralSession instance
        endpoint: The API endpoint
        params: Dictionary of OData query parameters
    """

    def __init__(self, session: "BusinessCentralSession", endpoint: str) -> None:
        """
        Initialize the QueryBuilder.

        Args:
            session: The BusinessCentralSession instance to use for requests
            endpoint: The API endpoint for this query
        """
        self.session = session
        self.endpoint = endpoint
        self.params: dict[str, Any] = {}

    def filter(self, query: str) -> "QueryBuilder":
        """
        Add a $filter parameter to the query.

        This method allows filtering the results using OData filter expressions.
        The filter is applied on the server side before results are returned.

        Args:
            query: The OData filter expression (e.g., "status eq 'Active'")

        Returns:
            QueryBuilder: The QueryBuilder instance for method chaining

        Example:
            ```python
            query.filter("status eq 'Active' and balance gt 1000")
            ```
        """
        self.params["$filter"] = query
        return self

    def order_by(self, query: str) -> "QueryBuilder":
        """
        Add an $orderby parameter to the query.

        This method allows sorting the results using OData orderby expressions.
        Multiple fields can be specified, separated by commas.

        Args:
            query: The OData orderby expression (e.g., "name asc, createdDate desc")

        Returns:
            QueryBuilder: The QueryBuilder instance for method chaining

        Example:
            ```python
            query.order_by("name asc, createdDate desc")
            ```
        """
        self.params["$orderby"] = query
        return self

    def select(self, query: str | list[str]) -> "QueryBuilder":
        """
        Add a $select parameter to the query.

        This method allows selecting specific fields from the results.
        If not specified, all fields are returned.

        Args:
            query: A comma-separated string or a list of field names to select

        Returns:
            QueryBuilder: The QueryBuilder instance for method chaining

        Example:
            ```python
            query.select(["number", "name", "email"])
            # or
            query.select("number,name,email")
            ```
        """
        if isinstance(query, list):
            self.params["$select"] = ",".join(query)
        else:
            self.params["$select"] = query
        return self

    def top(self, count: int) -> "QueryBuilder":
        """
        Add a $top parameter to the query.

        This method limits the number of results returned by the query.
        It's useful for pagination or when you only need a subset of the data.

        Args:
            count: The maximum number of records to return

        Returns:
            QueryBuilder: The QueryBuilder instance for method chaining

        Example:
            ```python
            query.top(100)  # Return at most 100 records
            ```
        """
        self.params["$top"] = count
        return self

    def skip(self, count: int) -> "QueryBuilder":
        """
        Add a $skip parameter to the query.

        This method skips a specified number of results, which is useful for
        pagination when combined with $top.

        Args:
            count: The number of records to skip

        Returns:
            QueryBuilder: The QueryBuilder instance for method chaining

        Example:
            ```python
            query.skip(100).top(50)  # Skip first 100 records, then return 50
            ```
        """
        self.params["$skip"] = count
        return self

    async def fetch(self, as_df: bool = False):  # type: ignore
        """
        Execute the query and fetch the results.

        This method sends the constructed query to the Business Central API and
        returns the results. The results can be returned either as a list of
        dictionaries or as a Polars DataFrame.

        Args:
            as_df: If True and polars is installed, return data as a Polars DataFrame.
                  Otherwise, returns a list of dictionaries.

        Returns:
            Union[list[dict[str, Any]], PolarsDataFrame]: The query results

        Example:
            ```python
            # Get results as list of dicts
            results = await query.fetch()

            # Get results as Polars DataFrame (if polars is installed)
            df = await query.fetch(as_df=True)
            ```
        """
        response_data: list[dict[str, Any]] = await self.session.get_data(
            self.endpoint, self.params
        )

        if as_df:
            if POLARS_AVAILABLE and pl:
                return pl.DataFrame(response_data)
            else:
                logger.warning(
                    "Polars library not found. Returning data as list of dicts instead of DataFrame. "
                    "To use DataFrame functionality, install polars: pip install polars"
                )
                return response_data
        else:
            return response_data
