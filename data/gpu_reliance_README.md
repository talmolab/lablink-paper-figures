# GPU Hardware Reliance Data

## Overview

This directory contains data tracking the evolution of GPU hardware dependencies in scientific Python packages from 2010-2025. The analysis demonstrates how GPU requirements have transitioned from optional acceleration to practical necessities for many computational workflows.

## Data Sources

### Primary: PyPI JSON API

- **URL**: `https://pypi.org/pypi/{package}/json`
- **Rationale**: Consistent historical metadata, no rate limits, proven reliability
- **Coverage**: All package versions with release dates and dependency information
- **Limitations**: PyPI `requires_dist` may not capture all GPU requirements (some packages bundle CUDA in wheels)

### Validation: GitHub Repositories

- **Purpose**: Manual validation of 20-30 key milestone versions
- **Method**: Review release notes, documentation, and CUDA file history
- **Stored in**: `raw/gpu_reliance/github_validation/validation_log.csv`

## GPU Dependency Scoring System

Each package version receives a GPU dependency score from 0-5:

| Score | Category | Definition | Examples |
|-------|----------|------------|----------|
| **0** | No GPU | No GPU support whatsoever | scikit-image < 0.25 |
| **1** | Optional | GPU support available but entirely optional | Numba with CUDA extras |
| **2** | Recommended | Works without GPU but severe performance degradation | Early ML frameworks |
| **3** | Practical Required | Technically optional but unusable without GPU for real workloads | TensorFlow 2.x, PyTorch |
| **4** | Hard Required | Installation or core features fail without CUDA/GPU libraries | JAX (requires external CUDA) |
| **5** | GPU-First | Designed exclusively for GPU, no CPU fallback | CuPy, Rapids cuDF |

## Packages Tracked

### Machine Learning / Deep Learning (6 packages)
- **TensorFlow** (+ tensorflow-gpu pre-2.1): Industry-standard, separate GPU package until 2.1.0
- **PyTorch** (torch): Research-focused, GPU bundled from start
- **JAX** (+jaxlib): Modern GPU-first design, requires external CUDA
- **Numba**: JIT compiler, optional CUDA support

### Scientific Computing (7 packages)
- **CuPy** (+ cuda-specific variants): NumPy-compatible GPU arrays, GPU-first design
- **Rapids cuDF**: GPU DataFrame library
- **scikit-image**: Example of CPU-only package transitioning to optional GPU

### Molecular Dynamics / Bioinformatics (2 packages)
- **OpenMM**: Built with GPU from inception (2010)
- **AlphaFold**: Modern AI requiring high-end GPUs

**Total**: 15 package variants aggregated into ~10 base packages

## Directory Structure

```
gpu_reliance/
├── raw/
│   ├── pypi_metadata/           # Raw PyPI JSON responses
│   │   ├── tensorflow_versions.json
│   │   ├── torch_versions.json
│   │   ├── cupy_versions.json
│   │   └── ...
│   └── github_validation/       # Manual validation data
│       └── validation_log.csv
└── processed/
    ├── gpu_timeseries.csv      # Clean time-series data
    ├── quality_report.txt       # Data quality summary
    └── source_attribution.csv   # Data source breakdown
```

## Data Collection

### Prerequisites
- Python 3.10+
- `requests` library
- Internet connection
- (Optional) GitHub personal access token for validation

### Running Data Collection

```bash
cd scripts/analysis

# Collect all packages (20-40 minutes)
uv run python collect_gpu_data.py --verbose

# Collect specific packages only
uv run python collect_gpu_data.py --packages tensorflow torch cupy

# Use GitHub token for validation (optional)
uv run python collect_gpu_data.py --github-token YOUR_TOKEN
```

###  Output

- Raw JSON files in `data/raw/gpu_reliance/pypi_metadata/`
- Each file contains all versions for one package with GPU metadata

## Data Processing

### Running Processing

```bash
cd scripts/analysis

# Process with default settings
uv run python process_gpu_data.py --verbose

# Custom minimum data points threshold
uv run python process_gpu_data.py --min-points 10
```

### Processing Steps

1. **Load raw JSON files** from PyPI metadata directory
2. **Normalize package variants**:
   - `cupy-cuda102`, `cupy-cuda110`, etc. → `cupy`
   - `tensorflow-gpu` → `tensorflow` (marked as separate variant pre-2.1)
3. **Filter low-quality data**: Exclude packages with <5 versions
4. **Generate outputs**:
   - `gpu_timeseries.csv`: Clean time-series data
   - `quality_report.txt`: Data quality summary
   - `source_attribution.csv`: Package counts by source

### Output Schema

**gpu_timeseries.csv columns:**
- `package`: Normalized package name
- `version`: Version string
- `date`: Release date (ISO format)
- `gpu_score`: GPU dependency score (0-5)
- `cuda_version`: Minimum CUDA version required (if specified)
- `gpu_deps_count`: Count of GPU-related dependencies
- `requires_external_cuda`: Boolean, True if CUDA not bundled
- `source`: Data source (always 'pypi')

## Methodology Notes

### Scoring Logic

**Automatic detection:**
- Score 0: No GPU keywords in dependencies
- Score 5: Package in `GPU_FIRST_PACKAGES` list (CuPy, cuDF, etc.)
- Score 4: Has required CUDA dependencies (not in extras)
- Score 3: Known to bundle CUDA (TensorFlow 2.x, PyTorch, JAX)
- Score 1-2: GPU keywords in extras or optional dependencies

**Manual refinement:**
- 20-30 key milestone versions reviewed via GitHub
- Documentation, release notes, and CUDA file history examined
- Scores adjusted based on actual installation requirements

### Package Variant Handling

**CuPy variants:**
- Historical: Separate PyPI packages per CUDA version
- `cupy-cuda102` (CUDA 10.2)
- `cupy-cuda110` (CUDA 11.0)
- `cupy-cuda11x` (CUDA 11.x)
- `cupy-cuda12x` (CUDA 12.x)
- Modern (v13+): Unified `cupy` package
- **Aggregation**: All variants merged into base `cupy` timeline

**TensorFlow variants:**
- Pre-2.1 (2016-2019): Separate `tensorflow` and `tensorflow-gpu` packages
- Post-2.1 (2020+): Unified `tensorflow` with bundled GPU support
- **Aggregation**: Both tracked, unification point annotated

### Known Limitations

1. **PyPI metadata coverage**: Some early versions have `requires_dist: null`
2. **Bundled CUDA detection**: Packages that ship CUDA in wheels may not declare it in dependencies
3. **Performance vs. requirement**: Distinguishing "recommended" from "required" is subjective
4. **External CUDA**: Some packages require system CUDA installation not reflected in metadata

### Validation

- **Date verification**: Cross-check PyPI dates against GitHub release tags
- **Spot-checking**: Manually verify 5-10 versions by actual installation
- **Expert review**: Have domain experts validate scoring for ambiguous cases

## Reproducibility

### Full Reproduction

```bash
# From repository root
cd scripts/analysis

# Step 1: Collect data (20-40 min)
uv run python collect_gpu_data.py --verbose

# Step 2: Process data (< 1 min)
uv run python process_gpu_data.py --verbose

# Step 3: Generate figures (< 1 min)
cd ../plotting
uv run python plot_gpu_reliance.py --format paper --verbose
```

### Expected Output

- **Data points**: 500-1000 total across all packages
- **Time span**: 2010-2025 (varies by package)
- **Packages included**: 8-10 after filtering (<5 version threshold)

## Citation

When using this data, cite:
- **Data source**: PyPI JSON API (https://pypi.org)
- **Collection date**: [See `gpu_reliance_metadata.txt` in figures/]
- **Methodology**: GPU dependency scoring (0-5 scale) based on PyPI metadata
- **Scope**: Direct Python dependencies only; does not capture system libraries or bundled CUDA

## Contact

For questions about data collection methodology or validation procedures, see the main repository README or open an issue.
