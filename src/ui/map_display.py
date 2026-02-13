"""Map display component for dual-map route visualization.

This module provides side-by-side map rendering for comparing A* and Dijkstra routes.
"""

import folium
import streamlit as st
from streamlit_folium import st_folium

from ..utils.types import Route


def render_dual_maps(
    astar_route: Route, dijkstra_route: Route, astar_map: folium.Map, dijkstra_map: folium.Map
) -> None:
    """Render side-by-side maps comparing A* and Dijkstra routes.

    Args:
        astar_route: Route object containing A* algorithm results
        dijkstra_route: Route object containing Dijkstra algorithm results
        astar_map: Folium map with A* route visualization
        dijkstra_map: Folium map with Dijkstra route visualization

    Example:
        >>> astar_route = Route(path=[...], total_distance=5.2, algorithm="A*", ...)
        >>> dijkstra_route = Route(path=[...], total_distance=5.2, algorithm="Dijkstra", ...)
        >>> render_dual_maps(astar_route, dijkstra_route, astar_map, dijkstra_map)
    """
    st.markdown("---")
    st.subheader("📍 Route Comparison")

    # Create two columns for side-by-side display
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔵 A* Algorithm")
        st.caption(
            f"Distance: {astar_route.total_distance:.2f} km | "
            f"Time: {astar_route.execution_time} ms"
        )

        # Render A* map
        st_folium(
            astar_map,
            width=500,
            height=400,
            returned_objects=[],  # Don't need interaction data
        )

    with col2:
        st.markdown("### 🔴 Dijkstra Algorithm")
        st.caption(
            f"Distance: {dijkstra_route.total_distance:.2f} km | "
            f"Time: {dijkstra_route.execution_time} ms"
        )

        # Render Dijkstra map
        st_folium(
            dijkstra_map,
            width=500,
            height=400,
            returned_objects=[],  # Don't need interaction data
        )
