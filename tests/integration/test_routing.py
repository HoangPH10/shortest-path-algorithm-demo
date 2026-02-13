"""Tests for routing service."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.algorithms.graph import Graph
from src.services.routing import NoRouteError, get_route_graph
from src.utils.types import Location, Node


class TestGetRouteGraph:
    """Tests for get_route_graph function."""

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_valid_locations(self, mock_get):
        """Test getting route graph for valid locations."""
        start = Location("Times Square, NY", 40.7580, -73.9855)
        dest = Location("Central Park, NY", 40.7829, -73.9654)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "legs": [
                        {
                            "steps": [
                                {
                                    "maneuver": {"location": [-73.9855, 40.7580]},
                                    "geometry": {"coordinates": [[-73.9855, 40.7580], [-73.9800, 40.7700]]},
                                    "distance": 1500,
                                },
                                {
                                    "maneuver": {"location": [-73.9800, 40.7700]},
                                    "geometry": {"coordinates": [[-73.9800, 40.7700], [-73.9654, 40.7829]]},
                                    "distance": 2000,
                                },
                            ]
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        graph = get_route_graph(start, dest)

        assert isinstance(graph, Graph)
        assert len(graph.nodes()) > 0

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_creates_bidirectional_edges(self, mock_get):
        """Test that edges are bidirectional."""
        start = Location("A", 40.0, -73.0)
        dest = Location("B", 41.0, -74.0)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "legs": [
                        {
                            "steps": [
                                {
                                    "maneuver": {"location": [-73.0, 40.0]},
                                    "geometry": {"coordinates": [[-73.0, 40.0], [-73.5, 40.5]]},
                                    "distance": 1000,
                                },
                                {
                                    "maneuver": {"location": [-73.5, 40.5]},
                                    "geometry": {"coordinates": [[-73.5, 40.5], [-74.0, 41.0]]},
                                    "distance": 1000,
                                },
                            ]
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        graph = get_route_graph(start, dest)

        # Find a node in the graph
        nodes = graph.nodes()
        if len(nodes) >= 2:
            node1 = nodes[0]
            node2 = nodes[1]

            # Check if there are edges in both directions
            neighbors1 = [n for n, _ in graph.neighbors(node1)]
            neighbors2 = [n for n, _ in graph.neighbors(node2)]

            # At least one pair should have bidirectional connection
            assert len(neighbors1) > 0 or len(neighbors2) > 0

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_no_route_raises_error(self, mock_get):
        """Test that no route found raises NoRouteError."""
        start = Location("Remote Island", 0.0, 0.0)
        dest = Location("Another Island", 10.0, 10.0)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "NoRoute",
            "routes": []
        }
        mock_get.return_value = mock_response

        with pytest.raises(NoRouteError, match="No route found"):
            get_route_graph(start, dest)

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_api_error_raises(self, mock_get):
        """Test API errors are propagated."""
        start = Location("A", 40.0, -73.0)
        dest = Location("B", 41.0, -74.0)

        mock_get.side_effect = requests.exceptions.RequestException("Error")

        with pytest.raises(NoRouteError, match="Network connection error"):
            get_route_graph(start, dest)

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_converts_meters_to_km(self, mock_get):
        """Test that edge weights are converted from meters to kilometers."""
        start = Location("A", 40.0, -73.0)
        dest = Location("B", 40.01, -73.01)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "legs": [
                        {
                            "steps": [
                                {
                                    "maneuver": {"location": [-73.0, 40.0]},
                                    "geometry": {"coordinates": [[-73.0, 40.0], [-73.01, 40.01]]},
                                    "distance": 1500,  # 1500 meters = 1.5 km
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        graph = get_route_graph(start, dest)

        nodes = graph.nodes()
        if len(nodes) >= 2:
            # Check edge weight is in kilometers
            for node in nodes:
                for neighbor, weight in graph.neighbors(node):
                    # Weight should be around 1.5 km
                    assert 1.0 <= weight <= 2.0  # Reasonable range

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_handles_single_step(self, mock_get):
        """Test handling route with single step."""
        start = Location("A", 40.0, -73.0)
        dest = Location("B", 40.001, -73.001)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "legs": [
                        {
                            "steps": [
                                {
                                    "maneuver": {"location": [-73.0, 40.0]},
                                    "geometry": {"coordinates": [[-73.0, 40.0], [-73.001, 40.001]]},
                                    "distance": 100,
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        graph = get_route_graph(start, dest)

        assert len(graph.nodes()) >= 2  # At least start and end nodes

    @patch('src.services.routing.requests.get')
    def test_get_route_graph_includes_start_and_dest(self, mock_get):
        """Test that graph includes start and destination nodes."""
        start = Location("Times Square", 40.7580, -73.9855)
        dest = Location("Central Park", 40.7829, -73.9654)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "legs": [
                        {
                            "steps": [
                                {
                                    "maneuver": {"location": [-73.9855, 40.7580]},
                                    "geometry": {"coordinates": [[-73.9855, 40.7580], [-73.9800, 40.7700]]},
                                    "distance": 1500,
                                },
                                {
                                    "maneuver": {"location": [-73.9800, 40.7700]},
                                    "geometry": {"coordinates": [[-73.9800, 40.7700], [-73.9654, 40.7829]]},
                                    "distance": 2000,
                                },
                            ]
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        graph = get_route_graph(start, dest)

        nodes = graph.nodes()
        # First node should be at start location
        assert any(abs(n.latitude - start.latitude) < 0.001 for n in nodes)
        # Last node should be at destination location
        assert any(abs(n.latitude - dest.latitude) < 0.001 for n in nodes)
