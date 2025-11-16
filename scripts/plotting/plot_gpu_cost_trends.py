"""Generate GPU cost trends visualization.

This script creates publication-quality visualizations of GPU pricing trends
for scientific computing, demonstrating the economic case for cloud-based
GPU access solutions like LabLink.

Usage:
    # Basic usage - paper preset
    python scripts/plotting/plot_gpu_cost_trends.py

    # Poster preset
    python scripts/plotting/plot_gpu_cost_trends.py --preset poster

    # With price-performance subplot
    python scripts/plotting/plot_gpu_cost_trends.py --include-performance

    # Custom data path
    python scripts/plotting/plot_gpu_cost_trends.py \
        --data data/raw/gpu_prices/ml_hardware.csv \
        --output figures/main/gpu_costs.png

Examples:
    # Generate paper figure (default)
    python scripts/plotting/plot_gpu_cost_trends.py

    # Generate poster with both price and performance plots
    python scripts/plotting/plot_gpu_cost_trends.py \
        --preset poster \
        --include-performance \
        --format pdf

    # Presentation format with verbose logging
    python scripts/plotting/plot_gpu_cost_trends.py \
        --preset presentation \
        --verbose
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gpu_costs import (
    calculate_statistics,
    filter_ml_gpus,
    load_gpu_dataset,
    prepare_time_series,
)

logger = logging.getLogger(__name__)

# Format presets matching repository conventions
FORMAT_PRESETS = {
    "paper": {
        "font_size": 14,
        "dpi": 300,
        "figsize": (6.5, 5),
        "line_width": 2.0,
        "marker_size": 6,
    },
    "poster": {
        "font_size": 20,
        "dpi": 300,
        "figsize": (12, 9),
        "line_width": 3.0,
        "marker_size": 10,
    },
    "presentation": {
        "font_size": 16,
        "dpi": 150,
        "figsize": (10, 7.5),
        "line_width": 2.5,
        "marker_size": 8,
    },
}


def setup_logging(verbose: bool = False) -> None:
    """Configure logging output.

    Args:
        verbose: Enable debug-level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def validate_data_quality(dataset: pd.DataFrame) -> None:
    """Validate dataset meets minimum quality standards.

    Args:
        dataset: Filtered GPU dataset

    Raises:
        ValueError: If data quality is insufficient
    """
    logger.info("Validating data quality...")

    # Check minimum GPU count
    if len(dataset) < 50:
        raise ValueError(
            f"Insufficient data: only {len(dataset)} GPUs after filtering. "
            "Expected at least 50 for meaningful visualization."
        )

    # Verify date range coverage
    min_year = dataset["release_date"].dt.year.min()
    max_year = dataset["release_date"].dt.year.max()

    if min_year > 2010:
        logger.warning(
            f"Limited historical coverage: earliest GPU is from {min_year} "
            "(expected 2010 or earlier)"
        )

    if max_year < 2023:
        logger.warning(
            f"Potentially outdated data: latest GPU is from {max_year} "
            "(expected 2023 or later)"
        )

    # Check price data completeness
    priced = dataset[dataset["price"].notna() & (dataset["price"] > 0)]
    completeness = len(priced) / len(dataset)

    logger.info(
        f"Price data completeness: {completeness:.1%} "
        f"({len(priced)}/{len(dataset)})"
    )

    if completeness < 0.7:
        logger.warning(
            f"Low price data completeness: {completeness:.1%}. "
            "Some GPUs will be excluded from visualization."
        )

    logger.info(
        f"Data quality validation passed: {len(dataset)} GPUs, "
        f"{min_year}-{max_year} coverage"
    )


def plot_price_trends(dataset: pd.DataFrame, preset: dict, ax=None) -> plt.Axes:
    """Plot GPU price trends over time.

    Args:
        dataset: Filtered GPU dataset with categories
        preset: Format preset configuration
        ax: Optional matplotlib axes (creates new figure if None)

    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=preset["figsize"], dpi=preset["dpi"])

    # Apply seaborn style
    sns.set_style("whitegrid")

    # Prepare time series for each category
    professional = prepare_time_series(dataset, category="professional")
    consumer = prepare_time_series(dataset, category="consumer")

    # Plot professional GPUs (solid line, dark blue)
    if len(professional) > 0:
        ax.plot(
            professional["release_date"],
            professional["price"],
            marker="o",
            linestyle="-",
            color="#1f77b4",
            linewidth=preset["line_width"],
            markersize=preset["marker_size"],
            label="Professional (Tesla, A100, H100)",
            alpha=0.8,
        )

    # Plot consumer GPUs (dashed line, light blue)
    if len(consumer) > 0:
        ax.plot(
            consumer["release_date"],
            consumer["price"],
            marker="s",
            linestyle="--",
            color="#89CFF0",
            linewidth=preset["line_width"],
            markersize=preset["marker_size"],
            label="Consumer (RTX/GTX ≥5 TFLOPS)",
            alpha=0.8,
        )

    # Configure axes
    ax.set_xlabel("Year", fontsize=preset["font_size"])
    ax.set_ylabel("Launch Price (USD)", fontsize=preset["font_size"])
    ax.set_title(
        "GPU Cost Trends for Scientific Computing",
        fontsize=preset["font_size"] * 1.2,
        fontweight="bold",
        pad=15,
    )

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    # Add legend
    ax.legend(fontsize=preset["font_size"] * 0.9, loc="upper left", framealpha=0.9)

    # Configure tick sizes
    ax.tick_params(labelsize=preset["font_size"] * 0.9)

    # Add grid
    ax.grid(True, alpha=0.3)

    return ax


def add_gpu_annotations(ax: plt.Axes, dataset: pd.DataFrame, preset: dict) -> None:
    """Add annotations for key GPU models.

    Args:
        ax: Matplotlib axes object
        dataset: GPU dataset
        preset: Format preset configuration
    """
    # Key models to annotate
    key_models = {
        "V100": 2017,
        "2080 Ti": 2018,
        "A100": 2020,
        "H100": 2022,
    }

    for model_name, year in key_models.items():
        # Find matching GPU (case-insensitive substring match)
        matches = dataset[
            dataset["name"].str.contains(model_name, case=False, na=False)
            & (dataset["release_date"].dt.year == year)
            & dataset["price"].notna()
        ]

        if len(matches) > 0:
            gpu = matches.iloc[0]
            # Annotate with arrow pointing to the data point
            ax.annotate(
                model_name,
                xy=(gpu["release_date"], gpu["price"]),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=preset["font_size"] * 0.8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )


def calculate_price_performance(dataset: pd.DataFrame) -> pd.DataFrame:
    """Calculate FLOP/s per dollar metric.

    Args:
        dataset: GPU dataset

    Returns:
        Dataset with price_performance column added
    """
    df = dataset.copy()

    # Filter to rows with both price and performance data
    valid = (df["price"].notna()) & (df["price"] > 0) & (df["fp32_tflops"].notna())
    df = df[valid].copy()

    # Calculate GFLOP/s per USD
    df["price_performance"] = (
        df["fp32_tflops"] * 1000 / df["price"]
    )  # Convert to GFLOP/s

    return df


def plot_price_performance(dataset: pd.DataFrame, preset: dict, ax=None) -> plt.Axes:
    """Plot price-performance evolution over time.

    Args:
        dataset: Filtered GPU dataset
        preset: Format preset configuration
        ax: Optional matplotlib axes

    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=preset["figsize"], dpi=preset["dpi"])

    # Calculate price-performance
    df = calculate_price_performance(dataset)

    if len(df) == 0:
        logger.warning("No GPUs with both price and performance data")
        return ax

    # Plot by category
    professional = df[df["category"] == "professional"]
    consumer = df[df["category"] == "consumer"]

    if len(professional) > 0:
        ax.scatter(
            professional["release_date"],
            professional["price_performance"],
            marker="o",
            s=preset["marker_size"] ** 2,
            color="#1f77b4",
            label="Professional",
            alpha=0.7,
        )

    if len(consumer) > 0:
        ax.scatter(
            consumer["release_date"],
            consumer["price_performance"],
            marker="s",
            s=preset["marker_size"] ** 2,
            color="#89CFF0",
            label="Consumer",
            alpha=0.7,
        )

    # Fit exponential trend line
    if len(df) > 5:
        # Convert dates to numeric (years since first GPU)
        min_date = df["release_date"].min()
        df["years_since_start"] = (
            df["release_date"] - min_date
        ).dt.days / 365.25

        # Log-transform for exponential fit
        log_perf = np.log(df["price_performance"])
        slope, intercept, r_value, _, _ = stats.linregress(
            df["years_since_start"], log_perf
        )

        # Calculate doubling time
        doubling_time = np.log(2) / slope

        # Plot trend line
        years_range = np.linspace(0, df["years_since_start"].max(), 100)
        dates_range = min_date + pd.to_timedelta(years_range * 365.25, unit="D")
        trend = np.exp(intercept + slope * years_range)

        ax.plot(
            dates_range,
            trend,
            "--",
            color="red",
            linewidth=preset["line_width"],
            alpha=0.6,
            label=f"Trend (doubles ~{doubling_time:.1f} years)",
        )

    # Configure axes
    ax.set_xlabel("Year", fontsize=preset["font_size"])
    ax.set_ylabel("GFLOP/s per USD", fontsize=preset["font_size"])
    ax.set_title(
        "GPU Price-Performance Evolution",
        fontsize=preset["font_size"] * 1.2,
        fontweight="bold",
        pad=15,
    )

    # Log scale for y-axis
    ax.set_yscale("log")

    # Add legend
    ax.legend(fontsize=preset["font_size"] * 0.9, loc="upper left", framealpha=0.9)

    # Configure tick sizes
    ax.tick_params(labelsize=preset["font_size"] * 0.9)

    # Add grid
    ax.grid(True, alpha=0.3, which="both")

    return ax


def generate_metadata_file(
    output_path: Path, dataset: pd.DataFrame, statistics: dict, preset: str, format: str
) -> None:
    """Generate metadata documentation file.

    Args:
        output_path: Path where figure was saved
        dataset: Filtered GPU dataset
        statistics: Statistics from calculate_statistics
        preset: Preset name used
        format: Output format used
    """
    metadata_path = output_path.parent / (output_path.stem + "-metadata.txt")

    with open(metadata_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("GPU COST TRENDS METADATA\n")
        f.write("=" * 70 + "\n\n")

        # Data source
        f.write("DATA SOURCE\n")
        f.write("-" * 70 + "\n")
        f.write("Dataset: Epoch AI Machine Learning Hardware Database\n")
        f.write("URL: https://epoch.ai/data/machine-learning-hardware\n")
        f.write("License: CC BY 4.0 (Creative Commons Attribution)\n")
        f.write("Citation: Epoch AI (2024), 'Data on Machine Learning Hardware',\n")
        f.write("          Available at: https://epoch.ai/data/machine-learning-hardware\n\n")

        # Generation info
        f.write("GENERATION INFO\n")
        f.write("-" * 70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Preset: {preset}\n")
        f.write(f"Output Format: {format}\n\n")

        # Dataset statistics
        f.write("DATASET STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total GPUs Analyzed: {statistics['total_gpus']}\n")

        min_date = statistics["date_range"]["min"]
        max_date = statistics["date_range"]["max"]
        f.write(
            f"Date Range: {min_date.year}-{min_date.month:02d} to "
            f"{max_date.year}-{max_date.month:02d}\n"
        )

        prof_count = statistics.get("price_professional", {}).get("count", 0)
        cons_count = statistics.get("price_consumer", {}).get("count", 0)
        f.write(f"Professional GPUs: {prof_count}\n")
        f.write(f"Consumer GPUs: {cons_count}\n\n")

        # Price statistics
        f.write("PRICE STATISTICS\n")
        f.write("-" * 70 + "\n")

        if "price_overall" in statistics:
            overall = statistics["price_overall"]
            f.write(
                f"Overall Price Range: ${overall['min']:,.0f} - "
                f"${overall['max']:,.0f}\n"
            )
            f.write(f"Overall Median: ${overall['median']:,.0f}\n\n")

        if "price_professional" in statistics:
            prof = statistics["price_professional"]
            if prof["count"] > 0:
                f.write(
                    f"Professional - Range: ${prof['min']:,.0f} - ${prof['max']:,.0f}\n"
                )
                f.write(f"Professional - Median: ${prof['median']:,.0f}\n")
                f.write(f"Professional - Count: {prof['count']}\n\n")

        if "price_consumer" in statistics:
            cons = statistics["price_consumer"]
            if cons["count"] > 0:
                f.write(
                    f"Consumer - Range: ${cons['min']:,.0f} - ${cons['max']:,.0f}\n"
                )
                f.write(f"Consumer - Median: ${cons['median']:,.0f}\n")
                f.write(f"Consumer - Count: {cons['count']}\n\n")

        # Data quality
        f.write("DATA QUALITY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Price Data Completeness: {statistics['price_completeness']:.1%}\n")
        f.write(
            f"Performance Data Completeness: "
            f"{statistics['performance_completeness']:.1%}\n"
        )

        f.write("\n" + "=" * 70 + "\n")

    logger.info(f"Saved metadata to {metadata_path}")


def save_figure(fig: plt.Figure, output_path: Path, format: str, dpi: int) -> None:
    """Save figure to file(s).

    Args:
        fig: Matplotlib figure
        output_path: Output file path
        format: Format ("png", "pdf", or "both")
        dpi: DPI for raster formats
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "both":
        # Save PNG
        png_path = output_path.with_suffix(".png")
        fig.savefig(png_path, format="png", dpi=dpi, bbox_inches="tight")
        logger.info(f"Saved PNG: {png_path} ({png_path.stat().st_size / 1024:.1f} KB)")

        # Save PDF
        pdf_path = output_path.with_suffix(".pdf")
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
        logger.info(f"Saved PDF: {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")

    elif format == "png":
        output_path = output_path.with_suffix(".png")
        fig.savefig(output_path, format="png", dpi=dpi, bbox_inches="tight")
        logger.info(
            f"Saved PNG: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)"
        )

    elif format == "pdf":
        output_path = output_path.with_suffix(".pdf")
        fig.savefig(output_path, format="pdf", bbox_inches="tight")
        logger.info(
            f"Saved PDF: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)"
        )

    else:
        raise ValueError(f"Unsupported format: {format}")

    plt.close(fig)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate GPU cost trends visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--preset",
        choices=["paper", "poster", "presentation"],
        default="paper",
        help="Format preset (default: paper)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figures/main/gpu_cost_trends.png"),
        help="Output file path (default: figures/main/gpu_cost_trends.png)",
    )

    parser.add_argument(
        "--format",
        choices=["png", "pdf", "both"],
        default="both",
        help="Output format (default: both)",
    )

    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/raw/gpu_prices/ml_hardware.csv"),
        help="Path to Epoch AI dataset (default: data/raw/gpu_prices/ml_hardware.csv)",
    )

    parser.add_argument(
        "--include-performance",
        action="store_true",
        help="Include price-performance subplot",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    args = parse_args()
    setup_logging(args.verbose)

    logger.info("Starting GPU cost trends visualization")

    try:
        # Load dataset
        logger.info(f"Loading dataset from {args.data}")
        dataset = load_gpu_dataset(args.data)
        logger.info(f"Loaded {len(dataset)} GPUs from raw dataset")

        # Filter to ML-relevant GPUs
        filtered = filter_ml_gpus(dataset)
        logger.info(
            f"Filtered to {len(filtered)} ML-relevant GPUs "
            f"({len(filtered[filtered['category']=='professional'])} professional, "
            f"{len(filtered[filtered['category']=='consumer'])} consumer)"
        )

        # Validate data quality
        validate_data_quality(filtered)

        # Calculate statistics
        statistics = calculate_statistics(filtered)

        # Get preset configuration
        preset = FORMAT_PRESETS[args.preset]
        logger.info(
            f"Using {args.preset} preset: {preset['figsize']} @ "
            f"{preset['dpi']} DPI"
        )

        # Generate figure(s)
        if args.include_performance:
            # Create 1x2 subplot grid
            fig, (ax1, ax2) = plt.subplots(
                1,
                2,
                figsize=(preset["figsize"][0] * 2, preset["figsize"][1]),
                dpi=preset["dpi"],
            )

            # Plot price trends
            plot_price_trends(filtered, preset, ax=ax1)
            add_gpu_annotations(ax1, filtered, preset)

            # Plot price-performance
            plot_price_performance(filtered, preset, ax=ax2)

            plt.tight_layout()

        else:
            # Single price trends figure
            fig, ax = plt.subplots(figsize=preset["figsize"], dpi=preset["dpi"])
            plot_price_trends(filtered, preset, ax=ax)
            add_gpu_annotations(ax, filtered, preset)
            plt.tight_layout()

        # Save figure
        save_figure(fig, args.output, args.format, preset["dpi"])

        # Generate metadata
        generate_metadata_file(
            args.output,
            filtered,
            statistics,
            args.preset,
            args.format,
        )

        logger.info("Successfully generated GPU cost trends visualization")
        logger.info(f"Output: {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate visualization: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())