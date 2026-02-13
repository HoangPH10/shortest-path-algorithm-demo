"""Tests for graph data structures (Node, Edge, Graph)."""

import pytest

from src.algorithms.graph import Edge, Graph, Node


class TestNode:
    """Tests for Node dataclass."""

    def test_node_creation(self) -> None:
        """Test creating a node with valid data."""
        node = Node(id="node_1", latitude=40.7580, longitude=-73.9855)
        assert node.id == "node_1"
        assert node.latitude == 40.7580
        assert node.longitude == -73.9855

    def test_node_equality(self) -> None:
        """Test nodes are equal if IDs match."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_1", latitude=41.0, longitude=-74.0)  # Different coords, same ID
        node3 = Node(id="node_2", latitude=40.0, longitude=-73.0)

        assert node1 == node2  # Same ID
        assert node1 != node3  # Different ID

    def test_node_hashing(self) -> None:
        """Test nodes can be used as dictionary keys and in sets."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node3 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        # Nodes with same ID should hash to same value
        assert hash(node1) == hash(node2)

        # Can use nodes in sets
        node_set = {node1, node2, node3}
        assert len(node_set) == 2  # node1 and node2 are duplicates

        # Can use nodes as dictionary keys
        node_dict = {node1: "value1", node3: "value2"}
        assert node_dict[node2] == "value1"  # node2 same as node1


class TestEdge:
    """Tests for Edge dataclass."""

    def test_edge_creation(self) -> None:
        """Test creating an edge with valid weight."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)
        edge = Edge(from_node=node1, to_node=node2, weight=100.5)

        assert edge.from_node == node1
        assert edge.to_node == node2
        assert edge.weight == 100.5

    def test_edge_negative_weight_rejection(self) -> None:
        """Test edges reject negative weights."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        with pytest.raises(ValueError, match="Edge weight must be positive"):
            Edge(from_node=node1, to_node=node2, weight=-10.0)

    def test_edge_zero_weight_rejection(self) -> None:
        """Test edges reject zero weight."""
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        with pytest.raises(ValueError, match="Edge weight must be positive"):
            Edge(from_node=node1, to_node=node2, weight=0.0)


class TestGraph:
    """Tests for Graph class."""

    def test_graph_creation(self) -> None:
        """Test creating an empty graph."""
        graph = Graph()
        assert len(graph.nodes()) == 0

    def test_add_node(self) -> None:
        """Test adding nodes to graph."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        graph.add_node(node1)
        graph.add_node(node2)

        nodes = graph.nodes()
        assert len(nodes) == 2
        assert node1 in nodes
        assert node2 in nodes

    def test_add_duplicate_node(self) -> None:
        """Test adding same node twice doesn't duplicate."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)

        graph.add_node(node1)
        graph.add_node(node1)

        assert len(graph.nodes()) == 1

    def test_add_edge(self) -> None:
        """Test adding edges between nodes."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(node1, node2, weight=100.0)

        neighbors = graph.neighbors(node1)
        assert len(neighbors) == 1
        assert neighbors[0] == (node2, 100.0)

    def test_add_bidirectional_edge(self) -> None:
        """Test adding edges in both directions."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(node1, node2, weight=100.0, bidirectional=True)

        # Check both directions exist
        assert len(graph.neighbors(node1)) == 1
        assert len(graph.neighbors(node2)) == 1
        assert graph.neighbors(node1)[0] == (node2, 100.0)
        assert graph.neighbors(node2)[0] == (node1, 100.0)

    def test_add_edge_auto_adds_nodes(self) -> None:
        """Test adding edge automatically adds nodes if not present."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)

        graph.add_edge(node1, node2, weight=100.0)

        assert len(graph.nodes()) == 2
        assert node1 in graph.nodes()
        assert node2 in graph.nodes()

    def test_neighbors_nonexistent_node(self) -> None:
        """Test querying neighbors of nonexistent node returns empty list."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)

        neighbors = graph.neighbors(node1)
        assert neighbors == []

    def test_multiple_edges_from_node(self) -> None:
        """Test node can have multiple outgoing edges."""
        graph = Graph()
        node1 = Node(id="node_1", latitude=40.0, longitude=-73.0)
        node2 = Node(id="node_2", latitude=41.0, longitude=-74.0)
        node3 = Node(id="node_3", latitude=42.0, longitude=-75.0)

        graph.add_edge(node1, node2, weight=100.0)
        graph.add_edge(node1, node3, weight=150.0)

        neighbors = graph.neighbors(node1)
        assert len(neighbors) == 2
        assert (node2, 100.0) in neighbors
        assert (node3, 150.0) in neighbors
