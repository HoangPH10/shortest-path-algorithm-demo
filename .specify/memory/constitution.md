<!--
Sync Impact Report - Constitution v1.0.0 (Initial Ratification)
=================================================================
Version Change: N/A → 1.0.0
Change Type: MAJOR (Initial constitution ratification)

Modified Principles: N/A (Initial version)
Added Sections: All sections (initial creation)
Removed Sections: None

Template Consistency Status:
✅ plan-template.md - Updated Constitution Check gates to align with core principles
✅ spec-template.md - Verified requirement sections align with UX consistency and testability
✅ tasks-template.md - Verified task categorization includes algorithm testing and performance validation
⚠ Command files (.github/prompts/*.md) - No updates required (agent-agnostic references verified)

Follow-up TODOs: None
-->

# Route Pathfinding Visualizer Constitution

## Core Principles

### I. Code Quality & Maintainability

**All code MUST adhere to the following non-negotiable standards:**

- **Modularity**: Algorithm implementations (A*, Dijkstra) MUST be separated from UI components in distinct, testable modules (e.g., `src/algorithms/`, `src/ui/`, `src/services/`)
- **Type Safety**: All functions MUST include type hints for parameters and return values; mypy validation MUST pass with strict mode
- **Documentation**: Every public function and class MUST have docstrings explaining purpose, parameters, return values, and examples
- **Code Style**: Code MUST follow PEP 8 standards; formatters (black, isort) and linters (pylint, flake8) MUST be configured and pass with score ≥ 8.5/10
- **DRY Principle**: No duplication of algorithm logic; shared utilities (graph structures, heuristics) MUST be abstracted into reusable components
- **Naming Conventions**: Variables and functions use snake_case; classes use PascalCase; constants use UPPER_SNAKE_CASE; names MUST be descriptive (e.g., `calculate_manhattan_distance` not `calc_dist`)

**Rationale**: Academic project requires demonstration of software engineering best practices and maintainability for evaluation; clean code ensures algorithm correctness is verifiable.

### II. Testing Standards (NON-NEGOTIABLE)

**Test-Driven Development (TDD) is MANDATORY for all algorithm implementations:**

- **Test-First Workflow**: For each algorithm (A*, Dijkstra), unit tests MUST be written and approved before implementation begins
- **Coverage Requirements**: Minimum 90% code coverage for algorithm modules; minimum 75% for UI components
- **Test Categories**:
  - **Unit Tests**: Each algorithm function (pathfinding, heuristic calculations, graph operations) MUST have isolated unit tests with mock data
  - **Algorithm Correctness Tests**: MUST verify optimal path found for known test cases (e.g., simple grids, known shortest paths)
  - **Edge Case Tests**: MUST handle invalid inputs (no path exists, same start/destination, invalid coordinates)
  - **Integration Tests**: MUST verify end-to-end flow from user input → API call → algorithm execution → visualization
- **Assertion Standards**: All assertions MUST have descriptive messages; use pytest fixtures for test data
- **Performance Tests**: Algorithm execution MUST be benchmarked; regression tests MUST ensure performance doesn't degrade

**Rationale**: Algorithm correctness is the core academic requirement; automated testing ensures implementations match theoretical expectations and prevents regressions.

### III. User Experience Consistency

**All UI interactions MUST provide a predictable, intuitive, and responsive experience:**

- **Input Validation**: Begin and destination inputs MUST validate addresses in real-time; provide clear error messages for invalid inputs (e.g., "Address not found. Please enter a valid location.")
- **Visual Feedback**: During pathfinding computation, MUST display loading indicator with progress message (e.g., "Calculating A* route...")
- **Map Visualization Standards**:
  - Both algorithm routes MUST be displayed simultaneously with distinct colors (e.g., A* = blue, Dijkstra = red)
  - Route paths MUST be clearly visible with stroke width ≥ 3px and opacity ≥ 0.7
  - Start and destination markers MUST be visually distinct with labeled icons
  - Legend MUST explain route colors, markers, and any performance metrics shown
- **Comparison Metrics**: UI MUST display side-by-side comparison of both algorithms (path length, nodes explored, execution time)
- **Responsive Design**: Map MUST resize appropriately; controls MUST remain accessible on screens ≥ 1024px wide
- **Error Handling**: All errors (API failures, routing failures) MUST display user-friendly messages with suggested actions; errors MUST NOT crash the application

**Rationale**: Consistent UX ensures the project demonstrates professional interface design and makes algorithm comparison accessible to non-technical evaluators.

### IV. Performance Requirements

**System MUST meet the following performance benchmarks:**

- **Algorithm Execution Time**: Pathfinding for typical city routes (≤ 100 nodes) MUST complete within 2 seconds on standard hardware
- **API Response Time**: Google Maps API calls MUST have timeout of 5 seconds; failures MUST be handled gracefully
- **UI Responsiveness**: Map rendering and route visualization MUST complete within 1 second after algorithm completes
- **Memory Efficiency**: Graph data structures MUST use adjacency lists (not matrices) to minimize memory footprint for large road networks
- **Optimization Requirements**:
  - A* heuristic MUST be admissible and consistent (use Euclidean or Manhattan distance)
  - Graph preprocessing (if any) MUST be cached to avoid redundant computations
  - Dijkstra implementation MUST use priority queue (heapq) for O(E log V) complexity
- **Scalability Testing**: Algorithms MUST be tested with graphs up to 1000 nodes; performance degradation MUST be documented

**Rationale**: Performance demonstrates algorithmic efficiency understanding; meeting benchmarks proves theoretical complexity translates to practical implementation.

### V. Algorithm Correctness & Transparency

**Algorithm implementations MUST be verifiable and educationally transparent:**

- **Correctness Guarantees**:
  - A* MUST find optimal path when using admissible heuristic; correctness MUST be verified with test cases
  - Dijkstra MUST find shortest path in weighted graphs; results MUST match known solutions for test graphs
  - Both algorithms MUST produce identical path lengths (may differ in nodes explored)
- **Step-by-Step Tracing**: Implementations MUST support logging mode that outputs algorithm steps (nodes visited, current cost, heuristic values) for educational verification
- **Configurable Heuristics**: A* MUST allow switching between heuristic functions (Euclidean, Manhattan, Diagonal) to demonstrate impact on performance
- **Comparative Analysis**: Application MUST display metrics proving algorithmic differences (A* explores fewer nodes due to heuristic guidance)
- **Source Attribution**: Any external references (algorithms textbooks, optimization techniques) MUST be cited in code comments

**Rationale**: Academic integrity requires demonstrating understanding of algorithm theory; transparency allows instructors to verify implementation correctness.

## Technical Stack & Constraints

**Technology Requirements:**

- **Frontend Framework**: Streamlit (latest stable version) for rapid UI development and interactive visualization
- **Mapping Service**: Google Maps Platform (Maps JavaScript API, Directions API, Geocoding API)
- **Language & Runtime**: Python 3.9+ with type hints enabled
- **Required Libraries**:
  - `streamlit` (UI framework)
  - `folium` (map visualization, alternative to native Google Maps if needed)
  - `networkx` (graph data structures and utilities)
  - `googlemaps` (Google Maps API client)
  - `pytest` (testing framework)
  - `black`, `isort`, `pylint` (code quality tools)
- **API Key Management**: Google Maps API key MUST be stored in environment variables (`.env` file), NEVER hardcoded; `.env.example` MUST be provided
- **Dependency Management**: All dependencies MUST be pinned in `pyproject.toml` with version ranges; `uv` package manager preferred for fast, reproducible installs
- **Data Format**: Graph data (if preloaded) MUST use JSON or GeoJSON format; road network data MUST be retrieved via Google Maps APIs in real-time

**Constraints:**

- **No External Pathfinding Libraries**: Implementations of A* and Dijkstra MUST be written from scratch; using libraries like `networkx.astar_path` is PROHIBITED for core algorithms
- **Academic Honesty**: All code MUST be original work; any adapted algorithms MUST cite sources and explain modifications
- **Budget**: Google Maps API usage MUST stay within free tier limits ($200/month credit); implement request caching if needed

## Development Workflow

**Code Quality Gates (enforced at every commit/PR):**

1. **Pre-commit Checks**:
   - Black formatter MUST auto-format code (line length = 100)
   - isort MUST organize imports
   - mypy MUST validate type hints with `--strict` flag
   - pylint MUST pass with score ≥ 8.5/10

2. **Testing Gates**:
   - All unit tests MUST pass (`pytest tests/unit/`)
   - Algorithm correctness tests MUST pass (`pytest tests/algorithms/`)
   - Code coverage MUST meet thresholds (90% algorithms, 75% UI)

3. **Documentation Requirements**:
   - All new functions MUST include docstrings
   - README.md MUST be updated if user-facing features change
   - Algorithm implementations MUST include inline comments explaining key steps

**Review Process:**

- **Self-Review Checklist**: Before marking work complete, verify all Constitution principles are met using `.specify/templates/checklist-template.md`
- **Complexity Justification**: Any algorithmic optimization (beyond textbook A*/Dijkstra) MUST be documented in plan.md with rationale

**Deployment:**

- **Local Development**: Application MUST run with `uv run streamlit run main.py` after environment setup
- **Configuration**: Google Maps API key MUST be configurable via `.env` file
- **Demo Readiness**: Application MUST include example routes in README.md for quick demonstration

## Governance

**Constitution Authority:**

This Constitution supersedes all other development practices and preferences. All features, tasks, and code reviews MUST verify compliance with these principles.

**Amendment Process:**

- Amendments require updating version number per semantic versioning (see below)
- Major changes (new principles, principle removals) require MAJOR version bump
- Minor changes (new sections, expanded guidance) require MINOR version bump
- Clarifications and non-semantic edits require PATCH version bump
- All amendments MUST update the Sync Impact Report (HTML comment at top of this file)
- Dependent templates (plan-template.md, spec-template.md, tasks-template.md) MUST be reviewed and updated for consistency

**Versioning Policy:**

- **MAJOR.MINOR.PATCH** format (semantic versioning)
- Version changes MUST be documented in Sync Impact Report
- Breaking changes (principle removals, incompatible requirement changes) trigger MAJOR bump

**Compliance Review:**

- All specifications (`specs/*/spec.md`) MUST reference relevant constitution principles in requirements
- All implementation plans (`specs/*/plan.md`) MUST include "Constitution Check" gate validating compliance
- All tasks (`specs/*/tasks.md`) MUST tag tasks with applicable principles for traceability
- All code reviews MUST verify adherence to Code Quality & Maintainability and Testing Standards principles

**Runtime Guidance:**

For AI agent development guidance and execution workflows, refer to command files in `.github/prompts/speckit.*.prompt.md`.

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
