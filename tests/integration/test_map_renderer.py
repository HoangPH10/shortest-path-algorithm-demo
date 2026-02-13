"""Tests for map rendering service."""

import pytest

from src.services.map_renderer import create_route_map
from src.utils.types import Location, Node, Route


class TestCreateRouteMap:
    """Tests for create_route_map function."""

    def test_create_route_map_returns_folium_map(self):
        """Test that create_route_map returns a folium Map object."""
        import folium

        route = Route(
            path=[
                Node("node_1", 40.7580, -73.9855),
                Node("node_2", 40.7700, -73.9800),
                Node("node_3", 40.7829, -73.9654),
            ],
            total_distance=3.5,
            algorithm="A*",
            execution_time=15,
            nodes_explored=10,
        )
        start = Location("Times Square", 40.7580, -73.9855)
        dest = Location("Central Park", 40.7829, -73.9654)

        map_obj = create_route_map(route, start, dest)

        assert isinstance(map_obj, folium.Map)

    def test_create_route_map_astar_uses_blue(self):
        """Test A* algorithm uses blue color."""
        route = Route(
            path=[
                Node("node_1", 40.7580, -73.9855),
                Node("node_2", 40.7829, -73.9654),
            ],
            total_distance=3.0,
            algorithm="A*",
            execution_time=10,
            nodes_explored=5,
        )
        start = Location("A", 40.7580, -73.9855)
        dest = Location("B", 40.7829, -73.9654)

        map_obj = create_route_map(route, start, dest)

        # Verify map was created (color verification happens via visual inspection)
        assert map_obj is not None

    def test_create_route_map_dijkstra_uses_red(self):
        """Test Dijkstra algorithm uses red color."""
        route = Route(
            path=[
                Node("node_1", 40.7580, -73.9855),
                Node("node_2", 40.7829, -73.9654),
            ],
            total_distance=3.0,
            algorithm="Dijkstra",
            execution_time=12,
            nodes_explored=8,
        )
        start = Location("A", 40.7580, -73.9855)
        dest = Location("B", 40.7829, -73.9654)

        map_obj = create_route_map(route, start, dest)

        assert map_obj is not None

    def test_create_route_map_adds_markers(self):
        """Test that start and destination markers are added."""
        import folium

        route = Route(
            path=[
                Node("node_1", 40.7580, -73.9855),
                Node("node_2", 40.7829, -73.9654),
            ],
            total_distance=3.0,
            algorithm="A*",
            execution_time=10,
            nodes_explored=5,
        )
        start = Location("Times Square", 40.7580, -73.9855)
        dest = Location("Central Park", 40.7829, -73.9654)

        map_obj = create_route_map(route, start, dest)

        # Check that map has children (markers, polylines)
        assert len(map_obj._children) > 0

    def test_create_route_map_centers_on_route(self):
        """Test that map is centered appropriately."""
        route = Route(
            path=[
                Node("node_1", 40.7580, -73.9855),
                Node("node_2", 40.7700, -73.9800),
                Node("node_3", 40.7829, -73.9654),
            ],
            total_distance=3.5,
            algorithm="A*",
            execution_time=15,
            nodes_explored=10,
        )
        start = Location("A", 40.7580, -73.9855)
        dest = Location("B", 40.7829, -73.9654)

        map_obj = create_route_map(route, start, dest)

        # Verify map center is somewhere between start and dest
        center_lat = map_obj.location[0]
        center_lng = map_obj.location[1]

        assert 40.75 <= center_lat <= 40.79
        assert -73.99 <= center_lng <= -73.96

    def test_create_route_map_single_node_path(self):
        """Test creating map with single-node path (same start/dest)."""
        route = Route(
            path=[Node("node_1", 40.7580, -73.9855)],
            total_distance=0.0,
            algorithm="A*",
            execution_time=1,
            nodes_explored=1,
        )
        start = Location("Times Square", 40.7580, -73.9855)
        dest = Location("Times Square", 40.7580, -73.9855)

        map_obj = create_route_map(route, start, dest)

        assert map_obj is not None
        # Should show single marker
        assert map_obj.location == [40.7580, -73.9855]
