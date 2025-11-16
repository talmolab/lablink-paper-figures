#!/usr/bin/env python3
"""Collect historical GPU dependency data for scientific Python packages.

This script collects GPU-related metadata from PyPI to track the evolution
of GPU hardware dependencies in scientific software from 2010-2025.
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# GPU-related package mapping
GPU_PACKAGES = {
    # Machine Learning / Deep Learning
    'tensorflow': 'pypi',
    'tensorflow-gpu': 'pypi',  # Separate package until TF 2.1
    'torch': 'pypi',
    'jax': 'pypi',
    'jaxlib': 'pypi',
    'numba': 'pypi',

    # Scientific Computing
    'cupy': 'pypi',
    'cupy-cuda102': 'pypi',
    'cupy-cuda110': 'pypi',
    'cupy-cuda11x': 'pypi',
    'cupy-cuda12x': 'pypi',
    'cudf': 'pypi',
    'scikit-image': 'pypi',

    # Molecular Dynamics / Biology
    'openmm': 'pypi',
    'alphafold': 'pypi',
}

# GPU-first packages (score 5)
GPU_FIRST_PACKAGES = ['cupy', 'cucim', 'cudf', 'rapids', 'cuml', 'cugraph']

# Packages that bundle CUDA (score 3)
BUNDLED_CUDA_PACKAGES = ['tensorflow', 'torch', 'jax']

# Packages with optional GPU support not declared in PyPI metadata (score 2)
OPTIONAL_GPU_PACKAGES = ['numba']

# Molecular dynamics packages with GPU as practical requirement (score 4)
# These don't declare CUDA in PyPI but GPU is essential for usability
MD_GPU_PACKAGES = ['openmm']

# GPU-related keywords for detection
GPU_KEYWORDS = ['cuda', 'cudnn', 'gpu', 'nvidia', 'cupy', 'opencl', 'rocm']


class GPUDataCollector:
    """Collects GPU dependency data from PyPI."""

    def __init__(self, output_dir: Path, github_token: Optional[str] = None):
        self.output_dir = output_dir
        self.github_token = github_token
        self.session = requests.Session()
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})

    def collect_pypi_gpu_data(self, package_name: str) -> Dict:
        """Collect GPU-related metadata from PyPI JSON API."""
        logger.info(f"Collecting GPU data for {package_name}...")

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

                # Get version-specific metadata for GPU dependency info
                try:
                    version_response = self.session.get(
                        f'https://pypi.org/pypi/{package_name}/{version}/json'
                    )
                    version_response.raise_for_status()
                    version_data = version_response.json()

                    requires_dist = version_data['info'].get('requires_dist', []) or []

                    # Extract GPU-related dependencies
                    gpu_deps = self._extract_gpu_dependencies(requires_dist)

                    # Calculate GPU score
                    gpu_score = self._calculate_gpu_score(
                        requires_dist=requires_dist,
                        package_name=package_name,
                        version=version
                    )

                    # Extract CUDA version requirement
                    cuda_version = self._extract_cuda_version(requires_dist)

                    # Check if requires external CUDA installation
                    requires_external_cuda = self._check_external_cuda_required(
                        package_name, version, requires_dist
                    )

                    versions_data.append({
                        'version': version,
                        'date': upload_time,
                        'gpu_score': gpu_score,
                        'cuda_version': cuda_version,
                        'gpu_dependencies': gpu_deps,
                        'gpu_deps_count': len(gpu_deps),
                        'requires_external_cuda': requires_external_cuda
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

    def _extract_gpu_dependencies(self, requires_dist: List[str]) -> List[str]:
        """Extract GPU-related dependencies from requires_dist."""
        gpu_deps = set()

        for req in (requires_dist or []):
            if req:
                # Extract package name before version specifier
                dep_name = req.split('[')[0].split(';')[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()

                # Check if GPU-related
                if any(kw in dep_name.lower() for kw in GPU_KEYWORDS):
                    gpu_deps.add(dep_name)

        return list(gpu_deps)

    def _calculate_gpu_score(self, requires_dist: List[str], package_name: str, version: str) -> int:
        """Calculate GPU dependency score (0-5) for package version.

        Score rubric:
        0: No GPU support
        1: Optional GPU (in extras)
        2: Recommended GPU (performance degradation without)
        3: Practical Required (bundled CUDA, unusable without GPU)
        4: Hard Required (installation fails without CUDA)
        5: GPU-First (designed exclusively for GPU)
        """
        # Convert to lowercase for matching
        deps_lower = [dep.lower() for dep in (requires_dist or [])]
        all_deps = ' '.join(deps_lower)

        # Score 5: Known GPU-first packages (check FIRST before keyword checks)
        # These packages bundle CUDA and may not declare it in PyPI metadata
        base_package = package_name.split('-')[0]  # Handle cupy-cuda* variants
        if any(pkg in base_package.lower() for pkg in GPU_FIRST_PACKAGES):
            return 5

        # Score 4: MD packages with GPU as practical requirement
        # Don't declare CUDA in PyPI but GPU is essential for usability
        if any(pkg in package_name.lower() for pkg in MD_GPU_PACKAGES):
            return 4

        # Score 2: Packages with optional GPU support not in PyPI metadata
        # (check before GPU keyword check since they may not declare deps)
        if any(pkg in package_name.lower() for pkg in OPTIONAL_GPU_PACKAGES):
            return 2

        # Score 0: No GPU keywords (check AFTER special package lists)
        if not any(kw in all_deps for kw in GPU_KEYWORDS):
            return 0

        # Score 4: Hard GPU requirements (cudatoolkit in required deps)
        required_cuda_packages = ['cudatoolkit', 'nvidia-cuda']
        if any(pkg in all_deps for pkg in required_cuda_packages):
            # Check if it's NOT in extras_require
            if 'extra' not in all_deps:
                return 4

        # Score 3: Bundled CUDA packages (TensorFlow 2.x, PyTorch)
        if any(pkg in package_name.lower() for pkg in BUNDLED_CUDA_PACKAGES):
            # TensorFlow unified GPU support starting from 2.1.0
            if 'tensorflow' in package_name.lower() and 'tensorflow-gpu' not in package_name.lower():
                try:
                    from packaging import version as pkg_version
                    if pkg_version.parse(version) >= pkg_version.parse('2.1.0'):
                        return 3
                except:
                    pass
            elif 'torch' in package_name.lower() or 'jax' in package_name.lower():
                return 3

        # Score 2-3: TensorFlow-GPU (separate package, practical requirement)
        if 'tensorflow-gpu' in package_name.lower():
            return 3

        # Score 1-2: Optional GPU (in extras or recommended)
        if 'extra' in all_deps or 'optional' in all_deps:
            return 1

        # Score 1: GPU mentioned but unclear
        return 1

    def _extract_cuda_version(self, requires_dist: List[str]) -> Optional[str]:
        """Extract minimum CUDA version requirement from dependencies."""
        for dep in (requires_dist or []):
            # Match patterns like: cudatoolkit >=11.2, nvidia-cuda-runtime-cu11
            match = re.search(r'cuda.*?([0-9]+\.[0-9]+)', dep, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _check_external_cuda_required(self, package_name: str, version: str, requires_dist: List[str]) -> bool:
        """Check if package requires external CUDA installation (not bundled)."""
        # Packages known to bundle CUDA in wheels (no external install needed)
        bundled_cuda = ['tensorflow', 'torch']
        if any(pkg in package_name.lower() for pkg in bundled_cuda):
            # TensorFlow started bundling CUDA in 2.x
            if 'tensorflow' in package_name.lower():
                try:
                    from packaging import version as pkg_version
                    if pkg_version.parse(version) >= pkg_version.parse('2.0.0'):
                        return False  # Bundled
                except:
                    pass
            else:
                return False  # PyTorch bundles CUDA

        # JAX, Numba, CuPy require external CUDA
        external_cuda_packages = ['jax', 'numba', 'cupy']
        if any(pkg in package_name.lower() for pkg in external_cuda_packages):
            return True

        # Check if cudatoolkit is in dependencies
        deps_lower = ' '.join([dep.lower() for dep in (requires_dist or [])])
        if 'cudatoolkit' in deps_lower or 'nvidia-cuda' in deps_lower:
            return True

        return False

    def collect_all_packages(self, packages: List[str]) -> None:
        """Collect GPU data for all specified packages."""
        for package in packages:
            source = GPU_PACKAGES.get(package)

            if not source:
                logger.warning(f"No source mapping for package {package}, skipping")
                continue

            if source == 'pypi':
                data = self.collect_pypi_gpu_data(package)
                output_file = self.output_dir / 'pypi_metadata' / f'{package}_versions.json'
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
        description="Collect historical GPU dependency data for scientific Python packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect data for all default packages
  python collect_gpu_data.py

  # Collect data for specific packages
  python collect_gpu_data.py --packages tensorflow torch cupy

  # Use GitHub token for higher rate limits (optional)
  python collect_gpu_data.py --github-token YOUR_TOKEN
        """
    )

    parser.add_argument(
        '--packages',
        nargs='+',
        default=list(GPU_PACKAGES.keys()),
        help='Packages to collect GPU data for (default: all configured packages)'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'data' / 'raw' / 'gpu_reliance',
        help='Output directory for collected data'
    )

    parser.add_argument(
        '--github-token',
        type=str,
        help='GitHub personal access token for higher API rate limits (optional)'
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

    logger.info(f"Collecting GPU dependency data for packages: {', '.join(args.packages)}")
    logger.info(f"Output directory: {args.output_dir}")

    collector = GPUDataCollector(args.output_dir, args.github_token)
    collector.collect_all_packages(args.packages)

    logger.info("GPU data collection complete!")


if __name__ == '__main__':
    main()