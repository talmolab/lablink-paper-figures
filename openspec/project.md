# Project Context

## Purpose
This repository contains figures and analysis code for the LabLink paper. LabLink is a dynamic VM allocation and management system for computational research workflows that enables researchers to dynamically provision and manage virtual machines for computational tasks in the cloud.

The primary goals are:
- Generate publication-quality figures for the LabLink paper
- Provide reproducible analysis and visualization code
- Document data processing pipelines for performance metrics and benchmarks

## Tech Stack
- **Python 3.10+** - Core language
- **uv** - Fast Python package installer and resolver (preferred over pip/conda)
- **NumPy** - Numerical computing
- **pandas** - Data manipulation and analysis
- **Matplotlib** - Primary plotting library
- **Seaborn** - Statistical data visualization
- **Plotly** - Interactive visualizations
- **SciPy** - Scientific computing
- **scikit-learn** - Machine learning utilities
- **Jupyter Lab** - Interactive notebook environment (dev only)
- **pytest** - Testing framework (dev only)
- **Ruff** - Linting and formatting (dev only)

## Project Conventions

### Code Style
- **Line length**: 88 characters (Black-compatible)
- **Python version**: 3.10+ features allowed
- **Formatting**: Use `ruff format .` for automatic formatting
- **Linting**: Use `ruff check .` to check for issues
- **Import ordering**: Automatically sorted by Ruff (stdlib, third-party, local)
- **Type hints**: Encouraged but not strictly required
- **Docstrings**: Use for public functions and classes

### Architecture Patterns
- **Modular design**: Reusable code goes in `src/`, scripts go in `scripts/`
- **Separation of concerns**:
  - `data/raw/` - Original, immutable data files
  - `data/processed/` - Cleaned, transformed data ready for plotting
  - `scripts/analysis/` - Data processing and analysis
  - `scripts/plotting/` - Figure generation
  - `notebooks/` - Exploratory analysis and interactive work
  - `figures/main/` - Main text figures
  - `figures/supplementary/` - Supplementary figures
- **Notebook-to-script workflow**: Prototype in Jupyter, refactor to scripts for reproducibility

### Testing Strategy
- **Framework**: pytest
- **Test location**: `tests/` directory
- **Naming convention**: `test_*.py` files, `test_*` functions
- **Coverage**: Use pytest-cov for coverage reports
- **Focus**: Test data processing functions and reusable modules in `src/`
- **Running**: `uv run pytest`

### Git Workflow
- **Default branch**: `main`
- **Commit style**: Descriptive messages explaining "why" not just "what"
- **Branch strategy**: Feature branches for significant changes
- **Code review**: Recommended for collaborative work
- **Pre-commit checks**: Run `ruff check` and `ruff format` before committing

## Domain Context
- **LabLink ecosystem**: This repo is part of a larger project with related repositories:
  - [lablink](https://github.com/talmolab/lablink) - Core system with allocator and client services
  - [lablink-template](https://github.com/talmolab/lablink-template) - Infrastructure-as-code deployment
  - [sleap-lablink](https://github.com/talmolab/sleap-lablink) - SLEAP-specific deployment example
- **Cloud computing**: Focus on VM provisioning, dynamic allocation, and cloud resource management
- **Research workflows**: Target audience is computational researchers
- **Performance metrics**: Likely analyzing VM allocation times, scaling efficiency, cost optimization
- **Academic publication**: Code must be reproducible and well-documented for peer review

## Important Constraints
- **Reproducibility**: All figures must be reproducible from code and data
- **Python version**: Minimum 3.10+ required
- **Publication quality**: Figures must meet journal standards (DPI, sizing, fonts)
- **Data privacy**: Ensure no sensitive cloud credentials or private data in repository
- **Package management**: Use `uv` for all dependency management (not pip or conda)

## External Dependencies
- **uv package manager**: Required for installation (`uv sync`)
- **Related LabLink services**: May need to reference architecture/data from core LabLink repos
- **Cloud platforms**: Analysis may involve AWS, GCP, or Azure metrics (to be determined)
- **SLEAP**: Computer vision framework (referenced in related repos, may appear in benchmarks)
