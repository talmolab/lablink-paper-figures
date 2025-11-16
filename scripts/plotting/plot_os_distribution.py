#!/usr/bin/env python3
"""Generate publication-quality pie chart showing OS distribution.

This script creates a simple, clear pie chart visualization of operating system
distribution across LabLink users, with configurable formatting for different
contexts (paper, poster).
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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
    }
}


class OSDistributionPlotter:
    """Creates pie chart visualization of OS distribution."""

    def __init__(self, data_file: Path, format_preset: str = 'paper'):
        """Initialize plotter with data and format settings.

        Args:
            data_file: Path to CSV file with os_name and percentage columns
            format_preset: Format preset name ('paper' or 'poster')
        """
        self.data = pd.read_csv(data_file)
        self.preset = FORMAT_PRESETS[format_preset]
        self.format_name = format_preset

        # Set up matplotlib style
        sns.set_style("white")  # Clean background for pie chart
        sns.set_context("paper", font_scale=self.preset['font_size'] / 12)

        # Use colorblind-friendly palette
        self.colors = sns.color_palette("colorblind", n_colors=len(self.data))

    def plot_pie_chart(self, output_path: Path) -> None:
        """Generate the OS distribution pie chart.

        Args:
            output_path: Output path without extension (PNG and PDF will be added)
        """
        logger.info("Generating OS distribution pie chart...")

        fig, ax = plt.subplots(figsize=self.preset['figsize'])

        # Extract data
        os_names = self.data['os_name'].tolist()
        percentages = self.data['percentage'].tolist()

        # Create labels with percentages
        labels = [f"{name}\n{pct:.1f}%" for name, pct in zip(os_names, percentages)]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            percentages,
            labels=labels,
            colors=self.colors,
            autopct='',  # We include percentage in labels
            startangle=90,  # Start from top
            textprops={'fontsize': self.preset['font_size']},
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )

        # Make label text bold for better readability
        for text in texts:
            text.set_fontweight('bold')

        # Add title
        ax.set_title(
            'Operating System Distribution of SLEAP Users',
            fontsize=self.preset['font_size'] + 2,
            fontweight='bold',
            pad=20
        )

        # Equal aspect ratio ensures circular pie
        ax.axis('equal')

        plt.tight_layout()

        # Save figure in both PNG and PDF formats
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

    def generate_metadata(self, output_path: Path, data_file: Path) -> None:
        """Generate metadata file documenting the figure generation.

        Args:
            output_path: Output path for metadata file
            data_file: Path to source data file
        """
        metadata = {
            'generation_timestamp': datetime.now().isoformat(),
            'format_preset': self.format_name,
            'data_source_file': str(data_file),
            'os_distribution': dict(zip(
                self.data['os_name'].tolist(),
                self.data['percentage'].tolist()
            )),
            'total_percentage': self.data['percentage'].sum()
        }

        metadata_file = output_path.parent / 'os_distribution_metadata.txt'
        with open(metadata_file, 'w') as f:
            f.write("OS Distribution Figure Metadata\n")
            f.write("=" * 50 + "\n\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

        logger.info(f"Saved metadata: {metadata_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate OS distribution pie chart",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate paper format
  python plot_os_distribution.py --format paper

  # Generate poster format
  python plot_os_distribution.py --format poster

  # Custom output directory
  python plot_os_distribution.py --format paper --output-dir ../../figures/supplementary
        """
    )

    parser.add_argument(
        '--data-file',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'processed' / 'os_distribution' / 'os_stats.csv',
        help='Path to OS distribution CSV file'
    )

    parser.add_argument(
        '--format',
        choices=['paper', 'poster'],
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
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading data from: {args.data_file}")
    logger.info(f"Using format preset: {args.format} - {FORMAT_PRESETS[args.format]['description']}")
    logger.info(f"Output directory: {args.output_dir}")

    plotter = OSDistributionPlotter(args.data_file, args.format)

    # Generate pie chart
    output_path = args.output_dir / 'os_distribution'
    plotter.plot_pie_chart(output_path)

    # Generate metadata
    plotter.generate_metadata(output_path, args.data_file)

    logger.info("Figure generation complete!")


if __name__ == '__main__':
    main()
