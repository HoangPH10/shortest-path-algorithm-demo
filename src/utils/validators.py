"""Input validation utilities for route visualization application.

This module provides validation functions for addresses, coordinates,
and edge cases following US2 requirements for robust error handling.
"""

from .types import Location


class ValidationError(Exception):
    """Raised when validation fails for user input."""


def validate_non_empty_addresses(start: str, destination: str) -> None:
    """Validate that both addresses are non-empty.

    Args:
        start: Start address string
        destination: Destination address string

    Raises:
        ValidationError: If either address is empty or only whitespace

    Example:
        >>> validate_non_empty_addresses("Times Square", "Central Park")
        >>> validate_non_empty_addresses("", "Central Park")
        Traceback (most recent call last):
        ...
        ValidationError: Start address cannot be empty
    """
    if not start or not start.strip():
        raise ValidationError(
            "Start address cannot be empty. "
            "Please enter a valid location (e.g., 'Times Square, New York')"
        )
    if not destination or not destination.strip():
        raise ValidationError(
            "Destination address cannot be empty. "
            "Please enter a valid location (e.g., 'Central Park, New York')"
        )


def validate_coordinates(latitude: float, longitude: float) -> None:
    """Validate latitude and longitude are within valid ranges.

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees

    Raises:
        ValidationError: If coordinates are out of valid range

    Example:
        >>> validate_coordinates(40.7128, -74.0060)  # NYC
        >>> validate_coordinates(91.0, 0.0)
        Traceback (most recent call last):
        ...
        ValidationError: Latitude must be between -90 and 90 degrees
    """
    if not -90 <= latitude <= 90:
        raise ValidationError(f"Latitude must be between -90 and 90 degrees. Got: {latitude}")
    if not -180 <= longitude <= 180:
        raise ValidationError(f"Longitude must be between -180 and 180 degrees. Got: {longitude}")


def validate_same_location(start: Location, destination: Location) -> None:
    """Validate that start and destination are different locations.

    Uses a tolerance of 0.0001 degrees (~11 meters) to account for
    geocoding precision differences.

    Args:
        start: Starting location
        destination: Destination location

    Raises:
        ValidationError: If locations are the same or within tolerance

    Example:
        >>> start = Location("Times Square", 40.758896, -73.985130)
        >>> dest = Location("Central Park", 40.785091, -73.968285)
        >>> validate_same_location(start, dest)
        >>> validate_same_location(start, start)
        Traceback (most recent call last):
        ...
        ValidationError: Start and destination are the same location
    """
    # Use tolerance of 0.0001 degrees (~11 meters)
    tolerance = 0.0001

    lat_diff = abs(start.latitude - destination.latitude)
    lng_diff = abs(start.longitude - destination.longitude)

    if lat_diff < tolerance and lng_diff < tolerance:
        raise ValidationError(
            f"Start and destination are the same location: {start.address}. "
            "Please enter two different locations to calculate a route."
        )
