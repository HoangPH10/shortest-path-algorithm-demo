"""A* pathfinding algorithm implementation."""

import heapq
import time
from typing import Callable, Dict, List, Tuple

from src.algorithms.graph import Graph
from src.utils.types import Node, PathfindingResult, Route


def astar(
    graph: Graph,
    start: Node,
    goal: Node,
    heuristic: Callable[[Node, Node], float]
) -> PathfindingResult:
    """Execute A* pathfinding algorithm on graph.

    Args:
        graph: Road network graph with nodes and weighted edges
        start: Starting node (must exist in graph)
        goal: Destination node (must exist in graph)
        heuristic: Function that estimates distance between two nodes
                   Must be admissible (never overestimate) and consistent

    Returns:
        PathfindingResult with:
        - success=True, route=Route if path found
        - success=False, error=str if no path exists

    Raises:
        ValueError: If start or goal not in graph
        ValueError: If heuristic is not callable
    """
    # Validate inputs
    if start not in graph.nodes():
        return PathfindingResult(
            success=False,
            error=f"Start node {start.id} not found in graph"
        )
    
    if goal not in graph.nodes():
        return PathfindingResult(
            success=False,
            error=f"Goal node {goal.id} not found in graph"
        )
    
    if not callable(heuristic):
        return PathfindingResult(
            success=False,
            error="Heuristic must be a callable function"
        )

    # Start timing
    start_time = time.time()

    # Handle same start and goal
    if start == goal:
        execution_time = int((time.time() - start_time) * 1000)
        route = Route(
            path=[start],
            total_distance=0.0,
            algorithm="A*",
            execution_time=execution_time,
            nodes_explored=1,
            explored_nodes=[start],
            open_set_nodes=[start],
            explored_edges=[]
        )
        return PathfindingResult(success=True, route=route)

    # Initialize data structures
    # Priority queue: (f_score, counter, node) - counter prevents Node comparison
    # f_score = g_score + heuristic(node, goal)
    counter = 0
    pq: List[Tuple[float, int, Node]] = [(heuristic(start, goal), counter, start)]
    counter += 1
    
    # g_score: actual distance from start to node
    g_score: Dict[Node, float] = {start: 0.0}
    
    # Parent tracking for path reconstruction
    came_from: Dict[Node, Node] = {}
    
    # Visited set to avoid reprocessing
    visited = set()
    
    # Tracking for visualization
    explored_nodes: List[Node] = []
    open_set_nodes: List[Node] = [start]
    explored_edges: List[Tuple[Node, Node]] = []

    # Main A* loop
    while pq:
        _, _, current = heapq.heappop(pq)

        # Skip if already visited
        if current in visited:
            continue
        
        # Mark as visited
        visited.add(current)
        explored_nodes.append(current)

        # Goal found
        if current == goal:
            break

        # Explore neighbors
        for neighbor, edge_weight in graph.neighbors(current):
            # Track ALL edges we examine from visited nodes (even to visited neighbors)
            explored_edges.append((current, neighbor))
            
            if neighbor in visited:
                continue

            # Calculate tentative g_score
            tentative_g_score = g_score[current] + edge_weight

            # If we found a better path to neighbor
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                came_from[neighbor] = current
                heapq.heappush(pq, (f_score, counter, neighbor))
                counter += 1
                
                # Track for visualization
                if neighbor not in open_set_nodes:
                    open_set_nodes.append(neighbor)

    # Check if goal was reached
    if goal not in came_from and goal != start:
        execution_time = int((time.time() - start_time) * 1000)
        print("[A*] Failed - No path found")
        return PathfindingResult(
            success=False,
            error=f"No path found from {start.id} to {goal.id}"
        )

    # Reconstruct path
    path: List[Node] = []
    current_node = goal
    while current_node != start:
        path.append(current_node)
        current_node = came_from[current_node]
    path.append(start)
    path.reverse()

    # Calculate execution time
    execution_time = int((time.time() - start_time) * 1000)

    # Debug output
    print("\n[A* DEBUG]")
    print(f"  Nodes explored: {len(explored_nodes)}")
    print(f"  Open set nodes: {len(open_set_nodes)}")
    print(f"  Edges explored: {len(explored_edges)}")
    print(f"  Path length: {len(path)} nodes")
    print(f"  Total distance: {g_score[goal]:.2f} km")
    print(f"  Execution time: {execution_time} ms")

    # Create route
    route = Route(
        path=path,
        total_distance=g_score[goal],
        algorithm="A*",
        execution_time=execution_time,
        nodes_explored=len(explored_nodes),
        explored_nodes=explored_nodes,
        open_set_nodes=open_set_nodes,
        explored_edges=explored_edges
    )

    return PathfindingResult(success=True, route=route)
