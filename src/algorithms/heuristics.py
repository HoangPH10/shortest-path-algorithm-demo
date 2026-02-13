"""Heuristic functions for A* pathfinding algorithm."""

import math

from src.utils.types import Node


def euclidean_distance(node1: Node, node2: Node) -> float:
    """Calculate Haversine distance between two nodes in kilometers.

    Uses the Haversine formula to calculate great-circle distance
    between two points on Earth's surface. This is an admissible
    heuristic for A* (never overestimates true distance).

    Args:
        node1: First node
        node2: Second node

    Returns:
        Distance in kilometers
    """
    if node1 == node2:
        return 0.0

    # Convert to radians
    lat1 = math.radians(node1.latitude)
    lon1 = math.radians(node1.longitude)
    lat2 = math.radians(node2.latitude)
    lon2 = math.radians(node2.longitude)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in kilometers
    radius_km = 6371.0

    return radius_km * c


def manhattan_distance(node1: Node, node2: Node) -> float:
    """Calculate Manhattan distance between two nodes in kilometers.

    Approximates distance as sum of north-south and east-west distances.
    Useful for grid-like road networks. Less accurate than Haversine but
    computationally simpler.

    Args:
        node1: First node
        node2: Second node

    Returns:
        Manhattan distance in kilometers
    """
    if node1 == node2:
        return 0.0

    # Convert latitude/longitude differences to approximate kilometers
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)

    lat_diff = abs(node2.latitude - node1.latitude)
    lon_diff = abs(node2.longitude - node1.longitude)

    avg_lat = (node1.latitude + node2.latitude) / 2
    lat_dist = lat_diff * 111.0
    lon_dist = lon_diff * 111.0 * math.cos(math.radians(avg_lat))

    return lat_dist + lon_dist


def diagonal_distance(node1: Node, node2: Node) -> float:
    """Calculate diagonal (Chebyshev) distance between two nodes in kilometers.

    Approximates distance allowing diagonal moves. Useful for graphs
    where diagonal movement has same cost as cardinal movement.

    Args:
        node1: First node
        node2: Second node

    Returns:
        Diagonal distance in kilometers
    """
    if node1 == node2:
        return 0.0

    # Convert latitude/longitude differences to approximate kilometers
    lat_diff = abs(node2.latitude - node1.latitude)
    lon_diff = abs(node2.longitude - node1.longitude)

    avg_lat = (node1.latitude + node2.latitude) / 2
    lat_dist = lat_diff * 111.0
    lon_dist = lon_diff * 111.0 * math.cos(math.radians(avg_lat))

    # Diagonal distance: max of horizontal and vertical distances
    # (since diagonal moves are allowed)
    return max(lat_dist, lon_dist)


def simple_distance(node1: Node, node2: Node) -> float:
    """Calculate fast approximate distance between two nodes in kilometers.

    Uses simple Euclidean distance in lat/lon space with basic scaling.
    This is the fastest heuristic but least accurate. Good for performance
    when accuracy is less critical.

    Args:
        node1: First node
        node2: Second node

    Returns:
        Approximate distance in kilometers
    """
    if node1 == node2:
        return 0.0

    # Simple approximation without trigonometric functions
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km at equator, scales with latitude
    lat_diff = node2.latitude - node1.latitude
    lon_diff = node2.longitude - node1.longitude
    
    # Use average latitude for longitude scaling (simple approximation)
    avg_lat = (node1.latitude + node2.latitude) / 2
    # Simplified cos approximation: cos(lat) ≈ 1 - lat²/2 (for small angles in radians)
    # For lat in degrees, approximate cos factor
    lat_factor = 1.0 - (avg_lat / 90.0) ** 2 * 0.5
    
    # Calculate approximate distance
    lat_km = lat_diff * 111.0
    lon_km = lon_diff * 111.0 * lat_factor
    
    # Euclidean distance
    return math.sqrt(lat_km * lat_km + lon_km * lon_km)
