"""Metrics display component for route comparison.

This module provides tabular comparison of algorithm performance metrics.
"""

from typing import Dict

import pandas as pd
import streamlit as st

from ..utils.types import Route


def calculate_performance_summary(astar_route: Route, dijkstra_route: Route) -> Dict[str, float]:
    """Calculate performance comparison metrics between A* and Dijkstra.

    Args:
        astar_route: Route from A* algorithm
        dijkstra_route: Route from Dijkstra algorithm

    Returns:
        Dictionary with speedup_factor, node_reduction_pct, and path_match

    Example:
        >>> summary = calculate_performance_summary(astar, dijkstra)
        >>> summary['speedup_factor']  # 2.5 means A* is 2.5x faster
        2.5
    """
    # Calculate speedup factor (how many times faster A* is)
    if astar_route.execution_time > 0:
        speedup_factor = dijkstra_route.execution_time / astar_route.execution_time
    else:
        speedup_factor = 1.0

    # Calculate node reduction percentage
    if dijkstra_route.nodes_explored > 0:
        node_reduction_pct = (
            (dijkstra_route.nodes_explored - astar_route.nodes_explored)
            / dijkstra_route.nodes_explored
            * 100
        )
    else:
        node_reduction_pct = 0.0

    # Check if path lengths match (within 0.1% tolerance)
    path_match = abs(astar_route.total_distance - dijkstra_route.total_distance) < (
        astar_route.total_distance * 0.001
    )

    return {
        "speedup_factor": speedup_factor,
        "node_reduction_pct": node_reduction_pct,
        "path_match": path_match,
    }


def render_metrics_table(astar_route: Route, dijkstra_route: Route) -> None:
    """Render comparison table showing algorithm performance metrics.

    Args:
        astar_route: Route object containing A* algorithm results
        dijkstra_route: Route object containing Dijkstra algorithm results

    Example:
        >>> astar_route = Route(path=[...], total_distance=5.2, algorithm="A*",
        ...                     execution_time=42, nodes_explored=120)
        >>> dijkstra_route = Route(path=[...], total_distance=5.2, algorithm="Dijkstra",
        ...                        execution_time=58, nodes_explored=180)
        >>> render_metrics_table(astar_route, dijkstra_route)
    """
    st.markdown("---")
    st.subheader("📊 Performance Metrics")

    # Create comparison dataframe
    metrics_data = {
        "Metric": [
            "Execution Time (ms)",
            "Path Length (km)",
            "Nodes Explored",
        ],
        "A* Algorithm": [
            f"{astar_route.execution_time}",
            f"{astar_route.total_distance:.2f}",
            f"{astar_route.nodes_explored}",
        ],
        "Dijkstra Algorithm": [
            f"{dijkstra_route.execution_time}",
            f"{dijkstra_route.total_distance:.2f}",
            f"{dijkstra_route.nodes_explored}",
        ],
    }

    df = pd.DataFrame(metrics_data)

    # Display as styled table
    st.table(df.set_index("Metric"))

    # Calculate and display performance summary
    summary = calculate_performance_summary(astar_route, dijkstra_route)

    # Path correctness verification
    if summary["path_match"]:
        st.success("✓ Both algorithms found optimal paths of equal length")
    else:
        st.warning(
            f"⚠️ Path lengths differ: A*={astar_route.total_distance:.2f}km, "
            f"Dijkstra={dijkstra_route.total_distance:.2f}km"
        )

    # Performance comparison summary
    if summary["speedup_factor"] >= 1.0:
        st.info(
            f"🚀 **A* Performance**: "
            f"{summary['speedup_factor']:.2f}× faster than Dijkstra "
            f"and explored {summary['node_reduction_pct']:.1f}% fewer nodes "
            f"due to heuristic guidance"
        )
    else:
        # Edge case where Dijkstra might be faster on very small graphs
        st.info(
            f"📊 **Performance**: "
            f"Dijkstra was {1/summary['speedup_factor']:.2f}× faster "
            f"(A* explored {summary['node_reduction_pct']:.1f}% fewer nodes but took longer)"
        )

    # Educational note
    st.caption(
        "💡 **Why A* is typically faster**: A* uses a heuristic function (Euclidean distance) "
        "to guide its search toward the goal, exploring fewer irrelevant nodes. "
        "Dijkstra explores nodes uniformly in all directions without goal awareness."
    )
