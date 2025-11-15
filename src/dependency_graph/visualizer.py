"""Visualize dependency graphs with publication-quality layouts."""

import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)

# Preset configurations
PRESETS = {
    "paper": {
        "figsize": (12, 10),
        "node_label_fontsize": 14,
        "edge_label_fontsize": 12,
        "title_fontsize": 32,
        "annotation_fontsize": 12,
        "dpi": 300,
        "spring_k": 0.15,
        "node_size_min": 100,
        "node_size_max": 2000,
        "edge_width": 0.5,
        "edge_alpha": 0.3,
        "edge_color": "#888888",
    },
    "poster": {
        "figsize": (18, 15),
        "node_label_fontsize": 20,
        "edge_label_fontsize": 18,
        "title_fontsize": 48,
        "annotation_fontsize": 18,
        "dpi": 300,
        "spring_k": 0.22,
        "node_size_min": 150,
        "node_size_max": 3000,
        "edge_width": 1.5,
        "edge_alpha": 0.5,
        "edge_color": "#666666",
    },
}

# Color scheme (colorblind-friendly)
CATEGORY_COLORS = {
    "ml": "#d62728",  # Red
    "scientific": "#1f77b4",  # Blue
    "data": "#2ca02c",  # Green
    "visualization": "#9467bd",  # Purple
    "utilities": "#7f7f7f",  # Gray
}


def calculate_graph_metrics(G: nx.DiGraph) -> dict[str, Any]:
    """Calculate network analysis metrics for the dependency graph.

    Args:
        G: NetworkX directed graph

    Returns:
        Dictionary with graph metrics including degree centrality, statistics
    """
    logger.info("Calculating graph metrics...")

    # Degree centrality (normalized by max possible connections)
    degree_centrality = nx.degree_centrality(G)

    # In-degree (number of packages depending on this package)
    in_degree = dict(G.in_degree())

    # Out-degree (number of dependencies this package has)
    out_degree = dict(G.out_degree())

    # Total degree
    total_degree = {node: in_degree[node] + out_degree[node] for node in G.nodes()}

    # Summary statistics
    degrees = list(total_degree.values())
    metrics = {
        "degree_centrality": degree_centrality,
        "in_degree": in_degree,
        "out_degree": out_degree,
        "total_degree": total_degree,
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "mean_degree": np.mean(degrees) if degrees else 0,
        "max_degree": max(degrees) if degrees else 0,
        "min_degree": min(degrees) if degrees else 0,
    }

    # Find top packages by degree
    top_packages = sorted(total_degree.items(), key=lambda x: x[1], reverse=True)[:10]
    metrics["top_packages"] = top_packages

    logger.info(
        f"Graph metrics: {metrics['num_nodes']} nodes, {metrics['num_edges']} edges, "
        f"mean degree: {metrics['mean_degree']:.2f}"
    )

    return metrics


def create_graph_layout(
    G: nx.DiGraph, layout_type: str = "spring", seed: int = 42, **kwargs
) -> dict:
    """Generate graph layout using specified algorithm.

    Args:
        G: NetworkX directed graph
        layout_type: Layout algorithm ('spring' or 'kamada_kawai')
        seed: Random seed for reproducibility
        **kwargs: Additional parameters for layout algorithm

    Returns:
        Dictionary mapping nodes to (x, y) positions
    """
    logger.info(f"Computing {layout_type} layout...")

    if layout_type == "spring":
        k = kwargs.get("k", 0.15)
        iterations = kwargs.get("iterations", 50)
        pos = nx.spring_layout(G, k=k, iterations=iterations, seed=seed)
    elif layout_type == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:
        raise ValueError(f"Unknown layout type: {layout_type}")

    logger.info(f"Layout computed for {len(pos)} nodes")
    return pos


def generate_metadata_file(
    G: nx.DiGraph,
    output_path: Path,
    metrics: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    """Generate metadata text file documenting the dependency graph.

    Args:
        G: NetworkX directed graph
        output_path: Path where figure was saved
        metrics: Graph metrics from calculate_graph_metrics
        metadata: Additional metadata (source, depth, timestamp, etc.)
    """
    metadata_path = output_path.parent / (output_path.stem + "-metadata.txt")

    with open(metadata_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("SLEAP DEPENDENCY GRAPH METADATA\n")
        f.write("=" * 70 + "\n\n")

        f.write("GENERATION INFO\n")
        f.write("-" * 70 + "\n")
        f.write(f"Generated: {metadata.get('timestamp', 'N/A')}\n")
        f.write(f"SLEAP Source: {metadata.get('source', 'N/A')}\n")
        f.write(f"Preset: {metadata.get('preset', 'N/A')}\n")
        f.write(f"Max Depth: {metadata.get('max_depth', 'unlimited')}\n")
        f.write(f"Include Optional: {metadata.get('include_optional', 'N/A')}\n")
        f.write(f"Output Format: {metadata.get('format', 'N/A')}\n\n")

        f.write("GRAPH STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Packages: {metrics['num_nodes']}\n")
        f.write(f"Total Dependencies (edges): {metrics['num_edges']}\n")
        f.write(f"Mean Degree: {metrics['mean_degree']:.2f}\n")
        f.write(f"Max Degree: {metrics['max_degree']}\n")
        f.write(f"Min Degree: {metrics['min_degree']}\n")
        f.write(f"Dependency Depth: {metadata.get('max_depth', 'N/A')}\n\n")

        f.write("TOP 20 MOST CONNECTED PACKAGES\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'Package':<40} {'Degree':<10}\n")
        f.write("-" * 70 + "\n")
        for pkg, deg in metrics["top_packages"][:20]:
            f.write(f"{pkg:<40} {deg:<10}\n")

        f.write("\n" + "=" * 70 + "\n")

    logger.info(f"Saved metadata to {metadata_path}")


def visualize_dependency_graph(
    G: nx.DiGraph,
    output_path: Path,
    preset: str = "paper",
    layout_type: str = "spring",
    title: str = "SLEAP Dependency Network",
    show_labels: bool = True,
    label_threshold: int = 5,
    format: str = "png",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Create publication-quality visualization of dependency graph.

    Args:
        G: NetworkX directed graph with package nodes
        output_path: Path to save figure
        preset: Preset configuration ('paper' or 'poster')
        layout_type: Graph layout algorithm
        title: Figure title
        show_labels: Whether to show node labels
        label_threshold: Minimum degree to show label
        format: Output format ('png', 'svg', 'pdf')
        metadata: Optional dict with generation metadata for metadata file
    """
    logger.info(f"Visualizing dependency graph with {preset} preset")

    # Get preset configuration
    if preset not in PRESETS:
        raise ValueError(
            f"Unknown preset: {preset}. Choose from {list(PRESETS.keys())}"
        )

    config = PRESETS[preset]

    # Calculate metrics
    metrics = calculate_graph_metrics(G)

    # Create layout
    pos = create_graph_layout(G, layout_type=layout_type, k=config["spring_k"])

    # Create figure
    fig, ax = plt.subplots(figsize=config["figsize"], dpi=config["dpi"])

    # Extract node attributes
    categories = nx.get_node_attributes(G, "category")
    node_colors = [
        CATEGORY_COLORS.get(categories.get(node, "utilities"), "#7f7f7f")
        for node in G.nodes()
    ]

    # Scale node sizes by degree centrality
    degree_cent = metrics["degree_centrality"]
    node_sizes = [
        config["node_size_min"]
        + (config["node_size_max"] - config["node_size_min"]) * degree_cent.get(node, 0)
        for node in G.nodes()
    ]

    # Draw edges with preset configuration
    nx.draw_networkx_edges(
        G,
        pos,
        ax=ax,
        edge_color=config["edge_color"],
        alpha=config["edge_alpha"],
        arrows=True,
        arrowsize=10,
        arrowstyle="->",
        connectionstyle="arc3,rad=0.1",
        width=config["edge_width"],
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        linewidths=1,
        edgecolors="#333333",
    )

    # Draw labels for top-N most connected nodes
    if show_labels:
        total_degree = metrics["total_degree"]
        # Get top packages by degree and filter by threshold
        top_packages = sorted(total_degree.items(), key=lambda x: x[1], reverse=True)
        labels_to_show = {
            node: node
            for node, deg in top_packages
            if deg >= label_threshold
        }

        nx.draw_networkx_labels(
            G,
            pos,
            labels=labels_to_show,
            font_size=config["node_label_fontsize"],
            font_weight="bold",
            font_color="#000000",
            ax=ax,
        )

        logger.info(
            f"Showing labels for {len(labels_to_show)} top connected nodes "
            f"(degree >= {label_threshold})"
        )

    # Add title
    ax.set_title(title, fontsize=config["title_fontsize"], fontweight="bold", pad=20)

    # Add summary statistics text box
    depth_str = metadata.get("max_depth", "N/A") if metadata else "N/A"
    stats_text = (
        f"Total Packages: {metrics['num_nodes']}\n"
        f"Connections: {metrics['num_edges']}\n"
        f"Mean Degree: {metrics['mean_degree']:.1f}\n"
        f"Dependency Depth: {depth_str}\n\n"
        f"Top 5 Most Connected:\n"
    )

    for pkg, deg in metrics["top_packages"][:5]:
        stats_text += f"  {pkg}: {deg}\n"

    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=config["annotation_fontsize"],
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        family="monospace",
    )

    # Add legend for categories
    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=color,
            markersize=10,
            label=cat.title(),
        )
        for cat, color in CATEGORY_COLORS.items()
    ]

    ax.legend(
        handles=legend_elements,
        loc="lower right",
        fontsize=config["annotation_fontsize"],
        framealpha=0.9,
    )

    # Remove axes
    ax.axis("off")
    plt.tight_layout()

    # Save figure
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "png":
        plt.savefig(output_path, format="png", dpi=config["dpi"], bbox_inches="tight")
    elif format == "svg":
        plt.savefig(output_path, format="svg", bbox_inches="tight")
    elif format == "pdf":
        plt.savefig(output_path, format="pdf", bbox_inches="tight")
    else:
        raise ValueError(f"Unsupported format: {format}")

    logger.info(f"Saved visualization to {output_path}")
    plt.close()

    # Generate metadata file if metadata provided
    if metadata:
        generate_metadata_file(G, output_path, metrics, metadata)


def create_degree_distribution_plot(
    G: nx.DiGraph, output_path: Path, preset: str = "paper"
) -> None:
    """Create supplementary plot showing degree distribution (power-law).

    Args:
        G: NetworkX directed graph
        output_path: Path to save figure
        preset: Preset configuration
    """
    config = PRESETS[preset]
    metrics = calculate_graph_metrics(G)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(config["figsize"][0], config["figsize"][1] // 2)
    )

    degrees = list(metrics["total_degree"].values())

    # Linear scale histogram
    ax1.hist(degrees, bins=30, color="#1f77b4", alpha=0.7, edgecolor="black")
    ax1.set_xlabel("Degree", fontsize=config["node_label_fontsize"])
    ax1.set_ylabel("Frequency", fontsize=config["node_label_fontsize"])
    ax1.set_title("Degree Distribution", fontsize=config["title_fontsize"] // 2)
    ax1.grid(alpha=0.3)

    # Log-log scale (power-law)
    degree_counts = {}
    for deg in degrees:
        degree_counts[deg] = degree_counts.get(deg, 0) + 1

    x = sorted(degree_counts.keys())
    y = [degree_counts[deg] for deg in x]

    ax2.loglog(x, y, "o", color="#d62728", markersize=8, alpha=0.7)
    ax2.set_xlabel("Degree (log scale)", fontsize=config["node_label_fontsize"])
    ax2.set_ylabel("Frequency (log scale)", fontsize=config["node_label_fontsize"])
    ax2.set_title("Power-Law Distribution", fontsize=config["title_fontsize"] // 2)
    ax2.grid(alpha=0.3, which="both")

    plt.tight_layout()
    plt.savefig(output_path, dpi=config["dpi"], bbox_inches="tight")
    logger.info(f"Saved degree distribution plot to {output_path}")
    plt.close()