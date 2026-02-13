# UI Contracts

**Module**: `src/ui/`  
**Purpose**: Streamlit user interface components

## Input Form Component

```python
def render_input_form() -> Tuple[str, str, bool]:
    """
    Render input form for start/destination addresses.
    
    Returns:
        Tuple of (start_address, destination_address, calculate_clicked)
        - start_address: Text from start input field
        - destination_address: Text from destination input field
        - calculate_clicked: True if "Calculate Routes" button clicked
        
    UI Elements:
        - Two text input fields side-by-side (st.columns)
        - "Calculate Routes" button (primary style)
        - Input placeholders with example addresses
        
    Validation (displayed inline):
        - If calculate clicked with empty fields → st.error()
        
    Example:
        >>> # In Streamlit app
        >>> start, dest, clicked = render_input_form()
        >>> if clicked and start and dest:
        >>>     # Process inputs
    """
```

**Behavior Contract**:
- Input fields persist values across Streamlit reruns (using st.session_state)
- Button is disabled while routes are calculating (prevent duplicate requests)
- Placeholder text: "e.g., Times Square, New York"

---

## Map Display Component

```python
def render_dual_maps(
    astar_result: PathfindingResult,
    dijkstra_result: PathfindingResult,
    start: Location,
    destination: Location
) -> None:
    """
    Render side-by-side maps for A* and Dijkstra results.
    
    Args:
        astar_result: Result from A* algorithm
        dijkstra_result: Result from Dijkstra algorithm  
        start: Starting location (for markers)
        destination: Destination location (for markers)
        
    UI Layout:
        - Two columns (st.columns)
        - Left column: A* algorithm map (blue route)
        - Right column: Dijkstra algorithm map (red route)
        - Each column has subheader with algorithm name
        
    Error Handling:
        - If astar_result.success == False → display st.warning() with error
        - If dijkstra_result.success == False → display st.warning() with error
        - If both fail → display st.error() suggesting different addresses
        
    Map Properties:
        - Both maps same zoom level and center for fair comparison
        - Width: 500px, Height: 400px
        - Rendered via streamlit-folium component
        
    Example:
        >>> render_dual_maps(astar_res, dijkstra_res, start_loc, dest_loc)
        >>> # Displays two maps in Streamlit UI
    """
```

**Contract Tests** (UI testing with Streamlit requires manual verification):
```python
# Manual test checklist (tests/ui/test_map_display.py)
def test_dual_maps_display_checklist():
    """
    Manual Test Checklist for render_dual_maps:
    
    [ ] Both maps visible side-by-side on desktop (≥1024px width)
    [ ] Maps stack vertically on mobile (<1024px width)
    [ ] A* map shows blue route (#4285F4)
    [ ] Dijkstra map shows red route (#EA4335)
    [ ] Both maps have start marker (green) and destination marker (red)
    [ ] Maps are centered on route midpoint
    [ ] Zoom level shows entire route
    [ ] If algorithm fails, warning message displayed instead of map
    """
```

---

## Metrics Display Component

```python
def render_metrics_table(
    astar_result: PathfindingResult,
    dijkstra_result: PathfindingResult
) -> None:
    """
    Render performance comparison table.
    
    Args:
        astar_result: Result from A* algorithm (must have success=True)
        dijkstra_result: Result from Dijkstra algorithm (must have success=True)
        
    UI Elements:
        - Subheader: "Performance Comparison"
        - Table with 3 rows × 3 columns:
          | Metric | A* | Dijkstra |
          |--------|-------|----------|
          | Execution Time | Xms | Yms |
          | Nodes Explored | N | M |
          | Path Length | Z km | Z km |
        - Summary text highlighting winner (e.g., "A* was 2.7× faster")
        
    Formatting:
        - Execution time in milliseconds (integer)
        - Nodes explored as integer count
        - Path length in kilometers (1 decimal place)
        - Winner highlighted with st.success() if performance delta > 20%
        
    Example:
        >>> render_metrics_table(astar_res, dijkstra_res)
        >>> # Displays comparison table in Streamlit UI
    """
```

**Metrics Calculation Contract**:
```python
def calculate_performance_summary(
    astar_route: Route,
    dijkstra_route: Route
) -> Dict[str, Any]:
    """
    Calculate comparative performance metrics.
    
    Returns:
        Dict with keys:
        - 'faster_algorithm': "A*" or "Dijkstra"
        - 'speedup_factor': float (e.g., 2.7 means 2.7× faster)
        - 'node_reduction_pct': float (e.g., 60.0 means 60% fewer nodes)
        - 'path_length_match': bool (True if distances within 0.1%)
        
    Example:
        >>> summary = calculate_performance_summary(astar_route, dijkstra_route)
        >>> assert summary['faster_algorithm'] == "A*"
        >>> assert summary['speedup_factor'] > 1.0
        >>> assert summary['path_length_match'] == True
    """
```

---

## Loading Indicator Component

```python
@contextmanager
def show_loading(message: str = "Calculating routes...") -> None:
    """
    Display loading spinner during route calculation.
    
    Args:
        message: Text to show below spinner
        
    Usage:
        >>> with show_loading("Calculating routes..."):
        >>>     # Perform long-running operation
        >>>     results = calculate_routes(start, dest)
        >>> # Spinner automatically hidden after block completes
    """
```

**Contract**: 
- Spinner visible during context block execution
- Spinner hidden when context exits (even on exception)
- Message displayed below spinner animation

---

## Error Display Component

```python
def display_error(error_type: str, message: str) -> None:
    """
    Display user-friendly error message.
    
    Args:
        error_type: Category of error ("validation", "api", "routing")
        message: Error message to display
        
    Error Styles:
        - "validation" → st.warning() (yellow, user input issue)
        - "api" → st.error() (red, system failure)
        - "routing" → st.info() (blue, informational - no route exists)
        
    User Guidance:
        - Validation errors suggest fixes (e.g., "Enter both addresses")
        - API errors suggest retry (e.g., "Try again in a moment")
        - Routing errors suggest alternatives (e.g., "Try different addresses")
        
    Example:
        >>> display_error("validation", "Start address cannot be empty")
        >>> # Shows yellow warning box with message
    """
```

**Error Message Contracts**:
```python
# tests/ui/test_error_messages.py
def test_error_messages_follow_ux_principles():
    """
    Error Message Contract Tests:
    
    [ ] All messages start with what happened (not technical details)
    [ ] All messages suggest what user should do next
    [ ] No stack traces or technical jargon shown to user
    [ ] Messages use friendly tone (not "ERROR:" or "FAILED")
    
    Examples:
    ✅ "Address not found. Please enter a valid location."
    ✅ "Service temporarily unavailable. Please try again in a moment."
    ❌ "GeocodeError: Invalid API response format"
    ❌ "FATAL: NoneType object has no attribute 'coordinates'"
    """
```

---

## Session State Management

```python
def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables.
    
    Session Variables:
        - 'start_address': str (persisted text input)
        - 'dest_address': str (persisted text input)
        - 'last_results': Optional[Tuple[PathfindingResult, PathfindingResult]]
        - 'calculation_count': int (for analytics)
        
    Called at start of main() to ensure variables exist.
    """

def cache_results(
    astar_result: PathfindingResult,
    dijkstra_result: PathfindingResult
) -> None:
    """
    Store results in session state to prevent recalculation.
    
    Args:
        astar_result: A* algorithm result
        dijkstra_result: Dijkstra algorithm result
        
    Caching Strategy:
        - Results stored until new calculation triggered
        - Prevents re-running algorithms on UI interactions
        - Cleared when input addresses change
    """
```

---

## Main Application Contract

```python
def main() -> None:
    """
    Main Streamlit application entry point.
    
    Execution Flow:
        1. Configure Streamlit page (title, layout, icon)
        2. Initialize session state
        3. Render input form
        4. If calculate clicked and inputs valid:
           a. Show loading indicator
           b. Geocode addresses
           c. Build route graph
           d. Run A* and Dijkstra algorithms
           e. Cache results
        5. If results available, render:
           a. Dual maps
           b. Metrics table
        6. Handle errors with user-friendly messages
        
    Error Recovery:
        - Geocoding errors → display error, keep UI functional
        - API timeouts → suggest retry
        - Routing failures → suggest different addresses
        - Exceptions caught and logged, never crash UI
        
    Page Configuration:
        - Title: "Route Pathfinding Visualizer"
        - Layout: "wide" (full-width for dual maps)
        - Icon: 🗺️ (map emoji)
    """
```

**Application Contract Tests**:
```python
# Manual UI testing checklist
def test_application_workflow():
    """
    End-to-End UI Workflow Contract:
    
    [ ] Page loads with title and empty inputs
    [ ] Entering start/destination enables Calculate button
    [ ] Clicking Calculate shows loading spinner
    [ ] After calculation, two maps appear side-by-side
    [ ] Metrics table appears below maps
    [ ] Invalid address shows appropriate error
    [ ] Empty inputs show validation warning
    [ ] API failure shows error with retry suggestion
    [ ] Results persist when scrolling/interacting with UI
    [ ] New calculation replaces old results
    """
```

---

## Performance Contracts

```python
@pytest.mark.ui
def test_ui_rendering_performance():
    """
    Contract: UI renders in ≤1 second after algorithms complete.
    
    Measures time from:
    - Algorithm completion → Folium map generation → Streamlit display
    
    Expected: ≤1000ms total rendering time
    """
```

---

## Summary

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `render_input_form()` | User address inputs | None | (start, dest, clicked) |
| `render_dual_maps()` | Display algorithm routes | PathfindingResults × 2 | None (UI update) |
| `render_metrics_table()` | Performance comparison | PathfindingResults × 2 | None (UI update) |
| `show_loading()` | Loading indicator | message | Context manager |
| `display_error()` | Error messages | error_type, message | None (UI update) |
| `main()` | Application entry | None | None (runs app) |

**Contract Validation**: UI contracts validated through manual testing checklist and automated UI performance tests (where applicable).

**Constitution Alignment**: All UI components comply with Principle III (User Experience Consistency) - input validation, visual feedback, error handling, responsive design.
