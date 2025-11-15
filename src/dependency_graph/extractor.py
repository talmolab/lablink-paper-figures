"""Extract and build dependency graphs from Python package metadata."""

import logging
import re
import time
from pathlib import Path
from typing import Any

import networkx as nx
import requests

logger = logging.getLogger(__name__)

# Package categorization for visual encoding
PACKAGE_CATEGORIES = {
    "ml": [
        "torch",
        "pytorch",
        "tensorflow",
        "keras",
        "scikit-learn",
        "sklearn",
        "sleap",
        "sleap-nn",
        "sleap-io",
    ],
    "scientific": [
        "numpy",
        "scipy",
        "pandas",
        "sympy",
        "statsmodels",
        "scikit-image",
        "skimage",
    ],
    "data": [
        "pillow",
        "pil",
        "h5py",
        "opencv-python",
        "cv2",
        "imageio",
        "tifffile",
        "zarr",
    ],
    "visualization": [
        "matplotlib",
        "seaborn",
        "plotly",
        "bokeh",
        "altair",
        "pyqtgraph",
    ],
    "utilities": [
        "packaging",
        "typing-extensions",
        "importlib-metadata",
        "setuptools",
        "wheel",
        "pip",
    ],
}


def parse_pyproject_toml(path: Path) -> dict[str, Any]:
    """Parse pyproject.toml file and extract dependency information.

    Args:
        path: Path to pyproject.toml file or directory containing it

    Returns:
        Dictionary with 'dependencies' and 'optional-dependencies' keys

    Raises:
        FileNotFoundError: If pyproject.toml not found at path
        ValueError: If pyproject.toml is invalid
    """
    if path.is_dir():
        path = path / "pyproject.toml"

    if not path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {path}")

    logger.info(f"Parsing pyproject.toml from {path}")

    try:
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        try:
            import tomli as tomllib
        except ImportError:
            # Manual parsing fallback for simple cases
            return _parse_pyproject_manual(path)

    with open(path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    dependencies = project.get("dependencies", [])
    optional_deps = project.get("optional-dependencies", {})

    logger.info(
        f"Found {len(dependencies)} direct dependencies, "
        f"{sum(len(v) for v in optional_deps.values())} optional dependencies"
    )

    return {
        "dependencies": dependencies,
        "optional-dependencies": optional_deps,
    }


def _parse_pyproject_manual(path: Path) -> dict[str, Any]:
    """Fallback manual parser for pyproject.toml dependencies section."""
    dependencies = []
    optional_deps = {}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract main dependencies
    deps_match = re.search(
        r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL | re.MULTILINE
    )
    if deps_match:
        deps_str = deps_match.group(1)
        dependencies = [
            line.strip().strip('"').strip("'").strip(",")
            for line in deps_str.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

    return {"dependencies": dependencies, "optional-dependencies": optional_deps}


def fetch_remote_pyproject(url: str) -> dict[str, Any]:
    """Fetch pyproject.toml from a GitHub URL.

    Args:
        url: GitHub URL (blob or raw) to pyproject.toml

    Returns:
        Dictionary with dependency information

    Raises:
        requests.RequestException: If download fails
        ValueError: If URL is invalid or content cannot be parsed
    """
    # Convert GitHub blob URL to raw URL if needed
    if "github.com" in url and "/blob/" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace(
            "/blob/", "/"
        )

    logger.info(f"Fetching pyproject.toml from {url}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Save to temporary file and parse
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as f:
        f.write(response.text)
        temp_path = Path(f.name)

    try:
        return parse_pyproject_toml(temp_path)
    finally:
        temp_path.unlink()


def _normalize_package_name(pkg_spec: str) -> str:
    """Extract package name from dependency specification.

    Handles formats like:
    - numpy>=1.21.0
    - pandas[all]>=1.3.0
    - torch @ https://...
    """
    # Remove version specifiers and extras
    pkg = re.split(r"[>=<@\[]", pkg_spec)[0].strip()
    # Normalize to lowercase with hyphens
    return pkg.lower().replace("_", "-")


def fetch_pypi_metadata(package: str, retries: int = 3) -> dict[str, Any] | None:
    """Fetch package metadata from PyPI JSON API.

    Args:
        package: Package name (normalized)
        retries: Number of retry attempts on failure

    Returns:
        Package metadata dict or None if package not found
    """
    url = f"https://pypi.org/pypi/{package}/json"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                logger.warning(f"Package not found on PyPI: {package}")
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < retries - 1:
                wait_time = 2**attempt  # Exponential backoff
                logger.debug(
                    f"Retry {attempt + 1}/{retries} for {package} after {wait_time}s"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch metadata for {package}: {e}")
                return None


def extract_dependencies_from_metadata(metadata: dict[str, Any]) -> list[str]:
    """Extract dependency list from PyPI metadata.

    Args:
        metadata: PyPI JSON API response

    Returns:
        List of normalized package names
    """
    if not metadata or "info" not in metadata:
        return []

    requires_dist = metadata["info"].get("requires_dist", [])
    if not requires_dist:
        return []

    dependencies = []
    for req in requires_dist:
        # Skip conditional dependencies (platform-specific, extras, etc.)
        if ";" in req or "extra ==" in req:
            continue

        pkg_name = _normalize_package_name(req)
        if pkg_name:
            dependencies.append(pkg_name)

    return dependencies


def build_dependency_graph(
    root_dependencies: list[str],
    max_depth: int = 0,
    include_optional: bool = True,
    cache_dir: Path | None = None,
) -> dict[str, set[str]]:
    """Build transitive dependency graph from root packages.

    Args:
        root_dependencies: List of root package specifications
        max_depth: Maximum depth to traverse (0 = unlimited)
        include_optional: Whether to include optional dependencies
        cache_dir: Directory to cache PyPI responses (optional)

    Returns:
        Dictionary mapping package names to sets of their dependencies
    """
    dependency_graph = {}
    visited = set()
    to_process = [(pkg, 0) for pkg in root_dependencies]

    logger.info(
        f"Building dependency graph from {len(root_dependencies)} root packages"
    )

    while to_process:
        pkg_spec, depth = to_process.pop(0)
        pkg_name = _normalize_package_name(pkg_spec)

        if pkg_name in visited:
            continue
        if max_depth > 0 and depth >= max_depth:
            continue

        visited.add(pkg_name)
        logger.debug(f"Processing {pkg_name} at depth {depth}")

        # Fetch metadata
        metadata = fetch_pypi_metadata(pkg_name)
        if not metadata:
            dependency_graph[pkg_name] = set()
            continue

        # Extract dependencies
        deps = extract_dependencies_from_metadata(metadata)
        dependency_graph[pkg_name] = set(deps)

        # Add to processing queue
        for dep in deps:
            if dep not in visited:
                to_process.append((dep, depth + 1))

        # Be polite to PyPI
        time.sleep(0.1)

    logger.info(
        f"Built dependency graph with {len(dependency_graph)} packages, "
        f"{sum(len(v) for v in dependency_graph.values())} edges"
    )

    return dependency_graph


def categorize_package(package: str) -> str:
    """Categorize a package by domain.

    Args:
        package: Normalized package name

    Returns:
        Category string: 'ml', 'scientific', 'data', 'visualization', 'utilities'
    """
    package_lower = package.lower()

    for category, packages in PACKAGE_CATEGORIES.items():
        if any(pkg in package_lower for pkg in packages):
            return category

    # Heuristic fallback
    if any(
        prefix in package_lower
        for prefix in ["py", "lib", "python-", "types-", "typing-"]
    ):
        return "utilities"

    return "utilities"  # Default category


def create_networkx_graph(
    dependency_graph: dict[str, set[str]], root_package: str = "sleap"
) -> nx.DiGraph:
    """Convert dependency dictionary to NetworkX directed graph.

    Args:
        dependency_graph: Dict mapping packages to their dependencies
        root_package: Name of the root package (for special marking)

    Returns:
        NetworkX DiGraph with package nodes and dependency edges
    """
    G = nx.DiGraph()

    # Add nodes with attributes
    for package in dependency_graph:
        category = categorize_package(package)
        is_root = package.lower() == root_package.lower()
        G.add_node(package, category=category, is_root=is_root)

    # Add edges (dependencies)
    for package, deps in dependency_graph.items():
        for dep in deps:
            if dep in dependency_graph:  # Only add edges to known nodes
                G.add_edge(package, dep)

    logger.info(
        f"Created graph with {G.number_of_nodes()} nodes, "
        f"{G.number_of_edges()} edges"
    )

    return G