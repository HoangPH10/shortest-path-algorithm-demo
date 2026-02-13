"""Tests for error handling scenarios in services and main workflow.

This module tests US2 requirements for robust error handling and user-friendly
error messages.
"""

import unittest
from unittest.mock import MagicMock, patch

from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import requests

from src.services.geocoding import APIError, InvalidLocationError, geocode_address
from src.services.routing import NoRouteError, get_route_graph
from src.utils.types import Location
from src.utils.validators import ValidationError, validate_same_location


class TestGeocodingErrorHandling(unittest.TestCase):
    """Test error handling in geocoding service."""

    @patch('src.services.geocoding.Nominatim')
    def test_empty_results_raises_invalid_location_error(self, mock_nominatim_class) -> None:
        """Test that empty geocoding results raise InvalidLocationError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.return_value = None
        mock_nominatim_class.return_value = mock_geolocator

        with self.assertRaises(InvalidLocationError) as context:
            geocode_address("Nonexistent Place XYZ123")

        self.assertIn("not found", str(context.exception).lower())
        self.assertIn("valid location", str(context.exception).lower())

    @patch('src.services.geocoding.Nominatim')
    def test_api_timeout_raises_api_error(self, mock_nominatim_class) -> None:
        """Test that API timeout raises APIError with clear message."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.side_effect = GeocoderTimedOut("Request timeout")
        mock_nominatim_class.return_value = mock_geolocator

        with self.assertRaises(APIError) as context:
            geocode_address("Times Square, New York")

        self.assertIn("timed out", str(context.exception).lower())
        self.assertIn("10 seconds", str(context.exception))

    @patch('src.services.geocoding.Nominatim')
    def test_api_error_raises_api_error(self, mock_nominatim_class) -> None:
        """Test that API errors raise APIError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.side_effect = GeocoderServiceError("Service unavailable")
        mock_nominatim_class.return_value = mock_geolocator

        with self.assertRaises(APIError) as context:
            geocode_address("Times Square, New York")

        error_msg = str(context.exception).lower()
        self.assertIn("nominatim", error_msg)
        self.assertIn("service", error_msg)

    @patch('src.services.geocoding.Nominatim')
    def test_transport_error_raises_api_error(self, mock_nominatim_class) -> None:
        """Test that transport/network errors raise APIError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.side_effect = Exception("Network connection failed")
        mock_nominatim_class.return_value = mock_geolocator

        with self.assertRaises(APIError) as context:
            geocode_address("Times Square, New York")

        self.assertIn("connection", str(context.exception).lower())


class TestRoutingErrorHandling(unittest.TestCase):
    """Test error handling in routing service."""

    @patch('src.services.routing.requests.get')
    def test_empty_directions_raises_no_route_error(self, mock_get) -> None:
        """Test that empty directions results raise NoRouteError."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "NoRoute",
            "routes": []
        }
        mock_get.return_value = mock_response

        start = Location("Honolulu, HI", 21.3099, -157.8581)
        dest = Location("Tokyo, Japan", 35.6762, 139.6503)

        with self.assertRaises(NoRouteError) as context:
            get_route_graph(start, dest)

        self.assertIn("no route found", str(context.exception).lower())
        self.assertIn(start.address, str(context.exception))
        self.assertIn(dest.address, str(context.exception))

    @patch('src.services.routing.requests.get')
    def test_directions_api_error_raises_no_route_error(self, mock_get) -> None:
        """Test that API errors are wrapped in NoRouteError."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        start = Location("Point A", 0.0, 0.0)
        dest = Location("Point B", 1.0, 1.0)

        with self.assertRaises(NoRouteError):
            get_route_graph(start, dest)

    @patch('src.services.routing.requests.get')
    def test_directions_timeout_raises_no_route_error(self, mock_get) -> None:
        """Test that timeouts are wrapped in NoRouteError."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        start = Location("Point A", 0.0, 0.0)
        dest = Location("Point B", 1.0, 1.0)

        with self.assertRaises(NoRouteError) as context:
            get_route_graph(start, dest)

        self.assertIn("timed out", str(context.exception).lower())


class TestSameLocationValidation(unittest.TestCase):
    """Test validation of same location edge case."""

    def test_same_coordinates_raises_validation_error(self) -> None:
        """Test that identical coordinates raise ValidationError."""
        location = Location("Times Square", 40.758896, -73.985130)

        with self.assertRaises(ValidationError) as context:
            validate_same_location(location, location)

        self.assertIn("same location", str(context.exception).lower())
        self.assertIn("different", str(context.exception).lower())

    def test_very_close_coordinates_detected(self) -> None:
        """Test that coordinates within tolerance are detected as same."""
        start = Location("Location A", 40.758896, -73.985130)
        # 0.00005 degrees difference (~5.5 meters)
        dest = Location("Location B", 40.758900, -73.985135)

        with self.assertRaises(ValidationError):
            validate_same_location(start, dest)

    def test_sufficient_distance_passes(self) -> None:
        """Test that sufficiently distant locations pass validation."""
        start = Location("Times Square", 40.758896, -73.985130)
        dest = Location("Central Park", 40.785091, -73.968285)

        # Should not raise any exception
        try:
            validate_same_location(start, dest)
        except ValidationError:
            self.fail("Different locations should not raise ValidationError")


class TestErrorMessageQuality(unittest.TestCase):
    """Test that error messages are user-friendly and actionable."""

    @patch('src.services.geocoding.Nominatim')
    def test_invalid_location_suggests_action(self, mock_nominatim_class) -> None:
        """Test that InvalidLocationError suggests what to do."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.return_value = None
        mock_nominatim_class.return_value = mock_geolocator

        with self.assertRaises(InvalidLocationError) as context:
            geocode_address("asdfghjkl")

        error_msg = str(context.exception).lower()
        # Should contain address and suggestion
        self.assertIn("not found", error_msg)
        self.assertIn("valid", error_msg)

    @patch('src.services.routing.requests.get')
    def test_no_route_error_includes_addresses(self, mock_get) -> None:
        """Test that NoRouteError includes both addresses for clarity."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "NoRoute",
            "routes": []
        }
        mock_get.return_value = mock_response

        start = Location("Point A", 0.0, 0.0)
        dest = Location("Point B", 90.0, 180.0)

        with self.assertRaises(NoRouteError) as context:
            get_route_graph(start, dest)

        error_msg = str(context.exception)
        self.assertIn("Point A", error_msg)
        self.assertIn("Point B", error_msg)

    def test_same_location_error_suggests_different_locations(self) -> None:
        """Test that same location error suggests entering different locations."""
        location = Location("Same Place", 40.0, -74.0)

        with self.assertRaises(ValidationError) as context:
            validate_same_location(location, location)

        error_msg = str(context.exception).lower()
        self.assertIn("different", error_msg)
        self.assertIn("location", error_msg)


if __name__ == "__main__":
    unittest.main()
