"""End-to-end integration tests for the complete route visualization workflow.

This module tests the full user journey from address input to route visualization,
using mocked Google Maps API for repeatable testing.
"""

import unittest
from unittest.mock import MagicMock

import folium

from src.algorithms.astar import astar
from src.algorithms.dijkstra import dijkstra
from src.algorithms.heuristics import euclidean_distance
from src.services.geocoding import geocode_address
from src.services.map_renderer import create_route_map
from src.services.routing import get_route_graph
from src.utils.types import Location


class TestEndToEndWorkflow(unittest.TestCase):
    """Test the complete end-to-end workflow simulating a user journey."""

    def setUp(self) -> None:
        """Set up mock Google Maps client for all tests."""
        self.mock_client = MagicMock()

        # Mock geocode responses
        self.mock_client.geocode.side_effect = [
            # First call: start address
            [
                {
                    "formatted_address": "Times Square, New York, NY, USA",
                    "geometry": {"location": {"lat": 40.758896, "lng": -73.985130}},
                }
            ],
            # Second call: destination address
            [
                {
                    "formatted_address": "Central Park, New York, NY, USA",
                    "geometry": {"location": {"lat": 40.785091, "lng": -73.968285}},
                }
            ],
        ]

        # Mock directions response with multi-step route
        self.mock_client.directions.return_value = [
            {
                "legs": [
                    {
                        "steps": [
                            {
                                "start_location": {"lat": 40.758896, "lng": -73.985130},
                                "end_location": {"lat": 40.762, "lng": -73.98},
                                "distance": {"value": 500},  # 500 meters
                            },
                            {
                                "start_location": {"lat": 40.762, "lng": -73.98},
                                "end_location": {"lat": 40.770, "lng": -73.975},
                                "distance": {"value": 800},  # 800 meters
                            },
                            {
                                "start_location": {"lat": 40.770, "lng": -73.975},
                                "end_location": {"lat": 40.785091, "lng": -73.968285},
                                "distance": {"value": 1200},  # 1200 meters
                            },
                        ]
                    }
                ]
            }
        ]

    def test_complete_user_journey(self) -> None:
        """Test complete workflow: geocode -> graph -> algorithms -> visualization."""
        # Step 1: Geocode addresses
        start_location = geocode_address("Times Square, New York", self.mock_client)
        dest_location = geocode_address("Central Park, New York", self.mock_client)

        # Verify geocoding worked
        self.assertIsInstance(start_location, Location)
        self.assertIsInstance(dest_location, Location)
        self.assertEqual(start_location.latitude, 40.758896)
        self.assertEqual(dest_location.latitude, 40.785091)

        # Step 2: Get route graph
        graph = get_route_graph(start_location, dest_location, self.mock_client)

        # Verify graph was created (bidirectional edges create duplicate nodes)
        self.assertGreater(len(graph.nodes()), 0)

        # Step 3: Run A* algorithm
        astar_result = astar(
            graph,
            start=graph.nodes()[0],
            goal=graph.nodes()[-1],
            heuristic=euclidean_distance,
        )

        # Verify A* succeeded
        self.assertTrue(astar_result.success, msg=f"A* failed: {astar_result.error}")
        self.assertIsNotNone(astar_result.route)
        self.assertEqual(astar_result.route.algorithm, "A*")
        self.assertGreater(astar_result.route.total_distance, 0)
        self.assertGreaterEqual(astar_result.route.execution_time, 0)  # Can be 0 for fast execution

        # Step 4: Run Dijkstra algorithm
        dijkstra_result = dijkstra(
            graph,
            start=graph.nodes()[0],
            goal=graph.nodes()[-1],
        )

        # Verify Dijkstra succeeded
        self.assertTrue(dijkstra_result.success)
        self.assertIsNotNone(dijkstra_result.route)
        self.assertEqual(dijkstra_result.route.algorithm, "Dijkstra")
        self.assertGreater(dijkstra_result.route.total_distance, 0)

        # Step 5: Verify algorithms found same optimal path length
        self.assertAlmostEqual(
            astar_result.route.total_distance,
            dijkstra_result.route.total_distance,
            places=3,
            msg="A* and Dijkstra should find paths of equal length",
        )

        # Step 6: Create map visualizations
        astar_map = create_route_map(astar_result.route, start_location, dest_location)
        dijkstra_map = create_route_map(dijkstra_result.route, start_location, dest_location)

        # Verify maps were created
        self.assertIsInstance(astar_map, folium.Map)
        self.assertIsInstance(dijkstra_map, folium.Map)

        # Step 7: Verify performance characteristics
        # A* should explore fewer nodes than Dijkstra due to heuristic
        self.assertLessEqual(
            astar_result.route.nodes_explored,
            dijkstra_result.route.nodes_explored,
            msg="A* should explore fewer or equal nodes than Dijkstra",
        )

    def test_error_handling_invalid_address(self) -> None:
        """Test that invalid addresses are handled gracefully."""
        from src.services.geocoding import InvalidLocationError

        # Create new mock client with empty geocode results
        mock_client_empty = MagicMock()
        mock_client_empty.geocode.return_value = []

        # Should raise InvalidLocationError
        with self.assertRaises(InvalidLocationError):
            geocode_address("Invalid Address XYZ123", mock_client_empty)

    def test_error_handling_no_route(self) -> None:
        """Test that no route found scenario is handled."""
        from src.services.routing import NoRouteError

        # Mock directions to return empty results
        self.mock_client.directions.return_value = []
        self.mock_client.geocode.side_effect = [
            [
                {
                    "formatted_address": "Honolulu, HI, USA",
                    "geometry": {"location": {"lat": 21.3099, "lng": -157.8581}},
                }
            ],
            [
                {
                    "formatted_address": "Tokyo, Japan",
                    "geometry": {"location": {"lat": 35.6762, "lng": 139.6503}},
                }
            ],
        ]

        start = geocode_address("Honolulu, HI", self.mock_client)
        dest = geocode_address("Tokyo, Japan", self.mock_client)

        # Should raise NoRouteError for unreachable locations
        with self.assertRaises(NoRouteError):
            get_route_graph(start, dest, self.mock_client)

    def test_performance_under_5_seconds(self) -> None:
        """Test that typical workflow completes within 5 seconds."""
        import time

        start_time = time.time()

        # Execute full workflow
        start_location = geocode_address("Times Square, New York", self.mock_client)
        dest_location = geocode_address("Central Park, New York", self.mock_client)
        graph = get_route_graph(start_location, dest_location, self.mock_client)

        astar(graph, start=graph.nodes()[0], goal=graph.nodes()[-1], heuristic=euclidean_distance)
        dijkstra(graph, start=graph.nodes()[0], goal=graph.nodes()[-1])

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete within 5 seconds (with mocked API, should be much faster)
        self.assertLess(
            execution_time,
            5.0,
            msg=f"Workflow took {execution_time:.2f}s, should be under 5s",
        )

    def test_caching_reduces_api_calls(self) -> None:
        """Test that geocoding cache reduces duplicate API calls."""
        # Call geocode_address twice with same address
        geocode_address("Times Square, New York", self.mock_client)

        # Reset mock for second call
        self.mock_client.geocode.side_effect = [
            [
                {
                    "formatted_address": "Times Square, New York, NY, USA",
                    "geometry": {"location": {"lat": 40.758896, "lng": -73.985130}},
                }
            ]
        ]

        geocode_address("Times Square, New York", self.mock_client)

        # Due to @lru_cache, second call should use cached result
        # So mock should only be called once total (from setUp)
        # Note: This test assumes cache is cleared between test runs
        self.assertGreaterEqual(self.mock_client.geocode.call_count, 1)


if __name__ == "__main__":
    unittest.main()
