# Getting Started with LabLink Paper Figures

This guide will help you set up the repository and generate your first figure in less than 10 minutes.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10+** - Check with `python --version`
2. **uv package manager** - Install from [docs.astral.sh/uv](https://docs.astral.sh/uv/)
3. **graphviz** (for architecture diagrams) - System package:
   - macOS: `brew install graphviz`
   - Ubuntu/Debian: `sudo apt-get install graphviz`
   - Windows: Download from [graphviz.org](https://graphviz.org/download/)

4. **(Optional) Access to related repositories**:
   - [lablink-template](https://github.com/talmolab/lablink-template) - For architecture diagrams
   - [lablink](https://github.com/talmolab/lablink) - For detailed analysis

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/talmolab/lablink-paper-figures.git
cd lablink-paper-figures
```

### Step 2: Install Dependencies

```bash
# Install all dependencies (creates .venv automatically)
uv sync

# Or install with development tools (Jupyter, pytest, ruff)
uv sync --all-extras
```

This will:
- Create a virtual environment in `.venv/`
- Install all required packages from `pyproject.toml`
- Lock dependencies in `uv.lock` for reproducibility

### Step 3: Verify Installation

```bash
# Run tests
uv run pytest

# Check formatting
uv run ruff check .
```

If tests pass, you're ready to generate figures!

## Generate Your First Figure

Let's generate a simple analysis figure that doesn't require external data.

### Option 1: Generate a QR Code (Simplest)

```bash
uv run python scripts/plotting/generate_qr_codes.py
```

**Output**: QR codes in `figures/main/qr-*.png`

**What this does**: Generates QR codes for GitHub repositories and documentation links.

### Option 2: Generate GPU Cost Trends (Requires Data Download)

#### Download Data

1. Visit [epoch.ai/data/machine-learning-hardware](https://epoch.ai/data/machine-learning-hardware)
2. Click "Download Data" to get the ZIP file
3. Extract and place `ml_hardware.csv` in `data/raw/gpu_prices/`

```bash
# Create directory if needed
mkdir -p data/raw/gpu_prices

# Place downloaded ml_hardware.csv here
ls data/raw/gpu_prices/ml_hardware.csv  # Verify file exists
```

#### Generate Figure

```bash
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset paper
```

**Output**:
- `figures/main/gpu_cost_trends.png` (300 DPI)
- `figures/main/gpu_cost_trends.pdf` (vector)
- `figures/main/gpu_cost_trends-metadata.txt` (data source info)

**What this shows**: GPU pricing trends from 2006-2025, motivating LabLink's cloud-based GPU access.

### Option 3: Generate Architecture Diagram (Requires lablink-template)

#### Clone lablink-template

```bash
# Go to parent directory
cd ..

# Clone lablink-template repository
git clone https://github.com/talmolab/lablink-template.git

# Return to lablink-paper-figures
cd lablink-paper-figures
```

#### Generate Diagram

```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type main \
  --fontsize-preset paper
```

**Output**:
- `figures/run_YYYYMMDD_HHMMSS/diagrams/lablink-architecture.png`
- Timestamped folder for version control

**What this shows**: LabLink system overview with allocator, VMs, and logging flow.

## Understanding Output Locations

Figures are generated in different locations depending on the workflow:

### Timestamped Run Folders (Default, Gitignored)
```
figures/run_20251116_120345/
└── diagrams/
    ├── lablink-architecture.png
    └── diagram_metadata.txt
```

**Purpose**: Temporary review, version comparison
**Git status**: Gitignored (not committed)

### Main and Supplementary (Final Versions, Committed)
```
figures/
├── main/               # Main text figures (committed to git)
│   ├── lablink-architecture.pdf
│   ├── gpu_cost_trends.png
│   └── ...
└── supplementary/      # Supplementary figures (committed to git)
    └── ...
```

**Purpose**: Final publication-ready figures
**Git status**: Tracked and committed

### When to Use Each

- **Timestamped runs**: Default behavior, good for iterating and reviewing
- **Main/Supplementary**: Use `--output-dir figures/main` for final versions to commit

## Next Steps

### Explore Architecture Diagrams

Generate all 12 infrastructure diagrams:

```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all \
  --fontsize-preset poster \
  --format pdf
```

See [Architecture Diagrams Documentation](figures/architecture-diagrams/) for details on each diagram type.

### Explore Analysis Figures

Try generating other analysis figures:

```bash
# Software complexity (requires data collection, ~20-40 min first run)
cd scripts/analysis
uv run python collect_dependency_data.py
uv run python process_dependency_data.py
cd ../plotting
uv run python plot_software_complexity.py --preset paper

# SLEAP dependency graph (requires SLEAP repo or GitHub URL)
uv run python generate_sleap_dependency_graph.py \
  --sleap-source https://github.com/talmolab/sleap/blob/develop/pyproject.toml \
  --preset paper

# Deployment impact (data already included)
uv run python plot_deployment_impact.py --preset paper
```

See [Analysis Figures Documentation](figures/analysis-figures/) for all available figures.

### Understand Font Presets

All scripts support three font size presets:

| Preset | Font Size | Use Case | When to Use |
|--------|-----------|----------|-------------|
| `paper` | 14pt | Academic papers | Default, two-column journals |
| `poster` | 20pt | Conference posters | Large-format, must be readable at distance |
| `presentation` | 16pt | Slide decks | Projector display, presentations |

**Example**:
```bash
# For paper submission
uv run python scripts/plotting/<script>.py --preset paper

# For conference poster
uv run python scripts/plotting/<script>.py --preset poster
```

### Understand the LabLink System

The architecture diagrams visualize the LabLink system. To understand what they show:

- Read [Architecture Documentation](architecture/README.md)
- See [LabLink Infrastructure Analysis](architecture/infrastructure.md)
- Review [API Endpoints](architecture/api-endpoints.md) (22 Flask endpoints)
- Learn about [Key Workflows](architecture/workflows.md) (CRD, VM provisioning, logging)

### Set Up Convenience Environment Variables

Avoid repeating paths by setting environment variables:

```bash
# For architecture diagrams
export LABLINK_TERRAFORM_DIR=../lablink-template/lablink-infrastructure

# For SLEAP dependency graph
export SLEAP_PATH=../sleap

# For GitHub API (higher rate limits)
export GITHUB_TOKEN=ghp_your_token_here

# Now you can run without --terraform-dir flag
uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type main
```

## Common Issues

### "GraphViz not found"

**Problem**: `graphviz` system package not installed

**Solution**:
- macOS: `brew install graphviz`
- Ubuntu: `sudo apt-get install graphviz`
- Windows: Download from [graphviz.org](https://graphviz.org/download/)
- Verify: `dot -V` should show version

### "Terraform directory not found"

**Problem**: lablink-template repository not cloned or path incorrect

**Solution**:
```bash
cd ..
git clone https://github.com/talmolab/lablink-template.git
cd lablink-paper-figures

# Then use correct path:
--terraform-dir ../lablink-template/lablink-infrastructure
```

### "Data file not found"

**Problem**: External dataset not downloaded (e.g., GPU costs)

**Solution**: Check `data/raw/<dataset>/README.md` for download instructions

**Example** (GPU costs):
1. Visit [epoch.ai/data/machine-learning-hardware](https://epoch.ai/data/machine-learning-hardware)
2. Download CSV
3. Place in `data/raw/gpu_prices/ml_hardware.csv`

### "API rate limit exceeded"

**Problem**: Too many GitHub API calls without authentication

**Solution**: Set GitHub token
```bash
export GITHUB_TOKEN=ghp_your_token_here
# Get token from: https://github.com/settings/tokens
```

### Broken arrows or overlapping text in diagrams

**Problem**: GraphViz layout issues

**Solution**: See [GraphViz Reference](development/graphviz-reference.md) for troubleshooting

## Development Workflow

If you want to contribute or modify figures:

1. **Read the contributing guide**: [Development Guide](development/contributing.md)
2. **Code style**: Run `uv run ruff format .` before committing
3. **Tests**: Run `uv run pytest` to ensure nothing breaks
4. **Documentation**: Update docs/ if adding new figures

## Quick Command Reference

```bash
# Installation
uv sync                          # Install dependencies
uv sync --all-extras            # Install with dev tools

# Run scripts
uv run python scripts/plotting/<script>.py

# Testing and formatting
uv run pytest                    # Run tests
uv run pytest -v                 # Verbose output
uv run ruff check .              # Lint code
uv run ruff format .             # Format code

# Jupyter notebooks
uv run jupyter lab               # Launch Jupyter

# Environment management
uv add <package>                 # Add dependency
uv remove <package>              # Remove dependency
```

## Getting Help

- **Documentation Index**: [docs/README.md](README.md)
- **Architecture Diagrams**: [docs/figures/architecture-diagrams/](figures/architecture-diagrams/)
- **Analysis Figures**: [docs/figures/analysis-figures/](figures/analysis-figures/)
- **GraphViz Issues**: [docs/development/graphviz-reference.md](development/graphviz-reference.md)
- **Main README**: [../README.md](../README.md)

## What's Next?

You're now ready to:

1. ✅ Generate any of the 20+ figures
2. ✅ Understand the LabLink architecture
3. ✅ Contribute new figures or analysis
4. ✅ Create publication-ready visualizations

Happy figure generation! 📊
