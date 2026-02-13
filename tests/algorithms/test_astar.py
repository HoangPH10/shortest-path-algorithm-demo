"""Tests for A* pathfinding algorithm."""

import pytest

from src.algorithms.astar import astar
from src.algorithms.heuristics import euclidean_distance
from src.utils.types import Node, PathfindingResult


class TestAstarBasic:
    """Basic A* algorithm tests."""

    def test_astar_same_start_goal(self, simple_grid_graph):
        """Test A* with same start and goal returns zero distance."""
        node = Node(id="node_0_0", latitude=0.0, longitude=0.0)

        result = astar(simple_grid_graph, node, node, euclidean_distance)

        assert isinstance(result, PathfindingResult)
        assert result.success is True
        assert result.route is not None
        assert result.route.total_distance == 0.0
        assert result.route.path == [node]
        assert result.route.algorithm == "A*"

    def test_astar_connected_graph_success(self, simple_grid_graph):
        """Test A* finds path in connected graph."""
        start = Node(id="node_0_0", latitude=0.0, longitude=0.0)
        goal = Node(id="node_2_2", latitude=2.0, longitude=2.0)

        result = astar(simple_grid_graph, start, goal, euclidean_distance)

        assert result.success is True
        assert result.route is not None
        assert result.route.path[0] == start
        assert result.route.path[-1] == goal
        assert result.route.total_distance > 0

    def test_astar_disconnected_graph_failure(self):
        """Test A* returns failure for disconnected nodes."""
        from src.algorithms.graph import Graph

        graph = Graph()
        node1 = Node(id="node1", latitude=0.0, longitude=0.0)
        node2 = Node(id="node2", latitude=10.0, longitude=10.0)

        # Add nodes but no edges (disconnected)
        graph.add_node(node1)
        graph.add_node(node2)

        result = astar(graph, node1, node2, euclidean_distance)

        assert result.success is False
        assert result.route is None
        assert result.error is not None
        assert "No path found" in result.error


class TestAstarCorrectness:
    """Tests verifying A* produces optimal paths."""

    def test_astar_optimal_path(self, known_shortest_path):
        """Test A* finds the known shortest path."""
        graph, start, goal, expected_distance = known_shortest_path

        result = astar(graph, start, goal, euclidean_distance)

        assert result.success is True
        assert result.route is not None
        # Allow small floating point tolerance
        assert abs(result.route.total_distance - expected_distance) < 0.01

    def test_astar_path_continuity(self, simple_grid_graph):
        """Test A* returns a continuous path (each node connects to next)."""
        start = Node(id="node_0_0", latitude=0.0, longitude=0.0)
        goal = Node(id="node_2_2", latitude=2.0, longitude=2.0)

        result = astar(simple_grid_graph, start, goal, euclidean_distance)

        assert result.success is True
        path = result.route.path

        # Verify each consecutive pair is connected by an edge
        for i in range(len(path) - 1):
            neighbors = simple_grid_graph.neighbors(path[i])
            neighbor_nodes = [n for n, _ in neighbors]
            assert path[i + 1] in neighbor_nodes


class TestAstarEdgeCases:
    """Edge case tests for A* algorithm."""

    def test_astar_invalid_start_node(self, simple_grid_graph):
        """Test A* with start node not in graph."""
        invalid_node = Node(id="invalid", latitude=99.0, longitude=99.0)
        goal = Node(id="node_0_0", latitude=0.0, longitude=0.0)

        result = astar(simple_grid_graph, invalid_node, goal, euclidean_distance)

        assert result.success is False
        assert result.error is not None

    def test_astar_invalid_goal_node(self, simple_grid_graph):
        """Test A* with goal node not in graph."""
        start = Node(id="node_0_0", latitude=0.0, longitude=0.0)
        invalid_node = Node(id="invalid", latitude=99.0, longitude=99.0)

        result = astar(simple_grid_graph, start, invalid_node, euclidean_distance)

        assert result.success is False
        assert result.error is not None

    def test_astar_none_heuristic(self, simple_grid_graph):
        """Test A* raises error with None heuristic."""
        start = Node(id="node_0_0", latitude=0.0, longitude=0.0)
        goal = Node(id="node_1_1", latitude=1.0, longitude=1.0)

        with pytest.raises(TypeError):
            astar(simple_grid_graph, start, goal, None)


class TestAstarPerformance:
    """Performance-related tests for A*."""

    def test_astar_tracks_nodes_explored(self, simple_grid_graph):
        """Test A* tracks number of nodes explored."""
        start = Node(id="node_0_0", latitude=0.0, longitude=0.0)
        goal = Node(id="node_2_2", latitude=2.0, longitude=2.0)

        result = astar(simple_grid_graph, start, goal, euclidean_distance)

        assert result.success is True
        assert result.route.nodes_explored > 0
        assert result.route.nodes_explored <= len(simple_grid_graph.nodes())

    def test_astar_tracks_execution_time(self, simple_grid_graph):
        """Test A* tracks execution time in milliseconds."""
        start = Node(id="node_0_0", latitude=0.0, longitude=0.0)
        goal = Node(id="node_2_2", latitude=2.0, longitude=2.0)

        result = astar(simple_grid_graph, start, goal, euclidean_distance)

        assert result.success is True
        assert result.route.execution_time >= 0
        # Should complete very quickly on small graph
        assert result.route.execution_time < 1000  # Less than 1 second
