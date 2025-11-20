# LabLink Paper Figures

This repository contains figures and analysis code for the LabLink paper.

## About LabLink

LabLink is a dynamic VM allocation and management system for computational research workflows. It enables researchers to dynamically provision and manage virtual machines for computational tasks in the cloud.

### Related Repositories

- [lablink](https://github.com/talmolab/lablink) - Core LabLink system with allocator and client services
- [lablink-template](https://github.com/talmolab/lablink-template) - Infrastructure-as-code template for deploying LabLink
- [sleap-lablink](https://github.com/talmolab/sleap-lablink) - SLEAP-specific deployment example

## Documentation

📚 **Comprehensive documentation** is available in the [`docs/`](docs/) directory:

- **[Documentation Index](docs/README.md)** - Main entry point with navigation to all documentation
- **[Getting Started](docs/getting-started.md)** - Installation and first figure tutorial
- **[Architecture Diagrams](docs/figures/architecture-diagrams/)** - 12 Terraform-based infrastructure diagrams
- **[Analysis Figures](docs/figures/analysis-figures/)** - Software complexity, GPU costs, dependencies, etc.
- **[LabLink Architecture](docs/architecture/)** - Analysis of LabLink system infrastructure
- **[Development Guide](docs/development/)** - Contributing, GraphViz reference, code style

## Repository Structure

```
lablink-paper-figures/
├── docs/              # Comprehensive documentation
│   ├── architecture/  # LabLink system analysis
│   ├── figures/       # Figure generation guides
│   │   ├── architecture-diagrams/  # 12 infrastructure diagrams
│   │   └── analysis-figures/       # 8+ analysis figures
│   ├── development/   # Developer documentation
│   └── archived/      # Historical development notes
├── data/              # Raw and processed data
│   ├── raw/           # Original data files (gitignored)
│   └── processed/     # Processed data ready for plotting
├── figures/           # Generated figures for the paper
│   ├── main/          # Main text figures (committed)
│   ├── supplementary/ # Supplementary figures (committed)
│   └── run_*/         # Timestamped runs (gitignored)
├── notebooks/         # Jupyter notebooks for exploratory analysis
├── scripts/           # Python scripts for data processing and plotting
│   ├── analysis/      # Data collection and processing
│   └── plotting/      # Figure generation (10 scripts)
├── src/               # Reusable modules
│   ├── diagram_gen/   # Infrastructure diagram generation
│   ├── terraform_parser/  # Terraform HCL parsing
│   └── dependency_graph/  # Network analysis
├── tests/             # Unit tests
└── openspec/          # Change management and proposals
```

## Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

### Installation

```bash
# Clone the repository
git clone https://github.com/talmolab/lablink-paper-figures.git
cd lablink-paper-figures

# Install dependencies (creates .venv automatically)
uv sync

# Activate the virtual environment
# On Unix/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Development Setup

For development work (includes Jupyter, testing, and linting tools):

```bash
uv sync --all-extras
```

### Running Jupyter

```bash
uv run jupyter lab
```

## Generated Figures

This repository generates **20+ publication-quality figures** for the LabLink paper, organized into two categories:

### Architecture Diagrams (12 diagrams)

Infrastructure diagrams generated from actual Terraform code to ensure accuracy:

1. **lablink-architecture** - System overview (allocator, VMs, logs)
2. **lablink-architecture-detailed** - Complete infrastructure with all AWS resources
3. **lablink-api-architecture** - Flask API with 22 endpoints across 5 functional groups
4. **lablink-vm-provisioning** - VM lifecycle with 3-phase startup sequence
5. **lablink-crd-connection** - CRD connection via PostgreSQL LISTEN/NOTIFY (15 steps)
6. **lablink-logging-pipeline** - CloudWatch → Lambda → Allocator → PostgreSQL flow
7. **lablink-database-schema** - PostgreSQL schema (runs in-container, NOT RDS)
8. **lablink-cicd-workflow** - GitHub Actions CI/CD pipeline
9. **lablink-network-flow** - Basic network routing
10. **lablink-network-flow-enhanced** - Network topology with ports & protocols
11. **lablink-monitoring** - VM health monitoring services
12. **lablink-data-collection** - SSH → Docker → rsync data export

→ [Full documentation](docs/figures/architecture-diagrams/)

### Analysis Figures (8+ figures)

Motivation and analysis figures supporting the paper:

1. **Software Complexity** - Dependency growth in scientific Python packages (2000-2025)
2. **SLEAP Dependency Graph** - Network visualization of computational research software complexity
3. **GPU Cost Trends** - Professional/consumer GPU pricing (2006-2025, Epoch AI dataset)
4. **Deployment Impact** - LabLink deployment history and workshop timeline
5. **OS Distribution** - Operating system analysis in computational research
6. **GPU Reliance** - Package GPU dependency scoring (0-5 scale)
7. **Configuration Hierarchy** - LabLink config.yaml structure visualization
8. **QR Codes** - Demo access codes and repository links

→ [Full documentation](docs/figures/analysis-figures/)

### Font Size Presets

All figures support three presets for different output contexts:

- **`paper`** (14pt) - Academic papers, two-column journals (default)
- **`poster`** (20pt) - Conference posters, large-format printing
- **`presentation`** (16pt) - Slide decks, projector display

### Output Formats

- **PNG** - 300 DPI raster, best for paper submissions
- **PDF** - Vector format, best for LaTeX papers
- **SVG** - Vector format, good for presentations

## Usage

### Generating Architecture Diagrams

This repository includes comprehensive architecture diagram generation for LabLink. The diagrams are automatically generated from Terraform infrastructure-as-code configurations to ensure accuracy.

#### Prerequisites

To generate diagrams, you need access to:
- Infrastructure Terraform: `../lablink-template/lablink-infrastructure`
- (Optional) Client VM Terraform: `../lablink/packages/allocator/src/lablink_allocator_service/terraform`

**Note**: The Terraform icon for the VM provisioning diagram is included in `assets/icons/terraform.svg`. If this file is missing, the diagram will use a generic placeholder icon.

#### Font Size Presets

Diagrams support three font size presets for different output contexts:

- **`paper`** (default): 14pt fonts for publications and papers
  - Node labels: 14pt
  - Edge labels: 14pt
  - Title: 32pt
  - Spacing: nodesep=0.6, ranksep=0.8

- **`poster`**: 20pt fonts for poster presentations
  - Node labels: 20pt (43% larger)
  - Edge labels: 20pt
  - Title: 48pt
  - Spacing: nodesep=0.9, ranksep=1.2 (50% more space to prevent overlap)

- **`presentation`**: 16pt fonts for slides
  - Node labels: 16pt
  - Edge labels: 16pt
  - Title: 40pt
  - Spacing: nodesep=0.75, ranksep=1.0

Use the `--fontsize-preset` flag to select a preset:
```bash
# Generate diagrams for poster presentation
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all-essential \
  --fontsize-preset poster
```

#### Diagram Types

**Priority 1 (Essential - for main paper):**
- `main` - System overview with Admin → Allocator → VMs → Logs
- `vm-provisioning` - VM provisioning & lifecycle with 3-phase startup
- `crd-connection` - CRD connection via PostgreSQL LISTEN/NOTIFY (unique architectural innovation)
- `logging-pipeline` - CloudWatch → Lambda → Allocator logging flow

**Priority 2 (Supplementary):**
- `cicd-workflow` - GitHub Actions CI/CD pipeline (7 workflows)
- `api-architecture` - Flask API endpoints (22 endpoints with auth)
- `network-flow-enhanced` - Network topology with ports & protocols
- `monitoring` - VM status & health monitoring services
- `data-collection` - SSH → Docker → rsync data export flow

**Legacy diagrams:**
- `detailed` - Complete infrastructure with all resources
- `network-flow` - Basic network routing diagram

#### Quick Start

Generate all essential diagrams:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --output-dir figures/main \
  --diagram-type all-essential
```

Generate all supplementary diagrams:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --output-dir figures/supplementary \
  --diagram-type all-supplementary
```

Generate a specific diagram:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --output-dir figures/main \
  --diagram-type crd-connection \
  --format png \
  --dpi 300
```

#### Environment Variables

You can set environment variables to avoid repeated CLI arguments:
```bash
export LABLINK_TERRAFORM_DIR=../lablink-template/lablink-infrastructure
export LABLINK_CLIENT_VM_TERRAFORM_DIR=../lablink/packages/allocator/src/lablink_allocator_service/terraform

uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type all-essential
```

#### Output Formats

Supported formats: `png` (default), `svg`, `pdf`
- PNG: Best for papers (300 DPI default)
- SVG: Vector format for presentations
- PDF: Vector format for LaTeX papers

#### Output Structure

Diagrams are generated in timestamped run folders for version control:
```
figures/
└── run_20251113_170838/
    ├── main/
    │   ├── lablink-architecture.png
    │   ├── lablink-vm-provisioning.png
    │   ├── lablink-crd-connection.png
    │   ├── lablink-logging-pipeline.png
    │   └── diagram_metadata.txt
    └── supplementary/
        ├── lablink-cicd-workflow.png
        ├── lablink-api-architecture.png
        └── ...
```

Each run folder contains both `main/` and `supplementary/` subdirectories based on which diagrams were generated. This structure makes it easy to:
- Track which diagrams were generated together
- Compare different versions
- Roll back to previous diagram sets

### Important: Output Directory Workflow

**Always generate to `figures/main/` or `figures/supplementary/`:**

```bash
# Correct - generates to figures/main/ and overwrites existing files
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --output-dir figures/main \
  --diagram-type all-essential
```

**DO NOT use custom output directories like `test_output/` or `review_figures/`** - these create clutter and are not tracked by git. The script will create timestamped run folders automatically (e.g., `figures/run_20251115_130350/`) which are gitignored for temporary review.

**DO NOT use `--no-timestamp-runs`** - this flag is only for special cases and can cause confusion about which files are current.

**Tracked files:**
- `figures/main/` - Final production versions (committed to git)
- `figures/supplementary/` - Supplementary diagrams (committed to git)

**Gitignored:**
- `figures/run_*/` - Timestamped run folders (temporary)
- `review_figures/`, `test_output/` - Any custom output directories

### Generating Scientific Software Complexity Figure

This repository includes tools to analyze and visualize dependency growth in scientific Python packages over time (2000-2025), demonstrating the increasing complexity of scientific software and motivating LabLink's value proposition for reproducible computational environments.

#### Overview

The software complexity analysis tracks 8-10 representative scientific Python packages:
- **Core Scientific Stack**: NumPy, SciPy, matplotlib, pandas (2001-2010 era)
- **Machine Learning**: TensorFlow, PyTorch, scikit-learn (2015+ deep learning era)
- **Domain/Workflow**: AstroPy, Jupyter (domain-specific and notebook workflows)

**Data sources**:
- **conda-forge** for compiled packages (captures system dependencies like BLAS, compilers)
- **PyPI** for pure-Python packages (simpler distributions)
- **GitHub** for validation

#### Quick Start

**Step 1: Collect dependency data** (requires internet, ~20-40 minutes):
```bash
cd scripts/analysis

# Collect data for all packages
uv run python collect_dependency_data.py

# Optional: use GitHub token for higher rate limits
uv run python collect_dependency_data.py --github-token YOUR_TOKEN
```

**Step 2: Process data into clean CSV**:
```bash
uv run python process_dependency_data.py
```

**Step 3: Generate figures**:
```bash
cd ../plotting

# Generate paper format (default: 14pt fonts, 300 DPI)
uv run python plot_software_complexity.py --format paper

# Generate poster format (20pt fonts for readability at distance)
uv run python plot_software_complexity.py --format poster

# Generate presentation format (16pt fonts for slides)
uv run python plot_software_complexity.py --format presentation
```

#### Output

The script generates:
- **Main figure**: `figures/main/software_complexity_over_time.{png,pdf}` - All packages over time with trend lines
- **Category comparison**: `figures/main/software_complexity_by_category.{png,pdf}` - Faceted by package category
- **Metadata**: `figures/main/software_complexity_metadata.txt` - Generation details and data sources

#### Configuration

**Format presets**:
- `paper`: 14pt fonts, 300 DPI, 6.5" width (two-column journal)
- `poster`: 20pt fonts, 300 DPI, 12" width (conference poster)
- `presentation`: 16pt fonts, 150 DPI, 10"x7.5" (slide deck)

**Advanced options**:
```bash
# Generate specific figures
uv run python plot_software_complexity.py --figures main

# Use custom data file
uv run python plot_software_complexity.py --data-file custom_data.csv

# Custom output directory
uv run python plot_software_complexity.py --output-dir figures/supplementary
```

#### How It Works

1. **Data collection**: Fetches historical dependency metadata from conda-forge feedstocks and PyPI API
2. **Processing**: Aggregates data, resolves conflicts (GitHub > conda-forge > PyPI), filters low-quality data
3. **Visualization**: Creates connected scatter plots with LOESS trend lines showing dependency growth

**Why conda-forge for scientific packages?**
conda-forge metadata includes complete system-level dependencies (BLAS, LAPACK, compilers) that PyPI omits. For example:
- PyPI SciPy 1.7.0: `requires_dist: ["numpy>=1.16.5"]` (1 dependency)
- conda-forge SciPy 1.7.0: `numpy, python, blas, libopenblas, libgfortran` (5+ dependencies)

This provides accurate complexity metrics that reflect what users actually experience.

See [`data/software_complexity_README.md`](data/software_complexity_README.md) for detailed documentation.

### Generating SLEAP Dependency Network Graph

This repository includes tools to generate dependency network visualizations for the SLEAP software package, demonstrating the complexity of modern computational research software to motivate LabLink's value proposition.

#### Overview

The dependency graph visualization shows:
- **Nodes**: Python packages (SLEAP and all transitive dependencies)
- **Edges**: Dependency relationships (directed arrows)
- **Visual encoding**:
  - Node size scaled by degree centrality (hub packages are larger)
  - Node color by package category (ML/scientific/data/visualization/utilities)
  - Labels shown for high-degree packages only
- **Statistics**: Total packages, dependencies, and top most-connected packages

#### Quick Start

Generate dependency graph using local SLEAP installation:
```bash
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --sleap-source C:/repos/sleap \
  --preset paper \
  --output-dir figures/main
```

Generate using GitHub URL (no local installation required):
```bash
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --sleap-source https://github.com/talmolab/sleap/blob/develop/pyproject.toml \
  --preset poster \
  --format svg
```

Use environment variable for convenience:
```bash
export SLEAP_PATH=C:/repos/sleap  # On Windows: set SLEAP_PATH=C:/repos/sleap
uv run python scripts/plotting/generate_sleap_dependency_graph.py
```

#### Configuration Options

**Presets** (matching repository conventions):
- `paper` (default): 14pt fonts, 12x10" figure, 300 DPI - for publications
- `poster`: 20pt fonts, 18x15" figure, 300 DPI - for poster presentations

**Output formats**:
- `png` (default): Raster image at 300 DPI
- `svg`: Vector graphics for presentations
- `pdf`: Vector graphics for LaTeX papers

**Advanced options**:
```bash
# Limit dependency depth (faster, smaller graph)
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --max-depth 2 \
  --label-threshold 3

# Exclude optional dependencies
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --exclude-optional

# Force refresh cached data
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --force-refresh

# Generate supplementary degree distribution plot
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --show-distribution

# Use different layout algorithm
uv run python scripts/plotting/generate_sleap_dependency_graph.py \
  --layout kamada_kawai
```

#### Output

The script generates:
- `sleap-dependency-graph.png` (or .svg, .pdf) - Main dependency network visualization
- `data/processed/sleap_dependencies.json` - Cached dependency data (speeds up subsequent runs)

Optional with `--show-distribution`:
- `sleap-dependency-distribution.png` - Degree distribution plots showing power-law characteristics

#### How It Works

1. **Dependency extraction**: Parses SLEAP's `pyproject.toml` to get direct dependencies
2. **Transitive resolution**: Recursively fetches dependency metadata from PyPI JSON API
3. **Graph construction**: Builds NetworkX directed graph with package categorization
4. **Layout computation**: Uses force-directed spring layout to emphasize hub packages
5. **Visualization**: Renders publication-quality figure with matplotlib/seaborn

**Note**: Initial run takes 1-2 minutes to fetch PyPI metadata for ~100-200 packages. Subsequent runs use cached data and complete in ~5 seconds.

### Generating GPU Cost Trends Visualization

This repository includes tools to visualize GPU pricing trends for scientific computing, demonstrating the sustained high cost of GPU hardware that motivates LabLink's cloud-based GPU access model.

#### Overview

The GPU cost trends visualization shows:
- **Price trends over time**: Launch MSRP of professional and consumer GPUs from 2006-2025
- **Professional GPUs**: Tesla, A100, H100, V100, P100 families (datacenter-class hardware)
- **Consumer GPUs**: RTX/GTX series with ≥5 TFLOPS (SLEAP-compatible cards)
- **Optional price-performance subplot**: FLOP/s per dollar showing efficiency improvements (~2.5 year doubling time)

The visualization uses the Epoch AI Machine Learning Hardware Database, a peer-reviewed dataset with 160+ GPUs covering ML-relevant hardware from 2006-2025.

#### Data Setup

Before generating figures, download the Epoch AI dataset:

1. Visit https://epoch.ai/data/machine-learning-hardware
2. Click "Download Data" to get the CSV file
3. Extract the ZIP and place `ml_hardware.csv` in `data/raw/gpu_prices/`

See [data/raw/gpu_prices/README.md](data/raw/gpu_prices/README.md) for detailed instructions.

#### Quick Start

Generate paper format figure (default):
```bash
uv run python scripts/plotting/plot_gpu_cost_trends.py
```

Generate poster format:
```bash
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset poster
```

Generate with price-performance subplot:
```bash
uv run python scripts/plotting/plot_gpu_cost_trends.py --include-performance
```

#### Configuration Options

**Presets** (matching repository conventions):
- `paper` (default): 14pt fonts, 6.5"x5" figure, 300 DPI - for two-column journals
- `poster`: 20pt fonts, 12"x9" figure, 300 DPI - for poster presentations
- `presentation`: 16pt fonts, 10"x7.5" figure, 150 DPI - for slide decks

**Output formats**:
- `both` (default): Generates both PNG and PDF versions
- `png`: Raster image at 300 DPI
- `pdf`: Vector graphics for LaTeX papers

**Advanced options**:
```bash
# Custom output path
uv run python scripts/plotting/plot_gpu_cost_trends.py \
  --output figures/supplementary/gpu_analysis.png

# Custom data path (if dataset is in different location)
uv run python scripts/plotting/plot_gpu_cost_trends.py \
  --data /path/to/ml_hardware.csv

# Verbose logging for debugging
uv run python scripts/plotting/plot_gpu_cost_trends.py --verbose
```

#### Output

The script generates:
- `gpu_cost_trends.png` (and/or .pdf) - Main price trends visualization
- `gpu_cost_trends-metadata.txt` - Data source, statistics, and generation details

With `--include-performance`:
- Creates 1x2 subplot grid with both price trends and price-performance evolution

#### Data Source

**Epoch AI Machine Learning Hardware Database**
- **URL**: https://epoch.ai/data/machine-learning-hardware
- **License**: CC BY 4.0 (free for academic and commercial use)
- **Coverage**: 160+ GPUs from 2006-2025 with pricing and performance metrics
- **Citation**: Epoch AI (2024), 'Data on Machine Learning Hardware'

#### GPU Selection Criteria

The visualization filters to ML-relevant GPUs:
- **Professional**: Tesla, A100, H100, V100, P100, A6000 families
- **Consumer**: RTX/GTX series with FP32 performance ≥ 5.0 TFLOPS
- **Excluded**: Mobile GPUs, laptop variants, low-performance gaming cards

This filtering ensures the visualization shows hardware actually used for scientific computing and pose estimation workloads like SLEAP.

#### Example Use Cases

**For LabLink paper motivation**:
```bash
# Generate both formats for paper figure
uv run python scripts/plotting/plot_gpu_cost_trends.py \
  --preset paper \
  --output figures/main/gpu_cost_trends.png \
  --format both
```

**For poster/presentation**:
```bash
# Larger fonts and price-performance comparison
uv run python scripts/plotting/plot_gpu_cost_trends.py \
  --preset poster \
  --include-performance \
  --format pdf
```

**Note**: First run validates data quality (minimum 50 GPUs, date range 2006+, >70% with pricing). If validation fails, check that you've downloaded the correct Epoch AI dataset.

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run ruff check .
uv run ruff format .
```

## Citation

If you use this work, please cite:

```bibtex
TODO: Add citation
```

## License

See LICENSE file for details.