"""Geocoding service wrapper.

Input:
- manual address text from user

Output:
- normalized geographic coordinates and formatted address
"""


def geocode_address(address: str) -> dict:
    """Convert text address to latitude/longitude.

    TODO:
    - call Google Geocoding API
    - return formatted address and coordinates
    - handle ambiguous addresses gracefully
    """
    return {"formatted_address": address, "latitude": None, "longitude": None}
