"""Main Streamlit application for route pathfinding visualization.

This application allows users to compare A* and Dijkstra algorithms on real-world routes
by visualizing them side-by-side on interactive maps.
"""

import os
import sys
from typing import Optional

import streamlit as st

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.algorithms.astar import astar
from src.algorithms.dijkstra import dijkstra
from src.algorithms.heuristics import euclidean_distance, simple_distance, manhattan_distance
from src.services.geocoding import geocode_address, InvalidLocationError, APIError
from src.services.map_renderer import create_route_map, create_road_network_map
from src.services.routing import (
    get_route_graph, 
    get_road_network_graph, 
    find_closest_node, 
    get_largest_connected_component,
    is_connected,
    NoRouteError
)
from src.ui.input_form import render_input_form
from src.ui.map_display import render_dual_maps
from src.ui.metrics_display import render_metrics_table
from src.utils.config import load_user_agent, get_osrm_server
from src.utils.types import Location, PathfindingResult, Route
from src.utils.validators import ValidationError, validate_non_empty_addresses, validate_same_location


def main() -> None:
    """Main application entry point.

    Orchestrates the workflow:
    1. Render input form for addresses
    2. Geocode addresses to coordinates
    3. Get route graph from OpenStreetMap
    4. Run A* and Dijkstra algorithms
    5. Create map visualizations
    6. Display dual maps and metrics
    """
    # Page configuration
    st.set_page_config(
        page_title="Route Pathfinding Visualizer",
        layout="wide",
        page_icon="🗺️",
        initial_sidebar_state="expanded",
    )

    # App header and description
    st.title("🗺️ Route Pathfinding Visualizer")
    st.markdown(
        """
        **Compare A* and Dijkstra pathfinding algorithms on real-world routes**
        
        This application demonstrates the efficiency of the A* algorithm compared to Dijkstra's algorithm.
        Enter two addresses below to visualize both algorithms' paths side-by-side and compare their performance metrics.
        
        ---
        """
    )

    # Sidebar with example routes
    with st.sidebar:
        st.header("📍 Example Routes")
        st.markdown("Click any example to auto-fill the form:")
        
        if st.button("🗽 Times Square → Central Park", use_container_width=True):
            st.session_state["start_address"] = "Times Square, New York, NY"
            st.session_state["dest_address"] = "Central Park, New York, NY"
            st.rerun()
        
        if st.button("🌉 City Hall → Golden Gate Bridge", use_container_width=True):
            st.session_state["start_address"] = "San Francisco City Hall, CA"
            st.session_state["dest_address"] = "Golden Gate Bridge, San Francisco, CA"
            st.rerun()
        
        if st.button("✈️ LAX → Disneyland", use_container_width=True):
            st.session_state["start_address"] = "Los Angeles International Airport, CA"
            st.session_state["dest_address"] = "Disneyland, Anaheim, CA"
            st.rerun()
        
        st.markdown("---")
        st.markdown(
            """
            ### ℹ️ About
            
            This application uses OpenStreetMap services to fetch real-world route data,
            then applies graph algorithms to find optimal paths.
            
            **Algorithms:**
            - **A***: Uses heuristic to guide search toward goal (faster)
            - **Dijkstra**: Explores all paths exhaustively (baseline)
            
            **Tech Stack:**
            - Python 3.10+
            - Streamlit
            - OpenStreetMap (Nominatim & OSRM)
            - Folium (maps)
            """
        )

    # Render input form
    start_address, dest_address, calculate_clicked = render_input_form()

    # Add option to visualize road network
    st.markdown("### 🛣️ Visualization Options")
    col1, col2 = st.columns(2)
    with col1:
        show_road_network = st.checkbox(
            "Show Complete Road Network",
            value=False,
            help="Display all roads in the area (using Overpass API) before running pathfinding algorithms"
        )
    with col2:
        visualization_detail = st.selectbox(
            "Exploration Detail",
            options=["High (slower)", "Medium", "Low (faster)", "Final path only"],
            index=1,
            help="Control how many explored nodes/edges to show. Lower = faster rendering."
        )
    
    # Map visualization detail to limits
    detail_limits = {
        "High (slower)": (3000, 1800),
        "Medium": (1500, 900),
        "Low (faster)": (600, 480),
        "Final path only": (0, 0),
    }
    max_edges, max_nodes = detail_limits[visualization_detail]

    # Process route calculation when button is clicked
    if calculate_clicked:
        try:
            # Validate addresses are non-empty (US2 validation)
            try:
                validate_non_empty_addresses(start_address, dest_address)
            except ValidationError as e:
                st.error(f"❌ Validation Error: {e}")
                st.info("💡 Please enter valid addresses for both start and destination")
                return

            # Show loading spinner during processing
            with st.spinner("🔍 Calculating routes..."):
                # Load OpenStreetMap configuration
                user_agent = load_user_agent()
                osrm_server = get_osrm_server()

                # Geocode addresses
                try:
                    start_location: Location = geocode_address(start_address, user_agent)
                    dest_location: Location = geocode_address(dest_address, user_agent)
                except InvalidLocationError as e:
                    st.error(f"❌ Location Not Found: {e}")
                    st.info(
                        "💡 Please check your address spelling and try again. "
                        "Try including city and country (e.g., 'Times Square, New York, USA')"
                    )
                    return
                except APIError as e:
                    if "timeout" in str(e).lower():
                        st.error("❌ Request Timeout: The geocoding service took too long to respond")
                        st.info("💡 Please try again in a moment. If the issue persists, check your internet connection")
                    elif "quota" in str(e).lower():
                        st.error("❌ API Quota Exceeded: Daily request limit reached")
                        st.info("💡 Please try again tomorrow or upgrade your Google Maps API plan")
                    else:
                        st.error(f"❌ Geocoding Service Error: {e}")
                        st.info("💡 The service is temporarily unavailable. Please try again in a few moments")
                    return

                # Validate locations are different (US2 validation)
                try:
                    validate_same_location(start_location, dest_location)
                except ValidationError as e:
                    st.warning(f"⚠️ {e}")
                    st.info("💡 Please enter two different locations to calculate a route")
                    return

                # Optional: Show road network visualization
                if show_road_network:
                    st.markdown("---")
                    st.markdown("### 🛣️ Complete Road Network in Area")
                    st.info(
                        "📍 This map shows all roads in the bounding box between your start and destination. "
                        "The pathfinding algorithms will search through this network to find optimal routes."
                    )
                    
                    try:
                        # Fetch complete road network using Overpass API
                        road_network_graph = get_road_network_graph(
                            start_location, 
                            dest_location,
                            padding=0.01  # ~1km padding around bounding box
                        )
                        
                        # Extract largest connected component to ensure path exists
                        road_network_graph = get_largest_connected_component(road_network_graph)
                        
                        # Create visualization
                        network_map = create_road_network_map(
                            road_network_graph,
                            start_location,
                            dest_location,
                            show_intersections=False
                        )
                        
                        # Display the map
                        import streamlit.components.v1 as components
                        components.html(network_map._repr_html_(), height=600)
                        
                        st.success(
                            f"✅ Road network loaded: {len(road_network_graph.nodes())} nodes, "
                            f"{sum(len(road_network_graph.neighbors(n)) for n in road_network_graph.nodes()) // 2} roads "
                            f"(largest connected component)"
                        )
                        
                        # Use road network graph for pathfinding
                        graph = road_network_graph
                        st.info("✨ Using complete road network for pathfinding algorithms")
                        
                    except NoRouteError as e:
                        st.warning(f"⚠️ Could not load road network: {e}")
                        st.info("💡 Falling back to route-based graph")
                        road_network_graph = None
                    except Exception as e:
                        st.warning(f"⚠️ Road network visualization error: {e}")
                        st.info("💡 Falling back to route-based graph")
                        road_network_graph = None
                        road_network_graph = None
                    
                    st.markdown("---")
                else:
                    road_network_graph = None

                # Get route graph from OSRM API if not using road network
                if road_network_graph is None:
                    try:
                        graph = get_route_graph(start_location, dest_location, osrm_server)
                    except NoRouteError as e:
                        if "no route found" in str(e).lower():
                            st.error("❌ No Route Found Between These Locations")
                            st.info(
                                "💡 These locations may not be connected by roads, or one may be unreachable. "
                                "Please try different addresses or verify both locations are accessible by car"
                            )
                        else:
                            st.error(f"❌ Routing Error: {e}")
                            st.info("💡 Unable to calculate route. Please try again")
                        return
                    except APIError as e:
                        st.error(f"❌ Routing Service Error: {e}")
                        st.info("💡 The routing service is temporarily unavailable. Please try again in a few moments")
                        return
                
                # Find start and goal nodes in the graph
                if road_network_graph is not None:
                    # For road network graph, find closest nodes to start and destination
                    start_node, start_dist = find_closest_node(start_location, graph)
                    goal_node, goal_dist = find_closest_node(dest_location, graph)
                    
                    st.info(
                        f"📍 Found closest nodes: Start ({start_dist*1000:.1f}m away), "
                        f"Destination ({goal_dist*1000:.1f}m away)"
                    )
                    
                    # Verify nodes are connected in the graph
                    if not is_connected(graph, start_node, goal_node):
                        st.error("❌ Start and destination nodes are not connected in the road network")
                        st.info(
                            "💡 The closest road nodes to your locations are in disconnected parts of the network. "
                            "Try increasing the search area padding or using different locations."
                        )
                        return
                else:
                    # For route graph, first and last nodes are start/destination
                    start_node = graph.nodes()[0]
                    goal_node = graph.nodes()[-1]

                # Run A* algorithm
                astar_result: PathfindingResult = astar(
                    graph,
                    start=start_node,
                    goal=goal_node,
                    heuristic=manhattan_distance,
                )

                if not astar_result.success or astar_result.route is None:
                    st.error(f"❌ A* Algorithm Failed: {astar_result.error}")
                    return

                # Run Dijkstra algorithm
                dijkstra_result: PathfindingResult = dijkstra(
                    graph,
                    start=start_node,
                    goal=goal_node,
                )

                if not dijkstra_result.success or dijkstra_result.route is None:
                    st.error(f"❌ Dijkstra Algorithm Failed: {dijkstra_result.error}")
                    return

                # Create map visualizations
                astar_map = create_route_map(
                    astar_result.route, start_location, dest_location,
                    max_explored_edges=max_edges,
                    max_explored_nodes=max_nodes
                )
                dijkstra_map = create_route_map(
                    dijkstra_result.route, start_location, dest_location,
                    max_explored_edges=max_edges,
                    max_explored_nodes=max_nodes
                )

                # Display results
                render_dual_maps(
                    astar_result.route,
                    dijkstra_result.route,
                    astar_map,
                    dijkstra_map,
                )
                render_metrics_table(astar_result.route, dijkstra_result.route)

                # Success message
                st.success("✅ Routes calculated successfully!")

        except Exception as e:
            # Catch-all for unexpected errors
            st.error(f"❌ Unexpected Error: {e}")
            st.info("💡 Please try again or contact support if the issue persists")
            # Re-raise in development for debugging
            if os.getenv("DEBUG", "false").lower() == "true":
                raise

    # Footer
    st.markdown("---")
    st.caption(
        "🎓 **Academic Project** | Discrete Mathematics and Algorithms | "
        "Constitution v1.0.0 | Built with Python, Streamlit, and OpenStreetMap"
    )


if __name__ == "__main__":
    main()
