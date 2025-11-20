# Figure Generation Documentation

This directory contains comprehensive documentation for generating all publication-quality figures for the LabLink paper.

## Figure Categories

### [Architecture Diagrams](architecture-diagrams/README.md) (12 diagrams)
Infrastructure diagrams generated from actual Terraform code in lablink-template repository.

**Generated from**: Terraform configuration files (source of truth)
**Script**: `scripts/plotting/generate_architecture_diagram.py`
**Requires**: Access to `lablink-template/lablink-infrastructure` directory

**Quick start**:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all --fontsize-preset poster
```

### [Analysis Figures](analysis-figures/README.md) (8+ figures)
Motivation and analysis figures supporting the LabLink paper.

**Includes**:
- Software complexity growth over time (2000-2025)
- SLEAP dependency network graph
- GPU cost trends (2006-2025)
- Deployment impact timeline
- OS distribution analysis
- GPU reliance scoring
- Configuration hierarchy visualization
- QR codes for demos

**Generated from**: Data analysis, PyPI/conda-forge APIs, external datasets
**Scripts**: Various in `scripts/plotting/`

## Common Patterns

All figure generation scripts in this repository follow consistent patterns:

### Font Size Presets

Every script supports three presets for different output contexts:

| Preset | Font Size | Use Case | DPI | Dimensions |
|--------|-----------|----------|-----|------------|
| `paper` | 14pt | Academic papers, two-column journals | 300 | ~6.5" width |
| `poster` | 20pt | Conference posters, large format | 300 | ~12" width |
| `presentation` | 16pt | Slide decks, presentations | 150-300 | 10"x7.5" |

**Usage**:
```bash
# Generate for paper
uv run python scripts/plotting/<script>.py --preset paper

# Generate for poster
uv run python scripts/plotting/<script>.py --preset poster

# Generate for presentation
uv run python scripts/plotting/<script>.py --preset presentation
```

### Output Formats

All scripts support multiple output formats:

- **PNG** (default) - Raster at 300 DPI, best for papers
- **PDF** - Vector format for LaTeX, lossless scaling
- **SVG** - Vector format for web, presentations
- **both** / **all** - Generate multiple formats

**Usage**:
```bash
# PNG only (default)
uv run python scripts/plotting/<script>.py --format png

# PDF for LaTeX papers
uv run python scripts/plotting/<script>.py --format pdf

# Both PNG and PDF
uv run python scripts/plotting/<script>.py --format both
```

### Output Locations

**Always use these directories** for final figures:

- `figures/main/` - Main text figures (committed to git)
- `figures/supplementary/` - Supplementary figures (committed to git)
- `figures/run_YYYYMMDD_HHMMSS/` - Timestamped review folders (gitignored)

**DO NOT** use custom directories like `test_output/` or `review_figures/`

### Metadata Files

All scripts generate metadata files documenting:
- Data sources (URLs, API endpoints, file paths)
- Generation parameters (presets, versions, timestamps)
- Statistics (data points, date ranges, package counts)
- Dependencies (Python packages, external tools)

**Example**: `gpu_cost_trends-metadata.txt`

## Quick Reference

### Generate All Architecture Diagrams
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all \
  --fontsize-preset poster \
  --format pdf \
  --output-dir figures/main
```

### Generate Key Analysis Figures
```bash
# Software complexity
uv run python scripts/plotting/plot_software_complexity.py --preset paper

# GPU cost trends
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset poster --include-performance

# SLEAP dependencies
uv run python scripts/plotting/generate_sleap_dependency_graph.py --preset paper --format pdf
```

## Environment Variables

Set these for convenience (optional):

```bash
# Architecture diagrams
export LABLINK_TERRAFORM_DIR=../lablink-template/lablink-infrastructure
export LABLINK_CLIENT_VM_TERRAFORM_DIR=../lablink/packages/allocator/src/lablink_allocator_service/terraform

# SLEAP dependencies
export SLEAP_PATH=../sleap

# GitHub API (higher rate limits)
export GITHUB_TOKEN=ghp_your_token_here
```

## Documentation Structure

```
figures/
├── architecture-diagrams/          # 12 Terraform-based diagrams
│   ├── README.md                   # Overview and categories
│   ├── generating.md               # CLI usage and examples
│   └── diagram-reference.md        # Detailed description of each diagram
└── analysis-figures/               # 8+ analysis and motivation figures
    ├── README.md                   # Overview of all analysis figures
    ├── software-complexity.md      # Dependency growth analysis
    ├── sleap-dependencies.md       # Network graph generation
    ├── gpu-costs.md                # GPU pricing trends
    ├── deployment-impact.md        # Workshop timeline
    ├── os-distribution.md          # OS analysis
    ├── gpu-reliance.md             # GPU dependency scoring
    ├── configuration-hierarchy.md  # Config visualization
    └── qr-codes.md                 # QR code generation
```

## Troubleshooting

**GraphViz errors** (architecture diagrams):
- See [GraphViz Reference](../development/graphviz-reference.md)
- Check system graphviz installation: `dot -V`

**Missing data files**:
- Check `data/raw/<dataset>/README.md` for download instructions
- Run collection scripts in `scripts/analysis/` first

**Font size issues**:
- Use `--fontsize-preset poster` for large-format printing
- Test at actual print/display dimensions

**API rate limits**:
- Set `GITHUB_TOKEN` environment variable
- Use cached data with `--force-refresh` flag only when needed

## Related Documentation

- [Getting Started](../getting-started.md) - Installation and first figure tutorial
- [Development Guide](../development/contributing.md) - Adding new figures
- [GraphViz Reference](../development/graphviz-reference.md) - Diagram troubleshooting

## See Also

- Main [README.md](../../README.md) - Repository overview with all figure examples
- [Architecture Documentation](../architecture/README.md) - Understanding LabLink system
