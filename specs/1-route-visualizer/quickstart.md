# Quickstart Guide: Dual-Map Route Visualizer

**Feature**: 1-route-visualizer  
**Phase**: 1 (Design & Contracts)  
**Date**: 2026-02-06  
**Audience**: Developers implementing the feature

## Purpose

This guide provides step-by-step instructions for implementing and using the route visualizer application. It bridges the gap between design documents and actual coding.

## Prerequisites

Before starting implementation:

1. **Review Planning Documents**:
   - [spec.md](spec.md) - Feature requirements and user stories
   - [plan.md](plan.md) - Technical context and architecture
   - [research.md](research.md) - Technology decisions and best practices
   - [data-model.md](data-model.md) - Core entities and relationships
   - [contracts/](contracts/) - Function interfaces and contracts

2. **Development Environment**:
   - Python 3.9 or higher installed
   - `uv` package manager (or `pip`)
   - Git for version control
   - Google Maps API key ([get one here](https://developers.google.com/maps/documentation/javascript/get-api-key))
   - Code editor with Python support (VS Code recommended)

3. **Constitution Review**:
   - Read [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
   - Understand TDD requirements (90% algorithm coverage, 75% UI coverage)
   - Familiarize with code quality standards (black, isort, mypy, pylint)

## Phase 0: Project Setup

### Step 1: Create Project Structure

```bash
# From repository root
mkdir -p src/{algorithms,services,ui,utils}
mkdir -p tests/{algorithms,integration,performance}
touch src/__init__.py src/{algorithms,services,ui,utils}/__init__.py
touch tests/__init__.py
```

Verify structure matches [plan.md](plan.md#project-structure):
```
src/
├── algorithms/
│   └── __init__.py
├── services/
│   └── __init__.py
├── ui/
│   └── __init__.py
└── utils/
    └── __init__.py
tests/
├── algorithms/
├── integration/
└── performance/
```

### Step 2: Install Dependencies

```bash
# Using uv (recommended)
uv add streamlit folium googlemaps networkx pytest pytest-cov black isort mypy pylint streamlit-folium python-dotenv

# Or using pip
pip install streamlit folium googlemaps networkx pytest pytest-cov black isort mypy pylint streamlit-folium python-dotenv
```

Expected `pyproject.toml` dependencies:
```toml
[project]
name = "route-visualizer"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "streamlit>=1.30.0",
    "folium>=0.15.0",
    "googlemaps>=4.10.0",
    "networkx>=3.2.0",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.12.0",
    "isort>=5.13.0",
    "mypy>=1.8.0",
    "pylint>=3.0.0",
    "streamlit-folium>=0.16.0",
    "python-dotenv>=1.0.0"
]
```

### Step 3: Configure Development Tools

Create `pyproject.toml` configuration sections from [research.md](research.md#8-code-quality-tools-configuration):

```toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
disallow_untyped_defs = true

[tool.pylint.master]
fail-under = 8.5

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--cov=src", "--cov-report=html", "--cov-fail-under=85"]
```

### Step 4: Setup API Key

```bash
# Create .env file
echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env

# Add to .gitignore
echo ".env" >> .gitignore
```

**Important**: Never commit `.env` file. Use `.env.example` as template.

## Phase 1: Core Data Structures (TDD Workflow)

### Step 5: Implement Graph Data Structure

**Following TDD**: Write tests FIRST, then implementation.

#### 5a. Write Tests

Create `tests/algorithms/test_graph.py`:

```python
import pytest
from src.algorithms.graph import Graph, Node, Edge

def test_node_creation():
    """Test Node dataclass creation and immutability"""
    node = Node(id="A", latitude=40.7580, longitude=-73.9855)
    assert node.id == "A"
    assert node.latitude == 40.7580
    assert node.longitude == -73.9855
    assert hash(node)  # Node is hashable

def test_node_equality():
    """Test Node equality based on ID"""
    n1 = Node("A", 0, 0)
    n2 = Node("A", 0, 0)
    n3 = Node("B", 0, 0)
    assert n1 == n2
    assert n1 != n3

def test_graph_add_node():
    """Test adding nodes to graph"""
    graph = Graph()
    node = Node("A", 0, 0)
    graph.add_node(node)
    assert node in graph.nodes()

def test_graph_add_edge():
    """Test adding bidirectional edges"""
    graph = Graph()
    n1 = Node("A", 0, 0)
    n2 = Node("B", 1, 1)
    
    graph.add_edge(n1, n2, 100.0)
    
    # Both directions exist
    neighbors_n1 = graph.neighbors(n1)
    neighbors_n2 = graph.neighbors(n2)
    assert (n2, 100.0) in neighbors_n1
    assert (n1, 100.0) in neighbors_n2

def test_graph_rejects_negative_weights():
    """Test edge weight validation"""
    graph = Graph()
    n1 = Node("A", 0, 0)
    n2 = Node("B", 1, 1)
    
    with pytest.raises(ValueError, match="positive"):
        graph.add_edge(n1, n2, -10.0)
```

**Run tests (expect failures)**:
```bash
pytest tests/algorithms/test_graph.py
# All tests should FAIL (no implementation yet)
```

#### 5b. Implement Graph

Create `src/algorithms/graph.py` following [data-model.md](data-model.md#node):

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple

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

class Graph:
    def __init__(self):
        self._adjacency: Dict[Node, List[Tuple[Node, float]]] = {}
    
    def add_node(self, node: Node) -> None:
        if node not in self._adjacency:
            self._adjacency[node] = []
    
    def add_edge(self, from_node: Node, to_node: Node, weight: float) -> None:
        if weight <= 0:
            raise ValueError("Edge weight must be positive")
        self.add_node(from_node)
        self.add_node(to_node)
        self._adjacency[from_node].append((to_node, weight))
        self._adjacency[to_node].append((from_node, weight))  # Bidirectional
    
    def neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        return self._adjacency.get(node, [])
    
    def nodes(self) -> List[Node]:
        return list(self._adjacency.keys())
    
    def node_count(self) -> int:
        return len(self._adjacency)
    
    def edge_count(self) -> int:
        # Count unique edges (bidirectional counted once)
        return sum(len(neighbors) for neighbors in self._adjacency.values()) // 2
```

**Run tests again (expect passes)**:
```bash
pytest tests/algorithms/test_graph.py
# All tests should PASS
```

### Step 6: Implement Type Definitions

Create `src/utils/types.py` following [data-model.md](data-model.md):

```python
from dataclasses import dataclass
from typing import List, Optional

from src.algorithms.graph import Node

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

@dataclass
class Route:
    path: List[Node]
    total_distance: float  # kilometers
    algorithm: str
    execution_time: int  # milliseconds
    nodes_explored: int
    
    @property
    def path_length(self) -> int:
        return len(self.path)

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

**Test types**:
```bash
pytest tests/  # Include type tests in conftest.py or dedicated test file
mypy src/utils/types.py  # Verify type hints
```

## Phase 2: Algorithm Implementation (TDD)

### Step 7: Implement Heuristic Functions

#### 7a. Write Tests

Create `tests/algorithms/test_heuristics.py`:

```python
from src.algorithms.heuristics import euclidean_distance, manhattan_distance
from src.algorithms.graph import Node

def test_euclidean_distance_zero():
    """Same node returns zero distance"""
    node = Node("A", 40.7580, -73.9855)
    assert euclidean_distance(node, node) == 0.0

def test_euclidean_distance_positive():
    """Different nodes return positive distance"""
    n1 = Node("A", 40.7580, -73.9855)  # Times Square
    n2 = Node("B", 40.7829, -73.9654)  # Central Park
    dist = euclidean_distance(n1, n2)
    assert 2500 < dist < 3500  # ~3km in meters

def test_manhattan_greater_equal_euclidean():
    """Manhattan distance >= Euclidean distance"""
    n1 = Node("A", 0, 0)
    n2 = Node("B", 3, 4)
    euc = euclidean_distance(n1, n2)
    man = manhattan_distance(n1, n2)
    assert man >= euc
```

#### 7b. Implement Heuristics

Create `src/algorithms/heuristics.py`:

```python
import math
from src.algorithms.graph import Node

def euclidean_distance(node1: Node, node2: Node) -> float:
    """Calculate Euclidean distance in meters using Haversine formula"""
    lat1, lon1 = math.radians(node1.latitude), math.radians(node1.longitude)
    lat2, lon2 = math.radians(node2.latitude), math.radians(node2.longitude)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    radius_earth = 6371000  # meters
    return c * radius_earth

def manhattan_distance(node1: Node, node2: Node) -> float:
    """Calculate Manhattan distance (approximate for lat/lng)"""
    lat_diff = abs(node2.latitude - node1.latitude) * 111320  # meters per degree
    lon_diff = abs(node2.longitude - node1.longitude) * 111320 * math.cos(math.radians(node1.latitude))
    return lat_diff + lon_diff
```

**Run tests**:
```bash
pytest tests/algorithms/test_heuristics.py
```

### Step 8: Implement A* Algorithm

See [contracts/algorithm_contracts.py](contracts/algorithm_contracts.py) for full specification.

#### 8a. Write Tests First

Create `tests/algorithms/test_astar.py` with comprehensive tests from contract.

#### 8b. Implement A*

Create `src/algorithms/astar.py` following [research.md](research.md#2-a-algorithm-implementation-strategy).

**Verify**:
```bash
pytest tests/algorithms/test_astar.py
mypy src/algorithms/astar.py
```

### Step 9: Implement Dijkstra Algorithm

Similar TDD workflow to A*. See [contracts/algorithm_contracts.py](contracts/algorithm_contracts.py).

**Verify both algorithms produce same path lengths**:
```python
def test_astar_dijkstra_same_distance():
    graph = build_test_graph()
    start, goal = graph.nodes()[0], graph.nodes()[-1]
    
    astar_result = astar(graph, start, goal, euclidean_distance)
    dijkstra_result = dijkstra(graph, start, goal)
    
    assert astar_result.route.total_distance == dijkstra_result.route.total_distance
```

## Phase 3: Service Layer Implementation

### Step 10: Implement Configuration

Create `src/utils/config.py`:

```python
import os
from dotenv import load_dotenv
import googlemaps

load_dotenv()

def load_api_key() -> str:
    """Load Google Maps API key from environment"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_MAPS_API_KEY not set in environment")
    if not api_key.startswith("AIza"):
        raise ValueError("Invalid Google Maps API key format")
    return api_key

def create_gmaps_client() -> googlemaps.Client:
    """Create authenticated Google Maps client with timeout"""
    api_key = load_api_key()
    return googlemaps.Client(key=api_key, timeout=5)
```

### Step 11: Implement Geocoding Service

Following [contracts/service_contracts.py](contracts/service_contracts.py):

Create `src/services/geocoding.py` with TDD approach (tests first, then implementation).

### Step 12: Implement Routing Service

Create `src/services/routing.py` following contracts.

## Phase 4: UI Implementation

### Step 13: Implement Main Application

Create `main.py`:

```python
import streamlit as st
from src.ui.input_form import render_input_form
from src.ui.map_display import render_dual_maps
from src.ui.metrics_display import render_metrics_table
from src.services.geocoding import geocode_address
from src.services.routing import get_route_graph
from src.algorithms.astar import astar
from src.algorithms.dijkstra import dijkstra
from src.algorithms.heuristics import euclidean_distance
from src.utils.config import create_gmaps_client

st.set_page_config(
    page_title="Route Pathfinding Visualizer",
    layout="wide",
    page_icon="🗺️"
)

def main():
    st.title("🗺️ Route Pathfinding Visualizer")
    st.subheader("Compare A* and Dijkstra Algorithms")
    
    # Input form
    start, dest, clicked = render_input_form()
    
    if clicked and start and dest:
        with st.spinner("Calculating routes..."):
            try:
                # Geocode
                client = create_gmaps_client()
                start_loc = geocode_address(client, start)
                dest_loc = geocode_address(client, dest)
                
                # Build graph
                graph = get_route_graph(client, start_loc, dest_loc)
                
                # Run algorithms
                astar_result = astar(graph, graph.nodes()[0], graph.nodes()[-1], euclidean_distance)
                dijkstra_result = dijkstra(graph, graph.nodes()[0], graph.nodes()[-1])
                
                # Display results
                render_dual_maps(astar_result, dijkstra_result, start_loc, dest_loc)
                render_metrics_table(astar_result, dijkstra_result)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
```

### Step 14: Implement UI Components

Create each UI component in `src/ui/` following [contracts/ui_contracts.py](contracts/ui_contracts.py).

## Phase 5: Testing & Quality

### Step 15: Run Full Test Suite

```bash
# Unit tests
pytest tests/algorithms/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to verify 90% algorithm, 75% UI coverage
```

### Step 16: Code Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/ --strict

# Linting
pylint src/ --fail-under=8.5
```

### Step 17: Performance Benchmarks

```bash
pytest tests/performance/ -v
# Verify algorithms complete 100-node graphs in ≤2s
```

## Running the Application

```bash
# Start Streamlit app
uv run streamlit run main.py

# Or with pip
streamlit run main.py
```

Navigate to http://localhost:8501 and test with:
- **Start**: "Times Square, New York"
- **Destination**: "Central Park, New York"

## Troubleshooting

### Issue: "GOOGLE_MAPS_API_KEY not set"
**Solution**: Create `.env` file with your API key.

### Issue: Tests failing with import errors
**Solution**: Ensure `__init__.py` files exist in all packages.

### Issue: Geocoding errors
**Solution**: Verify API key has Geocoding API enabled in Google Cloud Console.

### Issue: Type errors with mypy
**Solution**: Add type stubs or ignore specific libraries in `pyproject.toml`.

## Next Steps

After completing quickstart:

1. **Run `/speckit.tasks` command** to generate detailed implementation task list
2. **Implement tasks in order** following TDD workflow
3. **Commit frequently** with descriptive messages
4. **Test coverage** - verify 90% algorithms, 75% UI before merging

## Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [Google Maps Platform](https://developers.google.com/maps)
- [Pytest Documentation](https://docs.pytest.org)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)

**Ready to implement!** Follow TDD workflow: tests → implementation → refactor.
