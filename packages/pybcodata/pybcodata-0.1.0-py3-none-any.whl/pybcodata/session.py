"""
Client class for Business Central OData API.

This class provides a robust interface to interact with Business Central's OData API,
including features like rate limiting, concurrent request handling, automatic retries,
and pagination support.

Example:
    ```python
    session = BusinessCentralSession(
        base_url="https://api.businesscentral.com/v2.0/",
        username="user",
        password="pass"
    )
    await session.check_credentials()
    data = await session.get_data("customers")
    ```
"""

import asyncio
from typing import TYPE_CHECKING, Any

import httpx
from aiolimiter import AsyncLimiter
from loguru import logger

if TYPE_CHECKING:
    from pybcodata.query import QueryBuilder


class BusinessCentralSession:
    """
    Client class for Business Central OData API.

    This class manages the connection to Business Central's OData API, handling
    authentication, rate limiting, concurrent requests, and automatic retries.
    It provides methods to fetch data and create query builders for specific endpoints.

    Args:
        base_url: The base URL of the Business Central OData API (e.g., "https://api.businesscentral.com/v2.0/")
        username: The username for authentication
        password: The password for authentication
        limit: Maximum number of requests allowed per period (default: 9)
        period: Time period in seconds for rate limiting (default: 1)
        max_concurrency: Maximum number of concurrent requests (default: 5)
        max_retries: Maximum number of retry attempts for failed requests (default: 3)
        base_backoff: Base time in seconds for exponential backoff between retries (default: 5.0)

    Attributes:
        base_url: The normalized base URL for API requests
        session: The underlying httpx.AsyncClient instance
        limiter: Rate limiter instance
        semaphore: Concurrency control semaphore
        max_retries: Maximum number of retry attempts
        base_backoff: Base backoff time for retries
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        limit: int = 9,
        period: int = 1,
        max_concurrency: int = 5,
        max_retries: int = 3,
        base_backoff: float = 5.0,
    ) -> None:
        # Normalize base URL by ensuring it ends with a single forward slash
        self.base_url = base_url.rstrip("/") + "/"

        # Initialize HTTP client with authentication and reasonable timeouts
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            auth=(username, password),
            timeout=httpx.Timeout(30.0, read=30.0, connect=30.0),
        )

        # Configure rate limiting and concurrency controls
        self.limiter = AsyncLimiter(limit, period)
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries
        self.base_backoff = base_backoff

    async def check_credentials(self) -> None:
        """
        Verify the authentication credentials by making a test request to the API.

        This method attempts to make a simple GET request to the base URL to verify
        that the provided credentials are valid and the API is accessible.

        Raises:
            ValueError: If the credentials are invalid (401 Unauthorized)
            ConnectionError: If there are network issues or server errors
            Exception: For any other unexpected errors
        """
        logger.debug(
            f"Validating credentials for Business Central API at {self.base_url}"
        )
        try:
            response = await self.session.get("")
            response.raise_for_status()
            logger.info(
                f"Successfully authenticated with Business Central API at {self.base_url}"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error(
                    f"Authentication failed for {self.base_url}. "
                    f"Status: 401 Unauthorized. Please verify your credentials."
                )
                raise ValueError("Invalid credentials") from e
            else:
                logger.error(
                    f"API request failed for {self.base_url}. "
                    f"Status: {e.response.status_code}. "
                    f"Response: {e.response.text}"
                )
                raise ConnectionError(
                    f"Failed to connect or authenticate: {e.response.status_code}"
                ) from e
        except httpx.RequestError as e:
            logger.error(
                f"Network error while connecting to {self.base_url}: {e}. "
                "Please check your network connection and API endpoint."
            )
            raise ConnectionError(f"Network or connection error: {e}") from e
        except Exception as e:
            logger.error(
                f"Unexpected error during credential validation for {self.base_url}: {e}. "
                "Please check the API configuration and try again."
            )
            raise

    def _get_backoff(self, attempt: int) -> float:
        """
        Calculate the backoff time for retry attempts using exponential backoff.

        The backoff time increases exponentially with each attempt to prevent
        overwhelming the server during retries.

        Args:
            attempt: The current retry attempt number (1-indexed)

        Returns:
            float: The backoff time in seconds
        """
        return self.base_backoff * (2 ** (attempt - 1))

    async def _make_request(
        self, url: str, params: dict[str, Any] = None
    ) -> httpx.Response:
        """
        Make an HTTP request with rate limiting, concurrency control, and automatic retries.

        This method handles the core request logic, including:
        - Rate limiting to prevent API overload
        - Concurrency control to manage parallel requests
        - Automatic retries with exponential backoff
        - Comprehensive error handling and logging

        Args:
            url: The URL to make the request to (can be relative to base_url)
            params: Optional query parameters for the request

        Returns:
            httpx.Response: The successful response from the request

        Raises:
            httpx.HTTPStatusError: If the request fails after retries with a non-retriable status
            httpx.RequestError: For connection issues not resolved by retries
            RuntimeError: If all retry attempts are exhausted without success
        """
        effective_url = url

        for attempt in range(self.max_retries + 1):
            logger.debug(
                f"Making request to {effective_url} (attempt {attempt + 1}/{self.max_retries + 1}) "
                f"with parameters: {params}"
            )
            async with self.semaphore:  # Control concurrent requests
                async with self.limiter:  # Enforce rate limits
                    try:
                        response = await self.session.get(url, params=params)
                        response.raise_for_status()
                        logger.debug(
                            f"Successfully completed request to {effective_url} on attempt {attempt + 1}"
                        )
                        return response
                    except httpx.HTTPStatusError as e:
                        # Retry on rate limits (429) or server errors (5xx)
                        if (
                            e.response.status_code == 429
                            or 500 <= e.response.status_code < 600
                        ):
                            logger.warning(
                                f"Received {e.response.status_code} error for {effective_url}. "
                                f"Attempt {attempt + 1}/{self.max_retries + 1}. "
                                f"Retrying with backoff..."
                            )
                            if attempt == self.max_retries:
                                logger.error(
                                    f"Maximum retry attempts ({self.max_retries + 1}) reached for {effective_url}. "
                                    f"Last error: {e.response.status_code}. "
                                    f"Aborting request."
                                )
                                raise
                            backoff = self._get_backoff(attempt + 1)
                            logger.info(
                                f"Waiting {backoff:.2f} seconds before retry attempt {attempt + 2} for {effective_url}"
                            )
                            await asyncio.sleep(backoff)
                            continue
                        else:
                            # Don't retry on client errors (4xx)
                            logger.error(
                                f"Request failed with non-retriable status {e.response.status_code} "
                                f"for {effective_url}. Response: {e.response.text}"
                            )
                            raise
                    except httpx.RequestError as e:
                        # Retry on network-related errors
                        logger.warning(
                            f"Network error ({type(e).__name__}) for {effective_url}. "
                            f"Attempt {attempt + 1}/{self.max_retries + 1}. "
                            f"Retrying with backoff..."
                        )
                        if attempt == self.max_retries:
                            logger.error(
                                f"Maximum retry attempts ({self.max_retries + 1}) reached for {effective_url} "
                                f"after network error. Last error: {e}. "
                                f"Aborting request."
                            )
                            raise
                        backoff = self._get_backoff(attempt + 1)
                        logger.info(
                            f"Waiting {backoff:.2f} seconds before retry attempt {attempt + 2} "
                            f"due to network error for {effective_url}"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    except Exception as e:
                        # Don't retry on unexpected errors
                        logger.error(
                            f"Unexpected error during request to {effective_url} on attempt {attempt + 1}: {e}"
                        )
                        raise

        # This should never be reached due to the raise statements above
        logger.critical(
            f"Request to {effective_url} exhausted all retry attempts without proper resolution. "
            "This indicates a logic error in the retry mechanism."
        )
        raise RuntimeError(
            f"Failed to get a response for {effective_url} after {self.max_retries + 1} attempts."
        )

    async def get_data(
        self, endpoint: str, params: dict[str, Any] = None
    ) -> list[dict[str, Any]]:
        """
        Fetch data from the specified endpoint with support for OData pagination.

        This method handles the complete data retrieval process, including:
        - Making the initial request
        - Processing the response
        - Following pagination links (@odata.nextLink)
        - Aggregating all results

        Args:
            endpoint: The API endpoint (relative to base_url)
            params: Optional query parameters for the request

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing the retrieved data

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            httpx.RequestError: For network errors
            httpx.JSONDecodeError: If the response cannot be parsed as JSON
        """
        # Normalize endpoint URL
        current_url = endpoint.lstrip("/")

        # Create a copy of parameters for the first request
        current_params = params.copy() if params else {}

        all_data: list[dict[str, Any]] = []

        page_count = 0
        while current_url:
            page_count += 1
            logger.debug(
                f"Fetching page {page_count} from {current_url} with parameters: {current_params}"
            )
            response_obj = await self._make_request(current_url, params=current_params)

            try:
                response_json = response_obj.json()
            except httpx.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON response from {current_url}. "
                    f"Parameters: {current_params}. "
                    f"Error: {e}. "
                    f"Response text: {response_obj.text}"
                )
                raise

            page_data = response_json.get("value", [])
            if isinstance(page_data, list):
                all_data.extend(page_data)
                logger.debug(
                    f"Retrieved {len(page_data)} items from page {page_count}. Total items so far: {len(all_data)}"
                )
            else:
                logger.warning(
                    f"Expected 'value' to be a list in response from {current_url}, but got {type(page_data)}"
                )

            # Check for next page
            current_url = response_json.get("@odata.nextLink")
            if current_url:
                logger.debug(f"Found next page link: {current_url}")
            else:
                logger.debug("No more pages available. Pagination complete.")
            current_params = {}  # Reset parameters for subsequent pages

        return all_data

    def source(self, endpoint: str) -> "QueryBuilder":
        """
        Create a query builder for the specified endpoint.

        This method provides a fluent interface for building OData queries
        with support for filtering, sorting, field selection, and pagination.

        Args:
            endpoint: The API endpoint to create a query builder for

        Returns:
            QueryBuilder: A new query builder instance for the specified endpoint
        """
        from pybcodata.query import QueryBuilder

        return QueryBuilder(self, endpoint)

    async def __aenter__(self):
        """Context manager entry point."""
        return self

    async def close(self):
        """Close the underlying HTTP client session."""
        await self.session.aclose()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Context manager exit point."""
        await self.close()
