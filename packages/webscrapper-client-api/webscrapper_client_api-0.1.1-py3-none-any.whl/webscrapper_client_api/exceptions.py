"""Webscrapper exceptions class"""


class WebscrapperAPIError(Exception):
    """Exception raised for errors in the Webscrapper API."""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
