# Architecture Diagrams (12 diagrams)

This directory documents the 12 infrastructure architecture diagrams generated from actual Terraform configuration files in the [lablink-template](https://github.com/talmolab/lablink-template) repository.

## Overview

These diagrams visualize the LabLink system's AWS infrastructure by parsing and rendering Terraform code. This ensures diagrams always reflect the actual deployed infrastructure.

**Source of truth**: Terraform `.tf` files in `lablink-template/lablink-infrastructure/`
**Generation script**: `scripts/plotting/generate_architecture_diagram.py`
**Output location**: `figures/main/` (for final versions)

## The 12 Diagrams

### Essential Diagrams (Priority 1 - Main Paper)

1. **lablink-architecture** (`main`) - System overview with allocator, VMs, logs
2. **lablink-vm-provisioning** - VM lifecycle with 3-phase startup sequence
3. **lablink-crd-connection** - CRD connection via PostgreSQL LISTEN/NOTIFY
4. **lablink-logging-pipeline** - CloudWatch → Lambda → Allocator logging flow

### Supplementary Diagrams (Priority 2 - Appendix/Detailed Analysis)

5. **lablink-cicd-workflow** - GitHub Actions CI/CD pipeline (7 workflows)
6. **lablink-api-architecture** - Flask API endpoints (22 endpoints with auth)
7. **lablink-network-flow-enhanced** - Network topology with ports & protocols
8. **lablink-monitoring** - VM status & health monitoring services
9. **lablink-data-collection** - SSH → Docker → rsync data export flow

### Legacy/Detailed Diagrams

10. **lablink-architecture-detailed** (`detailed`) - Complete infrastructure, all resources
11. **lablink-network-flow** - Basic network routing diagram
12. **lablink-database-schema** - PostgreSQL schema ERD

## Quick Start

### Generate All Essential Diagrams
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all-essential \
  --fontsize-preset poster \
  --output-dir figures/main
```

### Generate All Supplementary Diagrams
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all-supplementary \
  --fontsize-preset paper \
  --output-dir figures/supplementary
```

### Generate Single Diagram
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type crd-connection \
  --fontsize-preset poster \
  --format pdf
```

## Font Size Presets

Choose the appropriate preset for your output medium:

### Paper (14pt fonts)
Default for academic publications and two-column journals.

```bash
--fontsize-preset paper
```

**Specs**:
- Node labels: 14pt
- Edge labels: 14pt
- Title: 32pt
- Spacing: nodesep=0.6, ranksep=0.8

### Poster (20pt fonts)
For conference posters and large-format printing (must be readable at distance).

```bash
--fontsize-preset poster
```

**Specs**:
- Node labels: 20pt (43% larger than paper)
- Edge labels: 20pt
- Title: 48pt
- Spacing: nodesep=0.9, ranksep=1.2 (50% more space)

### Presentation (16pt fonts)
For slide decks and projector presentations.

```bash
--fontsize-preset presentation
```

**Specs**:
- Node labels: 16pt
- Edge labels: 16pt
- Title: 40pt
- Spacing: nodesep=0.75, ranksep=1.0

## Output Formats

- **PNG** (default) - 300 DPI raster, best for papers
- **SVG** - Vector format, good for presentations and web
- **PDF** - Vector format, best for LaTeX papers
- **all** - Generate all formats

```bash
# PNG for paper submission
--format png

# PDF for LaTeX
--format pdf

# All formats
--format all
```

## Output Directory Workflow

**ALWAYS use these directories**:

```bash
# Final production versions (committed to git)
--output-dir figures/main            # Main text figures
--output-dir figures/supplementary   # Supplementary figures

# Timestamped review (gitignored, auto-generated)
# Default behavior creates: figures/run_YYYYMMDD_HHMMSS/
```

**DO NOT** use custom directories like `test_output/` or `review_figures/`

**Disable timestamped folders** (only for special cases):
```bash
--no-timestamp-runs
```

## Prerequisites

### Required
1. **Terraform directory**: Path to `lablink-template/lablink-infrastructure`
2. **graphviz**: System package (`brew install graphviz` or `apt-get install graphviz`)
3. **Python environment**: `uv sync` to install dependencies

### Optional
- **Client VM Terraform**: For detailed VM provisioning diagrams
  ```bash
  --client-vm-terraform-dir ../lablink/packages/allocator/src/lablink_allocator_service/terraform
  ```

### Environment Variables (Optional)
```bash
export LABLINK_TERRAFORM_DIR=../lablink-template/lablink-infrastructure
export LABLINK_CLIENT_VM_TERRAFORM_DIR=../lablink/packages/allocator/src/lablink_allocator_service/terraform

# Then simply run:
uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type all
```

## CLI Options

```bash
python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir PATH                       # Required: path to Terraform files
  --diagram-type TYPE                        # all, all-essential, all-supplementary, or specific
  --fontsize-preset {paper|poster|presentation}  # Default: paper
  --format {png|svg|pdf|all}                 # Default: png
  --output-dir PATH                          # Default: figures/
  --dpi INT                                  # Default: 300
  --timestamp-runs / --no-timestamp-runs     # Default: enabled
  --verbose                                  # Enable debug logging
```

## Diagram Types

Use `--diagram-type` to control what gets generated:

| Type | Description | Diagrams |
|------|-------------|----------|
| `all` | All 12 diagrams | Everything |
| `all-essential` | Main paper figures | 4 essential diagrams |
| `all-supplementary` | Appendix figures | 5 supplementary diagrams |
| `main` | System overview | Single diagram |
| `detailed` | Detailed infrastructure | Single diagram |
| `api-architecture` | Flask API endpoints | Single diagram |
| `vm-provisioning` | VM lifecycle | Single diagram |
| `crd-connection` | CRD workflow | Single diagram |
| `logging-pipeline` | Logging flow | Single diagram |
| `database-schema` | PostgreSQL schema | Single diagram |
| `cicd-workflow` | CI/CD pipeline | Single diagram |
| `network-flow` | Basic network routing | Single diagram |
| `network-flow-enhanced` | Enhanced network topology | Single diagram |
| `monitoring` | Monitoring architecture | Single diagram |
| `data-collection` | Data export flow | Single diagram |

## Examples

### For Main Paper (Essential Diagrams)
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all-essential \
  --fontsize-preset paper \
  --format pdf \
  --output-dir figures/main
```

### For Conference Poster
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all-essential \
  --fontsize-preset poster \
  --format pdf \
  --output-dir figures/main
```

### Single Diagram for Review
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type crd-connection \
  --fontsize-preset paper \
  --format png
# Outputs to figures/run_YYYYMMDD_HHMMSS/diagrams/
```

## Output Structure

With timestamped runs (default):
```
figures/
├── run_20251116_004526/
│   └── diagrams/
│       ├── lablink-architecture.png
│       ├── lablink-vm-provisioning.png
│       ├── lablink-crd-connection.png
│       ├── lablink-logging-pipeline.png
│       └── diagram_metadata.txt
└── main/                           # Copy final versions here
    ├── lablink-architecture.pdf
    ├── lablink-vm-provisioning.pdf
    └── ...
```

## Troubleshooting

**GraphViz errors**:
- Check installation: `dot -V`
- See [GraphViz Reference](../../development/graphviz-reference.md)

**Missing Terraform directory**:
```
Error: Terraform directory not found
Solution: Check path to lablink-template/lablink-infrastructure
```

**Broken arrows or overlapping text**:
- Try different font preset
- See [GraphViz Reference](../../development/graphviz-reference.md) for edge routing fixes

**Database edges not visible** (fixed):
- Recent fix: Added `constraint="false"` to database edges
- Regenerate diagrams to get fix

## Recent Fixes

- ✅ Fixed missing database edges in API architecture (added `constraint="false"`)
- ✅ Fixed Flask icon in VM provisioning (now shows Python icon correctly)
- ✅ Fixed blank nodes in CI/CD workflow (added proper icons)
- ✅ Added PostgreSQL in-container clarification to labels
- ✅ Added detailed architecture preset support

## Detailed Documentation

- [Diagram Reference](diagram-reference.md) - Detailed description of each diagram
- [Generating Guide](generating.md) - Complete CLI documentation with all options
- [Architecture Analysis](../../architecture/README.md) - Understanding LabLink infrastructure

## See Also

- [GraphViz Settings Reference](../../development/graphviz-reference.md) - Technical diagram settings
- [Analysis Figures](../analysis-figures/README.md) - Other paper figures
- Main [README.md](../../../README.md) - Repository overview
