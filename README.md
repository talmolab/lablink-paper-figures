# LabLink Paper Figures

This repository contains figures and analysis code for the LabLink paper.

## About LabLink

LabLink is a dynamic VM allocation and management system for computational research workflows. It enables researchers to dynamically provision and manage virtual machines for computational tasks in the cloud.

### Related Repositories

- [lablink](https://github.com/talmolab/lablink) - Core LabLink system with allocator and client services
- [lablink-template](https://github.com/talmolab/lablink-template) - Infrastructure-as-code template for deploying LabLink
- [sleap-lablink](https://github.com/talmolab/sleap-lablink) - SLEAP-specific deployment example

## Repository Structure

```
lablink-paper-figures/
├── data/               # Raw and processed data
│   ├── raw/           # Original data files
│   └── processed/     # Processed data ready for plotting
├── figures/           # Generated figures for the paper
│   ├── main/         # Main text figures
│   └── supplementary/ # Supplementary figures
├── notebooks/         # Jupyter notebooks for analysis
├── scripts/          # Python scripts for data processing and plotting
│   ├── analysis/     # Data analysis scripts
│   └── plotting/     # Figure generation scripts
├── src/              # Source code for reusable modules
└── tests/            # Unit tests
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

## Usage

### Generating Architecture Diagrams

This repository includes comprehensive architecture diagram generation for LabLink. The diagrams are automatically generated from Terraform infrastructure-as-code configurations to ensure accuracy.

#### Prerequisites

To generate diagrams, you need access to:
- Infrastructure Terraform: `../lablink-template/lablink-infrastructure`
- (Optional) Client VM Terraform: `../lablink/packages/allocator/src/lablink_allocator_service/terraform`

**Note**: The Terraform icon for the VM provisioning diagram is included in `assets/icons/terraform.png`. If this file is missing, the diagram will use a generic placeholder icon.

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

Use `--no-timestamp-runs` to disable timestamping and generate directly to the output directory.

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