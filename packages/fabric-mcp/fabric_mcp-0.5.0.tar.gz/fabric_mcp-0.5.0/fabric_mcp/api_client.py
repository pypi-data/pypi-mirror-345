"""Fabric API Client for Python"""

import json
import os
from typing import Any, Dict, Optional

import requests  # Grouped external imports
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from fabric_mcp import __version__ as fabric_mcp_version
from fabric_mcp.utils import Log

logger = Log().logger

DEFAULT_BASE_URL = "http://127.0.0.1:8080"  # Default for fabric --serve
DEFAULT_TIMEOUT = 30  # seconds


class FabricApiClient:
    """Client for interacting with the Fabric REST API."""

    FABRIC_API_HEADER = "X-API-Key"
    REDACTED_HEADERS = ["Authorization", FABRIC_API_HEADER]

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initializes the Fabric API client.

        Args:
            base_url: The base URL for the Fabric API. Defaults to env
                      FABRIC_BASE_URL or DEFAULT_BASE_URL.
            api_key: The API key for authentication. Defaults to env FABRIC_API_KEY.

            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or os.environ.get("FABRIC_BASE_URL", DEFAULT_BASE_URL)
        self.api_key = api_key or os.environ.get("FABRIC_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            logger.warning(
                "Fabric API key not provided. If needed, set FABRIC_API_KEY variable."
            )

        self.session = requests.Session()
        # Basic user agent
        self.session.headers.update(
            {"User-Agent": f"FabricMCPClient/v{fabric_mcp_version}"}
        )
        if self.api_key:
            # Add Auth header
            self.session.headers.update({self.FABRIC_API_HEADER: f"{self.api_key}"})

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],  # Retry on server errors
            allowed_methods=[
                "HEAD",
                "GET",
                "OPTIONS",
                "POST",
                "PUT",
                "DELETE",
            ],  # Retry on these methods
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)  # Ensure HTTPS is also covered

        logger.info("FabricApiClient initialized for base URL: %s", self.base_url)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Makes a request to the Fabric API.

        Args:
            method: HTTP method (e.g., 'GET', 'POST').
            endpoint: API endpoint path (e.g., '/patterns').
            params: URL parameters.
            json_data: JSON payload for the request body.
            data: Raw data for the request body.
            headers: Additional request headers.

        Returns:
            The requests.Response object.

        Raises:
            requests.exceptions.RequestException: For connection errors, timeouts, etc.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        # Mask API key in logs
        log_headers = request_headers.copy()
        for header in self.REDACTED_HEADERS:
            if header in log_headers:
                log_headers[header] = "***REDACTED***"

        logger.debug("Request: %s %s", method, url)
        logger.debug("Headers: %s", log_headers)
        if params:
            logger.debug("Params: %s", params)
        if json_data:
            logger.debug("JSON Body: %s", json_data)
        elif data:
            logger.debug("Body: <raw data>")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                headers=request_headers,
                timeout=self.timeout,
            )
            logger.debug("Response Status: %s", response.status_code)
            # Log response body carefully, might be large or sensitive
            # logger.debug("Response Body: %s...", response.text[:500]) # Example

            # Raise HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s %s - %s", method, url, e)
            raise  # Re-raise the exception after logging

    # --- Public API Methods (Wrapped signatures for line length) ---

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> requests.Response:
        """Sends a GET request."""
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs,
    ) -> requests.Response:
        """Sends a POST request."""
        return self._request("POST", endpoint, json_data=json_data, data=data, **kwargs)

    def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs,
    ) -> requests.Response:
        """Sends a PUT request."""
        return self._request("PUT", endpoint, json_data=json_data, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Sends a DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)


# Example usage (optional, for testing)
if __name__ == "__main__":

    def main():
        """Main function to demonstrate the Fabric API client."""
        # Assumes FABRIC_API_KEY is set in the environment
        client = FabricApiClient()
        api_response = None
        try:
            # Example: Try to get list of strategies
            print("Attempting to connect to Fabric API...")
            api_response = client.get("/strategies")
            print("Successfully connected and received response:")
            # This specific call might raise JSONDecodeError
            print(api_response.json())
        # Catch JSON decoding errors specifically first
        except (requests.exceptions.JSONDecodeError, json.JSONDecodeError) as e:
            print(f"Failed to decode JSON response: {e}")
            # Optionally print the raw text if decoding fails
            if api_response is not None:
                print(f"Raw response text: {api_response.text[:500]}...")
        # Catch other request-related errors (Connection, Timeout, HTTPError, etc.)
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect or get response: {e}")
        # Removed the generic 'except Exception' for the example

    main()
