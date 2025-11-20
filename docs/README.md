# LabLink Paper Figures - Documentation

This directory contains comprehensive documentation for the **lablink-paper-figures** repository, which generates publication-quality figures for the LabLink paper by analyzing the LabLink system from the [lablink](https://github.com/talmolab/lablink) and [lablink-template](https://github.com/talmolab/lablink-template) repositories.

## Where to Start

**New to this repository?**
→ Start with [Getting Started](getting-started.md) for installation and your first figure

**Want to generate architecture diagrams?**
→ See [Architecture Diagrams](figures/architecture-diagrams/README.md) for the 12 Terraform-based diagrams

**Want to generate analysis figures?**
→ See [Analysis Figures](figures/analysis-figures/README.md) for software complexity, GPU costs, etc.

**Understanding the LabLink system?**
→ See [Architecture Documentation](architecture/README.md) for LabLink infrastructure analysis

**Contributing to this repository?**
→ See [Contributing Guide](development/contributing.md) for code style and workflows

## Documentation Organization

```
docs/
├── getting-started.md             # Installation and first figure tutorial
├── architecture/                  # LabLink system analysis
│   ├── README.md                  # Architecture documentation index
│   ├── infrastructure.md          # AWS infrastructure details
│   ├── api-endpoints.md           # 22 Flask API endpoints
│   ├── database-schema.md         # PostgreSQL schema
│   ├── workflows.md               # CRD, VM provisioning, logging, CI/CD
│   └── configuration.md           # Configuration system
├── figures/                       # Figure generation documentation
│   ├── architecture-diagrams/     # 12 diagrams from Terraform analysis
│   │   ├── README.md              # Overview and diagram categories
│   │   ├── generating.md          # How to generate diagrams
│   │   └── diagram-reference.md   # Detailed description of each diagram
│   └── analysis-figures/          # Analysis and motivation figures
│       ├── README.md              # Overview of 8+ analysis figures
│       ├── software-complexity.md # Dependency growth over time
│       ├── sleap-dependencies.md  # SLEAP dependency network
│       ├── gpu-costs.md           # GPU pricing trends
│       └── ...                    # Other analysis figures
├── development/                   # Developer documentation
│   ├── graphviz-reference.md      # GraphViz settings and troubleshooting
│   └── contributing.md            # How to contribute
└── archived/                      # Historical development notes
    └── ...                        # Archived analysis and bug reports
```

## Quick Links

### Generate Figures

**Architecture Diagrams** (visualize LabLink infrastructure from Terraform):
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type all --fontsize-preset poster
```
→ [Full documentation](figures/architecture-diagrams/generating.md)

**Analysis Figures** (software complexity, GPU costs, etc.):
```bash
# Software complexity
uv run python scripts/plotting/plot_software_complexity.py --preset paper

# GPU cost trends
uv run python scripts/plotting/plot_gpu_cost_trends.py --preset poster

# SLEAP dependencies
uv run python scripts/plotting/generate_sleap_dependency_graph.py --preset paper
```
→ [Full documentation](figures/analysis-figures/README.md)

### Understand LabLink

- [Infrastructure Overview](architecture/infrastructure.md) - AWS resources, PostgreSQL in-container, Flask API
- [API Endpoints](architecture/api-endpoints.md) - 22 Flask endpoints across 5 functional groups
- [Key Workflows](architecture/workflows.md) - CRD connection, VM provisioning, logging pipeline
- [Database Schema](architecture/database-schema.md) - PostgreSQL tables and relationships

### Development

- [GraphViz Reference](development/graphviz-reference.md) - Diagram styling and troubleshooting
- [Contributing Guide](development/contributing.md) - Code style, testing, pull requests

## About This Repository

**Purpose**: Generate publication-quality figures for the LabLink academic paper

**Key Features**:
- 12 architecture diagrams generated from actual Terraform infrastructure code
- 8+ analysis figures supporting the paper's motivation and findings
- Reproducible figure generation with consistent presets (paper/poster/presentation)
- Comprehensive analysis documentation of the LabLink system

**Tech Stack**: Python 3.10+, uv package manager, diagrams library, GraphViz, matplotlib, seaborn

**Related Repositories**:
- [lablink](https://github.com/talmolab/lablink) - Core LabLink system (what we analyze)
- [lablink-template](https://github.com/talmolab/lablink-template) - Infrastructure code (what we visualize)

## Documentation Philosophy

This documentation follows these principles:

1. **Evidence-based**: Technical claims cite source files (e.g., `Dockerfile:13`, `main.tf:143`)
2. **Accuracy**: All infrastructure analysis verified against actual lablink/lablink-template code
3. **Completeness**: Every diagram type and figure script documented
4. **Navigable**: Clear hierarchy with cross-references and quick links
5. **Reproducible**: Step-by-step instructions for regenerating all figures

## Need Help?

- Check [Getting Started](getting-started.md) for common setup issues
- See [GraphViz Reference](development/graphviz-reference.md) for diagram troubleshooting
- Review the main [README.md](../README.md) for repository overview

## Recent Updates

- Added comprehensive documentation for all 12 architecture diagrams
- Documented 8+ analysis figure types with generation guides
- Consolidated LabLink infrastructure analysis with evidence citations
- Created clear hierarchy separating architecture analysis from figure generation
