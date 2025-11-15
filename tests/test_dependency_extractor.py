"""Tests for dependency graph extraction."""

import tempfile
from pathlib import Path

import pytest

from src.dependency_graph.extractor import (
    _normalize_package_name,
    categorize_package,
    create_networkx_graph,
    extract_dependencies_from_metadata,
    parse_pyproject_toml,
)


def test_normalize_package_name():
    """Test package name normalization."""
    assert _normalize_package_name("numpy>=1.21.0") == "numpy"
    assert _normalize_package_name("pandas[all]>=1.3.0") == "pandas"
    assert _normalize_package_name("torch @ https://example.com") == "torch"
    assert _normalize_package_name("scikit-learn") == "scikit-learn"
    assert _normalize_package_name("Pillow") == "pillow"


def test_categorize_package():
    """Test package categorization."""
    assert categorize_package("torch") == "ml"
    assert categorize_package("numpy") == "scientific"
    assert categorize_package("pillow") == "data"
    assert categorize_package("matplotlib") == "visualization"
    assert categorize_package("typing-extensions") == "utilities"
    assert categorize_package("unknown-package") == "utilities"


def test_parse_pyproject_toml():
    """Test parsing pyproject.toml file."""
    # Create temporary pyproject.toml
    content = """
[project]
dependencies = [
    "numpy>=1.21.0",
    "pandas>=1.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
"""

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False
    ) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = parse_pyproject_toml(temp_path)
        assert len(result["dependencies"]) == 2
        assert "numpy>=1.21.0" in result["dependencies"]
        assert "dev" in result["optional-dependencies"]
    finally:
        temp_path.unlink()


def test_extract_dependencies_from_metadata():
    """Test extracting dependencies from PyPI metadata."""
    metadata = {
        "info": {
            "requires_dist": [
                "numpy>=1.20.0",
                "scipy>=1.7.0",
                "matplotlib>=3.0; extra == 'viz'",  # Should be skipped
            ]
        }
    }

    deps = extract_dependencies_from_metadata(metadata)
    assert "numpy" in deps
    assert "scipy" in deps
    assert len(deps) == 2  # matplotlib should be excluded (conditional)


def test_create_networkx_graph():
    """Test creating NetworkX graph from dependency dict."""
    dep_graph = {
        "sleap": {"numpy", "scipy"},
        "numpy": set(),
        "scipy": {"numpy"},
    }

    G = create_networkx_graph(dep_graph, root_package="sleap")

    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 3
    assert G.has_edge("sleap", "numpy")
    assert G.has_edge("sleap", "scipy")
    assert G.has_edge("scipy", "numpy")

    # Check node attributes
    assert G.nodes["sleap"]["is_root"] is True
    assert G.nodes["numpy"]["is_root"] is False