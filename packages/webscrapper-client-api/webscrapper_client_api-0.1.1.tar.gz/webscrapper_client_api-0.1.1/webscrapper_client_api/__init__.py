"""
Webscrapper Client API
A client for the webscrapper API that provides methods for page retrieval and RKN checks.
"""

from .client import WebscrapperClientAPI
from .async_client import WebscrapperClientAPIAsync
from .exceptions import WebscrapperAPIError

__all__ = ["WebscrapperClientAPI", "WebscrapperClientAPIAsync", "WebscrapperAPIError"]
__version__ = "0.1.0"
