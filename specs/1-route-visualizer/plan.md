# Implementation Plan: Dual-Map Route Visualizer

**Branch**: `1-route-visualizer` | **Date**: 2026-02-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/1-route-visualizer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a Streamlit web application that visualizes and compares A* and Dijkstra pathfinding algorithms on real-world routes. Users enter start and destination addresses, and the system displays two side-by-side maps showing routes calculated by each algorithm, along with performance metrics (distance, execution time, nodes explored). Core technical approach: Python-based single-page application using Streamlit for UI, Google Maps APIs for geocoding and road network data, custom implementations of A* and Dijkstra algorithms (no external pathfinding libraries), and folium/pydeck for map visualization.

## Technical Context

**Language/Version**: Python 3.9+ (type hints enabled, mypy strict mode)  
**Primary Dependencies**: streamlit (UI framework), folium (map visualization), googlemaps (API client), networkx (graph utilities), pytest (testing), black/isort/pylint (code quality)  
**Storage**: N/A (stateless application, no persistent storage required)  
**Testing**: pytest with pytest-cov for coverage reporting (90% target for algorithms, 75% for UI)  
**Target Platform**: Local development server (Windows/Linux/macOS), browser-based UI (Chrome, Firefox, Edge, Safari)  
**Project Type**: Single project (Streamlit web application with algorithm library)  
**Performance Goals**: Algorithm execution ≤2s for typical routes (≤100 nodes), total response time ≤5s including API calls, map rendering ≤1s post-algorithm  
**Constraints**: Google Maps API free tier ($200/month), no external pathfinding libraries (algorithms from scratch), algorithms must use optimal data structures (adjacency list, priority queue)  
**Scale/Scope**: Educational/demonstration project, single-user local execution, support for routes up to 1000 nodes, 3 user stories (P1: MVP visualization, P2: validation, P3: performance metrics)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Route Pathfinding Visualizer Constitution v1.0.0:

- [x] **Code Quality & Maintainability**: Feature design includes modular algorithm separation (src/algorithms/, src/ui/, src/services/), type hints with mypy strict mode, comprehensive docstrings, PEP 8 compliance via black/isort/pylint
- [x] **Testing Standards**: TDD workflow planned with pytest framework, unit tests for algorithm functions, correctness tests for known paths, edge case tests, integration tests for end-to-end flows; coverage targets: 90% algorithms, 75% UI
- [x] **User Experience Consistency**: Input validation (non-empty addresses, valid geocoding), visual feedback (loading indicators during computation), map visualization standards (distinct colors for A*/Dijkstra, 3px stroke, labeled markers), error handling with user-friendly messages
- [x] **Performance Requirements**: Algorithm execution time target ≤2s for typical routes (≤100 nodes), Google Maps API timeout 5s, map rendering ≤1s; optimization strategies: adjacency list graphs, priority queue (heapq) for Dijkstra, admissible heuristic for A*
- [x] **Algorithm Correctness**: Correctness verification via unit tests with known shortest paths, comparative analysis metrics (execution time, nodes explored, path length equality), support for logging mode to trace algorithm steps

**GATE STATUS: ✅ PASSED** - All constitution principles are addressed in the feature design.

*No violations detected. No entries in Complexity Tracking required.*

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── algorithms/
│   ├── __init__.py
│   ├── astar.py              # A* implementation with configurable heuristics
│   ├── dijkstra.py           # Dijkstra implementation with priority queue
│   ├── graph.py              # Graph data structures (Node, Edge, adjacency list)
│   └── heuristics.py         # Heuristic functions (Euclidean, Manhattan, Diagonal)
├── services/
│   ├── __init__.py
│   ├── geocoding.py          # Google Maps Geocoding API integration
│   ├── routing.py            # Google Maps Directions API integration
│   └── map_renderer.py       # Folium map generation and styling
├── ui/
│   ├── __init__.py
│   ├── input_form.py         # Streamlit input components (text fields, buttons)
│   ├── map_display.py        # Dual-map layout and visualization
│   └── metrics_display.py    # Performance metrics comparison table
└── utils/
    ├── __init__.py
    ├── config.py             # Environment variables, API key loading
    ├── validators.py         # Input validation helpers
    └── types.py              # Type definitions (Location, Route, PathfindingResult)

tests/
├── algorithms/
│   ├── test_astar.py         # A* unit tests + correctness tests
│   ├── test_dijkstra.py      # Dijkstra unit tests + correctness tests
│   ├── test_graph.py         # Graph data structure tests
│   └── test_heuristics.py    # Heuristic function tests
├── integration/
│   ├── test_end_to_end.py    # Full user journey tests
│   └── test_api_integration.py  # Google Maps API integration tests
├── performance/
│   └── test_benchmarks.py    # Algorithm performance benchmarks
└── conftest.py               # Pytest fixtures and test configuration

main.py                       # Streamlit application entry point
pyproject.toml                # Dependencies and project metadata
.env                          # Environment variables (not committed)
.env.example                  # Environment variable template
```

**Structure Decision**: Selected **Single Project** structure because this is a standalone Streamlit application without separate frontend/backend concerns. All code runs in a single Python process with Streamlit handling both UI rendering and algorithm execution. The src/ directory is organized by technical concern (algorithms, services, ui, utils) to enforce modularity per Constitution Principle I. Tests mirror the src/ structure for clarity.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
