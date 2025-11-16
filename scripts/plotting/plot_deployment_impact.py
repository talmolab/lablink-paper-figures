#!/usr/bin/env python3
"""Generate publication-quality timeline figure showing LabLink deployment impact.

This script creates a timeline visualization of workshops and training events
where LabLink was deployed, showing participant counts, audience diversity,
and geographic reach across 14 events from February 2024 to October 2025.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
        'font_size': 12,
        'dpi': 300,
        'figsize': (10, 6),
        'description': 'Two-column journal layout'
    },
    'poster': {
        'font_size': 18,
        'dpi': 300,
        'figsize': (16, 10),
        'description': 'Conference poster (readable at distance)'
    }
}

# Audience type color mapping (colorblind-friendly)
AUDIENCE_COLORS = {
    'K-12': '#1f77b4',  # Blue
    'K-12 Educators': '#ff7f0e',  # Orange
    'Undergraduate/Graduate': '#2ca02c',  # Green
    'Undergraduate': '#2ca02c',  # Green (same as Undergraduate/Graduate)
    'Graduate/Faculty': '#d62728',  # Red
    'RSE': '#8c564b',  # Brown
    'Graduate': '#e377c2'  # Pink
}


class DeploymentImpactPlotter:
    """Creates timeline visualization of LabLink deployment impact."""

    def __init__(self, data_file: Path, format_preset: str = 'paper'):
        """Initialize plotter with data and format settings.

        Args:
            data_file: Path to CSV file with workshop metadata
            format_preset: Format preset name ('paper' or 'poster')
        """
        self.data = pd.read_csv(data_file)
        # Convert date column to datetime
        self.data['date'] = pd.to_datetime(self.data['date'])
        # Sort by date
        self.data = self.data.sort_values('date').reset_index(drop=True)

        self.preset = FORMAT_PRESETS[format_preset]
        self.format_name = format_preset

        # Set up matplotlib style
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=self.preset['font_size'] / 12)

    def plot_timeline(self, output_path: Path) -> None:
        """Generate the deployment impact timeline figure.

        Args:
            output_path: Output path without extension (PNG and PDF will be added)
        """
        logger.info("Generating deployment impact timeline...")

        fig, ax = plt.subplots(figsize=self.preset['figsize'])

        # Create horizontal bar chart
        y_positions = np.arange(len(self.data))

        # Plot bars colored by audience type
        for idx, row in self.data.iterrows():
            color = AUDIENCE_COLORS.get(row['audience_type'], '#7f7f7f')
            ax.barh(
                idx,
                row['participants'],
                color=color,
                alpha=0.8,
                edgecolor='white',
                linewidth=1.5
            )

            # Add participant count inside bar if space allows, otherwise outside
            if row['participants'] > 30:
                ax.text(
                    row['participants'] / 2,
                    idx,
                    f"{int(row['participants'])}",
                    ha='center',
                    va='center',
                    fontweight='bold',
                    fontsize=self.preset['font_size'] - 2,
                    color='white'
                )
            else:
                ax.text(
                    row['participants'] + 5,
                    idx,
                    f"{int(row['participants'])}",
                    ha='left',
                    va='center',
                    fontweight='bold',
                    fontsize=self.preset['font_size'] - 2
                )

        # Set y-axis labels (workshop names + dates)
        labels = []
        for _, row in self.data.iterrows():
            date_str = row['date'].strftime('%b %Y')
            # Truncate long event names for readability
            event_name = row['event_name']
            if len(event_name) > 45:
                event_name = event_name[:42] + '...'
            labels.append(f"{date_str}: {event_name}")

        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels, fontsize=self.preset['font_size'] - 3)

        # Set x-axis
        ax.set_xlabel('Number of Participants', fontsize=self.preset['font_size'])
        ax.set_xlim(0, self.data['participants'].max() * 1.15)

        # Add title
        total_participants = self.data['participants'].sum()
        total_events = len(self.data)
        ax.set_title(
            f'LabLink Deployment Impact: {total_events} Workshops, {int(total_participants)} Participants\n'
            f'February 2024 - October 2025',
            fontsize=self.preset['font_size'] + 2,
            fontweight='bold',
            pad=20
        )

        # Create legend for audience types
        unique_audiences = self.data['audience_type'].unique()
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, fc=AUDIENCE_COLORS.get(aud, '#7f7f7f'),
                         edgecolor='white', linewidth=1.5, alpha=0.8)
            for aud in unique_audiences
        ]
        ax.legend(
            legend_elements,
            unique_audiences,
            loc='upper right',
            fontsize=self.preset['font_size'] - 3,
            title='Audience Type',
            title_fontsize=self.preset['font_size'] - 2,
            framealpha=0.9
        )

        # Add vertical grid only for readability
        ax.grid(True, axis='x', alpha=0.3, zorder=0)
        ax.set_axisbelow(True)

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
            'total_workshops': len(self.data),
            'total_participants': int(self.data['participants'].sum()),
            'date_range': {
                'start': str(self.data['date'].min().date()),
                'end': str(self.data['date'].max().date())
            },
            'audience_types': self.data['audience_type'].unique().tolist(),
            'geographic_locations': self.data['location'].unique().tolist()
        }

        metadata_file = output_path.parent / 'deployment_impact_metadata.txt'
        with open(metadata_file, 'w') as f:
            f.write("Deployment Impact Figure Metadata\n")
            f.write("=" * 50 + "\n\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

        logger.info(f"Saved metadata: {metadata_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate LabLink deployment impact timeline figure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate paper format
  python plot_deployment_impact.py --format paper

  # Generate poster format
  python plot_deployment_impact.py --format poster

  # Custom output directory
  python plot_deployment_impact.py --format paper --output-dir ../../figures/supplementary
        """
    )

    parser.add_argument(
        '--data-file',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'processed' / 'deployment_impact' / 'workshops.csv',
        help='Path to workshop metadata CSV file'
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

    plotter = DeploymentImpactPlotter(args.data_file, args.format)

    # Generate timeline figure
    output_path = args.output_dir / 'deployment_impact'
    plotter.plot_timeline(output_path)

    # Generate metadata
    plotter.generate_metadata(output_path, args.data_file)

    logger.info("Figure generation complete!")


if __name__ == '__main__':
    main()