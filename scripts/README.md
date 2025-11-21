# Scripts Directory

This directory contains Python scripts for data processing, analysis, and figure generation.

## Directory Structure

```
scripts/
├── analysis/         # Data collection and processing scripts
│   ├── collect_dependency_data.py     # Fetch PyPI/conda-forge metadata
│   ├── process_dependency_data.py     # Clean and aggregate dependency data
│   └── ...
└── plotting/         # Figure generation scripts (10 scripts)
    ├── generate_architecture_diagram.py      # 12 Terraform-based diagrams
    ├── generate_sleap_dependency_graph.py    # SLEAP dependency network
    ├── generate_qr_codes.py                   # QR codes for demos
    ├── plot_software_complexity.py            # Dependency growth over time
    ├── plot_gpu_cost_trends.py                # GPU pricing trends
    ├── plot_gpu_reliance.py                   # GPU dependency scoring
    ├── plot_deployment_impact.py              # Workshop timeline
    ├── plot_os_distribution.py                # OS analysis
    ├── plot_configuration_hierarchy.py        # LabLink config visualization
    └── plot_configuration_hierarchy_simple.py # Simplified config diagram
```

## Script Categories

### Analysis Scripts (`scripts/analysis/`)

**Purpose**: Collect and process raw data for analysis figures.

Data collection and processing with caching, API rate limiting, and validation.

**Example workflow**:
```bash
cd scripts/analysis
uv run python collect_dependency_data.py --github-token YOUR_TOKEN
uv run python process_dependency_data.py
# Output: data/processed/dependency_data.csv
```

### Plotting Scripts (`scripts/plotting/`)

**Purpose**: Generate publication-quality figures with consistent styling.

All scripts support:
- `--preset {paper|poster|presentation}` - Font size presets
- `--format {png|pdf|svg|both|all}` - Output formats
- `--output-dir` - Output location
- `--verbose` - Debug logging

**Example**:
```bash
cd scripts/plotting
uv run python plot_gpu_cost_trends.py --preset poster --format pdf
```

## Common Usage Patterns

### Font Size Presets
```bash
--preset paper          # 14pt fonts (default)
--preset poster         # 20pt fonts (large format)
--preset presentation   # 16pt fonts (slides)
```

### Output Formats
```bash
--format png      # 300 DPI raster (default)
--format pdf      # Vector for LaTeX
--format both     # PNG + PDF
--format all      # PNG + PDF + SVG
```

### Environment Variables
```bash
export LABLINK_TERRAFORM_DIR=../lablink-template/lablink-infrastructure
export SLEAP_PATH=../sleap
export GITHUB_TOKEN=ghp_your_token
```

## All Plotting Scripts

1. **generate_architecture_diagram.py** - 12 Terraform-based infrastructure diagrams
2. **generate_sleap_dependency_graph.py** - SLEAP dependency network
3. **generate_qr_codes.py** - QR codes for demos
4. **plot_software_complexity.py** - Dependency growth (2000-2025)
5. **plot_gpu_cost_trends.py** - GPU pricing trends (2006-2025)
6. **plot_deployment_impact.py** - Workshop timeline
7. **plot_os_distribution.py** - OS analysis
8. **plot_gpu_reliance.py** - GPU dependency scoring
9. **plot_configuration_hierarchy.py** - Config visualization (detailed)
10. **plot_configuration_hierarchy_simple.py** - Config visualization (simple)

See [Figure Documentation](../docs/figures/) for detailed usage of each script.

## Related Documentation

- [Architecture Diagrams](../docs/figures/architecture-diagrams/) - 12 infrastructure diagrams
- [Analysis Figures](../docs/figures/analysis-figures/) - 8+ analysis figures
- [Data Directory](../data/README.md) - Data sources
- [Development Guide](../docs/development/) - Contributing
