"""Geocoding service using OpenStreetMap Nominatim API."""

from functools import lru_cache

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from src.utils.types import Location


class InvalidLocationError(Exception):
    """Raised when a location cannot be geocoded."""


class APIError(Exception):
    """Raised when Nominatim API encounters an error."""


@lru_cache(maxsize=100)
def geocode_address(address: str, user_agent: str = "RoutePathfindingVisualizer/0.1.0") -> Location:
    """Convert an address string to geographic coordinates.

    Uses OpenStreetMap Nominatim API with LRU caching to reduce API calls.

    Args:
        address: Human-readable address string
        user_agent: User agent string for API requests

    Returns:
        Location with formatted address and coordinates

    Raises:
        ValueError: If address is empty or whitespace-only
        InvalidLocationError: If address cannot be geocoded
        APIError: If API request fails (timeout, network error, service error)
    """
    if not address or not address.strip():
        raise ValueError("Address cannot be empty")

    try:
        geolocator = Nominatim(user_agent=user_agent, timeout=10)
        result = geolocator.geocode(address)
    except GeocoderTimedOut as e:
        raise APIError(f"API request timed out after 10 seconds: {e}") from e
    except GeocoderServiceError as e:
        raise APIError(f"Nominatim service error: {e}") from e
    except Exception as e:
        raise APIError(f"Network connection error: {e}") from e

    if not result:
        raise InvalidLocationError(
            f"Address not found: '{address}'. "
            "Please enter a valid location (e.g., 'Times Square, New York')"
        )

    return Location(
        address=result.address,
        latitude=result.latitude,
        longitude=result.longitude,
    )
