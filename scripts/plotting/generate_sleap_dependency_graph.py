"""Generate SLEAP dependency network visualization.

This script extracts SLEAP's full transitive dependency tree and creates
publication-quality network graphs showing the complexity of the software
ecosystem. Supports configurable presets for paper and poster outputs.

Usage:
    # Use local SLEAP installation
    python scripts/plotting/generate_sleap_dependency_graph.py \\
        --sleap-source C:/repos/sleap \\
        --preset paper \\
        --output-dir figures/main

    # Use GitHub URL
    python scripts/plotting/generate_sleap_dependency_graph.py \\
        --sleap-source https://github.com/talmolab/sleap/blob/develop/pyproject.toml \\
        --preset poster \\
        --format svg

    # Use environment variable
    set SLEAP_PATH=C:/repos/sleap
    python scripts/plotting/generate_sleap_dependency_graph.py
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.dependency_graph import (
    build_dependency_graph,
    create_networkx_graph,
    fetch_remote_pyproject,
    parse_pyproject_toml,
    visualize_dependency_graph,
)
from src.dependency_graph.visualizer import create_degree_distribution_plot

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging output."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate SLEAP dependency network visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--sleap-source",
        type=str,
        default=None,
        help="Path to SLEAP directory or GitHub URL to pyproject.toml "
        "(default: SLEAP_PATH env var or C:/repos/sleap)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("figures/main"),
        help="Output directory for generated figures (default: figures/main)",
    )

    parser.add_argument(
        "--preset",
        choices=["paper", "poster"],
        default="paper",
        help="Font and spacing preset (default: paper)",
    )

    parser.add_argument(
        "--format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output format (default: png)",
    )

    parser.add_argument(
        "--dpi", type=int, default=300, help="DPI for raster formats (default: 300)"
    )

    parser.add_argument(
        "--layout",
        choices=["spring", "kamada_kawai"],
        default="spring",
        help="Graph layout algorithm (default: spring)",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=0,
        help="Maximum dependency tree depth (0 = unlimited, default: 0)",
    )

    parser.add_argument(
        "--exclude-optional",
        action="store_true",
        help="Exclude optional dependencies",
    )

    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh dependency data (ignore cache)",
    )

    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory for caching dependency data (default: data/processed)",
    )

    parser.add_argument(
        "--show-distribution",
        action="store_true",
        help="Also generate degree distribution plot",
    )

    parser.add_argument(
        "--label-threshold",
        type=int,
        default=5,
        help="Minimum degree to show node label (default: 5)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def get_sleap_source(args: argparse.Namespace) -> str | Path:
    """Determine SLEAP source from arguments, environment, or default."""
    if args.sleap_source:
        return args.sleap_source

    if "SLEAP_PATH" in os.environ:
        return Path(os.environ["SLEAP_PATH"])

    # Default path
    return Path("C:/repos/sleap")


def load_or_build_dependency_graph(
    sleap_source: str | Path,
    cache_path: Path,
    force_refresh: bool,
    max_depth: int,
    include_optional: bool,
) -> dict:
    """Load cached dependency graph or build new one."""
    # Check cache
    if cache_path.exists() and not force_refresh:
        logger.info(f"Loading cached dependency data from {cache_path}")
        with open(cache_path, "r") as f:
            cache_data = json.load(f)

        # Convert sets back from lists
        graph = {k: set(v) for k, v in cache_data["graph"].items()}
        logger.info(
            f"Loaded cache from {cache_data['timestamp']} "
            f"({len(graph)} packages)"
        )
        return graph

    # Parse dependencies
    logger.info(f"Extracting dependencies from {sleap_source}")

    if isinstance(sleap_source, str) and sleap_source.startswith("http"):
        dep_data = fetch_remote_pyproject(sleap_source)
    else:
        dep_data = parse_pyproject_toml(Path(sleap_source))

    # Combine dependencies
    all_deps = dep_data["dependencies"][:]
    if include_optional:
        for opt_deps in dep_data["optional-dependencies"].values():
            all_deps.extend(opt_deps)

    # Always include sleap-nn from the nn-cuda128 optional dependency group
    # This is a critical runtime dependency for SLEAP's deep learning functionality
    if not any("sleap-nn" in dep for dep in all_deps):
        # Add the nn-cuda128 variant: sleap-nn[torch]>=0.0.2
        nn_cuda128_deps = dep_data["optional-dependencies"].get("nn-cuda128", [])
        if nn_cuda128_deps and not include_optional:
            # Only add if we're excluding optional deps (otherwise already included)
            all_deps.extend(nn_cuda128_deps)
            logger.info(f"Added nn-cuda128 dependencies: {nn_cuda128_deps}")

    logger.info(f"Found {len(all_deps)} total dependencies to analyze")

    # Build transitive graph
    graph = build_dependency_graph(
        all_deps, max_depth=max_depth, include_optional=include_optional
    )

    # Cache results
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_data = {
        "graph": {k: list(v) for k, v in graph.items()},  # Convert sets to lists
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "source": str(sleap_source),
        "max_depth": max_depth,
        "include_optional": include_optional,
    }

    with open(cache_path, "w") as f:
        json.dump(cache_data, f, indent=2)

    logger.info(f"Cached dependency data to {cache_path}")

    return graph


def main() -> int:
    """Main execution function."""
    args = parse_args()
    setup_logging(args.verbose)

    logger.info("Starting SLEAP dependency graph generation")

    # Determine SLEAP source
    sleap_source = get_sleap_source(args)
    logger.info(f"Using SLEAP source: {sleap_source}")

    # Validate source
    if isinstance(sleap_source, Path):
        if sleap_source.is_dir():
            pyproject_path = sleap_source / "pyproject.toml"
        else:
            pyproject_path = sleap_source

        if not pyproject_path.exists():
            logger.error(f"pyproject.toml not found at {pyproject_path}")
            logger.error("Please verify SLEAP source path or use --sleap-source")
            return 1

    # Cache path
    cache_path = args.cache_dir / "sleap_dependencies.json"

    try:
        # Load or build dependency graph
        dependency_graph = load_or_build_dependency_graph(
            sleap_source,
            cache_path,
            args.force_refresh,
            args.max_depth,
            not args.exclude_optional,
        )

        # Create NetworkX graph
        G = create_networkx_graph(dependency_graph, root_package="sleap")

        # Generate visualization
        output_filename = f"sleap-dependency-graph.{args.format}"
        output_path = args.output_dir / output_filename

        logger.info(f"Generating {args.preset} visualization...")

        # Prepare metadata for documentation
        import datetime
        metadata = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": str(sleap_source),
            "preset": args.preset,
            "max_depth": args.max_depth if args.max_depth > 0 else "unlimited",
            "include_optional": not args.exclude_optional,
            "format": args.format,
        }

        visualize_dependency_graph(
            G,
            output_path,
            preset=args.preset,
            layout_type=args.layout,
            title="SLEAP Dependency Network",
            show_labels=True,
            label_threshold=args.label_threshold,
            format=args.format,
            metadata=metadata,
        )

        logger.info(f"Successfully generated {output_path}")

        # Optional: degree distribution plot
        if args.show_distribution:
            dist_filename = f"sleap-dependency-distribution.{args.format}"
            dist_path = args.output_dir / dist_filename

            logger.info("Generating degree distribution plot...")
            create_degree_distribution_plot(G, dist_path, preset=args.preset)
            logger.info(f"Successfully generated {dist_path}")

        logger.info("Done!")
        return 0

    except Exception as e:
        logger.error(f"Failed to generate dependency graph: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
