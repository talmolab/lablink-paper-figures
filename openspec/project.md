# Project Context

## Purpose
This repository contains figures and analysis code for the LabLink paper. LabLink is a dynamic VM allocation and management system for computational research workflows that enables researchers to dynamically provision and manage virtual machines for computational tasks in the cloud.

The primary goals are:
- Generate publication-quality figures for the LabLink paper
- Provide reproducible analysis and visualization code
- Document data processing pipelines for performance metrics and benchmarks

## Tech Stack

### Core Python Environment
- **Python 3.10+** - Core language with modern type hints and syntax features
- **uv** - Fast Python package installer and resolver (ALWAYS use instead of pip/conda)

### Data Analysis & Visualization
- **NumPy** - Numerical computing and array operations
- **pandas** - Data manipulation and analysis
- **Matplotlib** - Primary plotting library for publication-quality figures
- **Seaborn** - Statistical data visualization built on matplotlib
- **Plotly** - Interactive visualizations
- **SciPy** - Scientific computing and statistical functions

### Specialized Libraries
- **scikit-learn** - Machine learning utilities
- **diagrams** - Infrastructure architecture diagram generation (Python-based)
- **graphviz** - Graph visualization engine for DOT format diagrams
- **networkx** - Network/graph data structures and algorithms (dependency graphs)
- **PyYAML** - YAML parsing for configuration files
- **requests** - HTTP library for API calls (PyPI metadata, etc.)
- **qrcode[pil]** - QR code generation with PIL imaging support
- **opencv-python-headless** - Computer vision for QR code processing (headless for server deployment)
- **pyzbar** - QR code and barcode decoding

### Development Tools (Optional)
- **Jupyter Lab** - Interactive notebook environment
- **pytest** - Testing framework
- **pytest-cov** - Code coverage reporting
- **Ruff** - Fast Python linter and formatter (replaces flake8, black, isort)

## Project Conventions

### Code Style
- **Line length**: 88 characters (Black-compatible)
- **Python version**: 3.10+ features allowed (structural pattern matching, improved typing)
- **Formatting**: Use `uv run ruff format .` for automatic formatting
- **Linting**: Use `uv run ruff check .` to check for issues
- **Import ordering**: Automatically sorted by Ruff (stdlib, third-party, local)
- **Type hints**: Encouraged for function signatures, not strictly required for variables
- **Docstrings**: Required for public functions and classes, Google-style format preferred
- **No emojis**: Never use emojis or special Unicode characters (cross-platform compatibility)

### Figure Generation Standards
All plotting scripts must follow these conventions:

**Presets** (consistent across all scripts):
- `paper` - 14pt fonts, 300 DPI, ~6.5" width (two-column journal format)
- `poster` - 20pt fonts, 300 DPI, ~12" width (conference poster readability)
- `presentation` - 16pt fonts, 150 DPI, 10"x7.5" (slide deck aspect ratio)

**Output formats**:
- `png` - Default for papers (300 DPI raster, good compression)
- `pdf` - Vector format for LaTeX papers (lossless scaling)
- `svg` - Vector format for presentations (web-friendly)

**File organization**:
- Final figures: `figures/main/` and `figures/supplementary/` (committed to git)
- Timestamped runs: `figures/run_YYYYMMDD_HHMMSS/` (gitignored, for review)
- Always generate metadata `.txt` files documenting data sources and parameters

**Quality requirements**:
- Minimum 300 DPI for raster images
- Readable fonts at target size (test at actual print/display dimensions)
- Consistent color schemes across related figures
- Clear axis labels with units
- Legends positioned to avoid data occlusion

### Architecture Patterns
- **Modular design**: Reusable code goes in `src/`, scripts go in `scripts/`
- **Separation of concerns**:
  - `data/raw/` - Original, immutable data files (gitignored except READMEs)
  - `data/processed/` - Cleaned, transformed data ready for plotting
  - `scripts/analysis/` - Data processing and analysis (e.g., dependency collection)
  - `scripts/plotting/` - Figure generation (e.g., architecture diagrams, GPU trends)
  - `notebooks/` - Exploratory analysis and interactive work
  - `figures/main/` - Main text figures (committed to git)
  - `figures/supplementary/` - Supplementary figures (committed to git)
  - `src/` - Organized by domain:
    - `diagram_gen/` - Infrastructure diagram generation logic
    - `terraform_parser/` - Terraform HCL parsing utilities
    - `dependency_graph/` - Dependency network analysis
    - `gpu_costs/` - GPU pricing data processing
- **Notebook-to-script workflow**: Prototype in Jupyter, refactor to scripts for reproducibility
- **Configuration presets**: Consistent `paper`, `poster`, `presentation` presets across all plotting scripts
- **Timestamped outputs**: Optional timestamped run folders for versioning (gitignored)

### Common Workflows

**Adding a new figure**:
1. Explore data in Jupyter notebook (`notebooks/exploratory/`)
2. Extract reusable logic to `src/<domain>/` module
3. Create plotting script in `scripts/plotting/plot_<figure_name>.py`
4. Add data collection script if needed in `scripts/analysis/`
5. Document data sources in `data/raw/<dataset>/README.md`
6. Generate figures with preset: `uv run python scripts/plotting/plot_<figure>.py --preset paper`
7. Commit final figures to `figures/main/` and update main README

**Data processing pattern**:
1. **Collection**: `scripts/analysis/collect_*.py` - Fetch from APIs, download datasets
2. **Processing**: `scripts/analysis/process_*.py` - Clean, transform, aggregate data
3. **Storage**: Save to `data/processed/<dataset>.csv` or `.json`
4. **Visualization**: `scripts/plotting/plot_*.py` - Read processed data, generate figures

**Caching strategy**:
- Cache expensive API calls to `data/processed/` with timestamp metadata
- Use `--force-refresh` flags to bypass cache when needed
- Document cache invalidation logic in script help text

**Environment variables** (optional convenience):
- `LABLINK_TERRAFORM_DIR` - Path to lablink-template Terraform code
- `SLEAP_PATH` - Path to SLEAP repository clone
- `GITHUB_TOKEN` - GitHub personal access token (higher API rate limits)

### Testing Strategy
- **Framework**: pytest with pytest-cov
- **Test location**: `tests/` directory mirroring `src/` structure
- **Naming convention**: `test_*.py` files, `test_*` functions
- **Coverage**: Run `uv run pytest --cov=src --cov-report=term-missing`
- **Focus**: Test data processing functions and reusable modules in `src/`
- **Running tests**: `uv run pytest` (standard) or `uv run pytest -v` (verbose)
- **Best practices**:
  - Use fixtures for common test data
  - Mock external API calls (PyPI, GitHub) to avoid network dependencies
  - Test both happy paths and error conditions
  - Keep tests fast and isolated

### Error Handling & Debugging
- **Logging**: Use Python `logging` module, not print statements
  - Scripts should support `--verbose` or `-v` flag for debug logging
  - Default to INFO level, use DEBUG for detailed diagnostics
- **Error messages**: Include context and actionable suggestions
  - Bad: "File not found"
  - Good: "Config file not found at path/to/config.yaml. Run with --help to see required files."
- **Data validation**: Check assumptions early (file existence, API responses, data quality)
- **Graceful degradation**: Handle missing optional dependencies with clear error messages
  - Example: "graphviz not found. Install with 'brew install graphviz' to generate diagrams."
- **API rate limits**: Implement exponential backoff, cache responses, document token requirements
- **Debugging flags**: Support `--dry-run`, `--verbose`, `--debug` where applicable

### Git Workflow
- **Default branch**: `main`
- **Commit style**: Descriptive messages explaining "why" not just "what"
- **Branch strategy**: Feature branches for significant changes
- **Code review**: Recommended for collaborative work
- **Pre-commit checks**: Run `uv run ruff check .` and `uv run ruff format .` before committing

### uv Best Practices
**ALWAYS use `uv` for package management - never use pip, conda, or poetry directly.**

**Common commands**:
- `uv sync` - Install/update all dependencies from lockfile (creates `.venv` automatically)
- `uv sync --all-extras` - Install with dev dependencies (Jupyter, pytest, ruff)
- `uv add <package>` - Add new dependency to `pyproject.toml` and install
- `uv add --dev <package>` - Add development dependency
- `uv remove <package>` - Remove dependency
- `uv run <command>` - Run command in virtual environment (auto-activates)
- `uv pip list` - List installed packages
- `uv pip freeze` - Show exact versions

**Virtual environment**:
- uv creates `.venv/` automatically on first `uv sync`
- No need to manually activate - use `uv run <command>` instead
- To manually activate (optional):
  - Unix/macOS: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\activate`

**Why uv over pip/conda**:
- 10-100x faster than pip
- Built-in lockfile support (`uv.lock`)
- Deterministic installs across machines
- No conda environment conflicts
- First-class PEP 621 `pyproject.toml` support

**Dependency resolution**:
- uv resolves dependencies automatically and updates `uv.lock`
- Lockfile ensures reproducible environments
- Commit both `pyproject.toml` and `uv.lock` to git

### Performance & Optimization
- **Data loading**: Use pandas `read_csv()` with appropriate dtypes, avoid iterrows()
- **Vectorization**: Prefer NumPy/pandas vectorized operations over Python loops
- **Caching**: Cache expensive computations (API calls, data processing) to `data/processed/`
- **Lazy evaluation**: Only load/process data when needed, support subset selection
- **Memory efficiency**: Use generators for large datasets, clean up temporary files
- **API calls**: Batch requests when possible, respect rate limits, use conditional requests
- **Profiling**: Use `cProfile` or `line_profiler` for performance-critical code
- **Benchmarking**: Document expected runtime for long-running scripts in help text

## Domain Context

### LabLink Ecosystem
This repository is part of the LabLink project for dynamic VM allocation in computational research:
- [lablink](https://github.com/talmolab/lablink) - Core system with allocator and client services
- [lablink-template](https://github.com/talmolab/lablink-template) - Infrastructure-as-code deployment templates
- [sleap-lablink](https://github.com/talmolab/sleap-lablink) - SLEAP-specific deployment example

### Research Domain
- **Cloud computing**: VM provisioning, dynamic allocation, cloud resource management (AWS focus)
- **Target audience**: Computational researchers, bioinformatics, computer vision workflows
- **Performance metrics**: VM allocation times, scaling efficiency, cost optimization
- **Academic publication**: Code must be reproducible and well-documented for peer review

### Figure Categories

**Architecture & System Design**:
- Infrastructure diagrams generated from Terraform code (source of truth)
- VM provisioning lifecycle visualization
- CRD connection mechanism (LISTEN/NOTIFY innovation)
- CI/CD workflow and API architecture

**Motivation Figures**:
- Software complexity growth over time (2000-2025 scientific Python packages)
- Dependency network visualization (SLEAP as case study)
- GPU hardware cost trends (2006-2025, Epoch AI dataset)

**Performance & Benchmarks**:
- (Future) VM allocation latency, scaling tests, cost analysis

## Important Constraints
- **Reproducibility**: All figures must be reproducible from code and data
- **Python version**: Minimum 3.10+ required (leverages structural pattern matching, typing improvements)
- **Publication quality**: Figures must meet journal standards:
  - 300 DPI for raster images (PNG)
  - Vector formats (PDF, SVG) for scalability
  - Consistent font sizing across presets (14pt paper, 20pt poster, 16pt presentation)
- **Data privacy**: Ensure no sensitive cloud credentials or private data in repository
- **Package management**: ALWAYS use `uv` for dependency management:
  - `uv add <package>` to add dependencies
  - `uv sync` to install/update environment
  - `uv run <command>` to execute in virtual environment
  - Never use pip, conda, or poetry directly
- **Cross-platform compatibility**: No emojis or special characters that break on Windows/Unix
- **Git hygiene**:
  - Commit final figures to `figures/main/` and `figures/supplementary/`
  - Gitignore timestamped run folders and raw data
  - Never commit virtual environments or cache directories

## External Dependencies

### Required
- **uv package manager**: Install from https://docs.astral.sh/uv/ (required for all operations)
- **graphviz system package**: Required for DOT format diagram rendering
  - macOS: `brew install graphviz`
  - Ubuntu/Debian: `apt-get install graphviz`
  - Windows: Download from https://graphviz.org/download/

### Optional (for specific features)
- **Related LabLink repositories**: For architecture diagram generation
  - `lablink-template` repository (Terraform infrastructure code)
  - `lablink` repository (client VM Terraform)
- **SLEAP repository**: For dependency graph generation
  - Can use local clone or GitHub URL
  - Set `SLEAP_PATH` environment variable for convenience
- **Internet access**: Required for:
  - PyPI API calls (dependency resolution, metadata fetching)
  - conda-forge feedstock data (software complexity analysis)
  - GitHub API (repository metadata, rate limit: 60/hour unauthenticated)
  - Epoch AI dataset downloads (GPU pricing data)

### Data Sources
- **PyPI JSON API**: https://pypi.org/pypi/<package>/json (dependency metadata)
- **conda-forge feedstocks**: https://github.com/conda-forge/<package>-feedstock (system dependencies)
- **Epoch AI ML Hardware Database**: https://epoch.ai/data/machine-learning-hardware (GPU pricing)
- **GitHub API**: https://api.github.com (repository validation, release dates)
