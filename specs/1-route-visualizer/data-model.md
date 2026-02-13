# Data Model: Dual-Map Route Visualizer

**Feature**: 1-route-visualizer  
**Phase**: 1 (Design & Contracts)  
**Date**: 2026-02-06  
**References**: [spec.md](spec.md#key-entities), [research.md](research.md)

## Purpose

This document defines the core data entities and their relationships for the route visualization application. All entities are designed to be technology-agnostic representations of domain concepts, with Python type-hinted implementations in `src/utils/types.py`.

## Core Entities

### Location

Represents a geographic point with address and coordinates.

**Attributes**:
- `address` (string): Human-readable formatted address (e.g., "Times Square, Manhattan, NY 10036, USA")
- `latitude` (float): Decimal degrees, range [-90, 90]
- `longitude` (float): Decimal degrees, range [-180, 180]

**Validation Rules**:
- Address must be non-empty string
- Latitude must be in valid range: -90 ≤ lat ≤ 90
- Longitude must be in valid range: -180 ≤ lon ≤ 180

**Usage**: Used for start and destination inputs, converted from user text via Geocoding API

**Python Implementation**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Location:
    address: str
    latitude: float
    longitude: float
    
    def __post_init__(self):
        if not self.address:
            raise ValueError("Address cannot be empty")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")
```

---

### Node

Represents a point in the road network graph (intersection or waypoint).

**Attributes**:
- `id` (string): Unique identifier (e.g., "node_0", "lat_lng_40.7580_-73.9855")
- `latitude` (float): Decimal degrees of node location
- `longitude` (float): Decimal degrees of node location

**Relationships**:
- Connected to other Nodes via Edges (adjacency list in Graph)

**Validation Rules**:
- ID must be unique within graph
- Latitude/longitude same constraints as Location

**Usage**: Building blocks of Graph data structure for pathfinding algorithms

**Python Implementation**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Node:
    id: str
    latitude: float
    longitude: float
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id
```

**Design Note**: `frozen=True` makes Node immutable and hashable, required for use as dictionary keys in Graph adjacency list and priority queue operations.

---

### Edge

Represents a road segment connecting two nodes in the graph.

**Attributes**:
- `from_node` (Node): Starting node of edge
- `to_node` (Node): Ending node of edge
- `weight` (float): Distance in meters (positive value)

**Validation Rules**:
- Weight must be > 0 (Dijkstra/A* require non-negative weights)
- from_node and to_node must be different nodes (no self-loops)

**Usage**: Stored in Graph adjacency list to represent road network connectivity

**Python Implementation**:
```python
from dataclasses import dataclass

@dataclass
class Edge:
    from_node: Node
    to_node: Node
    weight: float
    
    def __post_init__(self):
        if self.weight <= 0:
            raise ValueError(f"Edge weight must be positive, got {self.weight}")
        if self.from_node == self.to_node:
            raise ValueError("Self-loops not allowed")
```

**Design Note**: Not frozen because edges may be updated during graph construction; weight represents physical distance retrieved from Google Maps Directions API.

---

### Graph

Represents the road network as an adjacency list structure.

**Attributes**:
- `_adjacency` (Dict[Node, List[Tuple[Node, float]]]): Maps each node to list of (neighbor_node, edge_weight) tuples

**Methods**:
- `add_node(node: Node) -> None`: Add node to graph
- `add_edge(from_node: Node, to_node: Node, weight: float) -> None`: Add bidirectional edge (undirected graph for roads)
- `neighbors(node: Node) -> List[Tuple[Node, float]]`: Get all neighbors and edge weights for a node
- `nodes() -> List[Node]`: Get all nodes in graph
- `node_count() -> int`: Return number of nodes
- `edge_count() -> int`: Return number of edges

**Validation Rules**:
- Bidirectional edges (road networks are undirected)
- No duplicate edges between same node pair
- All edge weights must be positive

**Usage**: Central data structure passed to A* and Dijkstra algorithms

**Python Implementation** (see [research.md](research.md#5-graph-data-structure-design) for full code):
```python
class Graph:
    def __init__(self):
        self._adjacency: Dict[Node, List[Tuple[Node, float]]] = {}
    
    def add_edge(self, from_node: Node, to_node: Node, weight: float) -> None:
        self.add_node(from_node)
        self.add_node(to_node)
        self._adjacency[from_node].append((to_node, weight))
        self._adjacency[to_node].append((from_node, weight))  # Bidirectional
    
    # ... other methods
```

**Space Complexity**: O(V + E) where V = nodes, E = edges

---

### Route

Represents a calculated path through the graph from start to destination.

**Attributes**:
- `path` (List[Node]): Ordered sequence of nodes from start to destination
- `total_distance` (float): Sum of edge weights along path, in kilometers
- `algorithm` (string): Algorithm used ("A*" or "Dijkstra")
- `execution_time` (int): Time to compute route in milliseconds
- `nodes_explored` (int): Number of nodes visited during pathfinding

**Derived Attributes**:
- `path_length` (int): Number of nodes in path (len(path))
- `segments` (List[Tuple[Node, Node, float]]): List of (from, to, distance) for each edge in path

**Validation Rules**:
- Path must be non-empty if route exists
- First node must be start location, last node must be destination
- All consecutive nodes in path must be connected by edges in graph
- total_distance must equal sum of edge weights in path
- execution_time and nodes_explored must be non-negative

**Usage**: Returned by A* and Dijkstra algorithms, used for map visualization and metrics display

**Python Implementation**:
```python
from dataclasses import dataclass
from typing import List

@dataclass
class Route:
    path: List[Node]
    total_distance: float  # in kilometers
    algorithm: str
    execution_time: int  # milliseconds
    nodes_explored: int
    
    @property
    def path_length(self) -> int:
        return len(self.path)
    
    def segments(self) -> List[Tuple[Node, Node, float]]:
        """Get list of path segments with distances"""
        # Requires graph reference to lookup edge weights
        # Implementation returns [(node_i, node_i+1, distance), ...]
        pass
```

---

### PathfindingResult

Represents the outcome of a pathfinding algorithm execution, including success/failure status.

**Attributes**:
- `success` (bool): True if path found, False otherwise
- `route` (Route | None): Route object if success, None if failure
- `error` (string | None): Error message if failure (e.g., "No path found"), None if success

**Possible Error States**:
- "No path found" - Disconnected graph, no route exists
- "Start and destination are identical" - Same node for both
- "Invalid nodes" - Start or destination not in graph

**Validation Rules**:
- If success is True, route must not be None and error must be None
- If success is False, route must be None and error must be a non-empty string

**Usage**: Returned by pathfinding functions, allows UI to distinguish algorithmic failure from errors

**Python Implementation**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PathfindingResult:
    success: bool
    route: Optional[Route] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.success and (self.route is None or self.error is not None):
            raise ValueError("Success result must have route and no error")
        if not self.success and (self.route is not None or not self.error):
            raise ValueError("Failure result must have error and no route")
```

---

## Entity Relationships

```
┌──────────────┐
│   Location   │ (user input)
└──────┬───────┘
       │ geocoded to
       │
       ▼
 ┌──────────┐     contains      ┌──────────┐
 │   Node   │◀─────────────────▶│  Graph   │
 └────┬─────┘                   └────┬─────┘
      │                              │
      │ connected by                 │ used by algorithms
      │                              │
      ▼                              ▼
 ┌──────────┐              ┌─────────────────────┐
 │   Edge   │              │ Pathfinding Process │
 └──────────┘              └──────────┬──────────┘
                                      │
                                      │ produces
                                      │
                                      ▼
                           ┌────────────────────────┐
                           │ PathfindingResult      │
                           │  ├─ success: bool      │
                           │  ├─ route: Route?      │
                           │  └─ error: str?        │
                           └────────────────────────┘
                                      │
                                      │ contains (if success)
                                      │
                                      ▼
                           ┌────────────────────────┐
                           │       Route            │
                           │  ├─ path: List[Node]   │
                           │  ├─ total_distance     │
                           │  ├─ algorithm          │
                           │  ├─ execution_time     │
                           │  └─ nodes_explored     │
                           └────────────────────────┘
```

**Workflow**:
1. User enters start/destination addresses (strings)
2. Geocoding service converts to Location objects (lat/lng)
3. Routing service builds Graph with Nodes and Edges from Directions API
4. Pathfinding algorithms (A*/Dijkstra) process Graph
5. Algorithms return PathfindingResult with Route (if successful) or error message
6. UI renders Route path on map and displays metrics

---

## State Transitions

### PathfindingResult States

```
[User Input] → [Geocoding] → [Graph Building] → [Pathfinding]
                    │              │                  │
                    ▼ (error)      ▼ (error)         ▼
            ┌───────────────────────────────────────────┐
            │  PathfindingResult                        │
            │                                           │
            │  success=False                            │
            │  error="Invalid address" / "No path"      │
            └───────────────────────────────────────────┘
                                                         
                                                  ▼ (success)
                                          ┌──────────────────────┐
                                          │ PathfindingResult    │
                                          │                      │
                                          │ success=True         │
                                          │ route=Route(...)     │
                                          └──────────────────────┘
```

---

## Data Persistence

**Storage Strategy**: **No persistence** - This is a stateless application.

- All data is ephemeral within a single Streamlit session
- No database, files, or caching between application restarts
- Graph is rebuilt from Google Maps API for each route calculation
- Session state (`st.session_state`) stores results only during active browser session

**Rationale**: Educational demo application, no user accounts or historical data requirements

**Future Consideration**: If persistence needed, add SQLite database for:
- Caching geocoded addresses (reduce API calls)
- Storing calculation history for user review
- Pre-loaded test graphs for offline demo mode

---

## Type Safety & Validation

**Type Hints**: All entities use Python 3.9+ type hints with mypy strict mode validation

**Runtime Validation**: 
- Dataclass `__post_init__` methods enforce constraints (coordinate ranges, positive weights)
- Input validation in service layer before creating entities
- Custom exceptions for domain errors (e.g., `InvalidLocationError`, `GraphConstructionError`)

**Example Validation Flow**:
```python
# src/services/geocoding.py
def geocode_address(client: googlemaps.Client, address: str) -> Location:
    if not address.strip():
        raise ValueError("Address cannot be empty")  # Caught early
    
    result = client.geocode(address)
    if not result:
        raise InvalidLocationError(f"Address not found: {address}")
    
    # Create Location with validated data
    return Location(
        address=result[0]['formatted_address'],
        latitude=result[0]['geometry']['location']['lat'],  # API guarantees valid range
        longitude=result[0]['geometry']['location']['lng']
    )
```

---

## Summary

| Entity | Purpose | Key Attributes | Validation |
|--------|---------|----------------|------------|
| **Location** | Geographic point from user input | address, lat, lng | Non-empty address, valid coordinate ranges |
| **Node** | Graph vertex (intersection) | id, lat, lng | Unique ID, hashable, immutable |
| **Edge** | Graph edge (road segment) | from_node, to_node, weight | Positive weight, no self-loops |
| **Graph** | Road network structure | adjacency list | Bidirectional edges, O(V+E) memory |
| **Route** | Calculated path | path, distance, algorithm, time, nodes | Non-empty path, distance equals sum of weights |
| **PathfindingResult** | Algorithm outcome | success, route, error | Mutually exclusive success/error states |

**Design Principles**:
- **Immutability**: Nodes are frozen dataclasses (hashable for graph operations)
- **Type Safety**: Comprehensive type hints enable mypy validation
- **Validation**: Early validation in constructors prevents invalid states
- **Separation of Concerns**: Entities are data-only, logic in services/algorithms
- **Testability**: Simple dataclasses with no dependencies, easy to mock

**Next Steps**: See [contracts/](contracts/) for API-level contracts and [quickstart.md](quickstart.md) for usage examples.
