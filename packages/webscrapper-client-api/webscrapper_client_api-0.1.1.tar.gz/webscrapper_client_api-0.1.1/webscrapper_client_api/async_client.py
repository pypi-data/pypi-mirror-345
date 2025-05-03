"""
Webscrapper Client API Async
A client for the webscrapper API that provides methods for page retrieval and RKN checks.
"""

import json
import aiohttp
import asyncio
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlencode

from .exceptions import WebscrapperAPIError

class WebscrapperClientAPIAsync:
    """
    Async client for the webscrapper API
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

    async def __aenter__(self):
        """Initialize session when used as context manager"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session when context manager exits"""
        if self.session:
            await self.session.close()
            self.session = None

    def _get_session(self):
        """Get or create a session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session

    async def close(self):
        """Close the client session explicitly"""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_page(
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
            async with session.get(
                endpoint, headers=headers, params=params
            ) as response:
                result = await response.json()

                if response.status != 200:
                    error_msg = result.get("error", f"HTTP error {response.status}")
                    raise WebscrapperAPIError(error_msg, status_code=response.status)

                return result
        except aiohttp.ClientError as e:
            raise WebscrapperAPIError(f"HTTP request failed: {str(e)}")

    async def check_rkn(self, url: str) -> Dict[str, Any]:
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
            async with session.get(
                endpoint, params=params, headers=headers
            ) as response:
                result = await response.json()

                if response.status != 200:
                    error_msg = result.get("error", f"HTTP error {response.status}")
                    raise WebscrapperAPIError(error_msg, status_code=response.status)

                return result
        except aiohttp.ClientError as e:
            raise WebscrapperAPIError(f"HTTP request failed: {str(e)}")


