---
description: "Task list for Dual-Map Route Visualizer implementation"
---

# Tasks: Dual-Map Route Visualizer

**Input**: Design documents from `/specs/1-route-visualizer/`  
**Prerequisites**: plan.md (tech stack), spec.md (user stories), data-model.md (entities), contracts/ (function interfaces), research.md (decisions), quickstart.md (test scenarios)

**Constitution Compliance**: All tasks support TDD workflow (tests first), 90% algorithm coverage, 75% UI coverage, code quality standards (black, isort, mypy ≥strict, pylint ≥8.5)

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: `- [ ]` for incomplete, `- [x]` for complete
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3) - only for user story phase tasks
- **File paths**: All descriptions include exact file paths

## Path Conventions

**Single project structure** (from plan.md):
- Source: `src/algorithms/`, `src/services/`, `src/ui/`, `src/utils/`
- Tests: `tests/algorithms/`, `tests/integration/`, `tests/performance/`
- Root: `main.py`, `pyproject.toml`, `.env`, `.env.example`

---

## Implementation Strategy

**MVP-First Approach**: Deliver User Story 1 (P1) as complete, independently testable MVP before adding P2 and P3 enhancements.

**Independent Testing**: Each user story phase includes independent test criteria to verify that story works standalone.

**Parallel Execution**: Tasks marked `[P]` can be executed concurrently (different files, no blocking dependencies).

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and development environment

- [x] T001 Create project directory structure per plan.md (src/{algorithms,services,ui,utils}, tests/{algorithms,integration,performance})
- [x] T002 Initialize Python project with pyproject.toml including dependencies (streamlit, folium, googlemaps, networkx, pytest, black, isort, mypy, pylint)
- [x] T003 [P] Create .env.example template file with GOOGLE_MAPS_API_KEY placeholder
- [x] T004 [P] Configure code quality tools in pyproject.toml (black line-length=100, isort profile=black, mypy strict=true, pylint fail-under=8.5, pytest cov-fail-under=85)
- [x] T005 [P] Create .gitignore file with entries for .env, __pycache__, .venv, htmlcov/, .coverage, .mypy_cache/
- [x] T006 [P] Create all __init__.py files in src/ and tests/ directories

**Checkpoint**: Project structure complete, dependencies installable via `uv sync` or `pip install`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Constitution Alignment**:
- Code Quality: Type definitions, graph data structures with type hints
- Testing: pytest configuration, fixtures for test data
- Performance: Adjacency list graph (O(V+E) memory), priority queue utilities
- Algorithm Correctness: Test fixtures with known shortest paths

### Foundational Setup

- [x] T007 Create src/utils/types.py with Location dataclass (address: str, latitude: float, longitude: float) including validation
- [x] T008 [P] Add Route dataclass to src/utils/types.py (path: List[Node], total_distance: float, algorithm: str, execution_time: int, nodes_explored: int)
- [x] T009 [P] Add PathfindingResult dataclass to src/utils/types.py (success: bool, route: Optional[Route], error: Optional[str]) with validation
- [x] T010 [P] Create src/utils/config.py with load_api_key() and create_gmaps_client() functions using python-dotenv
- [x] T011 [P] Create src/utils/validators.py with address validation helper functions

### Graph Data Structure (Required for Algorithms)

- [x] T012 Write tests in tests/algorithms/test_graph.py for Node creation, equality, hashing (TDD: tests first)
- [x] T013 Write tests in tests/algorithms/test_graph.py for Graph add_node(), add_edge(), neighbors(), nodes() methods
- [x] T014 Write tests in tests/algorithms/test_graph.py for bidirectional edges and negative weight rejection
- [x] T015 Implement Node dataclass in src/algorithms/graph.py (@dataclass frozen=True, with __hash__ and __eq__)
- [x] T016 Implement Edge dataclass in src/algorithms/graph.py with weight validation (__post_init__ checks weight > 0)
- [x] T017 Implement Graph class in src/algorithms/graph.py with adjacency list (_adjacency: Dict[Node, List[Tuple[Node, float]]])
- [x] T018 Verify all graph tests pass and achieve >95% coverage for src/algorithms/graph.py

### Heuristic Functions (Required for A*)

- [x] T019 [P] Write tests in tests/algorithms/test_heuristics.py for euclidean_distance (same node=0, different nodes>0, admissibility)
- [x] T020 [P] Write tests in tests/algorithms/test_heuristics.py for manhattan_distance and diagonal_distance
- [x] T021 [P] Implement euclidean_distance() in src/algorithms/heuristics.py using Haversine formula for lat/lng
- [x] T022 [P] Implement manhattan_distance() and diagonal_distance() in src/algorithms/heuristics.py
- [x] T023 [P] Verify heuristic tests pass with >90% coverage

### Test Infrastructure

- [x] T024 [P] Create tests/conftest.py with pytest fixtures: simple_grid_graph (3x3 test graph), known_shortest_path (graph with verified optimal path)
- [x] T025 [P] Add mock_gmaps_client fixture to tests/conftest.py for unit testing services without API calls
- [x] T026 [P] Configure pytest.ini or pyproject.toml with test markers (unit, integration, slow, benchmark)

**Checkpoint**: Foundation ready - all data structures, utilities, and test infrastructure in place. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Basic Route Visualization (Priority: P1) 🎯 MVP

**Goal**: Implement core functionality - users can enter addresses, view dual maps with A*/Dijkstra routes, and see distance/time metrics

**Independent Test**: Enter "Times Square, New York" → "Central Park, New York", verify two maps appear with distinct blue (A*) and red (Dijkstra) routes, and distance/time shown below each map

**Constitution Requirements**: TDD mandatory, 90% algorithm coverage, user-friendly error handling, ≤2s execution time

### Algorithms Implementation (Core US1 Functionality)

#### A* Algorithm

- [x] T027 [P] [US1] Write unit tests in tests/algorithms/test_astar.py for astar() function (connected graph→success, disconnected→failure, same start/goal→zero distance)
- [x] T028 [P] [US1] Write correctness tests in tests/algorithms/test_astar.py verifying optimal paths on known test graphs (3x3 grid with expected distance)
- [x] T029 [P] [US1] Write edge case tests in tests/algorithms/test_astar.py (invalid nodes, None heuristic, empty graph)
- [x] T030 [US1] Implement astar() function in src/algorithms/astar.py using heapq priority queue, admissible heuristic, returning PathfindingResult
- [x] T031 [US1] Add type hints to src/algorithms/astar.py and verify mypy passes with --strict mode
- [x] T032 [US1] Add comprehensive docstrings to astar() following contract in contracts/algorithm_contracts.py
- [x] T033 [US1] Verify all A* tests pass and coverage >90% for src/algorithms/astar.py

#### Dijkstra Algorithm

- [x] T034 [P] [US1] Write unit tests in tests/algorithms/test_dijkstra.py for dijkstra() function (same structure as A* tests)
- [x] T035 [P] [US1] Write correctness tests in tests/algorithms/test_dijkstra.py verifying optimal paths match A* distances
- [x] T036 [P] [US1] Write edge case tests in tests/algorithms/test_dijkstra.py (negative weights→error, unreachable nodes)
- [x] T037 [US1] Implement dijkstra() function in src/algorithms/dijkstra.py using heapq priority queue, returning PathfindingResult
- [x] T038 [US1] Add type hints and docstrings to src/algorithms/dijkstra.py per contract
- [x] T039 [US1] Verify all Dijkstra tests pass and coverage >90% for src/algorithms/dijkstra.py

#### Algorithm Comparison Tests

- [x] T040 [US1] Write comparative test in tests/algorithms/test_astar.py verifying A* and Dijkstra produce identical path lengths on same graph
- [x] T041 [US1] Write performance comparison test verifying A* explores fewer nodes than Dijkstra (demonstrates heuristic efficiency)

### Services Implementation (US1 Dependencies)

#### Geocoding Service

- [x] T042 [P] [US1] Write unit tests in tests/integration/test_geocoding.py for geocode_address() (valid address, invalid address→error, empty string→ValueError)
- [x] T043 [P] [US1] Write tests for API timeout and quota exceeded scenarios
- [x] T044 [US1] Implement geocode_address() in src/services/geocoding.py using googlemaps client, returning Location
- [x] T045 [US1] Add InvalidLocationError and APIError exception classes to src/services/geocoding.py
- [x] T046 [US1] Implement @lru_cache(maxsize=100) for geocoding results to reduce API calls
- [x] T047 [US1] Add type hints, docstrings, verify mypy passes for src/services/geocoding.py

#### Routing Service

- [x] T048 [P] [US1] Write unit tests in tests/integration/test_routing.py for get_route_graph() (valid locations→Graph, no route→NoRouteError)
- [x] T049 [P] [US1] Write tests for parsing Google Directions API response into Graph nodes/edges
- [x] T050 [US1] Implement get_route_graph() in src/services/routing.py converting Directions API steps to Graph
- [x] T051 [US1] Add NoRouteError exception class and error handling for API failures
- [x] T052 [US1] Add type hints, docstrings, verify mypy passes for src/services/routing.py

#### Map Rendering Service

- [x] T053 [P] [US1] Write unit tests in tests/integration/test_map_renderer.py for create_route_map() (verify folium.Map created, blue for A*, red for Dijkstra)
- [x] T054 [P] [US1] Write tests verifying start marker (green) and destination marker (red) are added to maps
- [x] T055 [US1] Implement create_route_map() in src/services/map_renderer.py using folium polylines with color/weight/opacity
- [x] T056 [US1] Add route path polyline with stroke-width=4px, opacity=0.8, color based on algorithm (A*=#4285F4, Dijkstra=#EA4335)
- [x] T057 [US1] Add start/destination markers with custom icons and tooltips
- [x] T058 [US1] Configure map centering and zoom level to fit entire route
- [x] T059 [US1] Add type hints, docstrings, verify mypy passes for src/services/map_renderer.py

### UI Implementation (US1 User Interface)

#### Input Form Component

- [x] T060 [P] [US1] Implement render_input_form() in src/ui/input_form.py with two text inputs (st.text_input) and Calculate button (st.button)
- [x] T061 [P] [US1] Add input placeholders "e.g., Times Square, New York" to guide user entry
- [x] T062 [P] [US1] Configure button to be disabled during processing (prevent duplicate requests)
- [x] T063 [P] [US1] Return tuple (start_address: str, dest_address: str, calculate_clicked: bool)
- [x] T064 [P] [US1] Add type hints and docstrings to src/ui/input_form.py

#### Map Display Component

- [x] T065 [P] [US1] Implement render_dual_maps() in src/ui/map_display.py using st.columns for side-by-side layout
- [x] T066 [P] [US1] Add subheaders "A* Algorithm" and "Dijkstra Algorithm" above each map
- [x] T067 [P] [US1] Integrate streamlit-folium to render folium maps in Streamlit (st_folium)
- [x] T068 [P] [US1] Configure map width=500px, height=400px for each column
- [x] T069 [P] [US1] Add type hints and docstrings to src/ui/map_display.py

#### Metrics Display Component

- [x] T070 [P] [US1] Implement render_metrics_table() in src/ui/metrics_display.py creating comparison table with st.table()
- [x] T071 [P] [US1] Add three rows: "Execution Time (ms)", "Path Length (km)", "Nodes Explored" (defer nodes explored to US3)
- [x] T072 [P] [US1] Format distance to 2 decimal places, time as integer milliseconds
- [x] T073 [P] [US1] Add type hints and docstrings to src/ui/metrics_display.py

#### Main Application

- [x] T074 [US1] Create main.py with st.set_page_config(title="Route Pathfinding Visualizer", layout="wide", page_icon="🗺️")
- [x] T075 [US1] Implement main() function orchestrating workflow: input→geocode→graph→algorithms→display
- [x] T076 [US1] Add st.spinner("Calculating routes...") context manager during processing
- [x] T077 [US1] Integrate all components: render_input_form, geocode_address, get_route_graph, astar, dijkstra, create_route_map, render_dual_maps, render_metrics_table
- [x] T078 [US1] Add basic exception handling with st.error() for unhandled errors
- [x] T079 [US1] Add type hints and verify mypy passes for main.py

### US1 Integration Testing

- [x] T080 [US1] Write end-to-end test in tests/integration/test_end_to_end.py simulating full user journey with mock API (input→geocode→graph→algorithms→results)
- [x] T081 [US1] Verify integration test achieves >75% coverage for UI components
- [x] T082 [US1] Manual UI test: Run `streamlit run main.py`, enter Times Square→Central Park, verify dual maps appear with routes

**US1 Checkpoint**: At this point, User Story 1 (P1) is fully functional and testable independently. MVP delivers core value: dual-map algorithm comparison visualization.

**US1 Independent Test Criteria**:
- ✅ User can enter two addresses and click Calculate
- ✅ Two maps appear side-by-side with distinct routes (blue A*, red Dijkstra)
- ✅ Distance and execution time displayed below each map
- ✅ Routes complete within 5 seconds for typical city pairs
- ✅ All algorithm tests pass with >90% coverage
- ✅ UI components pass with >75% coverage

---

## Phase 4: User Story 2 - Input Validation and Error Handling (Priority: P2)

**Goal**: Add robust validation and user-friendly error messages for invalid inputs, API failures, and edge cases

**Independent Test**: Enter invalid address "asdfghjkl", verify error message "Start address not found. Please enter a valid location." appears without crashing

**Constitution Requirements**: UX Consistency principle - clear error messages, no crashes, suggested actions

### Validation Layer

- [x] T083 [P] [US2] Write tests in tests/unit/test_validators.py for validate_non_empty_addresses() (empty string→error, whitespace→error, valid→pass)
- [x] T084 [P] [US2] Write tests for validate_coordinates() checking lat/lng ranges (-90≤lat≤90, -180≤lng≤180)
- [x] T085 [P] [US2] Implement validation functions in src/utils/validators.py with descriptive error messages
- [x] T086 [P] [US2] Add type hints and docstrings to src/utils/validators.py

### Error Handling in Services

- [x] T087 [US2] Update geocode_address() in src/services/geocoding.py to catch googlemaps.exceptions (ApiError, Timeout, TransportError)
- [x] T088 [US2] Add specific error messages for each exception type (address not found, timeout, quota exceeded)
- [x] T089 [US2] Update get_route_graph() in src/services/routing.py to handle empty Directions API responses (no route exists)
- [x] T090 [US2] Add error handling for same start/destination location (return zero-distance result)
- [x] T091 [US2] Write tests in tests/integration/ verifying all error scenarios produce appropriate error messages

### UI Error Display

- [x] T092 [P] [US2] Create display_error() function in src/ui/input_form.py using st.error(), st.warning(), st.info() based on error type
- [x] T093 [P] [US2] Update render_input_form() to validate non-empty inputs before allowing calculation
- [x] T094 [US2] Update main() in main.py to catch all exception types and display user-friendly messages
- [x] T095 [US2] Add try-except blocks around geocoding with message "Start address not found. Please enter a valid location."
- [x] T096 [US2] Add try-except around routing with message "No route found between these locations. Please try different addresses."
- [x] T097 [US2] Add try-except around API errors with message "Service temporarily unavailable. Please try again in a moment."
- [x] T098 [US2] Implement button disable logic during processing (set disabled=True in session state)

### Edge Case Handling

- [x] T099 [P] [US2] Add check in main.py for identical start/destination addresses, display "Start and destination are the same location. No route needed."
- [x] T100 [P] [US2] Add distance check for very long routes (>500 miles), display warning "Route exceeds 500 miles. Processing may take longer."
- [x] T101 [P] [US2] Test rapid button clicking scenario, verify duplicate requests prevented by button disabling

### US2 Testing

- [x] T102 [US2] Write validation tests in tests/integration/test_error_handling.py for all error scenarios
- [x] T103 [US2] Manual UI test: Enter invalid addresses, verify appropriate error messages appear
- [x] T104 [US2] Manual UI test: Verify application never crashes, always shows error message with suggested action

**US2 Checkpoint**: User Story 2 complete - robust error handling ensures users are guided to successful inputs

**US2 Independent Test Criteria**:
- ✅ Empty input shows "Both addresses are required"
- ✅ Invalid address shows "Address not found. Please enter a valid location."
- ✅ Same start/dest shows "Same location" message
- ✅ API failures show "Service temporarily unavailable"
- ✅ No crashes under any invalid input scenario
- ✅ Button disabled during processing

---

## Phase 5: User Story 3 - Algorithm Performance Comparison (Priority: P3)

**Goal**: Display detailed performance metrics (nodes explored, speedup factor, heuristic efficiency analysis) to demonstrate algorithmic differences

**Independent Test**: Run any route, verify metrics table shows "Nodes Explored" row with A* < Dijkstra and summary "A* was X% faster and explored Y% fewer nodes"

**Constitution Requirements**: Algorithm Correctness principle - comparative analysis, educational transparency

### Enhanced Metrics Collection

- [ ] T105 [P] [US3] Update astar() in src/algorithms/astar.py to track nodes_explored counter (increment on each heappop)
- [ ] T106 [P] [US3] Update dijkstra() in src/algorithms/dijkstra.py to track nodes_explored counter
- [ ] T107 [P] [US3] Verify Route dataclass includes nodes_explored field in src/utils/types.py
- [ ] T108 [P] [US3] Write tests verifying A* explores fewer nodes than Dijkstra on test graphs

### Performance Summary Calculation

- [X] T109 [P] [US3] Create calculate_performance_summary() in src/ui/metrics_display.py
- [X] T110 [P] [US3] Calculate speedup_factor = dijkstra_time / astar_time
- [X] T111 [P] [US3] Calculate node_reduction_pct = (dijkstra_nodes - astar_nodes) / dijkstra_nodes * 100
- [X] T112 [P] [US3] Verify path_length_match = abs(astar_dist - dijkstra_dist) < 0.1% tolerance
- [X] T113 [P] [US3] Add type hints and tests for calculate_performance_summary()

### UI Enhancements

- [X] T114 [US3] Update render_metrics_table() in src/ui/metrics_display.py to add "Nodes Explored" row
- [X] T115 [US3] Add summary section below table with st.success() highlighting winner (e.g., "A* was 2.7× faster")
- [X] T116 [US3] Display node reduction percentage (e.g., "A* explored 60% fewer nodes due to heuristic guidance")
- [X] T117 [US3] Add check that both algorithms produce equal path lengths, display confirmation or warning if mismatch
- [X] T118 [US3] Format metrics with proper units (ms for time, count for nodes, km with 2 decimals for distance)

### Algorithm Tracing (Educational Feature)

- [ ] T119 [US3] Add optional trace_mode parameter to astar() logging algorithm steps (nodes visited, g/h scores)
- [ ] T120 [US3] Add optional trace_mode parameter to dijkstra() logging visited nodes and distances
- [ ] T121 [US3] Create display_algorithm_trace() in src/ui/metrics_display.py showing expandable trace logs with st.expander()
- [ ] T122 [US3] Add checkbox in UI to enable/disable trace mode (st.checkbox("Show algorithm trace"))

### US3 Testing

- [ ] T123 [US3] Write tests in tests/algorithms/ verifying nodes_explored tracking accuracy
- [ ] T124 [US3] Write tests for calculate_performance_summary() with various time/node combinations
- [ ] T125 [US3] Manual UI test: Verify metrics table shows all three rows (time, distance, nodes)
- [ ] T126 [US3] Manual UI test: Verify summary correctly identifies A* as faster and more efficient

**US3 Checkpoint**: User Story 3 complete - educational metrics demonstrate algorithmic differences and heuristic value

**US3 Independent Test Criteria**:
- ✅ Metrics table shows execution time, nodes explored, path length for both algorithms
- ✅ A* explores fewer nodes than Dijkstra (typically 40-60% reduction)
- ✅ Summary highlights performance winner with specific percentages
- ✅ Both algorithms produce equal path lengths (verifies correctness)
- ✅ Optional trace mode available for educational purposes

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements, performance optimization, comprehensive testing, documentation

### Performance Optimization

- [ ] T127 [P] Write performance benchmarks in tests/performance/test_benchmarks.py for 100-node and 1000-node graphs
- [ ] T128 [P] Verify A* completes 100-node graphs in ≤2s on standard hardware
- [ ] T129 [P] Verify Dijkstra completes 100-node graphs in ≤2s
- [ ] T130 [P] Profile algorithm execution with cProfile to identify bottlenecks
- [ ] T131 Optimize graph neighbor lookups if performance target not met (consider caching, data structure improvements)

### Code Quality Final Pass

- [X] T132 [P] Run black formatter on all src/ and tests/ files (black src/ tests/ --line-length 100)
- [X] T133 [P] Run isort on all files (isort src/ tests/ --profile black)
- [ ] T134 [P] Run mypy strict mode on src/ (mypy src/ --strict) and fix all errors
- [X] T135 [P] Run pylint on src/ (pylint src/ --fail-under=8.5) and address warnings to achieve ≥8.5 score
- [X] T136 Verify all type hints are present and accurate
- [X] T137 Verify all public functions have comprehensive docstrings

### Testing Final Pass

- [ ] T138 [P] Run full test suite (pytest tests/ -v) and verify all tests pass
- [ ] T139 [P] Generate coverage report (pytest --cov=src --cov-report=html --cov-report=term-missing)
- [ ] T140 Verify algorithm coverage ≥90% (src/algorithms/)
- [ ] T141 Verify UI coverage ≥75% (src/ui/)
- [ ] T142 Verify overall coverage ≥85%
- [ ] T143 Add missing tests for any uncovered edge cases or error paths
- [ ] T144 Write integration test with real Google Maps API (mark as @pytest.mark.slow, requires API key)

### Documentation

- [X] T145 [P] Update README.md with quickstart instructions (installation, API key setup, running app)
- [X] T146 [P] Add example routes to README.md (Times Square→Central Park, San Francisco City Hall→Golden Gate Bridge)
- [X] T147 [P] Document constitution compliance in README.md (TDD, coverage, code quality)
- [X] T148 [P] Add troubleshooting section to README.md (common errors, solutions)
- [X] T149 Verify .env.example has all required environment variables with descriptive comments
- [X] T150 Add inline code comments explaining complex algorithm logic (priority queue operations, heuristic calculations)

### User Experience Polish

- [X] T151 [P] Add app description and instructions at top of main.py UI ("Compare A* and Dijkstra pathfinding algorithms...")
- [X] T152 [P] Add sidebar with example routes users can click to auto-fill inputs (st.sidebar with example buttons)
- [X] T153 [P] Improve map legends to explain route colors and markers
- [X] T154 [P] Add footer with constitution version and project metadata
- [ ] T155 Test on different screen resolutions (1024px, 1440px, 1920px) and verify responsive layout

### Final Integration

- [ ] T156 End-to-end manual test: Full user journey from empty inputs → valid route → results display
- [ ] T157 End-to-end manual test: All error scenarios handled gracefully
- [ ] T158 End-to-end manual test: All three user stories (US1, US2, US3) work correctly
- [ ] T159 Verify application runs with `uv run streamlit run main.py` without errors
- [ ] T160 Review all code against Constitution checklist (modular, typed, tested, documented, performant)

**Final Checkpoint**: All user stories complete, code quality gates passed, ready for demo/submission

---

## Dependencies & Execution Order

### User Story Completion Order (Sequential)

```
Phase 1: Setup
      ↓
Phase 2: Foundational (Foundation complete before US work)
      ↓
Phase 3: US1 (P1) - Basic Visualization ← MVP DELIVERY
      ↓
Phase 4: US2 (P2) - Validation & Errors
      ↓
Phase 5: US3 (P3) - Performance Metrics
      ↓
Phase 6: Polish & Cross-Cutting
```

### Critical Dependencies

- **Foundational → US1**: Graph, heuristics, types MUST be complete before algorithms
- **Algorithms → Services**: A*/Dijkstra MUST be implemented before services can use them
- **Services → UI**: Geocoding, routing, map rendering MUST work before UI integration
- **US1 → US2**: Core functionality MUST work before adding validation
- **US1 → US3**: Basic metrics MUST exist before enhanced metrics

### Parallel Execution Opportunities

**Within Phase 2 (Foundational)**:
- T007-T011 (type definitions, config, validators) can run in parallel
- T019-T023 (heuristic functions) can run parallel to graph work

**Within Phase 3 (US1)**:
- T027-T033 (A* implementation) parallel to T034-T039 (Dijkstra implementation)
- T042-T047 (geocoding) parallel to T048-T052 (routing) parallel to T053-T059 (map rendering)
- T060-T073 (UI components) all parallel after services complete

**Within Phase 4 (US2)**:
- T083-T086 (validators) parallel to T092-T093 (UI error display)
- T099-T101 (edge case checks) can run in parallel

**Within Phase 5 (US3)**:
- T105-T108 (metrics collection) parallel to T109-T113 (summary calculation)
- T119-T122 (tracing) can run parallel to metrics UI

**Within Phase 6 (Polish)**:
- T127-T131 (performance) parallel to T132-T137 (code quality) parallel to T145-T150 (documentation)

---

## Suggested MVP Scope (Minimum Viable Product)

**For fastest value delivery, implement ONLY User Story 1 (P1) first**:

**MVP Tasks**: T001-T082 (Setup + Foundational + US1)
**MVP Deliverable**: Working dual-map visualizer with A*/Dijkstra comparison
**Estimated Tasks**: 82 tasks
**Value**: Demonstrates core algorithm comparison (primary project goal)

**After MVP validated, add enhancements**:
- **US2 (P2)**: T083-T104 - Improves user experience
- **US3 (P3)**: T105-T126 - Adds educational value
- **Polish**: T127-T160 - Production readiness

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 20 tasks (T007-T026)
- **Phase 3 (US1 - P1)**: 56 tasks (T027-T082) ← MVP
- **Phase 4 (US2 - P2)**: 22 tasks (T083-T104)
- **Phase 5 (US3 - P3)**: 22 tasks (T105-T126)
- **Phase 6 (Polish)**: 34 tasks (T127-T160)

**Total**: 160 tasks

**Parallel Opportunities**: ~45 tasks marked `[P]` can run concurrently (28% parallelizable)

**Constitution Compliance**: ✅ All tasks support TDD workflow, code quality standards, type safety, comprehensive testing

---

## Format Validation: ✅ ALL TASKS FOLLOW CHECKLIST FORMAT

**Verification**:
- ✅ Every task starts with `- [ ]` (markdown checkbox)
- ✅ Every task has sequential ID (T001-T160)
- ✅ Parallelizable tasks marked `[P]`
- ✅ User story tasks labeled `[US1]`, `[US2]`, or `[US3]`
- ✅ Setup/Foundational/Polish have NO story labels
- ✅ All tasks include exact file paths in descriptions
- ✅ No placeholder tasks or "TBD" entries

**Ready for /speckit.implement execution!** 🚀
