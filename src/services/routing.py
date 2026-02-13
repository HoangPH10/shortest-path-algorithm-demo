"""Routing service using OSRM (Open Source Routing Machine) API and Overpass API."""

import time
import requests

from src.algorithms.graph import Graph
from src.algorithms.heuristics import euclidean_distance
from src.utils.types import Location, Node


class NoRouteError(Exception):
    """Raised when no route can be found between locations."""


def find_closest_node(location: Location, graph: Graph) -> tuple[Node, float]:
    """Find the closest node in the graph to a given location.
    
    Args:
        location: Target location with latitude/longitude
        graph: Graph containing nodes to search
        
    Returns:
        Tuple of (closest_node, distance_in_km)
        
    Example:
        >>> closest, distance = find_closest_node(start_location, graph)
        >>> print(f"Closest node is {distance*1000:.1f} meters away")
    """
    all_nodes = graph.nodes()
    if not all_nodes:
        raise NoRouteError("Graph has no nodes")
    
    min_distance = float('inf')
    closest_node = all_nodes[0]
    
    # Create a temporary node object for the location
    location_node = Node(
        id="temp",
        latitude=location.latitude,
        longitude=location.longitude
    )
    
    for node in all_nodes:
        dist = euclidean_distance(location_node, node)
        if dist < min_distance:
            min_distance = dist
            closest_node = node
    
    return closest_node, min_distance


def is_connected(graph: Graph, start: Node, goal: Node) -> bool:
    """Check if two nodes are connected in the graph using BFS.
    
    Args:
        graph: Graph to check
        start: Starting node
        goal: Goal node
        
    Returns:
        True if nodes are connected, False otherwise
    """
    if start == goal:
        return True
    
    visited = {start}
    queue = [start]
    
    while queue:
        current = queue.pop(0)
        
        if current == goal:
            return True
        
        for neighbor, _ in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False


def get_largest_connected_component(graph: Graph) -> Graph:
    """Extract the largest connected component from a graph.
    
    Useful for road networks that may have disconnected segments.
    
    Args:
        graph: Input graph that may have multiple components
        
    Returns:
        New graph containing only the largest connected component
    """
    all_nodes = graph.nodes()
    if not all_nodes:
        return graph
    
    # Find all connected components using BFS
    components = []
    unvisited = set(all_nodes)
    
    while unvisited:
        # Start new component from an unvisited node
        start_node = next(iter(unvisited))
        component = {start_node}
        queue = [start_node]
        unvisited.remove(start_node)
        
        # BFS to find all nodes in this component
        while queue:
            current = queue.pop(0)
            for neighbor, _ in graph.neighbors(current):
                if neighbor in unvisited:
                    component.add(neighbor)
                    queue.append(neighbor)
                    unvisited.remove(neighbor)
        
        components.append(component)
    
    # Find largest component
    largest_component = max(components, key=len)
    
    print(f"\n[CONNECTIVITY DEBUG]")
    print(f"  Total components found: {len(components)}")
    print(f"  Largest component size: {len(largest_component)} nodes")
    print(f"  Other components: {[len(c) for c in components if c != largest_component][:10]}")
    
    # Build new graph with only largest component
    new_graph = Graph()
    for node in largest_component:
        for neighbor, weight in graph.neighbors(node):
            if neighbor in largest_component:
                new_graph.add_edge(node, neighbor, weight=weight, bidirectional=False)
    
    return new_graph


def get_road_network_graph(start: Location, destination: Location, padding: float = 0.01, 
                           overpass_server: str = "http://overpass-api.de/api/interpreter") -> Graph:
    """Fetch all roads in the area between start and destination using Overpass API.
    
    This creates a complete road network graph including all intersections and road segments
    in the bounding box defined by the start and destination coordinates.
    
    Args:
        start: Starting location
        destination: Destination location
        padding: Extra padding around bounding box in degrees (default: 0.01 ≈ 1km)
        overpass_server: Overpass API server URL
    
    Returns:
        Graph containing all roads in the bounding box with real intersections
        
    Raises:
        NoRouteError: If API request fails or no roads found
    """
    # Calculate bounding box
    min_lat = min(start.latitude, destination.latitude) - padding
    max_lat = max(start.latitude, destination.latitude) + padding
    min_lon = min(start.longitude, destination.longitude) - padding
    max_lon = max(start.longitude, destination.longitude) + padding
    
    # Overpass QL query for all roads in bounding box
    # We query for ways with highway tag (roads) and request full geometry
    query = f"""
    [out:json][timeout:300];
    (
      way["highway"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        response = requests.post(
            overpass_server,
            data={"data": query},
            timeout=300
        )
        response.raise_for_status()
        data = response.json()
        
    except requests.exceptions.Timeout as e:
        raise NoRouteError(f"Overpass API request timed out: {e}") from e
    except requests.exceptions.RequestException as e:
        raise NoRouteError(f"Network connection error: {e}") from e
    except ValueError as e:
        raise NoRouteError(f"Invalid response from Overpass API: {e}") from e
    
    if not data.get("elements"):
        raise NoRouteError(
            f"No roads found in area between {start.address} and {destination.address}. "
            "Try increasing the search area or check your coordinates."
        )
    
    # Build graph from OSM data
    graph = Graph()
    
    # First pass: collect all nodes (coordinates)
    osm_nodes = {}  # osm_id -> Node
    for element in data["elements"]:
        if element["type"] == "node":
            osm_id = element["id"]
            lat = element["lat"]
            lon = element["lon"]
            osm_nodes[osm_id] = Node(
                id=f"osm_{osm_id}",
                latitude=lat,
                longitude=lon
            )
    
    # Second pass: process ways (roads) and create edges
    for element in data["elements"]:
        if element["type"] == "way":
            node_refs = element.get("nodes", [])
            
            # # Skip ways with insufficient nodes
            # if len(node_refs) < 2:
            #     continue
            
            # Create edges between consecutive nodes in the way
            for i in range(len(node_refs) - 1):
                node1_id = node_refs[i]
                node2_id = node_refs[i + 1]
                
                # Skip if nodes not found in our node collection
                if node1_id not in osm_nodes or node2_id not in osm_nodes:
                    continue
                
                node1 = osm_nodes[node1_id]
                node2 = osm_nodes[node2_id]
                
                # Calculate distance between nodes
                distance = euclidean_distance(node1, node2)
                
                # Skip zero-distance edges
                if distance < 0.003:  # Less than 3 meters
                    continue
                
                # Determine if road is one-way
                tags = element.get("tags", {})
                oneway = tags.get("oneway", "no")
                
                # Add edge (bidirectional by default unless one-way)
                if oneway in ["yes", "true", "1"]:
                    graph.add_edge(node1, node2, weight=distance, bidirectional=False)
                else:
                    graph.add_edge(node1, node2, weight=distance, bidirectional=True)
    
    # Debug: Print graph statistics
    all_nodes = graph.nodes()
    print("\n[ROAD NETWORK GRAPH DEBUG]")
    print(f"  Bounding box: ({min_lat:.4f}, {min_lon:.4f}) to ({max_lat:.4f}, {max_lon:.4f})")
    print(f"  Total nodes: {len(all_nodes)}")
    print(f"  Total OSM ways processed: {sum(1 for e in data['elements'] if e['type'] == 'way')}")
    
    if all_nodes:
        total_edges = sum(len(graph.neighbors(n)) for n in all_nodes)
        print(f"  Total edges: {total_edges}")
        avg_neighbors = total_edges / len(all_nodes)
        print(f"  Average neighbors per node: {avg_neighbors:.2f}")
        # Check for intersections (nodes with >2 neighbors)
        intersections = sum(1 for n in all_nodes if len(graph.neighbors(n)) > 2)
        print(f"  Intersections (nodes with >2 neighbors): {intersections}")
    
    return graph


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
            if step_distance < 0.003:
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


def get_all_roads(graph: Graph) -> list[tuple[Node, Node, float]]:
    """Extract all unique roads (edges) from the graph.
    
    For bidirectional roads, only returns one direction to avoid duplicates.
    
    Args:
        graph: Graph containing road network
    
    Returns:
        List of tuples (from_node, to_node, distance) representing each road segment
        
    Example:
        >>> graph = get_road_network_graph(start, destination)
        >>> roads = get_all_roads(graph)
        >>> for from_node, to_node, distance in roads:
        >>>     print(f"Road from ({from_node.latitude}, {from_node.longitude}) "
        >>>           f"to ({to_node.latitude}, {to_node.longitude}): {distance:.3f} km")
    """
    roads = []
    seen_edges = set()
    
    for node in graph.nodes():
        for neighbor, weight in graph.neighbors(node):
            # Create edge identifier (sorted to catch bidirectional duplicates)
            edge_id = tuple(sorted([node.id, neighbor.id]))
            
            if edge_id not in seen_edges:
                seen_edges.add(edge_id)
                roads.append((node, neighbor, weight))
    
    return roads


def iterate_all_roads(graph: Graph):
    """Generator to iterate through all roads in the graph.
    
    Yields one road segment at a time to avoid loading all roads into memory.
    
    Args:
        graph: Graph containing road network
        
    Yields:
        Tuples of (from_node, to_node, distance) for each unique road segment
        
    Example:
        >>> graph = get_road_network_graph(start, destination)
        >>> for from_node, to_node, distance in iterate_all_roads(graph):
        >>>     print(f"Processing road: {distance:.3f} km")
    """
    seen_edges = set()
    
    for node in graph.nodes():
        for neighbor, weight in graph.neighbors(node):
            # Create edge identifier (sorted to catch bidirectional duplicates)
            edge_id = tuple(sorted([node.id, neighbor.id]))
            
            if edge_id not in seen_edges:
                seen_edges.add(edge_id)
                yield (node, neighbor, weight)
