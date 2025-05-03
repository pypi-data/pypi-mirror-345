"""
Integration tests for the WebscrapperClientAPI.

These tests require a valid API key and will make actual API calls.
Skip these tests during regular test runs by using:
    pytest -k "not integration"
"""

import os
import pytest
from dotenv import load_dotenv

from webscrapper_client_api import WebscrapperClientAPI

# Load environment variables
load_dotenv()

# Skip all tests in this module if SKIP_INTEGRATION is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION") == "1",
    reason="Integration tests skipped"
)


class TestIntegration:
    """Integration tests for WebscrapperClientAPI."""

    @pytest.mark.asyncio
    async def test_get_page_integration(self, base_url, api_key, test_url):
        """Test get_page against the real API."""
        async with WebscrapperClientAPI(base_url, api_key) as client:
            result = await client.get_page(url=test_url)
            
            # Basic validation
            assert result is not None
            assert "html" in result
            assert "status_code" in result
            assert "url" in result
            assert len(result["html"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_page_with_cookies_integration(self, base_url, api_key, test_url):
        """Test get_page with cookies against the real API."""
        cookies = {"test_cookie": "integration_test"}
        
        async with WebscrapperClientAPI(base_url, api_key) as client:
            result = await client.get_page(
                url=test_url,
                cookies=cookies,
                user_agent="WebscrapperClientAPI Integration Test",
                referer="https://github.com/yourusername/webscrapper-client-api"
            )
            
            # Basic validation
            assert result is not None
            assert "html" in result
            assert "status_code" in result
            assert "url" in result
            assert len(result["html"]) > 0
    
    @pytest.mark.asyncio
    async def test_check_rkn_integration(self, base_url, api_key, test_url):
        """Test check_rkn against the real API."""
        async with WebscrapperClientAPI(base_url, api_key) as client:
            result = await client.check_rkn(url=test_url)
            
            # Basic validation
            assert result is not None
            assert "blocked" in result
            assert isinstance(result["blocked"], bool)

            
