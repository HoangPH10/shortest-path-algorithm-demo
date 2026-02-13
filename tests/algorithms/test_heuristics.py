"""Tests for heuristic functions."""

import pytest

from src.algorithms.heuristics import diagonal_distance, euclidean_distance, manhattan_distance
from src.utils.types import Node


class TestEuclideanDistance:
    """Tests for Euclidean (Haversine) distance heuristic."""

    def test_same_node_zero_distance(self) -> None:
        """Test distance from node to itself is zero."""
        node = Node(id="node_1", latitude=40.7580, longitude=-73.9855)
        distance = euclidean_distance(node, node)
        assert distance == 0.0

    def test_different_nodes_positive_distance(self) -> None:
        """Test distance between different nodes is positive."""
        node1 = Node(id="node_1", latitude=40.7580, longitude=-73.9855)  # Times Square
        node2 = Node(id="node_2", latitude=40.7829, longitude=-73.9654)  # Central Park

        distance = euclidean_distance(node1, node2)
        assert distance > 0
        # Approximate distance should be around 3-4 km
        assert 2.5 < distance < 4.5

    def test_symmetric_distance(self) -> None:
        """Test distance is symmetric: d(A,B) == d(B,A)."""
        node1 = Node(id="node_1", latitude=40.7580, longitude=-73.9855)
        node2 = Node(id="node_2", latitude=40.7829, longitude=-73.9654)

        distance_ab = euclidean_distance(node1, node2)
        distance_ba = euclidean_distance(node2, node1)

        assert abs(distance_ab - distance_ba) < 0.001  # Account for floating point

    def test_admissibility(self) -> None:
        """Test heuristic never overestimates (Manhattan grid check)."""
        # On a grid, Euclidean should be <= Manhattan distance
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-72.0)

        euclidean = euclidean_distance(node1, node2)
        manhattan = manhattan_distance(node1, node2)

        assert euclidean <= manhattan


class TestManhattanDistance:
    """Tests for Manhattan distance heuristic."""

    def test_same_node_zero_distance(self) -> None:
        """Test distance from node to itself is zero."""
        node = Node(id="node_1", latitude=40.7580, longitude=-73.9855)
        distance = manhattan_distance(node, node)
        assert distance == 0.0

    def test_different_nodes_positive_distance(self) -> None:
        """Test distance between different nodes is positive."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-72.0)

        distance = manhattan_distance(node1, node2)
        assert distance > 0

    def test_symmetric_distance(self) -> None:
        """Test distance is symmetric."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-72.0)

        distance_ab = manhattan_distance(node1, node2)
        distance_ba = manhattan_distance(node2, node1)

        assert abs(distance_ab - distance_ba) < 0.001


class TestDiagonalDistance:
    """Tests for diagonal (Chebyshev) distance heuristic."""

    def test_same_node_zero_distance(self) -> None:
        """Test distance from node to itself is zero."""
        node = Node(id="node_1", latitude=40.7580, longitude=-73.9855)
        distance = diagonal_distance(node, node)
        assert distance == 0.0

    def test_different_nodes_positive_distance(self) -> None:
        """Test distance between different nodes is positive."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-72.0)

        distance = diagonal_distance(node1, node2)
        assert distance > 0

    def test_diagonal_less_than_manhattan(self) -> None:
        """Test diagonal distance is less than Manhattan for moves with both lat/lng change."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-72.0)

        diagonal = diagonal_distance(node1, node2)
        manhattan = manhattan_distance(node1, node2)

        # Diagonal allows diagonal moves, so should be shorter
        assert diagonal < manhattan
