# Development Documentation

This directory contains technical references and contribution guidelines for developers working on the lablink-paper-figures repository.

## Documentation Files

### [GraphViz Reference](graphviz-reference.md)
Technical reference for diagram styling, layout, and troubleshooting.

**Topics covered**:
- GraphViz DOT format basics
- Edge routing and constraint parameters
- Node and cluster styling
- Font and spacing presets
- Common layout issues and fixes
- Orthogonal splines (`splines="ortho"`)
- Cross-cluster edge routing

**Who needs this**: Developers working on architecture diagrams, troubleshooting rendering issues

### [Contributing Guide](contributing.md)
How to contribute to this repository.

**Topics covered**:
- Code style guidelines (Ruff, 88 char lines)
- Testing with pytest
- Adding new figures
- Documentation requirements
- Pull request process
- OpenSpec for change proposals

**Who needs this**: Anyone contributing code, figures, or documentation

## Quick Reference

### Code Style
- **Formatter**: `uv run ruff format .`
- **Linter**: `uv run ruff check .`
- **Line length**: 88 characters (Black-compatible)
- **Type hints**: Encouraged for function signatures
- **Docstrings**: Required for public functions (Google-style)

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Verbose output
uv run pytest -v
```

### Adding a New Figure

1. **Explore** in Jupyter notebook (`notebooks/exploratory/`)
2. **Extract** reusable logic to `src/<domain>/` module
3. **Create** plotting script in `scripts/plotting/plot_<figure>.py`
4. **Add** data collection script if needed (`scripts/analysis/`)
5. **Document** data sources in `data/raw/<dataset>/README.md`
6. **Generate** with presets:
   ```bash
   uv run python scripts/plotting/plot_<figure>.py --preset paper
   ```
7. **Commit** final figures to `figures/main/` and update main README
8. **Document** in `docs/figures/analysis-figures/<figure>.md`

### Figure Generation Standards

**Required**:
- Support `--preset {paper|poster|presentation}` flag
- Support `--format {png|pdf|svg|both}` flag
- Generate metadata `.txt` file with data sources
- Use `uv run` for all Python execution
- Default to `figures/main/` or `figures/supplementary/`

**Presets**:
- `paper`: 14pt fonts, 300 DPI, ~6.5" width
- `poster`: 20pt fonts, 300 DPI, ~12" width
- `presentation`: 16pt fonts, 150 DPI, 10"x7.5"

### Package Management

**ALWAYS use uv** (never pip, conda, or poetry):

```bash
# Add dependency
uv add <package>

# Add dev dependency
uv add --dev <package>

# Install/update environment
uv sync

# Install with dev tools
uv sync --all-extras

# Run command in environment
uv run <command>
```

### Git Workflow

1. **Create feature branch**: `git checkout -b feature-name`
2. **Make changes**: Edit code, add tests, update docs
3. **Format and lint**:
   ```bash
   uv run ruff format .
   uv run ruff check .
   ```
4. **Test**:
   ```bash
   uv run pytest
   ```
5. **Commit**:
   ```bash
   git add .
   git commit -m "Descriptive message explaining why"
   ```
6. **Push and create PR**:
   ```bash
   git push origin feature-name
   # Create pull request on GitHub
   ```

### OpenSpec Change Proposals

For significant changes (new features, breaking changes, major refactors):

1. **Create proposal**:
   ```bash
   cd openspec
   # Follow openspec/AGENTS.md for proposal format
   ```
2. **Validate**:
   ```bash
   openspec validate <change-id> --strict
   ```
3. **Apply** (after approval):
   ```bash
   openspec apply <change-id>
   ```

See `openspec/AGENTS.md` for full details.

## Development Environment Setup

### Prerequisites
- Python 3.10+
- uv package manager
- graphviz system package
- (Optional) Access to lablink/lablink-template repos

### Installation
```bash
# Clone repository
git clone https://github.com/talmolab/lablink-paper-figures.git
cd lablink-paper-figures

# Install dependencies with dev tools
uv sync --all-extras

# Verify installation
uv run pytest
uv run ruff check .
```

### Optional: Set up related repositories
```bash
# Clone LabLink repositories for architecture diagrams
cd ..
git clone https://github.com/talmolab/lablink-template.git
git clone https://github.com/talmolab/lablink.git

# Set environment variables
export LABLINK_TERRAFORM_DIR=../lablink-template/lablink-infrastructure
export LABLINK_CLIENT_VM_TERRAFORM_DIR=../lablink/packages/allocator/src/lablink_allocator_service/terraform
```

## Project Structure

```
lablink-paper-figures/
├── data/                    # Data files
│   ├── raw/                 # Original, immutable (gitignored except READMEs)
│   └── processed/           # Cleaned, transformed (some committed)
├── figures/                 # Generated figures
│   ├── main/                # Main text (committed)
│   ├── supplementary/       # Supplementary (committed)
│   └── run_*/               # Timestamped (gitignored)
├── notebooks/               # Jupyter notebooks (exploratory)
├── scripts/
│   ├── analysis/            # Data collection and processing
│   └── plotting/            # Figure generation
├── src/                     # Reusable modules
│   ├── diagram_gen/         # Infrastructure diagram logic
│   ├── terraform_parser/    # Terraform HCL parsing
│   ├── dependency_graph/    # Network analysis
│   └── gpu_costs/           # GPU pricing utilities
├── tests/                   # Unit tests
├── docs/                    # Documentation
│   ├── architecture/        # LabLink system analysis
│   ├── figures/             # Figure generation guides
│   └── development/         # This directory
└── openspec/                # Change management
    ├── changes/             # Change proposals
    └── specs/               # Capability specifications
```

## Common Development Tasks

### Run Tests
```bash
uv run pytest
uv run pytest -v              # Verbose
uv run pytest tests/test_foo.py  # Single file
uv run pytest -k test_bar     # Single test
```

### Check Code Quality
```bash
uv run ruff check .           # Lint
uv run ruff format .          # Format
uv run ruff check --fix .     # Auto-fix safe issues
```

### Generate Architecture Diagrams (development)
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type main \
  --verbose
# Outputs to timestamped run folder for review
```

### Generate Analysis Figure (development)
```bash
uv run python scripts/plotting/plot_gpu_cost_trends.py \
  --preset paper \
  --verbose
```

### Profile Performance
```bash
python -m cProfile -o profile.stats scripts/plotting/<script>.py
python -m pstats profile.stats
```

### Update Dependencies
```bash
uv add <new-package>          # Add and install
uv sync                       # Update from pyproject.toml
git add pyproject.toml uv.lock
git commit -m "Add <package> dependency"
```

## Debugging

### Enable Verbose Logging
Most scripts support `--verbose` or `-v`:
```bash
uv run python scripts/plotting/<script>.py --verbose
```

### GraphViz Issues
See [GraphViz Reference](graphviz-reference.md) for:
- Broken arrows / missing edges
- Overlapping text
- Layout problems
- Orthogonal routing issues

### API Rate Limits
```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Check remaining rate limit
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

### Missing Data Files
```bash
# Check data directory READMEs
find data -name "README.md" -exec cat {} \;
```

## Performance Optimization

- **Use cached data**: Don't use `--force-refresh` unless necessary
- **Profile slow code**: Use `cProfile` or `line_profiler`
- **Vectorize operations**: Prefer NumPy/pandas over Python loops
- **Batch API requests**: Reduce network calls
- **Document expected runtime**: Add to script help text

## Related Documentation

- [GraphViz Reference](graphviz-reference.md) - Diagram troubleshooting
- [Contributing Guide](contributing.md) - Full contribution workflow
- [Architecture Documentation](../architecture/README.md) - LabLink system analysis
- Main [README.md](../../README.md) - Repository overview

## External Resources

- [uv documentation](https://docs.astral.sh/uv/) - Package manager
- [Ruff documentation](https://docs.astral.sh/ruff/) - Linter and formatter
- [pytest documentation](https://docs.pytest.org/) - Testing framework
- [GraphViz documentation](https://graphviz.org/documentation/) - Diagram rendering
- [diagrams library](https://diagrams.mingrammer.com/) - Python diagram generation
