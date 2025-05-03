"""
Webscrapper Client API (Synchronous)
A synchronous client for the webscrapper API that provides methods for page retrieval and RKN checks.
"""

import json
import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlencode
from .exceptions import WebscrapperAPIError


class WebscrapperClientAPI:
    """
    Synchronous client for the webscrapper API.
    Provides methods for page retrieval and RKN checks.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://fetch.webnova.one",
        timeout: int = 120,
    ):
        """
        Initialize the webscrapper client API.

        Args:
            base_url: Base URL for the API (e.g., "https://fetch.webnova.one")
            api_key: API key for authentication
            timeout: Request timeout in seconds (default: 120)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = None

    def __enter__(self):
        """Initialize session when used as context manager"""
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close session when context manager exits"""
        if self.session:
            self.session.close()
            self.session = None

    def _get_session(self):
        """Get or create a session"""
        if self.session is None:
            self.session = requests.Session()
        return self.session

    def close(self):
        """Close the client session explicitly"""
        if self.session:
            self.session.close()
            self.session = None

    def get_page(
        self,
        url: str,
        use_selenium: bool = False,
        use_mobile: bool = False,
        user_agent: str = None,
        referer: str = None,
        method: str = "get",
        country: int = None,
        cookies: Optional[Union[Dict[str, str], List[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a web page through a proxy.

        Args:
            url: URL to retrieve
            use_selenium: Use Selenium for request (default: False)
            use_mobile: Use mobile proxy (default: False)
            user_agent: Custom User-Agent header
            referer: Custom referer (not used for Selenium)
            method: Request method: 'get' or 'head' (only applicable when Selenium not used)
            country: Proxy country ID
            cookies: Cookies to send with the request.
                    For non-selenium: dict of name:value pairs.
                    For selenium: list of objects with at least 'name' and 'value' keys.

        Returns:
            Dict with html content, error message, status code and final URL
        """
        params = {
            "url": url,
            "use_selenium": "1" if use_selenium else "",
            "use_mobile": "1" if use_mobile else "",
            "method": method,
        }

        # Add optional parameters if provided
        if user_agent:
            params["ua"] = user_agent
        if referer:
            params["referer"] = referer
        if country:
            params["country"] = str(country)
        if cookies:
            params["cookies"] = json.dumps(cookies)

        session = self._get_session()
        endpoint = f"{self.base_url}/api/get"
        headers = {"Authorization": f"api-key {self.api_key}"}

        try:
            response = session.get(
                endpoint, headers=headers, params=params, timeout=self.timeout
            )

            response.raise_for_status()  # Raise exception for HTTP errors
            result = response.json()

            return result
        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, "response") else None
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get(
                        "error", f"HTTP error {e.response.status_code}"
                    )
                except ValueError:
                    error_msg = f"HTTP error {e.response.status_code}"
            else:
                error_msg = f"HTTP request failed: {str(e)}"

            raise WebscrapperAPIError(error_msg, status_code=status_code)

    def check_rkn(self, url: str) -> Dict[str, Any]:
        """
        Check if a domain is blocked by RKN (Russian internet regulator).

        Args:
            url: URL to check

        Returns:
            Dict with RKN check results
        """
        params = {
            "url": url,
        }

        session = self._get_session()
        endpoint = f"{self.base_url}/api/rkn"
        headers = {"Authorization": f"api-key {self.api_key}"}

        try:
            response = session.get(
                endpoint, params=params, headers=headers, timeout=self.timeout
            )

            response.raise_for_status()  # Raise exception for HTTP errors
            result = response.json()

            return result
        except requests.RequestException as e:
            status_code = e.response.status_code if hasattr(e, "response") else None
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get(
                        "error", f"HTTP error {e.response.status_code}"
                    )
                except ValueError:
                    error_msg = f"HTTP error {e.response.status_code}"
            else:
                error_msg = f"HTTP request failed: {str(e)}"

            raise WebscrapperAPIError(error_msg, status_code=status_code)
