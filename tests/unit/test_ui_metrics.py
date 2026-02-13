"""Unit tests for UI component functions.

Tests for metrics calculation and display logic.
"""

import unittest

from src.ui.metrics_display import calculate_performance_summary
from src.utils.types import Location, Node, Route


class TestCalculatePerformanceSummary(unittest.TestCase):
    """Test calculate_performance_summary function."""

    def test_astar_faster_explores_fewer_nodes(self) -> None:
        """Test typical case where A* is faster and explores fewer nodes."""
        # Create test nodes
        nodes = [Node("node_0", 0.0, 0.0), Node("node_1", 1.0, 1.0)]

        astar = Route(
            path=nodes,
            total_distance=5.2,
            algorithm="A*",
            execution_time=42,
            nodes_explored=120,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=5.2,
            algorithm="Dijkstra",
            execution_time=58,
            nodes_explored=180,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        self.assertAlmostEqual(summary["speedup_factor"], 58 / 42, places=2)
        self.assertAlmostEqual(summary["node_reduction_pct"], (180 - 120) / 180 * 100, places=1)
        self.assertTrue(summary["path_match"])

    def test_equal_execution_times(self) -> None:
        """Test case where both algorithms have same execution time."""
        nodes = [Node("node_0", 0.0, 0.0)]

        astar = Route(
            path=nodes,
            total_distance=1.0,
            algorithm="A*",
            execution_time=50,
            nodes_explored=100,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=1.0,
            algorithm="Dijkstra",
            execution_time=50,
            nodes_explored=150,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        self.assertEqual(summary["speedup_factor"], 1.0)
        self.assertGreater(summary["node_reduction_pct"], 0)

    def test_zero_execution_time_handled(self) -> None:
        """Test edge case where A* execution time is zero."""
        nodes = [Node("node_0", 0.0, 0.0)]

        astar = Route(
            path=nodes,
            total_distance=1.0,
            algorithm="A*",
            execution_time=0,
            nodes_explored=10,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=1.0,
            algorithm="Dijkstra",
            execution_time=5,
            nodes_explored=20,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        # Should not crash, should default to 1.0
        self.assertEqual(summary["speedup_factor"], 1.0)

    def test_zero_nodes_explored_handled(self) -> None:
        """Test edge case where Dijkstra explored zero nodes."""
        nodes = [Node("node_0", 0.0, 0.0)]

        astar = Route(
            path=nodes,
            total_distance=1.0,
            algorithm="A*",
            execution_time=5,
            nodes_explored=0,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=1.0,
            algorithm="Dijkstra",
            execution_time=10,
            nodes_explored=0,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        # Should not crash, should default to 0.0
        self.assertEqual(summary["node_reduction_pct"], 0.0)

    def test_path_mismatch_detected(self) -> None:
        """Test detection when path lengths differ significantly."""
        nodes = [Node("node_0", 0.0, 0.0)]

        astar = Route(
            path=nodes,
            total_distance=5.0,
            algorithm="A*",
            execution_time=10,
            nodes_explored=50,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=6.0,  # 20% difference
            algorithm="Dijkstra",
            execution_time=15,
            nodes_explored=80,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        self.assertFalse(summary["path_match"])

    def test_path_match_within_tolerance(self) -> None:
        """Test that very small differences are considered matching."""
        nodes = [Node("node_0", 0.0, 0.0)]

        astar = Route(
            path=nodes,
            total_distance=10.0,
            algorithm="A*",
            execution_time=10,
            nodes_explored=50,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=10.0005,  # 0.005% difference
            algorithm="Dijkstra",
            execution_time=15,
            nodes_explored=80,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        self.assertTrue(summary["path_match"])

    def test_dijkstra_faster_case(self) -> None:
        """Test edge case where Dijkstra is faster (very small graphs)."""
        nodes = [Node("node_0", 0.0, 0.0), Node("node_1", 0.1, 0.1)]

        astar = Route(
            path=nodes,
            total_distance=0.1,
            algorithm="A*",
            execution_time=10,  # A* overhead on tiny graph
            nodes_explored=2,
        )
        dijkstra = Route(
            path=nodes,
            total_distance=0.1,
            algorithm="Dijkstra",
            execution_time=5,
            nodes_explored=3,
        )

        summary = calculate_performance_summary(astar, dijkstra)

        self.assertLess(summary["speedup_factor"], 1.0)
        self.assertEqual(summary["speedup_factor"], 5 / 10)


if __name__ == "__main__":
    unittest.main()
