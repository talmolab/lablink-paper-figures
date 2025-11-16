#!/usr/bin/env python3
"""Generate publication-quality figures showing scientific software complexity over time.

This script creates time-series visualizations of dependency growth across
scientific Python packages, with configurable formatting for different contexts
(paper, poster, presentation).
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Format presets
FORMAT_PRESETS = {
    'paper': {
        'font_size': 14,
        'dpi': 300,
        'figsize': (6.5, 5),
        'description': 'Two-column journal layout'
    },
    'poster': {
        'font_size': 20,
        'dpi': 300,
        'figsize': (12, 9),
        'description': 'Conference poster (readable at distance)'
    },
    'presentation': {
        'font_size': 16,
        'dpi': 150,
        'figsize': (10, 7.5),
        'description': 'Slide deck (16:9 aspect ratio)'
    }
}

# Package categories
PACKAGE_CATEGORIES = {
    'Core Scientific': ['numpy', 'scipy', 'matplotlib', 'pandas'],
    'Machine Learning': ['tensorflow', 'torch', 'scikit-learn'],
    'Domain/Workflow': ['astropy', 'jupyter']
}


class SoftwareComplexityPlotter:
    """Creates visualizations of software complexity trends."""

    def __init__(self, data_file: Path, format_preset: str = 'paper'):
        self.data = pd.read_csv(data_file)
        # Convert date column to datetime
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.preset = FORMAT_PRESETS[format_preset]
        self.format_name = format_preset

        # Set up matplotlib style
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=self.preset['font_size'] / 12)

        # Use colorblind-friendly palette
        self.colors = sns.color_palette("colorblind", n_colors=10)

    def plot_main_figure(self, output_path: Path) -> None:
        """Generate the main figure showing all packages over time."""
        logger.info("Generating main figure...")

        fig, ax = plt.subplots(figsize=self.preset['figsize'])

        # Get unique packages
        packages = self.data['package'].unique()

        # Determine if we need logarithmic scale
        dep_range = self.data['total_dependencies'].max() / (self.data['total_dependencies'].min() + 1)
        use_log_scale = dep_range > 100

        # Plot each package
        for idx, package in enumerate(packages):
            pkg_data = self.data[self.data['package'] == package].copy()
            pkg_data = pkg_data.sort_values('date')

            if len(pkg_data) < 2:
                logger.warning(f"Skipping {package}: insufficient data points")
                continue

            color = self.colors[idx % len(self.colors)]

            # Plot scatter points
            ax.scatter(
                pkg_data['date'],
                pkg_data['total_dependencies'],
                color=color,
                s=30,
                alpha=0.6,
                label=package,
                zorder=3
            )

            # Connect points chronologically
            ax.plot(
                pkg_data['date'],
                pkg_data['total_dependencies'],
                color=color,
                alpha=0.3,
                linewidth=1,
                zorder=2
            )

            # Add LOESS-style trend line if enough points
            if len(pkg_data) >= 5:
                try:
                    # Simple moving average for trend
                    window = min(5, len(pkg_data) // 2)
                    trend = pkg_data['total_dependencies'].rolling(window=window, center=True).mean()

                    ax.plot(
                        pkg_data['date'],
                        trend,
                        color=color,
                        alpha=0.5,
                        linewidth=2,
                        linestyle='--',
                        zorder=1
                    )
                except:
                    pass

        # Format axes
        ax.set_xlabel('Year', fontsize=self.preset['font_size'])
        ax.set_ylabel('Direct Dependencies', fontsize=self.preset['font_size'])
        ax.set_title('Scientific Software Complexity Growth Over Time',
                     fontsize=self.preset['font_size'] + 2,
                     fontweight='bold',
                     pad=20)

        if use_log_scale:
            ax.set_yscale('log')
            ax.set_ylabel('Direct Dependencies (log scale)', fontsize=self.preset['font_size'])

        # Format x-axis to show only first and last years (avoid overlapping labels)
        min_year = self.data['date'].dt.year.min()
        max_year = self.data['date'].dt.year.max()
        ax.set_xticks([self.data['date'].min(), self.data['date'].max()])
        ax.set_xticklabels([str(min_year), str(max_year)])

        # Format legend with categories
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(
            handles,
            labels,
            loc='upper left',
            fontsize=self.preset['font_size'] - 2,
            framealpha=0.9
        )

        # Add grid
        ax.grid(True, alpha=0.3, zorder=0)

        # Tight layout
        plt.tight_layout()

        # Save figure
        for ext in ['png', 'pdf']:
            output_file = Path(str(output_path) + f'.{ext}')
            plt.savefig(
                output_file,
                dpi=self.preset['dpi'],
                bbox_inches='tight',
                format=ext
            )
            logger.info(f"Saved: {output_file}")

        plt.close()

    def plot_category_comparison(self, output_path: Path) -> None:
        """Generate faceted plot showing each category separately."""
        logger.info("Generating category comparison figure...")

        # Count categories with data
        categories_with_data = []
        for cat_name, packages in PACKAGE_CATEGORIES.items():
            cat_data = self.data[self.data['package'].isin(packages)]
            if len(cat_data) > 0:
                categories_with_data.append(cat_name)

        if not categories_with_data:
            logger.warning("No data for category comparison")
            return

        n_cats = len(categories_with_data)
        fig, axes = plt.subplots(
            n_cats, 1,
            figsize=(self.preset['figsize'][0], self.preset['figsize'][1] * n_cats / 2),
            sharex=True
        )

        if n_cats == 1:
            axes = [axes]

        for idx, cat_name in enumerate(categories_with_data):
            ax = axes[idx]
            packages = PACKAGE_CATEGORIES[cat_name]
            cat_data = self.data[self.data['package'].isin(packages)]

            for pkg_idx, package in enumerate(cat_data['package'].unique()):
                pkg_data = cat_data[cat_data['package'] == package].sort_values('date')
                color = self.colors[pkg_idx % len(self.colors)]

                ax.scatter(pkg_data['date'], pkg_data['total_dependencies'],
                          color=color, label=package, alpha=0.6, s=25)
                ax.plot(pkg_data['date'], pkg_data['total_dependencies'],
                       color=color, alpha=0.3, linewidth=1)

            ax.set_ylabel('Dependencies', fontsize=self.preset['font_size'] - 2)
            ax.set_title(cat_name, fontsize=self.preset['font_size'], fontweight='bold')
            ax.legend(fontsize=self.preset['font_size'] - 4, loc='upper left')
            ax.grid(True, alpha=0.3)

        axes[-1].set_xlabel('Year', fontsize=self.preset['font_size'])
        fig.suptitle('Dependency Growth by Category',
                     fontsize=self.preset['font_size'] + 2,
                     fontweight='bold')

        plt.tight_layout()

        # Save
        for ext in ['png', 'pdf']:
            output_file = Path(str(output_path) + f'.{ext}')
            plt.savefig(output_file, dpi=self.preset['dpi'], bbox_inches='tight', format=ext)
            logger.info(f"Saved: {output_file}")

        plt.close()

    def generate_metadata(self, output_path: Path, data_file: Path) -> None:
        """Generate metadata file documenting the figure generation."""
        metadata = {
            'generation_timestamp': datetime.now().isoformat(),
            'format_preset': self.format_name,
            'data_source_file': str(data_file),
            'packages_included': self.data['package'].unique().tolist(),
            'total_data_points': len(self.data),
            'date_range': {
                'start': str(self.data['date'].min()),
                'end': str(self.data['date'].max())
            },
            'sources_used': self.data['source'].value_counts().to_dict() if 'source' in self.data.columns else {}
        }

        metadata_file = output_path.parent / 'software_complexity_metadata.txt'
        with open(metadata_file, 'w') as f:
            f.write("Scientific Software Complexity Figure Metadata\n")
            f.write("=" * 50 + "\n\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

        logger.info(f"Saved metadata: {metadata_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate software complexity figures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate paper format
  python plot_software_complexity.py --format paper

  # Generate poster format
  python plot_software_complexity.py --format poster --output-dir ../../figures/supplementary

  # Use custom data file
  python plot_software_complexity.py --data-file custom_data.csv
        """
    )

    parser.add_argument(
        '--data-file',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'processed' / 'software_complexity' / 'dependency_timeseries.csv',
        help='Path to processed dependency timeseries CSV file'
    )

    parser.add_argument(
        '--format',
        choices=['paper', 'poster', 'presentation'],
        default='paper',
        help='Format preset for the output figure'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'figures' / 'main',
        help='Output directory for generated figures'
    )

    parser.add_argument(
        '--figures',
        nargs='+',
        choices=['main', 'category', 'all'],
        default=['all'],
        help='Which figures to generate'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if not args.data_file.exists():
        logger.error(f"Data file not found: {args.data_file}")
        logger.info("Please run collect_dependency_data.py first to collect data")
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading data from: {args.data_file}")
    logger.info(f"Using format preset: {args.format} - {FORMAT_PRESETS[args.format]['description']}")
    logger.info(f"Output directory: {args.output_dir}")

    plotter = SoftwareComplexityPlotter(args.data_file, args.format)

    figures_to_generate = args.figures
    if 'all' in figures_to_generate:
        figures_to_generate = ['main', 'category']

    if 'main' in figures_to_generate:
        output_path = args.output_dir / 'software_complexity_over_time'
        plotter.plot_main_figure(output_path)

    if 'category' in figures_to_generate:
        output_path = args.output_dir / 'software_complexity_by_category'
        plotter.plot_category_comparison(output_path)

    # Generate metadata
    plotter.generate_metadata(args.output_dir / 'software_complexity_over_time', args.data_file)

    logger.info("Figure generation complete!")


if __name__ == '__main__':
    main()