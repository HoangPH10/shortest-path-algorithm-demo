"""Graph data structures for pathfinding algorithms."""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.utils.types import Node


@dataclass
class Edge:
    """Represents a directed edge in a graph.

    Attributes:
        from_node: Starting node
        to_node: Ending node
        weight: Edge weight (must be positive)
    """

    from_node: Node
    to_node: Node
    weight: float

    def __post_init__(self) -> None:
        """Validate edge weight is positive."""
        if self.weight <= 0:
            raise ValueError(f"Edge weight must be positive, got {self.weight}")


class Graph:
    """Adjacency list graph implementation for pathfinding.

    Stores nodes and weighted edges. Supports both directed and
    bidirectional edges.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._adjacency: Dict[Node, List[Tuple[Node, float]]] = {}

    def add_node(self, node: Node) -> None:
        """Add a node to the graph.

        Args:
            node: Node to add
        """
        if node not in self._adjacency:
            self._adjacency[node] = []

    def add_edge(
        self, from_node: Node, to_node: Node, weight: float, bidirectional: bool = False
    ) -> None:
        """Add an edge between two nodes.

        Automatically adds nodes if they don't exist.

        Args:
            from_node: Starting node
            to_node: Ending node
            weight: Edge weight (must be positive)
            bidirectional: If True, adds edge in both directions

        Raises:
            ValueError: If weight is not positive
        """
        if weight <= 0:
            raise ValueError(f"Edge weight must be positive, got {weight}")

        # Ensure both nodes exist
        self.add_node(from_node)
        self.add_node(to_node)

        # Add forward edge
        self._adjacency[from_node].append((to_node, weight))

        # Add reverse edge if bidirectional
        if bidirectional:
            self._adjacency[to_node].append((from_node, weight))

    def neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        """Get all neighbors of a node with edge weights.

        Args:
            node: Node to query

        Returns:
            List of (neighbor_node, edge_weight) tuples
        """
        return self._adjacency.get(node, [])

    def nodes(self) -> List[Node]:
        """Get all nodes in the graph.

        Returns:
            List of all nodes
        """
        return list(self._adjacency.keys())
