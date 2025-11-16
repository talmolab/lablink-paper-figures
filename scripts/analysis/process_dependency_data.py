#!/usr/bin/env python3
"""Process raw dependency data into cleaned time-series format.

This script aggregates data from conda-forge and PyPI sources, resolves conflicts,
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


class DependencyDataProcessor:
    """Processes raw dependency data into cleaned format."""

    def __init__(self, raw_data_dir: Path, output_dir: Path, min_data_points: int = 5):
        self.raw_data_dir = raw_data_dir
        self.output_dir = output_dir
        self.min_data_points = min_data_points
        self.quality_report = []

    def load_raw_data(self) -> List[Dict]:
        """Load all raw JSON data files."""
        logger.info("Loading raw data files...")

        all_data = []

        # Load conda-forge data
        conda_dir = self.raw_data_dir / 'conda_forge_metadata'
        if conda_dir.exists():
            for json_file in conda_dir.glob('*.json'):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        all_data.append(data)
                        logger.info(f"Loaded {json_file.name}: {len(data.get('versions', []))} versions")
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")

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

    def process_to_timeseries(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Convert raw data to time-series dataframe."""
        logger.info("Processing data to time-series format...")

        records = []

        for pkg_data in raw_data:
            package_name = pkg_data.get('package', 'unknown')
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
                        continue

                    total_deps = version_data.get('total_dependencies', 0)
                    version = version_data.get('version', 'unknown')

                    records.append({
                        'package': package_name,
                        'date': date,
                        'version': version,
                        'total_dependencies': total_deps,
                        'source': source
                    })

                except Exception as e:
                    logger.debug(f"Error processing version {version_data}: {e}")
                    continue

            # Quality check
            pkg_count = len([r for r in records if r['package'] == package_name])
            if pkg_count < self.min_data_points:
                self.quality_report.append({
                    'package': package_name,
                    'data_points': pkg_count,
                    'status': 'EXCLUDED',
                    'reason': f'Insufficient data points (< {self.min_data_points})'
                })
                # Remove records for this package
                records = [r for r in records if r['package'] != package_name]
                logger.warning(f"Excluding {package_name}: only {pkg_count} data points")
            else:
                self.quality_report.append({
                    'package': package_name,
                    'data_points': pkg_count,
                    'status': 'INCLUDED',
                    'reason': 'Sufficient data'
                })

        df = pd.DataFrame(records)

        if not df.empty:
            # Sort by package and date
            df = df.sort_values(['package', 'date'])

            # Remove duplicates (keep first occurrence)
            df = df.drop_duplicates(subset=['package', 'version'], keep='first')

            logger.info(f"Processed {len(df)} data points for {df['package'].nunique()} packages")

        return df

    def save_processed_data(self, df: pd.DataFrame) -> None:
        """Save processed data and quality report."""
        # Save time-series CSV
        output_file = self.output_dir / 'dependency_timeseries.csv'
        df.to_csv(output_file, index=False)
        logger.info(f"Saved processed data: {output_file}")

        # Save quality report
        quality_file = self.output_dir / 'quality_report.txt'
        with open(quality_file, 'w') as f:
            f.write("Data Quality Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Processing date: {datetime.now().isoformat()}\n")
            f.write(f"Minimum data points required: {self.min_data_points}\n\n")

            f.write("Package Status:\n")
            f.write("-" * 50 + "\n")
            for report in self.quality_report:
                f.write(f"{report['package']:20s} | {report['status']:10s} | "
                       f"{report['data_points']} points | {report['reason']}\n")

        logger.info(f"Saved quality report: {quality_file}")

        # Save source attribution
        if 'source' in df.columns:
            attribution = df.groupby(['package', 'source']).size().reset_index(name='count')
            attribution_file = self.output_dir / 'source_attribution.csv'
            attribution.to_csv(attribution_file, index=False)
            logger.info(f"Saved source attribution: {attribution_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process raw dependency data into cleaned time-series format"
    )

    parser.add_argument(
        '--raw-data-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'raw' / 'software_complexity',
        help='Directory containing raw JSON data files'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'processed' / 'software_complexity',
        help='Output directory for processed data'
    )

    parser.add_argument(
        '--min-data-points',
        type=int,
        default=5,
        help='Minimum number of data points required per package'
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

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing raw data from: {args.raw_data_dir}")
    logger.info(f"Output directory: {args.output_dir}")

    processor = DependencyDataProcessor(
        args.raw_data_dir,
        args.output_dir,
        args.min_data_points
    )

    # Load and process data
    raw_data = processor.load_raw_data()

    if not raw_data:
        logger.error("No raw data files found! Please run collect_dependency_data.py first.")
        sys.exit(1)

    df = processor.process_to_timeseries(raw_data)

    if df.empty:
        logger.error("No valid data after processing!")
        sys.exit(1)

    processor.save_processed_data(df)

    logger.info("Data processing complete!")


if __name__ == '__main__':
    main()