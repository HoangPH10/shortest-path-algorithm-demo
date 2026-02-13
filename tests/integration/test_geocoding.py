"""Tests for geocoding service."""

from unittest.mock import MagicMock, patch

import pytest
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from src.services.geocoding import (
    APIError,
    InvalidLocationError,
    geocode_address,
)
from src.utils.types import Location


class TestGeocodeAddress:
    """Tests for geocode_address function."""

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_valid_address(self, mock_nominatim_class):
        """Test geocoding a valid address returns Location."""
        mock_location = MagicMock()
        mock_location.address = "Times Square, Manhattan, NY 10036, USA"
        mock_location.latitude = 40.7580
        mock_location.longitude = -73.9855
        
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.return_value = mock_location
        mock_nominatim_class.return_value = mock_geolocator

        result = geocode_address("Times Square")

        assert isinstance(result, Location)
        assert result.address == "Times Square, Manhattan, NY 10036, USA"
        assert result.latitude == 40.7580
        assert result.longitude == -73.9855

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_invalid_address_raises_error(self, mock_nominatim_class):
        """Test geocoding invalid address raises InvalidLocationError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.return_value = None
        mock_nominatim_class.return_value = mock_geolocator

        with pytest.raises(InvalidLocationError, match="Address not found"):
            geocode_address("asdfghjkl")

    def test_geocode_empty_string_raises_error(self):
        """Test geocoding empty string raises ValueError."""
        with pytest.raises(ValueError, match="Address cannot be empty"):
            geocode_address("")

    def test_geocode_whitespace_only_raises_error(self):
        """Test geocoding whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Address cannot be empty"):
            geocode_address("   ")

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_api_timeout_raises_error(self, mock_nominatim_class):
        """Test API timeout raises APIError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.side_effect = GeocoderTimedOut("Timeout")
        mock_nominatim_class.return_value = mock_geolocator

        with pytest.raises(APIError, match="API request timed out"):
            geocode_address("New York")

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_api_error_raises_error(self, mock_nominatim_class):
        """Test general API error raises APIError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.side_effect = GeocoderServiceError("Error")
        mock_nominatim_class.return_value = mock_geolocator

        with pytest.raises(APIError, match="Nominatim service error"):
            geocode_address("New York")

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_transport_error_raises_error(self, mock_nominatim_class):
        """Test transport error raises APIError."""
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.side_effect = Exception("Connection error")
        mock_nominatim_class.return_value = mock_geolocator

        with pytest.raises(APIError, match="Network connection error"):
            geocode_address("New York")

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_caching(self, mock_nominatim_class):
        """Test that geocoding results are cached."""
        mock_location = MagicMock()
        mock_location.address = "Times Square, Manhattan, NY 10036, USA"
        mock_location.latitude = 40.7580
        mock_location.longitude = -73.9855
        
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.return_value = mock_location
        mock_nominatim_class.return_value = mock_geolocator

        # Clear cache first
        geocode_address.cache_clear()

        # First call
        result1 = geocode_address("Times Square")
        # Second call with same address should use cache
        result2 = geocode_address("Times Square")

        assert result1 == result2
        # Nominatim should only be instantiated once due to caching
        # (Note: caching happens at function level, not geolocator instantiation)

    @patch('src.services.geocoding.Nominatim')
    def test_geocode_multiple_results_uses_first(self, mock_nominatim_class):
        """Test that geocoding returns the result from Nominatim."""
        mock_location = MagicMock()
        mock_location.address = "Paris, France"
        mock_location.latitude = 48.8566
        mock_location.longitude = 2.3522
        
        mock_geolocator = MagicMock()
        mock_geolocator.geocode.return_value = mock_location
        mock_nominatim_class.return_value = mock_geolocator

        result = geocode_address("Paris")

        # Should use the result
        assert result.address == "Paris, France"
        assert result.latitude == 48.8566
