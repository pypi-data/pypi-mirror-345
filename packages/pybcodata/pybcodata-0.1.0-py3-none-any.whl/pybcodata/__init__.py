"""
Business Central OData API Client.

This package provides a Python client for interacting with Business Central's OData API.
It offers features like rate limiting, concurrent requests, automatic retries,
and pagination support. The client can be used to fetch data and perform queries
on Business Central entities.

Example:
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
        
        # Verify credentials
        await session.check_credentials()
        
        # Fetch data
        customers = await session.source("customers") \
            .filter("status eq 'Active'") \
            .select(["number", "name", "email"]) \
            .top(100) \
            .fetch()
        
        # Close the session
        await session.close()

    # Run the async code
    asyncio.run(main())
    ```
"""

from loguru import logger

from pybcodata.session import BusinessCentralSession

__all__ = ["BusinessCentralSession", "connect"]


def connect(
    base_url: str,
    username: str,
    password: str,
    limit: int = 9,
    period: int = 1,
    max_concurrency: int = 5,
    max_retries: int = 3,
    base_backoff: float = 5.0,
) -> BusinessCentralSession:
    """
    Create a new Business Central session.

    This function initializes and returns a BusinessCentralSession instance with
    the specified configuration. The session provides methods for interacting
    with the Business Central OData API, including data fetching and querying.

    The caller is responsible for:
    1. Calling `await session.check_credentials()` to verify authentication
    2. Using `await session.close()` when done to clean up resources
    3. Using the session within an async context

    Args:
        base_url: The base URL of the Business Central OData API
                  (e.g., "https://api.businesscentral.com/v2.0/")
        username: The username for authentication
        password: The password for authentication
        limit: Maximum number of requests allowed per period (default: 9)
        period: Time period in seconds for rate limiting (default: 1)
        max_concurrency: Maximum number of concurrent requests (default: 5)
        max_retries: Maximum number of retry attempts for failed requests (default: 3)
        base_backoff: Base time in seconds for exponential backoff between retries (default: 5.0)

    Returns:
        BusinessCentralSession: A new session instance configured with the provided parameters

    Example:
        ```python
        session = connect(
            base_url="https://api.businesscentral.com/v2.0/",
            username="user",
            password="pass",
            limit=5,  # 5 requests per second
            period=1,
            max_concurrency=3  # Maximum 3 concurrent requests
        )
        ```
    """
    logger.info(
        f"Initializing BusinessCentralSession for {base_url} "
        f"(rate limit: {limit}/{period}s, concurrency: {max_concurrency})"
    )
    return BusinessCentralSession(
        base_url=base_url,
        username=username,
        password=password,
        limit=limit,
        period=period,
        max_concurrency=max_concurrency,
        max_retries=max_retries,
        base_backoff=base_backoff,
    )
