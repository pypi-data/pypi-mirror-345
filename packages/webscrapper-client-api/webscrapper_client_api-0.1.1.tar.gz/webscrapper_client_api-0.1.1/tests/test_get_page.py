"""
Tests for the get_page method of the WebscrapperClientAPI.
"""

import pytest
import json
from urllib.parse import urlencode

from webscrapper_client_api import WebscrapperClientAPI, WebscrapperAPIError


class TestGetPage:
    """Tests for the get_page method."""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, client, mock_aioresponse, base_url, test_url, api_key):
        """Test basic functionality of get_page."""
        # Prepare mock response
        expected_result = {
            "html": "<html><body>Test page</body></html>",
            "status_code": "200",
            "url": test_url,
            "error": ""
        }
        
        # Setup mock response
        params = {"key": api_key, "url": test_url, "use_selenium": "", "use_mobile": "", "method": "get"}
        endpoint = f"{base_url}/api/get?{urlencode(params)}"
        mock_aioresponse.get(endpoint, status=200, payload=expected_result)
        
        # Call method
        result = await client.get_page(url=test_url)
        
        # Validate result
        assert result == expected_result
        assert result["html"] == expected_result["html"]
        assert result["status_code"] == expected_result["status_code"]
    
    @pytest.mark.asyncio
    async def test_get_page_with_cookies(self, client, mock_aioresponse, base_url, test_url, api_key):
        """Test get_page with cookies."""
        # Prepare mock response
        expected_result = {
            "html": "<html><body>Test page with cookies</body></html>",
            "status_code": "200",
            "url": test_url,
            "error": ""
        }
        
        # Test cookies
        cookies = {"session_id": "abc123", "user": "test"}
        
        # Setup mock response with cookies
        params = {
            "key": api_key, 
            "url": test_url, 
            "use_selenium": "", 
            "use_mobile": "", 
            "method": "get",
            "cookies": json.dumps(cookies)
        }
        endpoint = f"{base_url}/api/get?{urlencode(params)}"
        mock_aioresponse.get(endpoint, status=200, payload=expected_result)
        
        # Call method with cookies
        result = await client.get_page(url=test_url, cookies=cookies)
        
        # Validate result
        assert result == expected_result
        assert result["html"] == expected_result["html"]
    
    @pytest.mark.asyncio
    async def test_get_page_with_selenium(self, client, mock_aioresponse, base_url, test_url, api_key):
        """Test get_page with Selenium."""
        # Prepare mock response
        expected_result = {
            "html": "<html><body>Test page with Selenium</body></html>",
            "status_code": "200",
            "url": test_url,
            "error": "",
            "selenium": True
        }
        
        # Setup mock response for Selenium
        params = {
            "key": api_key, 
            "url": test_url, 
            "use_selenium": "1", 
            "use_mobile": "", 
            "method": "get"
        }
        endpoint = f"{base_url}/api/get?{urlencode(params)}"
        mock_aioresponse.get(endpoint, status=200, payload=expected_result)
        
        # Call method with Selenium
        result = await client.get_page(url=test_url, use_selenium=True)
        
        # Validate result
        assert result == expected_result
        assert result["selenium"] is True
    
    @pytest.mark.asyncio
    async def test_get_page_error(self, client, mock_aioresponse, base_url, test_url, api_key):
        """Test error handling in get_page."""
        # Prepare mock error response
        error_response = {
            "error": "No suitable proxies available"
        }
        
        # Setup mock error response
        params = {"key": api_key, "url": test_url, "use_selenium": "", "use_mobile": "", "method": "get"}
        endpoint = f"{base_url}/api/get?{urlencode(params)}"
        mock_aioresponse.get(endpoint, status=400, payload=error_response)
        
        # Call method and expect exception
        with pytest.raises(WebscrapperAPIError) as excinfo:
            await client.get_page(url=test_url)
        
        # Validate exception
        assert "No suitable proxies available" in str(excinfo.value)
        assert excinfo.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_page_with_all_params(self, client, mock_aioresponse, base_url, test_url, api_key):
        """Test get_page with all parameters."""
        # Prepare mock response
        expected_result = {
            "html": "<html><body>Test page with all params</body></html>",
            "status_code": "200",
            "url": test_url,
            "error": ""
        }
        
        # Test parameters
        cookies = {"session_id": "abc123"}
        user_agent = "Mozilla/5.0 (Test)"
        referer = "https://google.com"
        method = "head"
        country = 1
        
        # Setup mock response with all parameters
        params = {
            "key": api_key, 
            "url": test_url, 
            "use_selenium": "", 
            "use_mobile": "1", 
            "method": method,
            "cookies": json.dumps(cookies),
            "ua": user_agent,
            "referer": referer,
            "country": str(country)
        }
        endpoint = f"{base_url}/api/get?{urlencode(params)}"
        mock_aioresponse.get(endpoint, status=200, payload=expected_result)
        
        # Call method with all parameters
        result = await client.get_page(
            url=test_url,
            use_mobile=True,
            user_agent=user_agent,
            referer=referer,
            method=method,
            country=country,
            cookies=cookies
        )
        
        # Validate result
        assert result == expected_result
        
