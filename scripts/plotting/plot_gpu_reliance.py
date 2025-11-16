#!/usr/bin/env python3
"""Generate publication-quality figures showing GPU hardware reliance over time.

This script creates time-series visualizations of GPU dependency growth across
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
    'ML/Deep Learning': ['tensorflow', 'torch', 'jax', 'jaxlib', 'numba'],
    'Scientific Computing': ['cupy', 'cudf', 'scikit-image'],
    'Biology/Molecular Dynamics': ['openmm', 'alphafold']
}


class GPUReliancePlotter:
    """Creates visualizations of GPU hardware reliance trends."""

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

    def _add_gpu_scale_explanation(self, fig, ax) -> None:
        """Add GPU dependency scale explanation below figure.
        
        Places text in bottom margin, completely outside the plot area.
        """
        # Format-specific rubric text
        if self.format_name == 'paper':
            rubric_text = (
                "GPU Dependency Scale: "
                "0=No GPU support  |  1=Optional (extras)  |  2=Recommended  |  "
                "3=Practical required  |  4=Hard required  |  5=GPU-first"
            )
            fontsize = 8
            
        elif self.format_name == 'poster':
            rubric_text = (
                "GPU Dependency Scale:\n"
                "0 = No GPU support  |  1 = Optional (in extras only)  |  "
                "2 = Recommended (slow without)  |  3 = Practical required (bundled CUDA)\n"
                "4 = Hard required (install fails without CUDA)  |  "
                "5 = GPU-first (designed exclusively for GPU, no CPU fallback)"
            )
            fontsize = 14
            
        else:  # presentation
            rubric_text = (
                "GPU Dependency Scale: "
                "0=No support  |  1=Optional  |  2=Recommended  |  "
                "3=Practical required  |  4=Hard required  |  5=GPU-first"
            )
            fontsize = 11
        
        # Add text below the plot using figure coordinates
        # (0.5, 0) is bottom center of figure
        fig.text(
            0.5, 0.02,  # x, y in figure coordinates (centered, near bottom)
            rubric_text,
            ha='center',
            va='bottom',
            fontsize=fontsize,
            style='italic',
            wrap=True,
            bbox=dict(
                boxstyle='round,pad=0.8',
                facecolor='wheat',
                alpha=0.3,
                edgecolor='none'
            )
        )

    def plot_main_figure(self, output_path: Path) -> None:
        """Generate the main figure showing all packages over time."""
        logger.info("Generating main figure...")

        fig, ax = plt.subplots(figsize=self.preset['figsize'])

        # Get unique packages
        packages = self.data['package'].unique()

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
                pkg_data['gpu_score'],
                color=color,
                s=30,
                alpha=0.6,
                label=package,
                zorder=3
            )

            # Connect points chronologically
            ax.plot(
                pkg_data['date'],
                pkg_data['gpu_score'],
                color=color,
                alpha=0.3,
                linewidth=1,
                zorder=2
            )

        # Format axes
        ax.set_xlabel('Year', fontsize=self.preset['font_size'])
        ax.set_ylabel('GPU Dependency Level (0=None, 5=GPU-First)', fontsize=self.preset['font_size'])
        ax.set_title('GPU Hardware Reliance in Scientific Software Over Time',
                     fontsize=self.preset['font_size'] + 2,
                     fontweight='bold',
                     pad=20)

        # Set Y-axis limits to 0-5 range
        ax.set_ylim(-0.5, 5.5)
        ax.set_yticks([0, 1, 2, 3, 4, 5])

        # Format x-axis to show only first and last years (avoid overlapping labels)
        min_year = self.data['date'].dt.year.min()
        max_year = self.data['date'].dt.year.max()
        ax.set_xticks([self.data['date'].min(), self.data['date'].max()])
        ax.set_xticklabels([str(min_year), str(max_year)])

        # Format legend
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

        # Add GPU scale explanation
        self._add_gpu_scale_explanation(fig, ax)

        # Tight layout with space for bottom text
        plt.tight_layout(rect=[0, 0.08, 1, 1])

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

                ax.scatter(pkg_data['date'], pkg_data['gpu_score'],
                          color=color, label=package, alpha=0.6, s=25)
                ax.plot(pkg_data['date'], pkg_data['gpu_score'],
                       color=color, alpha=0.3, linewidth=1)

            ax.set_ylabel('GPU Level', fontsize=self.preset['font_size'] - 2)
            ax.set_title(cat_name, fontsize=self.preset['font_size'], fontweight='bold')
            ax.legend(fontsize=self.preset['font_size'] - 4, loc='upper left')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(-0.5, 5.5)
            ax.set_yticks([0, 1, 2, 3, 4, 5])

        axes[-1].set_xlabel('Year', fontsize=self.preset['font_size'])
        fig.suptitle('GPU Dependency Growth by Scientific Domain',
                     fontsize=self.preset['font_size'] + 2,
                     fontweight='bold',
                     y=0.98)

        # Add GPU scale explanation below all subplots
        self._add_gpu_scale_explanation(fig, axes[-1])

        plt.tight_layout(rect=[0, 0.08, 1, 0.96])

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

        metadata_file = output_path.parent / 'gpu_reliance_metadata.txt'
        with open(metadata_file, 'w') as f:
            f.write("GPU Hardware Reliance Figure Metadata\n")
            f.write("=" * 50 + "\n\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

        logger.info(f"Saved metadata: {metadata_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate GPU hardware reliance figures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate paper format
  python plot_gpu_reliance.py --format paper

  # Generate poster format
  python plot_gpu_reliance.py --format poster --output-dir ../../figures/supplementary

  # Use custom data file
  python plot_gpu_reliance.py --data-file custom_data.csv
        """
    )

    parser.add_argument(
        '--data-file',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'processed' / 'gpu_reliance' / 'gpu_timeseries.csv',
        help='Path to processed GPU time-series CSV file'
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
        logger.info("Please run collect_gpu_data.py and process_gpu_data.py first")
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading data from: {args.data_file}")
    logger.info(f"Using format preset: {args.format} - {FORMAT_PRESETS[args.format]['description']}")
    logger.info(f"Output directory: {args.output_dir}")

    plotter = GPUReliancePlotter(args.data_file, args.format)

    figures_to_generate = args.figures
    if 'all' in figures_to_generate:
        figures_to_generate = ['main', 'category']

    if 'main' in figures_to_generate:
        output_path = args.output_dir / 'gpu_reliance_over_time'
        plotter.plot_main_figure(output_path)

    if 'category' in figures_to_generate:
        output_path = args.output_dir / 'gpu_reliance_by_category'
        plotter.plot_category_comparison(output_path)

    # Generate metadata
    plotter.generate_metadata(args.output_dir / 'gpu_reliance_over_time', args.data_file)

    logger.info("Figure generation complete!")


if __name__ == '__main__':
    main()