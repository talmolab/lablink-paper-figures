#!/usr/bin/env python3
"""Process raw GPU dependency data into cleaned time-series format.

This script aggregates GPU data from PyPI sources, normalizes package variants,
and generates a cleaned CSV file suitable for visualization.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Package variant normalization mapping
PACKAGE_VARIANTS = {
    # CuPy variants → base package
    'cupy-cuda102': 'cupy',
    'cupy-cuda110': 'cupy',
    'cupy-cuda11x': 'cupy',
    'cupy-cuda12x': 'cupy',

    # TensorFlow variants → base package (pre-2.1)
    'tensorflow-gpu': 'tensorflow',
}


class GPUDataProcessor:
    """Processes raw GPU dependency data into cleaned format."""

    def __init__(self, raw_data_dir: Path, output_dir: Path, min_data_points: int = 5):
        self.raw_data_dir = raw_data_dir
        self.output_dir = output_dir
        self.min_data_points = min_data_points
        self.quality_report = []

    def load_raw_data(self) -> List[Dict]:
        """Load all raw JSON data files from PyPI metadata."""
        logger.info("Loading raw data files...")

        all_data = []

        # Load PyPI data
        pypi_dir = self.raw_data_dir / 'pypi_metadata'
        if pypi_dir.exists():
            for json_file in pypi_dir.glob('*.json'):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        all_data.append(data)
                        logger.info(f"Loaded {json_file.name}: {len(data.get('versions', []))} versions")
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")

        logger.info(f"Loaded data for {len(all_data)} packages")
        return all_data

    def normalize_package_name(self, package_name: str) -> str:
        """Normalize package variants to base package name."""
        return PACKAGE_VARIANTS.get(package_name, package_name)

    def process_to_timeseries(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Convert raw GPU data to time-series dataframe."""
        logger.info("Processing data to time-series format...")

        records = []

        for pkg_data in raw_data:
            original_package_name = pkg_data.get('package', 'unknown')
            package_name = self.normalize_package_name(original_package_name)
            source = pkg_data.get('source', 'unknown')
            versions = pkg_data.get('versions', [])

            for version_data in versions:
                try:
                    date_str = version_data.get('date', '')
                    if not date_str:
                        continue

                    # Parse date
                    try:
                        date = pd.to_datetime(date_str)
                    except:
                        logger.debug(f"Could not parse date: {date_str}")
                        continue

                    gpu_score = version_data.get('gpu_score', 0)
                    cuda_version = version_data.get('cuda_version', '')
                    gpu_deps_count = version_data.get('gpu_deps_count', 0)
                    requires_external_cuda = version_data.get('requires_external_cuda', False)

                    records.append({
                        'package': package_name,
                        'original_package': original_package_name,
                        'version': version_data.get('version', ''),
                        'date': date,
                        'gpu_score': gpu_score,
                        'cuda_version': cuda_version if cuda_version else None,
                        'gpu_deps_count': gpu_deps_count,
                        'requires_external_cuda': requires_external_cuda,
                        'source': source
                    })

                except Exception as e:
                    logger.debug(f"Error processing version {version_data.get('version')}: {e}")
                    continue

        # Create DataFrame
        df = pd.DataFrame(records)

        if df.empty:
            logger.warning("No valid data points found")
            return df

        # Sort by package and date
        df = df.sort_values(['package', 'date'])

        # Filter packages with insufficient data
        package_counts = df['package'].value_counts()
        valid_packages = package_counts[package_counts >= self.min_data_points].index

        for package in package_counts.index:
            count = package_counts[package]
            if count < self.min_data_points:
                self.quality_report.append({
                    'package': package,
                    'status': 'EXCLUDED',
                    'count': count,
                    'reason': f'Insufficient data points (< {self.min_data_points})'
                })
                logger.warning(f"Excluding {package}: only {count} data points")
            else:
                self.quality_report.append({
                    'package': package,
                    'status': 'INCLUDED',
                    'count': count,
                    'reason': 'Sufficient data'
                })

        # Filter DataFrame
        df = df[df['package'].isin(valid_packages)]

        logger.info(f"Processed {len(df)} data points for {len(valid_packages)} packages")

        return df

    def generate_quality_report(self) -> None:
        """Generate data quality report."""
        output_file = self.output_dir / 'quality_report.txt'

        with open(output_file, 'w') as f:
            f.write("GPU Data Quality Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Processing date: {datetime.now().isoformat()}\n")
            f.write(f"Minimum data points required: {self.min_data_points}\n\n")
            f.write("Package Status:\n")
            f.write("-" * 50 + "\n")

            for item in self.quality_report:
                status_label = f"{item['status']:<10}"
                count_label = f"{item['count']} points"
                f.write(f"{item['package']:<20} | {status_label} | {count_label:<15} | {item['reason']}\n")

        logger.info(f"Saved quality report: {output_file}")

    def generate_source_attribution(self, df: pd.DataFrame) -> None:
        """Generate source attribution CSV."""
        output_file = self.output_dir / 'source_attribution.csv'

        # Count data points by package and source
        attribution = df.groupby(['package', 'source']).size().reset_index(name='count')

        attribution.to_csv(output_file, index=False)
        logger.info(f"Saved source attribution: {output_file}")

    def save_timeseries(self, df: pd.DataFrame) -> None:
        """Save processed time-series data to CSV."""
        output_file = self.output_dir / 'gpu_timeseries.csv'

        # Select columns for output
        output_df = df[['package', 'version', 'date', 'gpu_score', 'cuda_version',
                        'gpu_deps_count', 'requires_external_cuda', 'source']]

        output_df.to_csv(output_file, index=False)
        logger.info(f"Saved processed data: {output_file}")

    def process_all(self) -> None:
        """Execute full processing pipeline."""
        # Load raw data
        raw_data = self.load_raw_data()

        if not raw_data:
            logger.error("No raw data found. Please run collect_gpu_data.py first.")
            return

        # Process to time-series
        df = self.process_to_timeseries(raw_data)

        if df.empty:
            logger.error("No valid data after processing")
            return

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Save outputs
        self.save_timeseries(df)
        self.generate_quality_report()
        self.generate_source_attribution(df)

        logger.info("Data processing complete!")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process raw GPU dependency data into cleaned time-series format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process data with default settings
  python process_gpu_data.py

  # Process with custom directories
  python process_gpu_data.py --raw-dir ../../data/raw/gpu_reliance --output-dir ../../data/processed/gpu_reliance

  # Use different minimum data points threshold
  python process_gpu_data.py --min-points 10
        """
    )

    parser.add_argument(
        '--raw-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'raw' / 'gpu_reliance',
        help='Directory containing raw JSON data'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'processed' / 'gpu_reliance',
        help='Output directory for processed data'
    )

    parser.add_argument(
        '--min-points',
        type=int,
        default=5,
        help='Minimum number of data points required per package (default: 5)'
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

    logger.info(f"Processing raw data from: {args.raw_dir}")
    logger.info(f"Output directory: {args.output_dir}")

    processor = GPUDataProcessor(args.raw_dir, args.output_dir, args.min_points)
    processor.process_all()


if __name__ == '__main__':
    main()