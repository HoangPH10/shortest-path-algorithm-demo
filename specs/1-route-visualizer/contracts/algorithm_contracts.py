# Algorithm Contracts

**Module**: `src/algorithms/`  
**Purpose**: Pathfinding algorithm implementations (A* and Dijkstra)

## Core Contracts

### astar() - A* Pathfinding Algorithm

```python
def astar(
    graph: Graph,
    start: Node,
    goal: Node,
    heuristic: Callable[[Node, Node], float]
) -> PathfindingResult:
    """
    Execute A* pathfinding algorithm on graph.
    
    Args:
        graph: Road network graph with nodes and weighted edges
        start: Starting node (must exist in graph)
        goal: Destination node (must exist in graph)
        heuristic: Function that estimates distance between two nodes
                   Must be admissible (never overestimate) and consistent
                   
    Returns:
        PathfindingResult with:
        - success=True, route=Route if path found
        - success=False, error=str if no path exists
        
    Raises:
        ValueError: If start or goal not in graph
        ValueError: If heuristic is not callable
        
    Performance:
        - Time complexity: O((V + E) log V) with priority queue
        - Space complexity: O(V) for visited/score dictionaries
        - Must complete typical routes (≤100 nodes) in ≤2 seconds
        
    Algorithm Properties:
        - Optimal: Finds shortest path when heuristic is admissible
        - Complete: Always finds path if one exists
        - Informed: Uses heuristic to guide search (explores fewer nodes than Dijkstra)
        
    Example:
        >>> graph = Graph()
        >>> start = Node("A", 0.0, 0.0)
        >>> goal = Node("E", 4.0, 4.0)
        >>> result = astar(graph, start, goal, euclidean_distance)
        >>> assert result.success == True
        >>> assert result.route.total_distance == 8.0
        >>> assert result.route.nodes_explored < 50  # Heuristic reduces search
    """
```

**Contract Tests**:
```python
# tests/algorithms/test_astar_contract.py
def test_astar_finds_path_in_connected_graph():
    """Contract: Returns success=True with route when path exists"""
    graph = build_simple_grid()  # 3x3 grid
    start = graph.nodes()[0]
    goal = graph.nodes()[-1]
    
    result = astar(graph, start, goal, euclidean_distance)
    
    assert result.success == True
    assert result.route is not None
    assert result.error is None
    assert result.route.path[0] == start
    assert result.route.path[-1] == goal

def test_astar_fails_in_disconnected_graph():
    """Contract: Returns success=False with error when no path"""
    graph = Graph()
    island1 = Node("A", 0, 0)
    island2 = Node("B", 10, 10)
    graph.add_node(island1)
    graph.add_node(island2)
    
    result = astar(graph, island1, island2, euclidean_distance)
    
    assert result.success == False
    assert result.route is None
    assert "No path found" in result.error

def test_astar_same_start_goal():
    """Contract: Returns zero-distance path when start == goal"""
    graph = Graph()
    node = Node("A", 0, 0)
    graph.add_node(node)
    
    result = astar(graph, node, node, euclidean_distance)
    
    assert result.success == True
    assert result.route.total_distance == 0
    assert len(result.route.path) == 1
```

---

### dijkstra() - Dijkstra Pathfinding Algorithm

```python
def dijkstra(
    graph: Graph,
    start: Node,
    goal: Node
) -> PathfindingResult:
    """
    Execute Dijkstra pathfinding algorithm on graph.
    
    Args:
        graph: Road network graph with nodes and weighted edges
        start: Starting node (must exist in graph)
        goal: Destination node (must exist in graph)
        
    Returns:
        PathfindingResult with:
        - success=True, route=Route if path found
        - success=False, error=str if no path exists
        
    Raises:
        ValueError: If start or goal not in graph
        ValueError: If graph contains negative edge weights
        
    Performance:
        - Time complexity: O((V + E) log V) with priority queue
        - Space complexity: O(V) for distance dictionary
        - Must complete typical routes (≤100 nodes) in ≤2 seconds
        
    Algorithm Properties:
        - Optimal: Always finds shortest path in non-negative weighted graphs
        - Complete: Always finds path if one exists
        - Uninformed: Explores nodes based solely on distance from start
        
    Comparison with A*:
        - Dijkstra explores more nodes (no heuristic guidance)
        - Both produce same path length for optimal solutions
        - Dijkstra may be faster on very dense graphs (less overhead)
        
    Example:
        >>> graph = Graph()
        >>> start = Node("A", 0.0, 0.0)
        >>> goal = Node("E", 4.0, 4.0)
        >>> result = dijkstra(graph, start, goal)
        >>> assert result.success == True
        >>> assert result.route.total_distance == 8.0
        >>> # Dijkstra explores more nodes than A* for same graph
        >>> assert result.route.nodes_explored > 50
    """
```

**Contract Tests**: Same structure as A* tests above

---

### Heuristic Functions

```python
def euclidean_distance(node1: Node, node2: Node) -> float:
    """
    Calculate Euclidean (straight-line) distance between two nodes.
    
    Args:
        node1: First node with lat/lng coordinates
        node2: Second node with lat/lng coordinates
        
    Returns:
        Distance in meters (approximate, using Haversine for lat/lng)
        
    Properties:
        - Admissible: Never overestimates actual road distance
        - Consistent: Satisfies triangle inequality h(A,C) ≤ h(A,B) + h(B,C)
        
    Example:
        >>> n1 = Node("A", 40.7580, -73.9855)  # Times Square
        >>> n2 = Node("B", 40.7829, -73.9654)  # Central Park
        >>> dist = euclidean_distance(n1, n2)
        >>> assert 2500 < dist < 3500  # ~3km straight line
    """

def manhattan_distance(node1: Node, node2: Node) -> float:
    """
    Calculate Manhattan (grid) distance between two nodes.
    Greater than or equal to Euclidean, still admissible.
    """

def diagonal_distance(node1: Node, node2: Node) -> float:
    """
    Calculate Chebyshev (diagonal) distance between two nodes.
    Allows diagonal movement, good for grid-like street layouts.
    """
```

---

## Graph Data Structure Contract

```python
class Graph:
    """
    Adjacency list representation of road network graph.
    """
    
    def add_node(self, node: Node) -> None:
        """Add node to graph. Idempotent."""
        
    def add_edge(self, from_node: Node, to_node: Node, weight: float) -> None:
        """
        Add bidirectional edge between nodes.
        
        Args:
            from_node: Start node (added if not exists)
            to_node: End node (added if not exists)
            weight: Edge weight in meters (must be > 0)
            
        Raises:
            ValueError: If weight <= 0
        """
        
    def neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        """
        Get all neighbors of node with edge weights.
        
        Returns:
            List of (neighbor_node, edge_weight) tuples
            Empty list if node has no neighbors or doesn't exist
        """
        
    def nodes(self) -> List[Node]:
        """Get all nodes in graph."""
        
    def node_count(self) -> int:
        """Return number of nodes in graph."""
        
    def edge_count(self) -> int:
        """Return number of unique edges (bidirectional counted once)."""
```

**Contract Tests**:
```python
def test_graph_bidirectional_edges():
    """Contract: add_edge creates edges in both directions"""
    graph = Graph()
    n1 = Node("A", 0, 0)
    n2 = Node("B", 1, 1)
    
    graph.add_edge(n1, n2, 100.0)
    
    # Both directions exist
    assert (n2, 100.0) in graph.neighbors(n1)
    assert (n1, 100.0) in graph.neighbors(n2)

def test_graph_rejects_negative_weights():
    """Contract: Raises ValueError for negative edge weights"""
    graph = Graph()
    n1 = Node("A", 0, 0)
    n2 = Node("B", 1, 1)
    
    with pytest.raises(ValueError, match="positive"):
        graph.add_edge(n1, n2, -10.0)
```

---

## Performance Contracts

**Execution Time Benchmarks** (tests/performance/test_benchmarks.py):

```python
@pytest.mark.benchmark
def test_astar_performance_100_nodes():
    """Contract: A* completes 100-node graph in ≤2 seconds"""
    graph = generate_random_graph(nodes=100, edges=300)
    start = graph.nodes()[0]
    goal = graph.nodes()[-1]
    
    start_time = time.perf_counter()
    result = astar(graph, start, goal, euclidean_distance)
    end_time = time.perf_counter()
    
    execution_time = (end_time - start_time) * 1000  # milliseconds
    assert execution_time <= 2000, f"A* took {execution_time}ms, expected ≤2000ms"
    assert result.success == True

@pytest.mark.benchmark
def test_algorithm_comparison():
    """Contract: A* explores fewer nodes than Dijkstra"""
    graph = generate_random_graph(nodes=100, edges=300)
    start = graph.nodes()[0]
    goal = graph.nodes()[-1]
    
    astar_result = astar(graph, start, goal, euclidean_distance)
    dijkstra_result = dijkstra(graph, start, goal)
    
    # Both find path with same distance
    assert astar_result.route.total_distance == dijkstra_result.route.total_distance
    
    # A* explores fewer nodes (heuristic guidance)
    assert astar_result.route.nodes_explored < dijkstra_result.route.nodes_explored
```

---

## Summary

| Function | Input | Output | Performance | Correctness |
|----------|-------|--------|-------------|-------------|
| `astar()` | Graph, start, goal, heuristic | PathfindingResult | O((V+E) log V), ≤2s | Optimal if heuristic admissible |
| `dijkstra()` | Graph, start, goal | PathfindingResult | O((V+E) log V), ≤2s | Optimal for non-negative weights |
| `euclidean_distance()` | Node, Node | float (meters) | O(1) | Admissible & consistent |

**Contract Validation**: All contracts are tested in `tests/algorithms/` with unit tests and performance benchmarks.
