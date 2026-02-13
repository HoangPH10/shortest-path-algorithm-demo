"""Pytest configuration and shared fixtures."""

from typing import Dict, List, Tuple
from unittest.mock import MagicMock

import pytest

from src.algorithms.graph import Graph
from src.utils.types import Node


@pytest.fixture
def simple_grid_graph() -> Graph:
    """Create a simple 3x3 grid graph for testing.

    Layout (distances are 1.0 between adjacent nodes):

    (0,0)----(0,1)----(0,2)
      |        |        |
    (1,0)----(1,1)----(1,2)
      |        |        |
    (2,0)----(2,1)----(2,2)

    Returns:
        Graph with 9 nodes and bidirectional edges
    """
    graph = Graph()

    # Create 3x3 grid of nodes
    nodes: Dict[Tuple[int, int], Node] = {}
    for row in range(3):
        for col in range(3):
            node = Node(
                id=f"node_{row}_{col}",
                latitude=float(row),
                longitude=float(col),
            )
            nodes[(row, col)] = node
            graph.add_node(node)

    # Add horizontal edges
    for row in range(3):
        for col in range(2):
            graph.add_edge(
                nodes[(row, col)],
                nodes[(row, col + 1)],
                weight=1.0,
                bidirectional=True,
            )

    # Add vertical edges
    for row in range(2):
        for col in range(3):
            graph.add_edge(
                nodes[(row, col)],
                nodes[(row + 1, col)],
                weight=1.0,
                bidirectional=True,
            )

    return graph


@pytest.fixture
def known_shortest_path() -> Tuple[Graph, Node, Node, float]:
    """Create a graph with a known shortest path for correctness testing.

    Graph structure (coordinates chosen so Euclidean heuristic is admissible):

    A --5-- B --3-- C
    |       |       |
    2       4       1
    |       |       |
    D --1-- E --2-- F

    Shortest path A -> F: A -> D -> E -> F (distance = 5)
    Alternative path: A -> B -> E -> F (distance = 12)
    Note: coordinates scaled so euclidean distances match edge weights

    Returns:
        Tuple of (graph, start_node, goal_node, expected_distance)
    """
    graph = Graph()

    # Create nodes with coordinates that allow admissible heuristic
    # Scale coordinates so Euclidean distance ≈ edge weight / 111 km
    scale = 0.01  # Each unit of edge weight = 0.01 degrees

    node_a = Node(id="A", latitude=0.0, longitude=0.0)
    node_b = Node(id="B", latitude=0.0, longitude=5 * scale)
    node_c = Node(id="C", latitude=0.0, longitude=8 * scale)
    node_d = Node(id="D", latitude=-2 * scale, longitude=0.0)
    node_e = Node(id="E", latitude=-2 * scale, longitude=1 * scale)
    node_f = Node(id="F", latitude=-2 * scale, longitude=3 * scale)

    # Add edges (bidirectional)
    graph.add_edge(node_a, node_b, weight=5.0, bidirectional=True)
    graph.add_edge(node_b, node_c, weight=3.0, bidirectional=True)
    graph.add_edge(node_a, node_d, weight=2.0, bidirectional=True)
    graph.add_edge(node_b, node_e, weight=4.0, bidirectional=True)
    graph.add_edge(node_c, node_f, weight=1.0, bidirectional=True)
    graph.add_edge(node_d, node_e, weight=1.0, bidirectional=True)
    graph.add_edge(node_e, node_f, weight=2.0, bidirectional=True)

    expected_distance = 5.0  # A -> D (2) -> E (1) -> F (2)

    return graph, node_a, node_f, expected_distance
