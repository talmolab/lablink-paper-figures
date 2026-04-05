"""Generate LabLink full infrastructure cost analysis figures for a tutorial session.

Produces three figures for a fixed-duration LabLink deployment:
  1. Cost breakdown table
  2. Vertical stacked bar chart
  3. Horizontal stacked bar chart

Supports format presets (paper, poster, presentation) so figures can be
resized for their intended use.

Usage:
    # Paper preset (default)
    python scripts/plotting/gpu_cost_analysis.py

    # Poster preset
    python scripts/plotting/gpu_cost_analysis.py --preset poster

    # Presentation preset, custom session parameters
    python scripts/plotting/gpu_cost_analysis.py \
        --preset presentation --vms 25 --hours 4
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# Format presets matching repository conventions
FORMAT_PRESETS: Dict[str, Dict] = {
    "paper": {
        "font_size": 12,
        "dpi": 300,
        "table_figsize": (10, 4.5),
        "stacked_figsize": (10, 7),
        "hbar_figsize": (12, 4.5),
        "description": "Scientific paper (single column)",
    },
    "poster": {
        "font_size": 18,
        "dpi": 300,
        "table_figsize": (14, 6.5),
        "stacked_figsize": (14, 10),
        "hbar_figsize": (16, 6),
        "description": "Conference poster (readable at distance)",
    },
    "presentation": {
        "font_size": 15,
        "dpi": 150,
        "table_figsize": (12, 5.5),
        "stacked_figsize": (12, 8.5),
        "hbar_figsize": (14, 5.5),
        "description": "Slide presentation (16:9 friendly)",
    },
}


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def compute_resources(vms: int, hours: int) -> List[Tuple[str, float, str]]:
    """Return (name, cost, color) rows for a LabLink session.

    Sources:
      EC2 pricing:  https://aws.amazon.com/ec2/pricing/on-demand/
      EBS pricing:  https://aws.amazon.com/ebs/pricing/
      ALB pricing:  https://aws.amazon.com/elasticloadbalancing/pricing/
      Public IPv4:  https://aws.amazon.com/vpc/pricing/ ($0.005/hr per addr)
      CloudWatch:   https://aws.amazon.com/cloudwatch/pricing/
      S3 pricing:   https://aws.amazon.com/s3/pricing/
      Route 53:     https://aws.amazon.com/route53/pricing/
    """
    return [
        (f"Client VMs ({vms}× g4dn.xlarge)", 0.526 * vms * hours, "#2563eb"),
        (f"Client EBS ({vms}× 80 GB gp3)", vms * 80 * 0.08 / 730 * hours, "#60a5fa"),
        ("Allocator VM (1× t3.large)", 0.0832 * hours, "#7c3aed"),
        (f"Public IPv4 ({vms + 1} addresses)", (vms + 1) * 0.005 * hours, "#059669"),
        ("ALB (SSL termination)", 0.0225 * hours + 2 * 0.008 * hours, "#f59e0b"),
        ("Monitoring (CW/CloudTrail/SNS)", 0.05, "#ef4444"),
        ("State & DNS (S3/DynamoDB/R53)", 0.02, "#6b7280"),
    ]


def plot_table(
    names: List[str],
    costs: List[float],
    total: float,
    vms: int,
    hours: int,
    preset: Dict,
    output_path: Path,
    fmt: str,
) -> None:
    fig, ax = plt.subplots(figsize=preset["table_figsize"])
    ax.axis("off")

    col_labels = ["Resource", "Cost"]
    rows = [[n, f"${c:.2f}"] for n, c in zip(names, costs)]
    rows.append(["TOTAL", f"${total:.2f}"])

    table = ax.table(cellText=rows, colLabels=col_labels, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(preset["font_size"] - 1)
    table.scale(1.0, 1.8)

    for j, w in enumerate([0.55, 0.20]):
        for i in range(len(rows) + 1):
            table[i, j].set_width(w)

    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#1e3a5f")
        table[0, j].set_text_props(color="white", fontweight="bold")

    for i in range(1, len(rows) + 1):
        for j in range(len(col_labels)):
            cell = table[i, j]
            if i == len(rows):
                cell.set_facecolor("#e0e7ff")
                cell.set_text_props(fontweight="bold")
            elif i % 2 == 0:
                cell.set_facecolor("#f0f4ff")
            else:
                cell.set_facecolor("white")
            if j == 1:
                cell._loc = "right"

    fig.suptitle(
        f"LabLink Infrastructure Cost  —  {vms} Client VMs × {hours} Hours  (us-west-2)",
        fontsize=preset["font_size"] + 1,
        fontweight="bold",
        y=0.96,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = output_path.with_suffix(f".{fmt}")
    fig.savefig(out, dpi=preset["dpi"], bbox_inches="tight", facecolor="white", format=fmt)
    plt.close(fig)
    logger.info(f"Saved: {out}")


def plot_stacked(
    names: List[str],
    costs: List[float],
    colors: List[str],
    total: float,
    vms: int,
    hours: int,
    preset: Dict,
    output_path: Path,
    fmt: str,
) -> None:
    fig, ax = plt.subplots(figsize=preset["stacked_figsize"])

    bar_bottom = 0.0
    for name, cost, color in zip(names, costs, colors):
        ax.bar(
            "4-Hour Session",
            cost,
            bottom=bar_bottom,
            color=color,
            label=f"{name}  (${cost:.2f})",
            width=0.45,
            edgecolor="white",
            linewidth=0.8,
        )
        if cost > total * 0.015:
            ax.text(
                0,
                bar_bottom + cost / 2,
                f"${cost:.2f}",
                ha="center",
                va="center",
                fontsize=preset["font_size"] - 2,
                fontweight="bold",
                color="white",
            )
        bar_bottom += cost

    ax.set_ylabel("Cost (USD)", fontsize=preset["font_size"] + 1)
    ax.set_ylim(0, total * 1.10)
    ax.set_xlim(-0.8, 0.8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    ax.text(
        0,
        total + 0.4,
        f"Total: ${total:.2f}",
        ha="center",
        va="bottom",
        fontsize=preset["font_size"] + 2,
        fontweight="bold",
    )
    ax.legend(
        loc="center left",
        bbox_to_anchor=(0.62, 0.5),
        fontsize=preset["font_size"] - 2,
        frameon=True,
        fancybox=True,
    )
    ax.set_title(
        f"LabLink Infrastructure Cost  —  {vms} VMs × {hours} Hours  (us-west-2)",
        fontsize=preset["font_size"] + 1,
        fontweight="bold",
        pad=16,
    )
    fig.tight_layout()
    out = output_path.with_suffix(f".{fmt}")
    fig.savefig(out, dpi=preset["dpi"], bbox_inches="tight", facecolor="white", format=fmt)
    plt.close(fig)
    logger.info(f"Saved: {out}")


def plot_hbar(
    names: List[str],
    costs: List[float],
    colors: List[str],
    total: float,
    vms: int,
    hours: int,
    preset: Dict,
    output_path: Path,
    fmt: str,
) -> None:
    fig, ax = plt.subplots(figsize=preset["hbar_figsize"])

    left = 0.0
    for name, cost, color in zip(names, costs, colors):
        ax.barh(
            "Session Cost",
            cost,
            left=left,
            color=color,
            label=f"{name}  (${cost:.2f})",
            height=0.5,
            edgecolor="white",
            linewidth=0.8,
        )
        if cost > total * 0.03:
            ax.text(
                left + cost / 2,
                0,
                f"${cost:.2f}",
                ha="center",
                va="center",
                fontsize=preset["font_size"] - 3,
                fontweight="bold",
                color="white",
            )
        left += cost

    ax.set_xlabel("Cost (USD)", fontsize=preset["font_size"] + 1)
    ax.set_xlim(0, total * 1.15)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)

    ax.text(
        total + 0.3,
        0,
        f"Total: ${total:.2f}",
        ha="left",
        va="center",
        fontsize=preset["font_size"] + 1,
        fontweight="bold",
    )
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=3,
        fontsize=preset["font_size"] - 3,
        frameon=True,
        fancybox=True,
    )
    ax.set_title(
        f"LabLink Infrastructure Cost Breakdown  —  {vms} VMs × {hours} Hours  (us-west-2)",
        fontsize=preset["font_size"] + 1,
        fontweight="bold",
        pad=14,
    )
    fig.tight_layout()
    out = output_path.with_suffix(f".{fmt}")
    fig.savefig(out, dpi=preset["dpi"], bbox_inches="tight", facecolor="white", format=fmt)
    plt.close(fig)
    logger.info(f"Saved: {out}")


def write_metadata(
    names: List[str],
    costs: List[float],
    total: float,
    vms: int,
    hours: int,
    preset_name: str,
    preset: Dict,
    fmt: str,
    output_dir: Path,
) -> None:
    """Write a metadata .txt file next to the generated figures."""
    meta_file = output_dir / "lablink_cost_analysis_metadata.txt"
    with open(meta_file, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("LABLINK INFRASTRUCTURE COST ANALYSIS METADATA\n")
        f.write("=" * 70 + "\n\n")

        f.write("GENERATION INFO\n")
        f.write("-" * 70 + "\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Preset: {preset_name} ({preset['description']})\n")
        f.write(f"Figure size (table): {preset['table_figsize']}\n")
        f.write(f"Figure size (stacked): {preset['stacked_figsize']}\n")
        f.write(f"Figure size (hbar): {preset['hbar_figsize']}\n")
        f.write(f"DPI: {preset['dpi']}\n")
        f.write(f"Output format: {fmt}\n\n")

        f.write("SESSION PARAMETERS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Client VMs: {vms}\n")
        f.write(f"Session duration: {hours} hours\n")
        f.write("Region: us-west-2\n")
        f.write("Pricing model: AWS on-demand\n\n")

        f.write("DATA SOURCES\n")
        f.write("-" * 70 + "\n")
        f.write("EC2 pricing:  https://aws.amazon.com/ec2/pricing/on-demand/\n")
        f.write("EBS pricing:  https://aws.amazon.com/ebs/pricing/\n")
        f.write("ALB pricing:  https://aws.amazon.com/elasticloadbalancing/pricing/\n")
        f.write("Public IPv4:  https://aws.amazon.com/vpc/pricing/\n")
        f.write("CloudWatch:   https://aws.amazon.com/cloudwatch/pricing/\n")
        f.write("S3 pricing:   https://aws.amazon.com/s3/pricing/\n")
        f.write("Route 53:     https://aws.amazon.com/route53/pricing/\n\n")

        f.write("COST BREAKDOWN\n")
        f.write("-" * 70 + "\n")
        for name, cost in zip(names, costs):
            f.write(f"  {name:<40s} ${cost:>7.2f}\n")
        f.write("-" * 70 + "\n")
        f.write(f"  {'TOTAL':<40s} ${total:>7.2f}\n\n")

        f.write("OUTPUT FILES\n")
        f.write("-" * 70 + "\n")
        exts = ["png", "pdf"] if fmt == "both" else [fmt]
        for stem in ("lablink_cost_table", "lablink_cost_stacked", "lablink_cost_hbar"):
            for ext in exts:
                f.write(f"  {stem}.{ext}\n")
    logger.info(f"Saved metadata: {meta_file}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--preset",
        choices=list(FORMAT_PRESETS.keys()),
        default="paper",
        help="Figure size/style preset (default: paper)",
    )
    p.add_argument(
        "--format",
        choices=["png", "pdf", "both"],
        default="both",
        help="Output file format (default: both)",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "figures" / "main",
        help="Directory to save output figures",
    )
    p.add_argument("--vms", type=int, default=25, help="Number of client VMs")
    p.add_argument("--hours", type=int, default=4, help="Session duration in hours")
    p.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    preset = FORMAT_PRESETS[args.preset]
    logger.info(f"Using {args.preset} preset: {preset['description']}")

    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["font.size"] = preset["font_size"]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    resources = compute_resources(args.vms, args.hours)
    names = [r[0] for r in resources]
    costs = [round(r[1], 2) for r in resources]
    colors = [r[2] for r in resources]
    total = sum(costs)

    formats = ["png", "pdf"] if args.format == "both" else [args.format]

    for fmt in formats:
        plot_table(
            names, costs, total, args.vms, args.hours, preset,
            args.output_dir / "lablink_cost_table", fmt,
        )
        plot_stacked(
            names, costs, colors, total, args.vms, args.hours, preset,
            args.output_dir / "lablink_cost_stacked", fmt,
        )
        plot_hbar(
            names, costs, colors, total, args.vms, args.hours, preset,
            args.output_dir / "lablink_cost_hbar", fmt,
        )

    write_metadata(
        names, costs, total, args.vms, args.hours,
        args.preset, preset, args.format, args.output_dir,
    )

    logger.info(f"Total session cost: ${total:.2f}")
    logger.info("Done.")


if __name__ == "__main__":
    main()
