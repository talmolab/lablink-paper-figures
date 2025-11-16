#!/usr/bin/env python3
"""Collect historical dependency data for scientific Python packages.

This script collects dependency data using a source-specific strategy:
- conda-forge for compiled scientific packages (NumPy, SciPy, matplotlib, pandas, scikit-learn, AstroPy)
- PyPI for pure-Python packages (TensorFlow, PyTorch, Jupyter)
- GitHub for validation (spot-checking key versions)
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

import requests
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Package source mapping
# Note: Using PyPI for all packages due to conda-forge using branch-based
# versioning instead of tags. PyPI provides consistent API and historical data.
PACKAGE_SOURCES = {
    # Core scientific packages - use PyPI (conda-forge uses branches not tags)
    'numpy': 'pypi',
    'scipy': 'pypi',
    'matplotlib': 'pypi',
    'pandas': 'pypi',
    'scikit-learn': 'pypi',
    'astropy': 'pypi',

    # ML and workflow packages - use PyPI
    'tensorflow': 'pypi',
    'torch': 'pypi',  # PyPI package name for PyTorch
    'jupyter': 'pypi',
}

# conda-forge feedstock repository names (may differ from package name)
CONDA_FEEDSTOCK_NAMES = {
    'scikit-learn': 'scikit-learn',
    'numpy': 'numpy',
    'scipy': 'scipy',
    'matplotlib': 'matplotlib',
    'pandas': 'pandas',
    'astropy': 'astropy',
}


class DependencyDataCollector:
    """Collects dependency data from multiple sources."""

    def __init__(self, output_dir: Path, github_token: Optional[str] = None):
        self.output_dir = output_dir
        self.github_token = github_token
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})

    def collect_pypi_data(self, package_name: str) -> Dict:
        """Collect dependency data from PyPI JSON API."""
        logger.info(f"Collecting PyPI data for {package_name}...")

        try:
            # Get all releases from PyPI
            response = self.session.get(f'https://pypi.org/pypi/{package_name}/json')
            response.raise_for_status()
            data = response.json()

            versions_data = []
            releases = data.get('releases', {})

            for version, files in releases.items():
                if not files:  # Skip empty releases
                    continue

                # Get upload time from first file
                upload_time = files[0].get('upload_time', '')

                # Get version-specific metadata for dependency info
                try:
                    version_response = self.session.get(
                        f'https://pypi.org/pypi/{package_name}/{version}/json'
                    )
                    version_response.raise_for_status()
                    version_data = version_response.json()

                    requires_dist = version_data['info'].get('requires_dist', []) or []

                    # Filter out extras and count unique dependencies
                    dependencies = set()
                    for req in requires_dist:
                        if req and not req.startswith('extra =='):
                            # Extract package name before any version specifier or extras
                            dep_name = req.split('[')[0].split(';')[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
                            if dep_name:
                                dependencies.add(dep_name)

                    versions_data.append({
                        'version': version,
                        'date': upload_time,
                        'total_dependencies': len(dependencies),
                        'dependencies': list(dependencies)
                    })

                except Exception as e:
                    logger.debug(f"Could not get metadata for {package_name} {version}: {e}")
                    continue

            logger.info(f"Collected {len(versions_data)} versions for {package_name} from PyPI")

            return {
                'package': package_name,
                'source': 'pypi',
                'collection_date': datetime.now().isoformat(),
                'versions': versions_data
            }

        except Exception as e:
            logger.error(f"Failed to collect PyPI data for {package_name}: {e}")
            return {'package': package_name, 'source': 'pypi', 'error': str(e), 'versions': []}

    def collect_conda_forge_data(self, package_name: str) -> Dict:
        """Collect dependency data from conda-forge feedstock repository."""
        logger.info(f"Collecting conda-forge data for {package_name}...")

        feedstock_name = CONDA_FEEDSTOCK_NAMES.get(package_name, package_name)
        feedstock_repo = f"{feedstock_name}-feedstock"

        try:
            # Get all tags/releases from the feedstock repository
            tags_url = f"https://api.github.com/repos/conda-forge/{feedstock_repo}/tags"
            response = self.session.get(tags_url)
            response.raise_for_status()
            tags = response.json()

            logger.info(f"Found {len(tags)} tags for {feedstock_repo}")

            versions_data = []

            # Sample tags to avoid rate limiting (get every Nth tag for large repos)
            sample_interval = max(1, len(tags) // 50)  # Max 50 versions
            sampled_tags = tags[::sample_interval]

            for tag in sampled_tags[:50]:  # Limit to 50 versions
                tag_name = tag['name']
                commit_sha = tag['commit']['sha']

                try:
                    # Get meta.yaml from this tag
                    meta_url = f"https://raw.githubusercontent.com/conda-forge/{feedstock_repo}/{commit_sha}/recipe/meta.yaml"
                    meta_response = self.session.get(meta_url)

                    if meta_response.status_code == 200:
                        meta_content = meta_response.text

                        # Parse dependencies from meta.yaml (simple parsing)
                        dependencies = self._parse_meta_yaml_dependencies(meta_content)

                        # Get commit date
                        commit_url = f"https://api.github.com/repos/conda-forge/{feedstock_repo}/commits/{commit_sha}"
                        commit_response = self.session.get(commit_url)
                        commit_data = commit_response.json()
                        commit_date = commit_data['commit']['committer']['date']

                        versions_data.append({
                            'version': tag_name,
                            'date': commit_date,
                            'commit_sha': commit_sha,
                            'total_dependencies': len(dependencies),
                            'dependencies': dependencies
                        })

                        logger.debug(f"Collected {tag_name}: {len(dependencies)} dependencies")

                except Exception as e:
                    logger.debug(f"Could not process tag {tag_name}: {e}")
                    continue

            logger.info(f"Collected {len(versions_data)} versions for {package_name} from conda-forge")

            return {
                'package': package_name,
                'source': 'conda-forge',
                'feedstock': feedstock_repo,
                'collection_date': datetime.now().isoformat(),
                'versions': versions_data
            }

        except Exception as e:
            logger.error(f"Failed to collect conda-forge data for {package_name}: {e}")
            return {'package': package_name, 'source': 'conda-forge', 'error': str(e), 'versions': []}

    def _parse_meta_yaml_dependencies(self, meta_yaml_content: str) -> List[str]:
        """Simple parser for extracting dependencies from meta.yaml."""
        dependencies = set()
        in_run_section = False

        for line in meta_yaml_content.split('\n'):
            stripped = line.strip()

            # Look for run requirements section
            if 'run:' in stripped:
                in_run_section = True
                continue

            # Exit run section when we hit another section
            if in_run_section and stripped and not stripped.startswith('-') and not stripped.startswith('#'):
                in_run_section = False

            # Extract dependencies from run section
            if in_run_section and stripped.startswith('-'):
                dep = stripped[1:].strip()
                # Remove version specifiers
                dep_name = dep.split()[0].split('=')[0].split('>')[0].split('<')[0].strip()
                if dep_name and not dep_name.startswith('{{'):  # Skip Jinja2 template variables
                    dependencies.add(dep_name)

        return list(dependencies)

    def collect_all_packages(self, packages: List[str]) -> None:
        """Collect data for all specified packages."""
        for package in packages:
            source = PACKAGE_SOURCES.get(package)

            if not source:
                logger.warning(f"No source mapping for package {package}, skipping")
                continue

            if source == 'pypi':
                data = self.collect_pypi_data(package)
                output_file = self.output_dir / 'pypi_metadata' / f'{package}_versions.json'
            elif source == 'conda-forge':
                data = self.collect_conda_forge_data(package)
                output_file = self.output_dir / 'conda_forge_metadata' / f'{package}_meta.json'
            else:
                logger.warning(f"Unknown source {source} for {package}")
                continue

            # Save to file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved data to {output_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect historical dependency data for scientific Python packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect data for all default packages
  python collect_dependency_data.py

  # Collect data for specific packages
  python collect_dependency_data.py --packages numpy scipy matplotlib

  # Use GitHub token for higher rate limits
  python collect_dependency_data.py --github-token YOUR_TOKEN
        """
    )

    parser.add_argument(
        '--packages',
        nargs='+',
        default=list(PACKAGE_SOURCES.keys()),
        help='Packages to collect data for (default: all configured packages)'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'raw' / 'software_complexity',
        help='Output directory for collected data'
    )

    parser.add_argument(
        '--github-token',
        type=str,
        help='GitHub personal access token for higher API rate limits'
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

    logger.info(f"Collecting dependency data for packages: {', '.join(args.packages)}")
    logger.info(f"Output directory: {args.output_dir}")

    collector = DependencyDataCollector(args.output_dir, args.github_token)
    collector.collect_all_packages(args.packages)

    logger.info("Data collection complete!")


if __name__ == '__main__':
    main()