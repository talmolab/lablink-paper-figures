# Add Scientific Software Complexity Over Time Figure

## Why

Scientific software has grown increasingly complex over the past two decades, with modern packages accumulating hundreds of dependencies. This complexity affects reproducibility, maintenance burden, and highlights the need for tools like LabLink that provide controlled computational environments. A figure showing dependency growth over time provides empirical evidence for these trends and contextualizes the LabLink contribution within the broader scientific computing landscape.

## What Changes

- Add new capability `software-complexity-analysis` for collecting and analyzing dependency data from scientific Python packages
- Create data collection script to gather historical dependency counts using conda-forge feedstocks (for compiled packages) and PyPI API (for pure-Python packages), with GitHub validation
- Implement visualization script that generates publication-quality time-series plots showing dependency growth
- Support configurable output formats (paper, poster, presentation) with appropriate font sizes and DPI
- Track 8-10 representative scientific packages spanning 2000-2025 across multiple domains (core scientific stack, modern ML, domain-specific tools)
- Generate both main figure (aggregate trends) and supplementary figures (per-package breakdowns)
- Use source-specific data collection strategy optimized for scientific software accuracy (conda-forge captures system dependencies that PyPI omits)

## Impact

- **Affected specs**: Creates new capability `software-complexity-analysis`
- **Affected code**:
  - New: `scripts/analysis/collect_dependency_data.py` - Data collection from conda-forge and PyPI
  - New: `scripts/plotting/plot_software_complexity.py` - Figure generation with configurability
  - New: `data/raw/software_complexity/conda_forge_metadata/` - conda-forge metadata JSONs
  - New: `data/raw/software_complexity/pypi_metadata/` - PyPI version metadata JSONs
  - New: `data/raw/software_complexity/github_validation/` - GitHub validation data
  - New: `data/processed/software_complexity/` - Cleaned time-series data
  - New: `figures/main/software_complexity_over_time.*` - Main figure outputs
  - New: `figures/supplementary/software_complexity_breakdown.*` - Per-package details
- **Dependencies**: Requires `requests` for API calls, `pandas` for data processing, `matplotlib`/`seaborn` for visualization, `pyyaml` for parsing conda-forge meta.yaml files (all already in project or trivial to add)
- **Data sources**:
  - conda-forge feedstock repositories (public GitHub repos, no auth required)
  - PyPI JSON API (public, no auth required)
  - GitHub API for validation (public, optional token for higher rate limits)