# Service Contracts

**Module**: `src/services/`  
**Purpose**: External service integrations (Google Maps APIs, map rendering)

## Geocoding Service

```python
def geocode_address(
    client: googlemaps.Client,
    address: str
) -> Location:
    """
    Convert address string to geographic coordinates.
    
    Args:
        client: Authenticated Google Maps client
        address: Human-readable address (e.g., "Times Square, New York")
        
    Returns:
        Location with formatted address and lat/lng coordinates
        
    Raises:
        ValueError: If address is empty or whitespace-only
        InvalidLocationError: If address not found by geocoding API
        APIError: If Google Maps API fails (network, quota, timeout)
        
    Performance:
        - Timeout: 5 seconds per Constitution
        - Caching: Results cached via @lru_cache (max 100 addresses)
        
    Example:
        >>> from googlemaps import Client
        >>> client = Client(key=API_KEY)
        >>> loc = geocode_address(client, "Times Square, New York")
        >>> assert loc.address == "Times Square, Manhattan, NY 10036, USA"
        >>> assert 40.757 < loc.latitude < 40.759
        >>> assert -73.987 < loc.longitude < -73.985
    """
```

**Contract Tests**:
```python
def test_geocode_valid_address(mock_gmaps_client):
    """Contract: Returns Location for valid address"""
    result = geocode_address(mock_gmaps_client, "Times Square, New York")
    
    assert isinstance(result, Location)
    assert result.address != ""
    assert -90 <= result.latitude <= 90
    assert -180 <= result.longitude <= 180

def test_geocode_empty_address():
    """Contract: Raises ValueError for empty address"""
    with pytest.raises(ValueError, match="empty"):
        geocode_address(mock_gmaps_client, "")

def test_geocode_invalid_address(mock_gmaps_client):
    """Contract: Raises InvalidLocationError for non-existent address"""
    mock_gmaps_client.geocode.return_value = []  # No results
    
    with pytest.raises(InvalidLocationError, match="not found"):
        geocode_address(mock_gmaps_client, "asdfghjkl123")

def test_geocode_api_timeout(mock_gmaps_client):
    """Contract: Raises APIError on timeout"""
    mock_gmaps_client.geocode.side_effect = googlemaps.exceptions.Timeout
    
    with pytest.raises(APIError, match="timeout"):
        geocode_address(mock_gmaps_client, "Some Address")
```

---

## Routing Service

```python
def get_route_graph(
    client: googlemaps.Client,
    start: Location,
    destination: Location
) -> Graph:
    """
    Build graph from Google Maps Directions API route.
    
    Args:
        client: Authenticated Google Maps client
        start: Starting location with coordinates
        destination: Destination location with coordinates
        
    Returns:
        Graph with nodes for route waypoints and edges for road segments
        
    Raises:
        ValueError: If start or destination has invalid coordinates
        NoRouteError: If no route exists between locations
        APIError: If Directions API fails
        
    Behavior:
        - Uses driving mode (car routes)
        - Single route (alternatives=False)
        - Parses route steps into graph nodes/edges
        - Edge weights are distances in meters
        
    Performance:
        - Timeout: 5 seconds
        - Expected graph size: 10-100 nodes for typical city routes
        
    Example:
        >>> start = Location("Start", 40.7580, -73.9855)
        >>> dest = Location("End", 40.7829, -73.9654)
        >>> graph = get_route_graph(client, start, dest)
        >>> assert graph.node_count() > 0
        >>> assert graph.edge_count() > 0
    """
```

**Contract Tests**:
```python
def test_route_graph_creation(mock_gmaps_client, sample_directions_response):
    """Contract: Returns valid Graph with nodes and edges"""
    mock_gmaps_client.directions.return_value = sample_directions_response
    
    start = Location("A", 40.7580, -73.9855)
    dest = Location("B", 40.7829, -73.9654)
    
    graph = get_route_graph(mock_gmaps_client, start, dest)
    
    assert isinstance(graph, Graph)
    assert graph.node_count() > 0
    assert graph.edge_count() > 0

def test_route_graph_no_route(mock_gmaps_client):
    """Contract: Raises NoRouteError when no route exists"""
    mock_gmaps_client.directions.return_value = []  # No routes
    
    start = Location("Island1", 0, 0)
    dest = Location("Island2", 90, 180)
    
    with pytest.raises(NoRouteError, match="No route found"):
        get_route_graph(mock_gmaps_client, start, dest)
```

---

## Map Rendering Service

```python
def create_route_map(
    route: Route,
    start: Location,
    destination: Location,
    algorithm: str
) -> folium.Map:
    """
    Generate Folium map with visualized route.
    
    Args:
        route: Calculated route with path nodes
        start: Starting location (for green marker)
        destination: Ending location (for red marker)
        algorithm: "A*" or "Dijkstra" (determines route color)
        
    Returns:
        Folium Map object with:
        - Route polyline (blue for A*, red for Dijkstra)
        - Start marker (green pin)
        - Destination marker (red pin)
        - Legend showing algorithm and colors
        
    Map Properties:
        - Centered on route midpoint
        - Zoom level auto-calculated to fit entire route
        - Stroke width: 4px, opacity: 0.8
        - Tile layer: OpenStreetMap or Google Maps
        
    Example:
        >>> route = Route(path=[n1, n2, n3], ...)
        >>> start = Location("Start", 40.7580, -73.9855)
        >>> dest = Location("End", 40.7829, -73.9654)
        >>> map_obj = create_route_map(route, start, dest, "A*")
        >>> assert isinstance(map_obj, folium.Map)
        >>> # Verify map contains polyline and markers
    """
```

**Contract Tests**:
```python
def test_create_route_map_astar():
    """Contract: Creates map with blue route for A*"""
    route = create_sample_route(algorithm="A*")
    start = Location("S", 0, 0)
    dest = Location("D", 1, 1)
    
    map_obj = create_route_map(route, start, dest, "A*")
    
    assert isinstance(map_obj, folium.Map)
    # Verify blue color (#4285F4) in map HTML
    html = map_obj._repr_html_()
    assert "#4285F4" in html  # A* blue color

def test_create_route_map_dijkstra():
    """Contract: Creates map with red route for Dijkstra"""
    route = create_sample_route(algorithm="Dijkstra")
    start = Location("S", 0, 0)
    dest = Location("D", 1, 1)
    
    map_obj = create_route_map(route, start, dest, "Dijkstra")
    
    html = map_obj._repr_html_()
    assert "#EA4335" in html  # Dijkstra red color
```

---

## Configuration Service

```python
def load_api_key() -> str:
    """
    Load Google Maps API key from environment.
    
    Returns:
        API key string from GOOGLE_MAPS_API_KEY environment variable
        
    Raises:
        EnvironmentError: If GOOGLE_MAPS_API_KEY not set
        
    Usage:
        - Reads from .env file via python-dotenv
        - Never log or display API key
        - Validate key format (starts with "AIza")
        
    Example:
        >>> api_key = load_api_key()
        >>> assert api_key.startswith("AIza")
    """

def create_gmaps_client() -> googlemaps.Client:
    """
    Create authenticated Google Maps client.
    
    Returns:
        googlemaps.Client configured with API key and timeout
        
    Configuration:
        - Timeout: 5 seconds per request
        - Retry: 3 attempts on network errors
        
    Example:
        >>> client = create_gmaps_client()
        >>> assert isinstance(client, googlemaps.Client)
    """
```

---

## Error Hierarchy

```python
class InvalidLocationError(ValueError):
    """Raised when geocoding fails to find address"""
    pass

class NoRouteError(ValueError):
    """Raised when no route exists between locations"""
    pass

class APIError(Exception):
    """Raised when Google Maps API fails (network, quota, timeout)"""
    pass

class QuotaExceededError(APIError):
    """Raised when API quota limit reached"""
    pass
```

**Error Contract Tests**:
```python
def test_invalid_location_error():
    """Contract: InvalidLocationError is ValueError subclass"""
    error = InvalidLocationError("Not found")
    assert isinstance(error, ValueError)

def test_api_error_message():
    """Contract: APIError includes descriptive message"""
    error = APIError("Timeout after 5s")
    assert "Timeout" in str(error)
```

---

## Performance Contracts

```python
@pytest.mark.integration
def test_geocoding_timeout():
    """Contract: Geocoding respects 5-second timeout"""
    client = create_gmaps_client()  # Real client for integration test
    
    start = time.perf_counter()
    try:
        # Simulate slow API by using invalid key (triggers timeout)
        geocode_address(client, "Some Address")
    except APIError:
        pass
    elapsed = time.perf_counter() - start
    
    assert elapsed <= 6.0, "Geocoding exceeded 5s timeout + 1s grace"

@pytest.mark.integration
@pytest.mark.slow
def test_full_workflow_performance():
    """Contract: Full geocode → route → graph workflow in ≤10s"""
    client = create_gmaps_client()
    
    start_time = time.perf_counter()
    
    start_loc = geocode_address(client, "Times Square, New York")
    dest_loc = geocode_address(client, "Central Park, New York")
    graph = get_route_graph(client, start_loc, dest_loc)
    
    elapsed = time.perf_counter() - start_time
    
    assert elapsed <= 10.0, f"Workflow took {elapsed}s, expected ≤10s"
    assert graph.node_count() > 0
```

---

## Summary

| Function | Purpose | Timeout | Errors |
|----------|---------|---------|--------|
| `geocode_address()` | Address → Location | 5s | ValueError, InvalidLocationError, APIError |
| `get_route_graph()` | Directions → Graph | 5s | NoRouteError, APIError |
| `create_route_map()` | Route → Folium Map | N/A | ValueError (invalid route) |
| `load_api_key()` | Load ENV config | N/A | EnvironmentError |
| `create_gmaps_client()` | Create API client | N/A | EnvironmentError |

**Contract Validation**: All contracts tested in `tests/integration/test_api_integration.py` with mocked and real API calls.
