# Add OS Distribution Pie Chart Figure

## Why

Operating system distribution data provides important context for understanding the computational environment requirements and accessibility of LabLink. Showing that 67% of users run Windows, 19% Linux, and 14% Mac demonstrates the cross-platform nature of modern scientific computing workflows and validates LabLink's design decision to support all major operating systems. This simple, clear visualization complements the technical figures (GPU reliance, software complexity) by grounding the paper in real user demographics.

## What Changes

- Add new capability `os-distribution-analysis` for creating a publication-quality pie chart visualization
- Implement simple data structure with hardcoded OS percentages: Windows 67%, Linux 19%, Mac 14%
- Create plotting script matching the visual style of existing figures (GPU reliance, software complexity)
- Support paper and poster format presets with appropriate sizing and DPI settings
- Follow the same architectural patterns and folder structure as other plotting scripts for consistency
- Generate PNG and PDF outputs following the same naming conventions

## Impact

- **Affected specs**: Creates new capability `os-distribution-analysis`
- **Affected code**:
  - New: `scripts/plotting/plot_os_distribution.py` - Pie chart generation with paper/poster presets
  - New: `data/processed/os_distribution/os_stats.csv` - Simple CSV with OS percentages
  - New: `figures/main/os_distribution.*` - Main figure outputs (PNG + PDF)
- **Dependencies**: Reuses existing dependencies (`matplotlib`, `seaborn`, `pandas`) - no new packages needed
- **Consistency with existing work**: Mirrors the format preset architecture and command-line interface from `plot_gpu_reliance.py` and `plot_software_complexity.py` for maintainability
