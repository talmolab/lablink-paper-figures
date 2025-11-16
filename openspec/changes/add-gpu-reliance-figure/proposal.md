# Add GPU Hardware Reliance in Scientific Software Figure

## Why

Scientific software has become increasingly dependent on GPU hardware over the past 15 years, transforming from optional acceleration to practical requirements for many computational workflows. This GPU dependency creates significant reproducibility and accessibility challenges: code that requires high-end GPUs cannot run on standard hardware, cloud costs escalate, and reproducibility suffers when specific GPU configurations are needed. A figure showing GPU reliance growth over time empirically demonstrates these hardware dependencies and strengthens the case for managed computational environments like LabLink that abstract hardware provisioning.

## What Changes

- Add new capability `gpu-reliance-analysis` for collecting and analyzing GPU dependency evolution in scientific Python packages
- Create data collection script to gather historical GPU dependency metadata using PyPI JSON API (primary) with GitHub validation for milestone versions
- Implement GPU dependency scoring system (0-5 scale) to quantify reliance levels from "no GPU support" to "GPU-first design"
- Track CUDA version requirements, GPU-specific package variants, and installation complexity over time
- Implement visualization script matching the style of `plot_software_complexity.py` with configurable formats (paper, poster, presentation)
- Track 10 representative scientific packages spanning 2010-2025 across multiple domains (ML/deep learning, scientific computing, molecular dynamics, bioinformatics)
- Generate both main figure (all packages showing GPU score evolution) and category comparison (faceted by domain)
- Follow the same architectural patterns and folder structure as the software complexity figure for consistency

## Impact

- **Affected specs**: Creates new capability `gpu-reliance-analysis`
- **Affected code**:
  - New: `scripts/analysis/collect_gpu_data.py` - GPU dependency data collection from PyPI
  - New: `scripts/analysis/process_gpu_data.py` - Data processing pipeline for GPU metrics
  - New: `scripts/plotting/plot_gpu_reliance.py` - Figure generation with paper/poster/presentation presets
  - New: `data/raw/gpu_reliance/pypi_metadata/` - PyPI metadata JSONs per package
  - New: `data/raw/gpu_reliance/github_validation/` - Manual validation data for key milestones
  - New: `data/processed/gpu_reliance/` - Cleaned time-series data with GPU scores
  - New: `figures/main/gpu_reliance_over_time.*` - Main figure outputs (PNG + PDF)
  - New: `figures/main/gpu_reliance_by_category.*` - Category comparison (PNG + PDF)
  - New: `data/gpu_reliance_README.md` - Methodology documentation
- **Dependencies**: Reuses existing dependencies (`requests`, `pandas`, `matplotlib`, `seaborn`) - no new packages needed
- **Data sources**:
  - PyPI JSON API (primary, public, no auth required) - proven reliable from software complexity implementation
  - GitHub repository analysis (validation only, optional token for higher rate limits)
- **Consistency with existing work**: Mirrors the architecture and code patterns from `add-software-complexity-figure` for maintainability