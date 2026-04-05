#!/usr/bin/env python3
"""Generate a bar-graph figure showing LabLink maintainability metrics.

Metrics computed per LabLink package (allocator, cli, client) using ``radon``:
  - Cyclomatic Complexity (CC): average CC per function definition in each file,
    aggregated across the package.
  - Lines of Code (LOC): physical lines of code (sum across all source files).
  - Maintainability Index (MI): average MI across source files (0-100 scale).

Reference thresholds for MI (Visual Studio / radon convention):
    MI < 65   : difficult to maintain
    65 <= MI < 85 : maintainable
    MI >= 85  : good maintainability
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


SKIP_DIRS = {".venv", "__pycache__", "build", "dist", ".git", "tests", "test"}


def collect_py_files(root: Path) -> List[Path]:
    """Recursively collect .py files under *root*, skipping venvs and tests."""
    files: List[Path] = []
    for dirpath, dirnames, filenames in __import__("os").walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith(".py"):
                files.append(Path(dirpath) / f)
    return files


def compute_metrics(pkg_root: Path) -> Dict[str, float]:
    """Compute CC (avg per function), LOC (sum), and MI (avg) for a package."""
    py_files = collect_py_files(pkg_root)
    total_loc = 0
    cc_values: List[float] = []
    mi_values: List[float] = []

    for fp in py_files:
        try:
            src = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Could not read {fp}: {e}")
            continue

        try:
            total_loc += analyze(src).loc
        except Exception:
            pass

        try:
            for block in cc_visit(src):
                cc_values.append(block.complexity)
        except Exception:
            pass

        try:
            mi_values.append(mi_visit(src, True))
        except Exception:
            pass

    return {
        "files": len(py_files),
        "loc": total_loc,
        "avg_cc": float(np.mean(cc_values)) if cc_values else 0.0,
        "avg_mi": float(np.mean(mi_values)) if mi_values else 0.0,
        "num_functions": len(cc_values),
    }


def plot_maintainability(
    metrics: Dict[str, Dict[str, float]],
    output_path: Path,
    dpi: int = 300,
) -> None:
    """Create a three-panel bar chart of CC, LOC, MI for each package."""
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.2)

    packages = list(metrics.keys())
    display_names = [p.capitalize() for p in packages]
    colors = sns.color_palette("colorblind", n_colors=len(packages))

    cc_vals = [metrics[p]["avg_cc"] for p in packages]
    loc_vals = [metrics[p]["loc"] for p in packages]
    mi_vals = [metrics[p]["avg_mi"] for p in packages]

    fig, axes = plt.subplots(1, 3, figsize=(14, 7))

    # --- Cyclomatic Complexity ---
    ax = axes[0]
    bars = ax.bar(display_names, cc_vals, color=colors, edgecolor="black", linewidth=0.8)
    ax.set_title("Cyclomatic Complexity", fontweight="bold", pad=10)
    ax.set_ylabel("Average CC per function")
    # Include McCabe threshold (10) in the visible range so the reference line fits.
    cc_ymax = max(max(cc_vals) * 1.25, 12.0)
    ax.set_ylim(0, cc_ymax)
    for b, v in zip(bars, cc_vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}",
                ha="center", va="bottom", fontsize=10)
    # Reference line: CC > 10 is considered complex per McCabe
    ax.axhline(10, color="red", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(len(packages) - 0.5, 10.2, "McCabe threshold (10)",
            color="red", fontsize=8, ha="right", va="bottom")

    # --- Lines of Code ---
    ax = axes[1]
    bars = ax.bar(display_names, loc_vals, color=colors, edgecolor="black", linewidth=0.8)
    ax.set_title("Lines of Code", fontweight="bold", pad=10)
    ax.set_ylabel("Physical LOC")
    ax.set_ylim(0, max(loc_vals) * 1.2)
    for b, v in zip(bars, loc_vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{int(v):,}",
                ha="center", va="bottom", fontsize=10)

    # --- Maintainability Index ---
    ax = axes[2]
    bars = ax.bar(display_names, mi_vals, color=colors, edgecolor="black", linewidth=0.8)
    ax.set_title("Maintainability Index", fontweight="bold", pad=10)
    ax.set_ylabel("MI (0-100)")
    ax.set_ylim(0, 100)
    for b, v in zip(bars, mi_vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}",
                ha="center", va="bottom", fontsize=10)

    # Shaded MI zones
    ax.axhspan(0, 65, facecolor="#f8d7da", alpha=0.35, zorder=0)
    ax.axhspan(65, 85, facecolor="#fff3cd", alpha=0.35, zorder=0)
    ax.axhspan(85, 100, facecolor="#d4edda", alpha=0.35, zorder=0)
    xmax = len(packages) - 0.5
    ax.text(xmax, 32.5, "Difficult (<65)", ha="right", va="center",
            fontsize=8, color="#842029")
    ax.text(xmax, 75, "Maintainable (65-85)", ha="right", va="center",
            fontsize=8, color="#664d03")
    ax.text(xmax, 92.5, "Good (>85)", ha="right", va="center",
            fontsize=8, color="#0f5132")

    fig.suptitle("LabLink Maintainability Metrics by Package",
                 fontsize=15, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.95))

    for ext in ("png", "pdf"):
        out = Path(str(output_path) + f".{ext}")
        plt.savefig(out, dpi=dpi, bbox_inches="tight", format=ext)
        logger.info(f"Saved: {out}")
    plt.close()


def write_metadata(metrics: Dict[str, Dict[str, float]],
                   source_root: Path,
                   output_dir: Path) -> None:
    meta_file = output_dir / "lablink_maintainability_metadata.txt"
    with open(meta_file, "w") as f:
        f.write("LabLink Maintainability Figure Metadata\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"generation_timestamp: {datetime.now().isoformat()}\n")
        f.write(f"source_root: {source_root}\n")
        f.write("tool: radon 6.x (cc_visit, mi_visit, raw.analyze)\n")
        f.write("excluded_dirs: " + ", ".join(sorted(SKIP_DIRS)) + "\n\n")
        f.write("Per-package metrics:\n")
        f.write(json.dumps(metrics, indent=2) + "\n")
    logger.info(f"Saved metadata: {meta_file}")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--source-root",
        type=Path,
        default=Path("/Users/andrewpark/talmolab/lablink/packages"),
        help="Root directory containing LabLink packages (allocator/cli/client).",
    )
    p.add_argument(
        "--packages",
        nargs="+",
        default=["allocator", "cli", "client"],
        help="Package subdirectories to analyze.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "figures" / "main",
    )
    return p.parse_args()


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metrics: Dict[str, Dict[str, float]] = {}
    for pkg in args.packages:
        root = args.source_root / pkg
        if not root.exists():
            logger.warning(f"Skipping missing package: {root}")
            continue
        logger.info(f"Analyzing {pkg} at {root}")
        metrics[pkg] = compute_metrics(root)
        logger.info(f"  {metrics[pkg]}")

    if not metrics:
        raise SystemExit("No packages analyzed; nothing to plot.")

    out_base = args.output_dir / "lablink_maintainability"
    plot_maintainability(metrics, out_base)
    write_metadata(metrics, args.source_root, args.output_dir)
    logger.info("Done.")


if __name__ == "__main__":
    main()
