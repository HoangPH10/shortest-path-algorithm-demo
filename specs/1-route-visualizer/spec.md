# Feature Specification: Dual-Map Route Visualizer

**Feature Branch**: `1-route-visualizer`  
**Created**: 2026-02-06  
**Status**: Draft  
**Input**: User description: "Implement a web page including two input texts one for start place one for destination place, the below will include 2 maps one for visualize A start path algorithm, one for visualize Dijkstra algorithm and the distance with the time processing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Route Visualization (Priority: P1)

A user wants to compare A* and Dijkstra pathfinding algorithms on a real-world route by entering start and destination addresses and viewing both algorithm results side-by-side.

**Why this priority**: This is the core functionality - the minimum viable product that demonstrates algorithm comparison. Without this, the application has no value.

**Independent Test**: Can be fully tested by entering "Times Square, New York" and "Central Park, New York", then verifying that two distinct maps appear showing different algorithm visualizations with route paths displayed.

**Acceptance Scenarios**:

1. **Given** the application is loaded, **When** user enters "San Francisco City Hall" in start input and "Golden Gate Bridge" in destination input and clicks visualize, **Then** two maps appear showing routes calculated by A* (top/left map) and Dijkstra (bottom/right map)
2. **Given** valid start and destination addresses are entered, **When** routes are calculated, **Then** each map displays the complete path from start to destination with distinct visual markers for start point (green) and destination point (red)
3. **Given** both routes are displayed, **When** user views the results, **Then** distance metrics (in miles/km) and processing time (in milliseconds) are shown below each respective map
4. **Given** routes are successfully calculated, **When** user compares the two maps, **Then** both algorithms produce valid paths (paths may differ in computation time but should have similar or identical distances for optimal path scenarios)

---

### User Story 2 - Input Validation and Error Handling (Priority: P2)

A user needs clear feedback when entering invalid addresses or when routing fails, ensuring the application guides them to successful inputs.

**Why this priority**: Essential for usable user experience, but application can demonstrate core algorithm functionality without sophisticated validation. This can be added after basic visualization works.

**Independent Test**: Can be tested independently by entering invalid addresses like "asdfghjkl" or "123456789" and verifying appropriate error messages appear without crashing the application.

**Acceptance Scenarios**:

1. **Given** user is on the application page, **When** user enters an invalid address "xyz123invalid" in start field and attempts to visualize, **Then** system displays error message "Start address not found. Please enter a valid location."
2. **Given** user has entered a valid start address, **When** user leaves destination field empty and clicks visualize, **Then** system displays error message "Both start and destination addresses are required."
3. **Given** user enters addresses where no valid route exists, **When** system attempts routing, **Then** system displays "No route found between these locations. Please try different addresses."
4. **Given** Google Maps API fails or times out, **When** system attempts geocoding or routing, **Then** system displays "Service temporarily unavailable. Please try again in a moment." and does not crash

---

### User Story 3 - Algorithm Performance Comparison (Priority: P3)

A user wants to understand the performance differences between A* and Dijkstra by viewing detailed metrics showing execution time, nodes explored, and path optimality.

**Why this priority**: Adds educational value and demonstrates algorithmic understanding, but basic visualization is sufficient for MVP. This enhances the learning experience.

**Independent Test**: Can be tested independently by running any route and verifying that metrics section below each map shows "Execution Time: Xms", "Nodes Explored: Y", and "Path Length: Z km".

**Acceptance Scenarios**:

1. **Given** both algorithms have completed route calculation, **When** user views results, **Then** each map displays execution time in milliseconds (e.g., "A*: 45ms", "Dijkstra: 120ms")
2. **Given** routes are calculated, **When** user views performance metrics, **Then** system displays number of nodes explored by each algorithm (demonstrating A* typically explores fewer nodes due to heuristic)
3. **Given** both routes are displayed, **When** user compares path lengths, **Then** system shows that both optimal algorithms produce paths of equal length (verifying correctness)
4. **Given** performance data is displayed, **When** user views the comparison, **Then** a summary section highlights the winner (e.g., "A* was 2.7x faster and explored 60% fewer nodes")

---

### Edge Cases

- What happens when user enters identical start and destination addresses? System should detect this and display "Start and destination are the same location. No route needed." with zero distance.
- How does system handle very long-distance routes (e.g., cross-country)? System should either process them (may take longer) or limit maximum distance and notify user "Route exceeds maximum distance of 500 miles. Please select closer locations."
- What happens when user rapidly clicks visualize button multiple times? System should disable button during processing to prevent duplicate requests.
- How does system handle special characters or non-Latin scripts in addresses? System should pass UTF-8 encoded addresses to Google Maps API which handles international addresses.
- What if API rate limits are exceeded? System should display "API request limit reached. Please wait before trying again."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide two separate text input fields labeled "Start Location" and "Destination Location" for user to enter addresses
- **FR-002**: System MUST validate that both input fields are non-empty before allowing route calculation
- **FR-003**: System MUST integrate with Google Maps Geocoding API to convert address strings to geographic coordinates (latitude/longitude)
- **FR-004**: System MUST display two separate map visualizations side-by-side or vertically stacked (responsive layout)
- **FR-005**: System MUST implement A* pathfinding algorithm from scratch (no external pathfinding libraries) using an admissible heuristic (Euclidean or Manhattan distance)
- **FR-006**: System MUST implement Dijkstra pathfinding algorithm from scratch (no external pathfinding libraries) using a priority queue
- **FR-007**: System MUST visualize the A* calculated route on the first map with a distinct color (e.g., blue path with 3px stroke)
- **FR-008**: System MUST visualize the Dijkstra calculated route on the second map with a distinct color (e.g., red path with 3px stroke)
- **FR-009**: System MUST display start location marker (green pin) and destination location marker (red pin) on both maps
- **FR-010**: System MUST calculate and display total route distance for both algorithms (in kilometers or miles)
- **FR-011**: System MUST measure and display algorithm execution time for both A* and Dijkstra (in milliseconds)
- **FR-012**: System MUST retrieve road network data from Google Maps Directions API or similar service to build graph structure
- **FR-013**: System MUST display clear error messages when inputs are invalid, locations are not found, or routing fails
- **FR-014**: System MUST show loading indicator with message (e.g., "Calculating routes...") while algorithms are processing
- **FR-015**: System MUST complete typical urban route calculations (≤100 nodes) within 2 seconds per algorithm

### Key Entities *(include if feature involves data)*

- **Location**: Represents a geographic point with address (string), latitude (float), longitude (float); used for start and destination inputs
- **Graph Node**: Represents an intersection or waypoint in the road network with ID, coordinates (lat/lng), and connected edges
- **Graph Edge**: Represents a road segment connecting two nodes with weight (distance in meters or travel time), start node ID, end node ID
- **Route**: Represents a calculated path with ordered list of nodes, total distance (float in km/miles), execution time (int in milliseconds), algorithm used (string: "A*" or "Dijkstra"), nodes explored count (int)
- **PathfindingResult**: Contains route object, success status (boolean), error message (string if failed), performance metrics (execution time, nodes explored)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully enter two addresses and receive route visualizations within 5 seconds of clicking the visualize button for typical urban routes
- **SC-002**: Both algorithms (A* and Dijkstra) produce valid paths for 95% of valid address pairs within typical road networks
- **SC-003**: When both algorithms find optimal paths, their calculated distances are identical (within 0.1% tolerance for floating-point differences)
- **SC-004**: A* algorithm explores fewer nodes than Dijkstra for at least 80% of test routes (demonstrating heuristic efficiency)
- **SC-005**: Algorithm execution time is under 2 seconds for routes with up to 100 nodes on standard development hardware
- **SC-006**: System displays appropriate error messages for 100% of invalid inputs without crashing
- **SC-007**: Users can visually distinguish between the two algorithm results through distinct map layouts/colors and clear labels
- **SC-008**: System correctly handles edge cases (same start/destination, no route exists, invalid addresses) with user-friendly messages in 100% of test scenarios

## Assumptions *(document reasonable defaults used)*

- **Assumption 1**: Google Maps APIs (Geocoding, Directions, Maps JavaScript) are available and API key is configured; free tier quota ($200/month) is sufficient for development and demonstration purposes
- **Assumption 2**: Users will primarily test with addresses within the same city or metropolitan area (typical distance < 50 miles) for optimal performance
- **Assumption 3**: Road network data retrieved from Google Maps can be converted to graph structure with nodes (intersections) and edges (road segments) suitable for pathfinding algorithms
- **Assumption 4**: Heuristic function for A* uses straight-line distance (Euclidean) which is admissible for road networks (never overestimates actual distance)
- **Assumption 5**: Users have modern web browsers (Chrome, Firefox, Edge, Safari) with JavaScript enabled and screen resolution ≥ 1024px wide
- **Assumption 6**: Application runs locally via Streamlit development server; deployment to production hosting is out of scope for initial version
- **Assumption 7**: Performance benchmarks assume standard development machine (quad-core processor, 8GB RAM); slower machines may exceed 2-second target
- **Assumption 8**: Route visualization uses 2D map view (satellite/terrain/roadmap); 3D visualization is not required

## Out of Scope *(explicitly excluded from this feature)*

- **Multi-waypoint routing**: Only direct start-to-destination routes; adding intermediate stops is not supported
- **Real-time traffic integration**: Routes based on static road network; live traffic data not considered
- **Turn-by-turn navigation**: Only path visualization; voice or text-based navigation instructions not included
- **Route preferences**: Cannot filter by highway/toll road avoidance, shortest vs fastest routes (algorithms find shortest path by distance)
- **Mobile-specific optimizations**: Responsive design targets desktop/laptop screens; dedicated mobile app interface not included
- **Historical route comparison**: Only current route calculation; saving/loading previous routes not supported
- **Alternative route suggestions**: Only single optimal path per algorithm; multiple route options not provided
- **Offline mode**: Requires internet connection for Google Maps APIs; offline map tiles not supported

## Dependencies *(external factors required for success)*

- **Google Maps API Access**: Valid API key with enabled services (Maps JavaScript API, Geocoding API, Directions API) is required
- **Python Environment**: Python 3.9+ with pip or uv package manager for installing dependencies
- **Streamlit Framework**: Application requires Streamlit for UI rendering and interactivity
- **Network Connectivity**: Internet connection required for API calls during development and runtime
- **Browser Compatibility**: Modern web browser with JavaScript and WebGL support for map rendering