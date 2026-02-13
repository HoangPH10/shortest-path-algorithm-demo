"""Core data types for the route pathfinding visualizer."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Location:
    """Represents a geographic point with address and coordinates.

    Attributes:
        address: Human-readable formatted address
        latitude: Decimal degrees, range [-90, 90]
        longitude: Decimal degrees, range [-180, 180]
    """

    address: str
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate location data."""
        if not self.address:
            raise ValueError("Address cannot be empty")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass(frozen=True)
class Node:
    """Represents a point in the road network graph.

    Attributes:
        id: Unique identifier for the node
        latitude: Decimal degrees of node location
        longitude: Decimal degrees of node location
    """

    id: str
    latitude: float
    longitude: float

    def __hash__(self) -> int:
        """Make Node hashable for use as dictionary keys."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Check equality based on node ID."""
        if not isinstance(other, Node):
            return False
        return self.id == other.id


@dataclass
class Route:
    """Represents a calculated route with performance metrics.

    Attributes:
        path: Ordered list of nodes forming the route (final optimal path)
        total_distance: Total route distance in kilometers
        algorithm: Name of algorithm used ("A*" or "Dijkstra")
        execution_time: Algorithm execution time in milliseconds
        nodes_explored: Number of nodes explored during search
        explored_nodes: List of all nodes that were explored (for visualization)
        open_set_nodes: List of all nodes added to priority queue (for visualization)
        explored_edges: List of all edges (from_node, to_node) explored during search
    """

    path: List[Node]
    total_distance: float
    algorithm: str
    execution_time: int
    nodes_explored: int
    explored_nodes: List[Node] = field(default_factory=list)
    open_set_nodes: List[Node] = field(default_factory=list)
    explored_edges: List[Tuple[Node, Node]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate route data."""
        if self.total_distance < 0:
            raise ValueError(f"Distance cannot be negative: {self.total_distance}")
        if self.execution_time < 0:
            raise ValueError(f"Execution time cannot be negative: {self.execution_time}")
        if self.nodes_explored < 0:
            raise ValueError(f"Nodes explored cannot be negative: {self.nodes_explored}")


@dataclass
class PathfindingResult:
    """Wrapper for pathfinding operation results.

    Attributes:
        success: Whether pathfinding succeeded
        route: The calculated route if successful
        error: Error message if failed
    """

    success: bool
    route: Optional[Route] = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate result consistency."""
        if self.success and self.route is None:
            raise ValueError("Successful result must include a route")
        if not self.success and self.error is None:
            raise ValueError("Failed result must include an error message")
