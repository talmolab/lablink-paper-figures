# Analysis Figures (8+ figures)

This directory documents the analysis and motivation figures supporting the LabLink paper. These figures demonstrate the need for LabLink through software complexity analysis, GPU cost trends, dependency visualization, and deployment impact assessment.

## Overview

Analysis figures are generated from data analysis, external datasets, and API calls (PyPI, conda-forge, Epoch AI, GitHub). Unlike architecture diagrams which parse Terraform, these figures require data collection and processing steps.

**Scripts location**: `scripts/plotting/` and `scripts/analysis/`
**Output location**: `figures/main/` and `figures/supplementary/`

## The 8+ Figure Types

### 1. Software Complexity Over Time
**Script**: `plot_software_complexity.py`
**Purpose**: Show exponential growth in scientific software dependencies (2000-2025) motivating need for reproducible environments

**Data source**: PyPI API, conda-forge feedstocks, GitHub
**Packages analyzed**: NumPy, SciPy, matplotlib, pandas, TensorFlow, PyTorch, scikit-learn, AstroPy, Jupyter

**Workflow**:
```bash
# 1. Collect data (20-40 minutes)
cd scripts/analysis
uv run python collect_dependency_data.py --github-token YOUR_TOKEN

# 2. Process data
uv run python process_dependency_data.py

# 3. Generate figure
cd ../plotting
uv run python plot_software_complexity.py --preset paper --format both
```

[Full documentation](software-complexity.md)

---

### 2. SLEAP Dependency Network
**Script**: `generate_sleap_dependency_graph.py`
**Purpose**: Visualize complexity of computational research software through SLEAP's dependency network

**Data source**: PyPI JSON API (transitive dependency resolution)
**Visualization**: Network graph with degree centrality sizing, categorical coloring

**Quick start**:
```bash
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --sleap-source ../sleap \
  --preset paper \
  --format pdf
```

[Full documentation](sleap-dependencies.md)

---

### 3. GPU Cost Trends
**Script**: `plot_gpu_cost_trends.py`
**Purpose**: Demonstrate sustained high cost of GPU hardware (2006-2025) motivating cloud-based access

**Data source**: Epoch AI Machine Learning Hardware Database (CC BY 4.0)
**Coverage**: 160+ GPUs with pricing and performance metrics

**Data setup**:
1. Download from https://epoch.ai/data/machine-learning-hardware
2. Extract to `data/raw/gpu_prices/ml_hardware.csv`

**Generate**:
```bash
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset poster --include-performance
```

[Full documentation](gpu-costs.md)

---

### 4. Deployment Impact Timeline
**Script**: `plot_deployment_impact.py`
**Purpose**: Show LabLink deployment history and workshop impact

**Data source**: `data/processed/deployment_impact/workshops.csv`

**Generate**:
```bash
uv run python scripts/plotting/plot_deployment_impact.py --preset paper
```

[Full documentation](deployment-impact.md)

---

### 5. OS Distribution Analysis
**Script**: `plot_os_distribution.py`
**Purpose**: Analyze operating system distribution in computational research

**Data source**: TBD (survey data, GitHub, conda-forge)

**Generate**:
```bash
uv run python scripts/plotting/plot_os_distribution.py --preset paper
```

[Full documentation](os-distribution.md)

---

### 6. GPU Reliance Scoring
**Script**: `plot_gpu_reliance.py`
**Purpose**: Score Python packages by GPU dependency level (0-5 scale)

**Data source**: PyPI requires_dist metadata
**Scoring methodology**:
- 0: No GPU support
- 1-2: Optional GPU acceleration
- 3-4: GPU-recommended
- 5: GPU-first packages (CuPy, Numba)

**Generate**:
```bash
uv run python scripts/plotting/plot_gpu_reliance.py --preset paper
```

[Full documentation](gpu-reliance.md)

---

### 7. Configuration Hierarchy
**Script**: `plot_configuration_hierarchy.py`, `plot_configuration_hierarchy_simple.py`
**Purpose**: Visualize LabLink's hierarchical configuration system

**Data source**: Analysis of `config.yaml` structure

**Generate**:
```bash
# Detailed version
uv run python scripts/plotting/plot_configuration_hierarchy.py --preset poster

# Simple version
uv run python scripts/plotting/plot_configuration_hierarchy_simple.py --preset paper
```

[Full documentation](configuration-hierarchy.md)

---

### 8. QR Codes
**Script**: `generate_qr_codes.py`
**Purpose**: Generate QR codes for demo access, GitHub repos, documentation

**Generate**:
```bash
uv run python scripts/plotting/generate_qr_codes.py
```

[Full documentation](qr-codes.md)

---

## Common Patterns

### Font Size Presets
All scripts support consistent presets:

```bash
--preset paper          # 14pt fonts, 300 DPI, ~6.5" width
--preset poster         # 20pt fonts, 300 DPI, ~12" width
--preset presentation   # 16pt fonts, 150 DPI, 10"x7.5"
```

### Output Formats
```bash
--format png      # Default, 300 DPI raster
--format pdf      # Vector for LaTeX
--format svg      # Vector for web/presentations
--format both     # PNG + PDF
```

### Output Location
```bash
--output figures/main           # Main text figures
--output figures/supplementary  # Supplementary figures
```

### Verbose Logging
```bash
--verbose  # or -v for detailed logging
```

## Data Collection Workflow

Some figures require multi-step data collection:

### 1. Software Complexity
```bash
scripts/analysis/collect_dependency_data.py    # Fetch from APIs (20-40 min)
scripts/analysis/process_dependency_data.py    # Clean and aggregate
scripts/plotting/plot_software_complexity.py   # Visualize
```

### 2. SLEAP Dependencies
```bash
# Auto-fetches and caches on first run
scripts/plotting/generate_sleap_dependency_graph.py
# Uses cached data on subsequent runs
```

### 3. GPU Cost Trends
```bash
# Manual download required
# 1. Visit https://epoch.ai/data/machine-learning-hardware
# 2. Download ml_hardware.csv to data/raw/gpu_prices/
scripts/plotting/plot_gpu_cost_trends.py
```

## Data Sources Summary

| Figure | Data Source | Collection Method | Cache Location |
|--------|-------------|-------------------|----------------|
| Software Complexity | PyPI, conda-forge, GitHub | `collect_dependency_data.py` | `data/processed/dependency_data.csv` |
| SLEAP Dependencies | PyPI JSON API | Auto-fetch on first run | `data/processed/sleap_dependencies.json` |
| GPU Costs | Epoch AI dataset | Manual download | `data/raw/gpu_prices/ml_hardware.csv` |
| Deployment Impact | Manual curation | CSV file | `data/processed/deployment_impact/workshops.csv` |
| OS Distribution | TBD | TBD | TBD |
| GPU Reliance | PyPI metadata | Part of software complexity | Uses processed data |
| Configuration | Code analysis | Static analysis | N/A |
| QR Codes | URLs | Encode to QR | `figures/main/qr-*.png` |

## Caching and Refresh

Most scripts cache API responses to avoid repeated network calls:

```bash
# Use cached data (default)
uv run python scripts/plotting/<script>.py

# Force refresh from APIs
uv run python scripts/plotting/<script>.py --force-refresh
```

## Environment Variables

Optional convenience variables:

```bash
# SLEAP dependencies
export SLEAP_PATH=../sleap

# GitHub API (higher rate limits)
export GITHUB_TOKEN=ghp_your_token_here
```

## Metadata Files

All scripts generate metadata files documenting:
- Data sources (URLs, API endpoints)
- Generation timestamp
- Package versions
- Data statistics (counts, date ranges)
- Parameters used

**Example**: `software_complexity_metadata.txt`, `gpu_cost_trends-metadata.txt`

## Troubleshooting

**API rate limits**:
```bash
# Set GitHub token for higher limits
export GITHUB_TOKEN=ghp_your_token_here
```

**Missing data files**:
```bash
# Check data/ subdirectory READMEs for download instructions
ls data/raw/*/README.md
```

**Slow data collection**:
```bash
# Use cached data (don't use --force-refresh unless needed)
# Expected times:
# - Software complexity: 20-40 minutes first run
# - SLEAP dependencies: 1-2 minutes first run
# - GPU costs: <1 minute (pre-downloaded dataset)
```

**Font size issues**:
```bash
# For large-format posters, use poster preset
--preset poster  # 20pt fonts, 43% larger

# Test at actual print dimensions
```

## Examples

### Generate All Analysis Figures for Paper
```bash
# Software complexity
uv run python scripts/plotting/plot_software_complexity.py --preset paper --format both

# SLEAP dependencies
uv run python scripts/plotting/generate_sleap_dependency_graph.py --preset paper --format pdf

# GPU costs
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset paper --format both

# Deployment impact
uv run python scripts/plotting/plot_deployment_impact.py --preset paper --format both

# OS distribution
uv run python scripts/plotting/plot_os_distribution.py --preset paper --format both

# GPU reliance
uv run python scripts/plotting/plot_gpu_reliance.py --preset paper --format both

# Configuration hierarchy
uv run python scripts/plotting/plot_configuration_hierarchy_simple.py --preset paper --format both

# QR codes
uv run python scripts/plotting/generate_qr_codes.py
```

### Generate for Poster Presentation
```bash
# Use poster preset for all figures
uv run python scripts/plotting/plot_software_complexity.py --preset poster --format pdf
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset poster --include-performance --format pdf
uv run python scripts/plotting/generate_sleap_dependency_graph.py --preset poster --format pdf
```

## Related Documentation

- [Architecture Diagrams](../architecture-diagrams/README.md) - Infrastructure visualization
- [Data Directory READMEs](../../../data/README.md) - Data sources and formats
- [Getting Started](../../getting-started.md) - Installation and setup
- Main [README.md](../../../README.md) - Repository overview

## Recent Updates

- Added QR code generation
- Added configuration hierarchy visualization
- Fixed GPU reliance scoring bug (see `docs/archived/gpu-reliance-bug-2025-11.md`)
- Added deployment impact timeline
- Improved font preset consistency across all scripts
