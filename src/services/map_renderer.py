"""Map rendering service using Folium."""

import folium

from src.algorithms.graph import Graph
from src.utils.types import Location, Route, Node


def create_route_map(route: Route, start: Location, destination: Location, 
                    max_explored_edges: int = 3000, max_explored_nodes: int = 2000) -> folium.Map:
    """Create an interactive map visualizing a route.

    Args:
        route: Route object with path and algorithm information
        start: Starting location
        destination: Destination location
        max_explored_edges: Maximum number of explored edges to render (default: 3000)
        max_explored_nodes: Maximum number of explored nodes to render (default: 2000)

    Returns:
        Folium Map object with route polyline and markers
    """
    # Define colors: blue for explored paths, red for final path
    explored_path_color = "#4285F4"  # Blue for explored paths
    final_path_color = "#EA4335"     # Red for final optimal path
    explored_color = "#6BA3FF"        # Medium Blue (visited nodes)
    open_set_color = "#C3DBFF"        # Very Light Blue (in queue nodes)

    # Calculate map center (midpoint of route)
    if route.path:
        avg_lat = sum(node.latitude for node in route.path) / len(route.path)
        avg_lng = sum(node.longitude for node in route.path) / len(route.path)
    else:
        avg_lat = start.latitude
        avg_lng = start.longitude

    # Create base map
    route_map = folium.Map(
        location=[avg_lat, avg_lng],
        zoom_start=13,
        tiles="OpenStreetMap",
    )

    # OPTIMIZATION: Use FeatureGroups to batch similar objects
    explored_edges_group = folium.FeatureGroup(name="Explored Edges")
    explored_nodes_group = folium.FeatureGroup(name="Explored Nodes")
    open_set_group = folium.FeatureGroup(name="Open Set Nodes")

    # LAYER 1: Add explored edges visualization (sampled for performance)
    if route.explored_edges and len(route.explored_edges) > 0:
        total_edges = len(route.explored_edges)
        
        # Sample edges if too many (take evenly distributed subset)
        if total_edges > max_explored_edges:
            step = total_edges // max_explored_edges
            sampled_edges = route.explored_edges[::step]
        else:
            sampled_edges = route.explored_edges
        
        # Batch add edges to feature group
        for from_node, to_node in sampled_edges:
            folium.PolyLine(
                locations=[[from_node.latitude, from_node.longitude],
                          [to_node.latitude, to_node.longitude]],
                color=explored_path_color,
                weight=2,  # Reduced from 3
                opacity=0.5,  # Reduced from 0.6
                popup=f"Explored: {from_node.id} → {to_node.id}",
            ).add_to(explored_edges_group)
        
        explored_edges_group.add_to(route_map)

    # LAYER 2: Add open_set nodes visualization (sampled)
    if route.open_set_nodes and len(route.open_set_nodes) > 0:
        total_open = len(route.open_set_nodes)
        
        # Sample if too many
        if total_open > max_explored_nodes // 2:
            step = total_open // (max_explored_nodes // 2)
            sampled_open = route.open_set_nodes[::step]
        else:
            sampled_open = route.open_set_nodes
        
        for node in sampled_open:
            folium.CircleMarker(
                location=[node.latitude, node.longitude],
                radius=1.5,  # Reduced from 2
                color=open_set_color,
                fill=True,
                fillColor=open_set_color,
                fillOpacity=0.3,
                weight=0.5,  # Reduced from 1
                opacity=0.4,  # Reduced from 0.5
                popup=f"In Queue: {node.id}",
            ).add_to(open_set_group)
        
        open_set_group.add_to(route_map)
    
    # LAYER 3: Add explored nodes visualization (sampled)
    if route.explored_nodes and len(route.explored_nodes) > 0:
        total_explored = len(route.explored_nodes)
        
        # Sample if too many
        if total_explored > max_explored_nodes:
            step = total_explored // max_explored_nodes
            sampled_nodes = route.explored_nodes[::step]
        else:
            sampled_nodes = route.explored_nodes
        
        for node in sampled_nodes:
            folium.CircleMarker(
                location=[node.latitude, node.longitude],
                radius=1.5,  # Reduced from 2
                color=explored_color,
                fill=True,
                fillColor=explored_color,
                fillOpacity=0.4,  # Reduced from 0.5
                weight=0.5,  # Reduced from 1
                opacity=0.6,  # Reduced from 0.7
                popup=f"Visited: {node.id}",
            ).add_to(explored_nodes_group)
        
        explored_nodes_group.add_to(route_map)

    # LAYER 4: Add final route polyline (RED color, thicker, drawn on top)
    if len(route.path) > 1:
        coordinates = [[node.latitude, node.longitude] for node in route.path]

        folium.PolyLine(
            locations=coordinates,
            color=final_path_color,
            weight=6,
            opacity=1.0,
            popup=f"{route.algorithm}: {route.total_distance:.2f} km",
        ).add_to(route_map)
        
        # LAYER 5: Add markers for each waypoint in the final path (on top of everything)
        for i, node in enumerate(route.path):
            folium.CircleMarker(
                location=[node.latitude, node.longitude],
                radius=5,
                color=final_path_color,
                fill=True,
                fillColor="white",
                fillOpacity=1.0,
                weight=2,
                popup=f"Path Node {i}: {node.id}",
            ).add_to(route_map)

    # LAYER 6: Add start marker (green)
    folium.Marker(
        location=[start.latitude, start.longitude],
        popup=f"<b>Start:</b><br>{start.address}",
        tooltip="Start Location",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(route_map)

    # LAYER 7: Add destination marker (red)
    folium.Marker(
        location=[destination.latitude, destination.longitude],
        popup=f"<b>Destination:</b><br>{destination.address}",
        tooltip="Destination",
        icon=folium.Icon(color="red", icon="stop", prefix="fa"),
    ).add_to(route_map)

    # Add custom legend showing route information
    # Calculate sampling info
    total_edges = len(route.explored_edges) if route.explored_edges else 0
    total_nodes = len(route.explored_nodes) if route.explored_nodes else 0
    total_open = len(route.open_set_nodes) if route.open_set_nodes else 0
    
    edges_sampled = total_edges > max_explored_edges
    nodes_sampled = total_nodes > max_explored_nodes
    open_sampled = total_open > max_explored_nodes // 2
    
    edges_text = f"{total_edges} edges" + (" (sampled)" if edges_sampled else "")
    nodes_text = f"{total_nodes}" + (" (sampled)" if nodes_sampled else "")
    open_text = f"{total_open}" + (" (sampled)" if open_sampled else "")
    
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 280px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px; border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <p style="margin: 0 0 8px 0; font-weight: bold; font-size: 15px;">
            {route.algorithm} Route
        </p>
        <p style="margin: 5px 0;">
            <span style="color: {final_path_color}; font-weight: bold;">━━━</span> 
            Final Path ({route.total_distance:.2f} km)
        </p>
        <p style="margin: 5px 0;">
            <span style="color: {explored_path_color}; font-weight: bold;">━━━</span> 
            Explored Paths ({edges_text})
        </p>
        <p style="margin: 5px 0;">
            <span style="background-color: {explored_color}; color: {explored_color}; border-radius: 50%; padding: 0 5px;">●</span> 
            Visited Nodes ({nodes_text})
        </p>
        <p style="margin: 5px 0;">
            <span style="background-color: {open_set_color}; color: {open_set_color}; border-radius: 50%; padding: 0 5px;">●</span> 
            Queue Nodes ({open_text})
        </p>
        <p style="margin: 8px 0 5px 0;">
            <i class="fa fa-play" style="color: green;"></i> Start Location
        </p>
        <p style="margin: 5px 0 0 0;">
            <i class="fa fa-stop" style="color: red;"></i> Destination
        </p>
    </div>
    '''
    route_map.get_root().html.add_child(folium.Element(legend_html))

    return route_map


def create_road_network_map(graph: Graph, start: Location, destination: Location, 
                            show_intersections: bool = True) -> folium.Map:
    """Create an interactive map visualizing the entire road network.
    
    Shows all roads in the bounding box area as a reference layer.
    Useful for understanding the complete road topology before pathfinding.
    
    Args:
        graph: Graph containing all roads in the area
        start: Starting location (for map centering and markers)
        destination: Destination location
        show_intersections: Whether to highlight intersection nodes (default: True)
    
    Returns:
        Folium Map object with all roads visualized
    """
    # Colors for road network visualization
    road_color = "#B0B0B0"           # Light gray for all roads
    intersection_color = "#FF6B6B"   # Red for intersections
    node_color = "#D0D0D0"           # Very light gray for regular nodes
    
    # Calculate map center
    all_nodes = graph.nodes()
    if all_nodes:
        avg_lat = sum(node.latitude for node in all_nodes) / len(all_nodes)
        avg_lng = sum(node.longitude for node in all_nodes) / len(all_nodes)
    else:
        avg_lat = (start.latitude + destination.latitude) / 2
        avg_lng = (start.longitude + destination.longitude) / 2
    
    # Create base map
    network_map = folium.Map(
        location=[avg_lat, avg_lng],
        zoom_start=13,
        tiles="OpenStreetMap",
    )
    
    # Track which edges we've drawn to avoid duplicates
    drawn_edges = set()
    
    # LAYER 1: Draw all road segments
    for node in all_nodes:
        for neighbor, weight in graph.neighbors(node):
            # Create unique edge identifier (sorted to catch bidirectional roads)
            edge_id = tuple(sorted([node.id, neighbor.id]))
            
            if edge_id not in drawn_edges:
                drawn_edges.add(edge_id)
                
                # Draw road segment
                folium.PolyLine(
                    locations=[[node.latitude, node.longitude],
                              [neighbor.latitude, neighbor.longitude]],
                    color=road_color,
                    weight=2,
                    opacity=0.6,
                    popup=f"Road: {weight:.3f} km",
                ).add_to(network_map)
    
    # LAYER 2: Draw intersection nodes (nodes with >2 connections)
    if show_intersections:
        intersections = []
        regular_nodes = []
        
        for node in all_nodes:
            neighbor_count = len(graph.neighbors(node))
            if neighbor_count > 2:
                intersections.append((node, neighbor_count))
            elif neighbor_count > 0:
                regular_nodes.append(node)
        
        # Draw regular nodes (smaller, lighter)
        for node in regular_nodes:
            folium.CircleMarker(
                location=[node.latitude, node.longitude],
                radius=1.5,
                color=node_color,
                fill=True,
                fillColor=node_color,
                fillOpacity=0.4,
                weight=1,
                popup=f"Node: {node.id}",
            ).add_to(network_map)
        
        # Draw intersections (larger, red)
        for node, neighbor_count in intersections:
            folium.CircleMarker(
                location=[node.latitude, node.longitude],
                radius=4,
                color=intersection_color,
                fill=True,
                fillColor=intersection_color,
                fillOpacity=0.7,
                weight=2,
                popup=f"Intersection: {neighbor_count} roads",
            ).add_to(network_map)
    
    # LAYER 3: Add start marker (green)
    folium.Marker(
        location=[start.latitude, start.longitude],
        popup=f"<b>Start:</b><br>{start.address}",
        tooltip="Start Location",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(network_map)
    
    # LAYER 4: Add destination marker (red)
    folium.Marker(
        location=[destination.latitude, destination.longitude],
        popup=f"<b>Destination:</b><br>{destination.address}",
        tooltip="Destination",
        icon=folium.Icon(color="red", icon="stop", prefix="fa"),
    ).add_to(network_map)
    
    # Add legend
    total_roads = len(drawn_edges)
    total_nodes = len(all_nodes)
    intersections_count = sum(1 for n in all_nodes if len(graph.neighbors(n)) > 2)
    
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 260px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px; border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <p style="margin: 0 0 8px 0; font-weight: bold; font-size: 15px;">
            Road Network Overview
        </p>
        <p style="margin: 5px 0;">
            <span style="color: {road_color}; font-weight: bold;">━━━</span> 
            Roads ({total_roads} segments)
        </p>
        <p style="margin: 5px 0;">
            <span style="background-color: {intersection_color}; color: {intersection_color}; border-radius: 50%; padding: 0 5px;">●</span> 
            Intersections ({intersections_count})
        </p>
        <p style="margin: 5px 0;">
            <span style="background-color: {node_color}; color: {node_color}; border-radius: 50%; padding: 0 5px;">●</span> 
            Road Points ({total_nodes - intersections_count})
        </p>
        <p style="margin: 8px 0 5px 0;">
            <i class="fa fa-play" style="color: green;"></i> Start Location
        </p>
        <p style="margin: 5px 0 0 0;">
            <i class="fa fa-stop" style="color: red;"></i> Destination
        </p>
    </div>
    '''
    network_map.get_root().html.add_child(folium.Element(legend_html))
    
    return network_map
