"""
This module contains various utility functions
"""
import os


def get_url_base() -> str:
    """
    Returns the base URL for the API which can be overridden from the URL_BASE environment variable
    """
    url_base = "https://battleshapi.pythonanywhere.com/api/aircraft_carrier"

    if os.getenv('URL_BASE') is not None:
        url_base = os.getenv('URL_BASE')

    return url_base
