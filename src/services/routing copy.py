"""Routing service using OSRM (Open Source Routing Machine) API."""

import requests

from src.algorithms.graph import Graph
from src.algorithms.heuristics import euclidean_distance
from src.utils.types import Location, Node


class NoRouteError(Exception):
    """Raised when no route can be found between locations."""


def get_route_graph(start: Location, destination: Location, osrm_server: str = "http://router.project-osrm.org") -> Graph:
    """Convert a route between two locations into a graph.

    Uses OSRM API to get route steps, then converts
    the steps into a graph with nodes (waypoints) and weighted edges (road segments).

    Args:
        start: Starting location
        destination: Destination location
        osrm_server: OSRM server URL (default: public OSRM server)

    Returns:
        Graph with nodes and bidirectional edges representing the route

    Raises:
        NoRouteError: If no route found or API error occurs
    """
    try:
        # OSRM route request with steps
        url = (
            f"{osrm_server}/route/v1/driving/"
            f"{start.longitude},{start.latitude};"
            f"{destination.longitude},{destination.latitude}"
            f"?steps=true&geometries=geojson"
        )
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
    except requests.exceptions.Timeout as e:
        raise NoRouteError(f"API request timed out: {e}") from e
    except requests.exceptions.RequestException as e:
        raise NoRouteError(f"Network connection error: {e}") from e
    except ValueError as e:
        raise NoRouteError(f"Invalid response from OSRM server: {e}") from e

    if data.get("code") != "Ok" or not data.get("routes"):
        raise NoRouteError(
            f"No route found between {start.address} and {destination.address}. "
            "Please try different locations or ensure they are accessible by road."
        )

    # Use first route (most recommended)
    route = data["routes"][0]
    graph = Graph()

    # Process all steps in all legs
    # Track nodes by coordinates to avoid duplicates
    nodes_by_coords: dict[tuple[float, float], Node] = {}
    node_counter = 0

    def get_or_create_node(lat: float, lng: float) -> Node:
        """Get existing node or create new one for given coordinates."""
        nonlocal node_counter
        coords = (lat, lng)
        if coords not in nodes_by_coords:
            nodes_by_coords[coords] = Node(
                id=f"node_{node_counter}",
                latitude=lat,
                longitude=lng,
            )
            node_counter += 1
        return nodes_by_coords[coords]

    for leg in route["legs"]:
        for step in leg["steps"]:
            # Get all coordinates from geometry to create a richer graph
            geometry = step["geometry"]
            coordinates = geometry["coordinates"]
            
            # Skip steps with too few coordinates
            if len(coordinates) < 2:
                continue
            
            # Total distance for this step
            step_distance = step["distance"] / 1000.0  # Convert to km
            
            # Skip steps with zero or very small distance
            if step_distance < 0.001:
                continue
            
            # Create nodes for all waypoints in the geometry
            # This creates a richer graph with more potential paths
            segment_nodes = []
            for lng, lat in coordinates:
                node = get_or_create_node(lat, lng)
                segment_nodes.append(node)
            
            # Calculate approximate distance per segment
            num_segments = len(segment_nodes) - 1
            if num_segments > 0:
                segment_distance = step_distance / num_segments
                
                # Add edges between consecutive waypoints
                for i in range(num_segments):
                    start_node = segment_nodes[i]
                    end_node = segment_nodes[i + 1]
                    
                    # Skip if same node
                    if start_node.id == end_node.id:
                        continue
                    
                    # Add bidirectional edge
                    graph.add_edge(start_node, end_node, weight=segment_distance, bidirectional=True)

    # Add skip connections to create alternative paths (makes Dijkstra vs A* difference visible)
    all_nodes = graph.nodes()
    all_nodes_list = list(all_nodes)
    
    # Add connections between nodes that are spatially close but not directly connected
    # This creates alternative routes that Dijkstra will explore but A* might skip
    for i, node1 in enumerate(all_nodes_list):
        for j in range(i + 2, min(i + 10, len(all_nodes_list))):  # Skip nearby nodes, connect to further ones
            node2 = all_nodes_list[j]
            
            # Calculate distance between nodes
            distance = euclidean_distance(node1, node2)
            
            # Only add edges for nodes that are reasonably close (within 0.5 km)
            # but not already directly connected
            if 0.05 < distance < 0.5:
                # Check if already connected
                neighbors = [n for n, _ in graph.neighbors(node1)]
                if node2 not in neighbors:
                    # Add edge with slightly higher weight (detour penalty)
                    graph.add_edge(node1, node2, weight=distance * 1.2, bidirectional=True)

    # Debug: Print graph statistics
    all_nodes = graph.nodes()
    print("\n[GRAPH DEBUG]")
    print(f"  Total nodes: {len(all_nodes)}")
    if all_nodes:
        avg_neighbors = sum(len(graph.neighbors(n)) for n in all_nodes) / len(all_nodes)
        print(f"  Average neighbors per node: {avg_neighbors:.2f}")
        # Check for branching
        branching_nodes = sum(1 for n in all_nodes if len(graph.neighbors(n)) > 2)
        print(f"  Nodes with >2 neighbors (branches): {branching_nodes}")

    return graph
