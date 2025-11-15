"""Tests for dependency graph visualization."""

import tempfile
from pathlib import Path

import networkx as nx
import pytest

from src.dependency_graph.visualizer import (
    calculate_graph_metrics,
    create_graph_layout,
)


def create_test_graph():
    """Create a simple test graph."""
    G = nx.DiGraph()
    G.add_node("sleap", category="ml", is_root=True)
    G.add_node("numpy", category="scientific", is_root=False)
    G.add_node("scipy", category="scientific", is_root=False)
    G.add_node("matplotlib", category="visualization", is_root=False)

    G.add_edge("sleap", "numpy")
    G.add_edge("sleap", "scipy")
    G.add_edge("sleap", "matplotlib")
    G.add_edge("scipy", "numpy")

    return G


def test_calculate_graph_metrics():
    """Test graph metrics calculation."""
    G = create_test_graph()
    metrics = calculate_graph_metrics(G)

    assert metrics["num_nodes"] == 4
    assert metrics["num_edges"] == 4
    assert "degree_centrality" in metrics
    assert "total_degree" in metrics
    assert "top_packages" in metrics

    # numpy should have highest in-degree (2 packages depend on it)
    assert metrics["in_degree"]["numpy"] == 2


def test_create_graph_layout():
    """Test graph layout generation."""
    G = create_test_graph()

    # Test spring layout
    pos = create_graph_layout(G, layout_type="spring", k=0.15)
    assert len(pos) == 4
    assert "sleap" in pos
    assert all(len(coords) == 2 for coords in pos.values())

    # Test Kamada-Kawai layout
    pos_kk = create_graph_layout(G, layout_type="kamada_kawai")
    assert len(pos_kk) == 4


def test_invalid_layout_type():
    """Test error handling for invalid layout type."""
    G = create_test_graph()

    with pytest.raises(ValueError, match="Unknown layout type"):
        create_graph_layout(G, layout_type="invalid")