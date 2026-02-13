"""Unit tests for input validation functions.

This module tests validation helpers for addresses, coordinates,
and edge case detection following US2 requirements.
"""

import unittest

from src.utils.validators import (
    ValidationError,
    validate_coordinates,
    validate_non_empty_addresses,
    validate_same_location,
)


class TestValidateNonEmptyAddresses(unittest.TestCase):
    """Test validate_non_empty_addresses function."""

    def test_valid_addresses(self) -> None:
        """Test that valid addresses pass validation."""
        # Should not raise any exception
        try:
            validate_non_empty_addresses("Times Square, New York", "Central Park, New York")
        except ValidationError:
            self.fail("Valid addresses should not raise ValidationError")

    def test_empty_start_address_raises_error(self) -> None:
        """Test that empty start address raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_non_empty_addresses("", "Central Park, New York")

        self.assertIn("Start address", str(context.exception))
        self.assertIn("cannot be empty", str(context.exception))

    def test_empty_destination_address_raises_error(self) -> None:
        """Test that empty destination address raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_non_empty_addresses("Times Square, New York", "")

        self.assertIn("Destination address", str(context.exception))
        self.assertIn("cannot be empty", str(context.exception))

    def test_whitespace_only_start_address_raises_error(self) -> None:
        """Test that whitespace-only start address raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_non_empty_addresses("   ", "Central Park, New York")

        self.assertIn("Start address", str(context.exception))

    def test_whitespace_only_destination_raises_error(self) -> None:
        """Test that whitespace-only destination raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_non_empty_addresses("Times Square, New York", "  \t\n  ")

        self.assertIn("Destination address", str(context.exception))

    def test_both_addresses_empty_raises_error(self) -> None:
        """Test that both addresses empty raises ValidationError."""
        with self.assertRaises(ValidationError):
            validate_non_empty_addresses("", "")


class TestValidateCoordinates(unittest.TestCase):
    """Test validate_coordinates function."""

    def test_valid_coordinates(self) -> None:
        """Test that valid coordinates pass validation."""
        # New York City coordinates
        try:
            validate_coordinates(40.7128, -74.0060)
        except ValidationError:
            self.fail("Valid coordinates should not raise ValidationError")

    def test_valid_boundary_coordinates(self) -> None:
        """Test coordinates at valid boundaries."""
        # North Pole
        validate_coordinates(90.0, 0.0)
        # South Pole
        validate_coordinates(-90.0, 0.0)
        # International Date Line
        validate_coordinates(0.0, 180.0)
        validate_coordinates(0.0, -180.0)

    def test_latitude_too_high_raises_error(self) -> None:
        """Test that latitude > 90 raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_coordinates(91.0, 0.0)

        self.assertIn("Latitude", str(context.exception))
        self.assertIn("90", str(context.exception))

    def test_latitude_too_low_raises_error(self) -> None:
        """Test that latitude < -90 raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_coordinates(-91.0, 0.0)

        self.assertIn("Latitude", str(context.exception))
        self.assertIn("-90", str(context.exception))

    def test_longitude_too_high_raises_error(self) -> None:
        """Test that longitude > 180 raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_coordinates(0.0, 181.0)

        self.assertIn("Longitude", str(context.exception))
        self.assertIn("180", str(context.exception))

    def test_longitude_too_low_raises_error(self) -> None:
        """Test that longitude < -180 raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            validate_coordinates(0.0, -181.0)

        self.assertIn("Longitude", str(context.exception))
        self.assertIn("-180", str(context.exception))

    def test_both_coordinates_invalid_raises_error(self) -> None:
        """Test that both invalid coordinates raises ValidationError."""
        with self.assertRaises(ValidationError):
            validate_coordinates(100.0, 200.0)


class TestValidateSameLocation(unittest.TestCase):
    """Test validate_same_location function."""

    def test_different_locations_pass(self) -> None:
        """Test that different locations pass validation."""
        from src.utils.types import Location

        start = Location("Times Square", 40.758896, -73.985130)
        dest = Location("Central Park", 40.785091, -73.968285)

        try:
            validate_same_location(start, dest)
        except ValidationError:
            self.fail("Different locations should not raise ValidationError")

    def test_same_exact_coordinates_raises_error(self) -> None:
        """Test that identical coordinates raise ValidationError."""
        from src.utils.types import Location

        start = Location("Location A", 40.758896, -73.985130)
        dest = Location("Location A", 40.758896, -73.985130)

        with self.assertRaises(ValidationError) as context:
            validate_same_location(start, dest)

        self.assertIn("same location", str(context.exception).lower())

    def test_coordinates_within_tolerance_raises_error(self) -> None:
        """Test that coordinates within 0.0001 degrees raise ValidationError."""
        from src.utils.types import Location

        # Coordinates differ by 0.00005 degrees (within tolerance)
        start = Location("Location A", 40.758896, -73.985130)
        dest = Location("Location B", 40.758900, -73.985135)  # Very close

        with self.assertRaises(ValidationError) as context:
            validate_same_location(start, dest)

        self.assertIn("same location", str(context.exception).lower())

    def test_coordinates_outside_tolerance_pass(self) -> None:
        """Test that coordinates > 0.0001 degrees apart pass validation."""
        from src.utils.types import Location

        # Coordinates differ by 0.001 degrees (outside tolerance)
        start = Location("Location A", 40.758896, -73.985130)
        dest = Location("Location B", 40.759896, -73.986130)

        try:
            validate_same_location(start, dest)
        except ValidationError:
            self.fail("Locations outside tolerance should not raise ValidationError")


if __name__ == "__main__":
    unittest.main()
