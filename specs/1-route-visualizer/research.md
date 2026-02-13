# Research: Dual-Map Route Visualizer

**Feature**: 1-route-visualizer  
**Phase**: 0 (Research & Technology Selection)  
**Date**: 2026-02-06

## Purpose

This document consolidates research findings and design decisions for implementing the dual-map route visualizer. It addresses technology choices, algorithm implementation strategies, API integration patterns, and best practices for the project.

## Technical Context Review

From [plan.md](plan.md), the Technical Context specified:
- **Language**: Python 3.9+ with type hints
- **Primary Dependencies**: streamlit, folium, googlemaps, networkx, pytest, black/isort/pylint
- **Performance Goals**: ≤2s algorithm execution, ≤5s total response time
- **Constraints**: No external pathfinding libraries, Google Maps API free tier

**Status**: All technical choices are concrete. No NEEDS CLARIFICATION markers were present.

## Research Topics

### 1. Map Visualization Library Selection

**Decision**: Use **folium** for map visualization

**Rationale**:
- **Folium strengths**: Python-native library built on Leaflet.js, generates standalone HTML maps easily embeddable in Streamlit, supports custom polylines with styling (colors, stroke width), marker customization, and OSM/Google tile layers
- **Integration with Streamlit**: `streamlit-folium` component allows direct rendering of folium maps in Streamlit UI with minimal code
- **Alternative considered - pydeck**: More powerful for 3D visualizations and large datasets, but adds complexity unnecessary for 2D route visualization; folium's simplicity better matches project scope
- **Alternative considered - Google Maps JavaScript API directly**: Requires complex JavaScript integration in Streamlit, folium abstracts this cleanly

**Best Practices**:
- Create separate `FoliumMapBuilder` class in `src/services/map_renderer.py` for map generation
- Use distinct color schemes for A* (blue, #4285F4) and Dijkstra (red, #EA4335) routes
- Set stroke weight to 4px for visibility, opacity 0.8 for overlap detection
- Use custom icon markers: green pin for start, red pin for destination
- Include legend as folium Control with algorithm labels and color mapping

**References**:
- Folium documentation: https://python-visualization.github.io/folium/
- Streamlit-folium integration: https://github.com/randyzwitch/streamlit-folium

---

### 2. A* Algorithm Implementation Strategy

**Decision**: Implement A* from scratch using **heapq** priority queue with **Euclidean distance heuristic** as default

**Rationale**:
- **Constitution compliance**: Principle V requires no external pathfinding libraries; algorithms must be original implementations
- **Admissibility**: Euclidean distance (straight-line) never overestimates actual road distance, ensuring A* finds optimal path
- **Consistency**: Euclidean heuristic satisfies triangle inequality, guaranteeing optimal path without reopening nodes
- **Performance**: heapq (min-heap) provides O(log n) insert/extract, achieving O((V + E) log V) overall complexity for A*

**Implementation Approach**:
```python
# Pseudocode structure for src/algorithms/astar.py
def astar(graph: Graph, start: Node, goal: Node, heuristic: Callable) -> PathfindingResult:
    open_set = [(0, start)]  # Priority queue: (f_score, node)
    came_from = {}           # Parent tracking for path reconstruction
    g_score = {start: 0}     # Cost from start to node
    f_score = {start: heuristic(start, goal)}  # g + h
    nodes_explored = 0
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        nodes_explored += 1
        
        if current == goal:
            return reconstruct_path(came_from, current, nodes_explored)
        
        for neighbor, edge_weight in graph.neighbors(current):
            tentative_g = g_score[current] + edge_weight
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return PathfindingResult(success=False, error="No path found")
```

**Configurable Heuristics** (per Constitution Principle V):
- **Euclidean**: `sqrt((x2-x1)^2 + (y2-y1)^2)` - Default, most accurate for road networks
- **Manhattan**: `|x2-x1| + |y2-y1|` - Faster computation, grid-like streets
- **Diagonal (Chebyshev)**: `max(|x2-x1|, |y2-y1|)` - Allows diagonal movement

**Best Practices**:
- Use `@dataclass` for Node/Edge types with comparison methods for heapq
- Add `visited` set to avoid duplicate processing
- Include performance instrumentation (time.perf_counter) for execution timing
- Support optional `trace_mode` parameter to log algorithm steps for debugging

**Testing Strategy**:
- Unit test with simple 3x3 grid graph with known optimal path (5 moves)
- Correctness test: verify A* finds same distance as Dijkstra on 10 random graphs
- Edge case: start == goal (return path with 0 distance)
- Edge case: no path exists (disconnected graph, return failure result)
- Performance test: 100-node graph completes in <500ms

**References**:
- Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths." *IEEE Transactions on Systems Science and Cybernetics*.
- Introduction to Algorithms (CLRS), Chapter 24: Single-Source Shortest Paths

---

### 3. Dijkstra Algorithm Implementation Strategy

**Decision**: Implement Dijkstra from scratch using **heapq** priority queue, identical structure to A* but without heuristic

**Rationale**:
- **Constitution compliance**: Original implementation required, no libraries
- **Optimal data structure**: Priority queue ensures O((V + E) log V) complexity vs O(V^2) with naive approach
- **Code reuse**: Share graph representation and path reconstruction with A*
- **Educational value**: Side-by-side comparison demonstrates heuristic impact (A* explores fewer nodes)

**Implementation Approach**:
```python
# Pseudocode structure for src/algorithms/dijkstra.py
def dijkstra(graph: Graph, start: Node, goal: Node) -> PathfindingResult:
    distances = {start: 0}
    pq = [(0, start)]  # (distance, node)
    came_from = {}
    nodes_explored = 0
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        nodes_explored += 1
        
        if current == goal:
            return reconstruct_path(came_from, current, nodes_explored)
        
        if current_dist > distances.get(current, float('inf')):
            continue  # Already found better path
        
        for neighbor, edge_weight in graph.neighbors(current):
            distance = current_dist + edge_weight
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                came_from[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))
    
    return PathfindingResult(success=False, error="No path found")
```

**Difference from A***: No heuristic function, priority solely based on distance from start (g-score)

**Best Practices**:
- Ensure consistent Node/Edge interfaces with A* implementation
- Use same performance instrumentation for fair comparison
- Share utility functions (reconstruct_path, distance calculations) in common module

**Testing Strategy**:
- Same test cases as A* to verify both produce identical path distances
- Comparative test: verify Dijkstra explores more nodes than A* on same graph (demonstrates heuristic efficiency)
- Non-negative weights assertion: raise error if edge weight < 0

---

### 4. Google Maps API Integration Patterns

**Decision**: Use **googlemaps** Python client for Geocoding and Directions APIs

**Rationale**:
- **Official client**: Maintained by Google, handles authentication, rate limiting, retries
- **Type safety**: Returns structured dictionaries easily converted to typed dataclasses
- **Error handling**: Provides specific exceptions for quota exceeded, invalid requests, network errors
- **Simplicity**: Single client instance handles multiple API services

**API Usage Strategy**:

**Geocoding API** (address → coordinates):
```python
# src/services/geocoding.py
def geocode_address(client: googlemaps.Client, address: str) -> Location:
    try:
        result = client.geocode(address)
        if not result:
            raise ValueError(f"Address not found: {address}")
        location = result[0]['geometry']['location']
        return Location(
            address=result[0]['formatted_address'],
            latitude=location['lat'],
            longitude=location['lng']
        )
    except googlemaps.exceptions.ApiError as e:
        raise APIError(f"Geocoding failed: {e}")
```

**Directions API** (route → graph structure):
```python
# src/services/routing.py
def get_route_graph(client: googlemaps.Client, start: Location, end: Location) -> Graph:
    try:
        result = client.directions(
            origin=(start.latitude, start.longitude),
            destination=(end.latitude, end.longitude),
            mode="driving",
            alternatives=False  # Single route
        )
        # Parse steps into graph nodes/edges
        graph = Graph()
        for step in result[0]['legs'][0]['steps']:
            start_loc = step['start_location']
            end_loc = step['end_location']
            distance = step['distance']['value']  # meters
            graph.add_edge(start_loc, end_loc, distance)
        return graph
    except googlemaps.exceptions.Timeout:
        raise APIError("Request timeout (>5s)")
```

**Best Practices**:
- **API key management**: Load from environment variable via `python-dotenv`
- **Timeout configuration**: Set 5-second timeout per Constitution
- **Rate limiting**: Cache geocoding results for same addresses (LRU cache, max 100 entries)
- **Error categories**: Distinguish between user errors (invalid address) and system errors (API down)
- **Fallback**: If Directions API fails, construct simplified graph from straight-line segments

**API Quota Management** (Free Tier: $200/month credit):
- Geocoding: $5/1000 requests = 40,000 free requests/month
- Directions: $5/1000 requests = 40,000 free requests/month
- **Mitigation**: Implement request caching, use single client instance, warn users about quota in UI

**References**:
- Google Maps Platform Documentation: https://developers.google.com/maps/documentation
- googlemaps Python client: https://github.com/googlemaps/google-maps-services-python

---

### 5. Graph Data Structure Design

**Decision**: Implement **adjacency list** representation using Python dictionaries

**Rationale**:
- **Memory efficiency**: Adjacency list uses O(V + E) memory vs O(V^2) for matrix
- **Performance**: Neighbor iteration is O(degree) vs O(V) for dense graphs
- **Constitution requirement**: Principle IV mandates adjacency lists for memory efficiency
- **Real-world suitability**: Road networks are sparse graphs (average degree 3-4), making adjacency lists optimal

**Implementation Approach**:
```python
# src/algorithms/graph.py
@dataclass(frozen=True)
class Node:
    id: str
    latitude: float
    longitude: float
    
    def __hash__(self):
        return hash(self.id)

@dataclass
class Edge:
    from_node: Node
    to_node: Node
    weight: float  # Distance in meters

class Graph:
    def __init__(self):
        self._adjacency: Dict[Node, List[Tuple[Node, float]]] = {}
    
    def add_node(self, node: Node) -> None:
        if node not in self._adjacency:
            self._adjacency[node] = []
    
    def add_edge(self, from_node: Node, to_node: Node, weight: float) -> None:
        self.add_node(from_node)
        self.add_node(to_node)
        self._adjacency[from_node].append((to_node, weight))
        # Undirected graph for roads
        self._adjacency[to_node].append((from_node, weight))
    
    def neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        return self._adjacency.get(node, [])
    
    def nodes(self) -> List[Node]:
        return list(self._adjacency.keys())
```

**Best Practices**:
- Use `frozen=True` dataclass for Node to make it hashable for dictionary keys
- Implement bidirectional edges for undirected road networks
- Add validation: assert weight > 0 (Dijkstra requires non-negative weights)
- Support graph serialization to JSON for testing fixtures

---

### 6. Streamlit UI Best Practices

**Decision**: Single-page layout with input form at top, dual maps below, metrics at bottom

**Rationale**:
- **User flow**: Natural top-to-bottom reading order (input → visualization → metrics)
- **Responsiveness**: Streamlit columns for side-by-side maps on desktop, stacked on mobile
- **Constitution compliance**: Principle III requires input validation, visual feedback, error handling

**Layout Structure**:
```python
# main.py (simplified)
st.title("Route Pathfinding Visualizer")
st.subheader("Compare A* and Dijkstra Algorithms")

# Input Section
col1, col2 = st.columns(2)
with col1:
    start_address = st.text_input("Start Location", placeholder="e.g., Times Square, New York")
with col2:
    dest_address = st.text_input("Destination Location", placeholder="e.g., Central Park, New York")

if st.button("Calculate Routes", type="primary"):
    if not start_address or not dest_address:
        st.error("Both start and destination addresses are required.")
    else:
        with st.spinner("Calculating routes..."):
            # Geocode, build graph, run algorithms
            # Display results

# Map Section (conditionally rendered after calculation)
if results_available:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A* Algorithm")
        st_folium(astar_map, width=500, height=400)
    with col2:
        st.subheader("Dijkstra Algorithm")
        st_folium(dijkstra_map, width=500, height=400)

# Metrics Section
if results_available:
    st.subheader("Performance Comparison")
    df = pd.DataFrame({
        "Metric": ["Execution Time", "Nodes Explored", "Path Length"],
        "A*": [f"{astar_time}ms", astar_nodes, f"{astar_dist}km"],
        "Dijkstra": [f"{dijkstra_time}ms", dijkstra_nodes, f"{dijkstra_dist}km"]
    })
    st.table(df)
```

**Input Validation Best Practices**:
- Non-empty check before API calls
- Real-time feedback via `st.error()`, `st.warning()`, `st.success()`
- Disable button during processing to prevent duplicate requests
- Use `st.session_state` to persist results across reruns

**Error Handling**:
- Geocoding failure: "Address not found. Please enter a valid location."
- API timeout: "Service temporarily unavailable. Please try again in a moment."
- No path found: "No route found between these locations."
- API quota: "API request limit reached. Please wait before trying again."

**Performance Optimization**:
- Cache geocoding results with `@st.cache_data`
- Avoid re-running algorithms on UI interactions (use session state)
- Lazy-load maps only after successful calculation

**References**:
- Streamlit documentation: https://docs.streamlit.io
- Streamlit-folium: https://github.com/randyzwitch/streamlit-folium

---

### 7. Testing Strategy & Coverage

**Decision**: Pytest with pytest-cov, 90% coverage for algorithms, 75% for UI

**Rationale**:
- **Constitution mandate**: Principle II requires TDD with specific coverage targets
- **Pytest advantages**: Fixtures for test data reuse, parametrized tests for multiple scenarios, coverage integration
- **Algorithm focus**: Higher coverage for critical pathfinding logic vs UI glue code

**Test Organization**:

**Algorithm Tests** (`tests/algorithms/`):
- **Unit tests**: Individual functions (heuristics, graph operations, path reconstruction)
- **Correctness tests**: Known shortest paths (manual verification)
  - 3x3 grid: verify 5-step path from (0,0) to (2,2)
  - 10-node test graph: verify specific distance
- **Edge case tests**: 
  - Same start/destination → 0 distance
  - Disconnected graph → failure result
  - Single node → 0 distance
- **Comparative tests**: A* vs Dijkstra produce same path length
- **Performance tests**: Measure execution time, log nodes explored

**Integration Tests** (`tests/integration/`):
- **End-to-end**: Mock Google Maps API, verify full flow (input → geocode → graph → algorithms → results)
- **API integration**: Test actual Geocoding/Directions API calls (mark as slow tests, skip in CI if no API key)

**Fixtures** (`tests/conftest.py`):
```python
@pytest.fixture
def simple_grid_graph():
    """3x3 grid graph for testing"""
    graph = Graph()
    # Build grid with unit edge weights
    # ...
    return graph

@pytest.fixture
def known_shortest_path():
    """Graph with verified optimal path"""
    return {
        'graph': ...,
        'start': Node('A', 0, 0),
        'goal': Node('E', 4, 4),
        'expected_distance': 8,
        'expected_nodes': 5
    }

@pytest.fixture
def mock_gmaps_client(monkeypatch):
    """Mock googlemaps client for unit tests"""
    # ...
```

**Coverage Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=85"  # Average of 90% + 75%
]

[tool.coverage.run]
omit = ["tests/*", "main.py"]

[tool.coverage.report]
precision = 2
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError"
]
```

**Best Practices**:
- Write tests BEFORE implementation (TDD workflow)
- Use descriptive test names: `test_astar_finds_optimal_path_in_grid_graph`
- Parametrize multiple scenarios: `@pytest.mark.parametrize("start, goal, expected", [...])`
- Mark slow tests: `@pytest.mark.slow` for API calls
- Separate test data fixtures from test logic

**References**:
- Pytest documentation: https://docs.pytest.org
- pytest-cov: https://pytest-cov.readthedocs.io

---

### 8. Code Quality Tools Configuration

**Decision**: Black (formatter), isort (import sorter), mypy (type checker), pylint (linter)

**Rationale**:
- **Constitution requirement**: Principle I mandates PEP 8 compliance, type hints, linting score ≥8.5/10
- **Black**: Opinionated formatter, zero configuration, ensures consistent style
- **isort**: Compatible with black, sorts imports per PEP 8
- **mypy**: Enforces type hints, catches type errors before runtime
- **pylint**: Comprehensive linter, checks code quality beyond style

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
skip_gitignore = true

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true

[[tool.mypy.overrides]]
module = "streamlit.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "folium.*"
ignore_missing_imports = true

[tool.pylint.master]
fail-under = 8.5
ignore = [".venv", "build", "dist"]

[tool.pylint.format]
max-line-length = 100

[tool.pylint.messages_control]
disable = [
    "C0111",  # missing-docstring (handled by mypy)
    "R0903"   # too-few-public-methods (common for dataclasses)
]
```

**Pre-commit Workflow**:
```bash
# Format code
black src/ tests/
isort src/ tests/

# Type check
mypy src/

# Lint
pylint src/ --fail-under=8.5

# Run tests
pytest tests/ --cov=src --cov-fail-under=85
```

**Best Practices**:
- Run black/isort before every commit (consider pre-commit hooks)
- Fix mypy errors immediately (strict mode catches issues early)
- Aim for pylint score 9.5+, justify any disabled rules
- Use inline type hints, avoid `# type: ignore` unless necessary

---

## Summary of Research Findings

| Topic | Chosen Approach | Key Rationale |
|-------|----------------|---------------|
| **Map Visualization** | Folium | Python-native, Streamlit integration, sufficient for 2D routes |
| **A* Algorithm** | From scratch, heapq, Euclidean heuristic | Constitution compliance, admissibility, O((V+E) log V) |
| **Dijkstra Algorithm** | From scratch, heapq | Constitution compliance, consistent with A* structure |
| **Google Maps API** | googlemaps client | Official, handles auth/retries, structured responses |
| **Graph Structure** | Adjacency list (dict) | Memory efficient O(V+E), Constitution requirement |
| **UI Framework** | Streamlit single-page | Rapid development, natural user flow, built-in components |
| **Testing** | Pytest + pytest-cov | Fixtures, parametrization, coverage reporting |
| **Code Quality** | Black + isort + mypy + pylint | Automated formatting, type safety, linting ≥8.5 |

**All research items resolved. No NEEDS CLARIFICATION remaining. Ready for Phase 1 (data model and contracts).**
