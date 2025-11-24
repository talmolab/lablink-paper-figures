# Contributing Guide

This guide explains how to contribute code, figures, and documentation to the lablink-paper-figures repository.

## Quick Start

```bash
# Clone and install
git clone https://github.com/talmolab/lablink-paper-figures.git
cd lablink-paper-figures
uv sync --all-extras

# Verify setup
uv run pytest
uv run ruff check .

# Create branch and make changes
git checkout -b your-feature-name
# ... make changes ...

# Format, lint, test
uv run ruff format .
uv run ruff check .
uv run pytest

# Commit and push
git add .
git commit -m "Your descriptive message"
git push origin your-feature-name
```

## Code Style Guidelines

### Python Formatting

We use **Ruff** for both linting and formatting (Black-compatible):

```bash
# Format all files
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix safe issues
uv run ruff check --fix .
```

### Style Rules

**Line length**: 88 characters (Black default)

**Imports**: Sorted automatically by Ruff
```python
# Standard library
import os
from pathlib import Path

# Third-party
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Local
from src.diagram_gen.generator import LabLinkDiagramBuilder
```

**Type hints**: Encouraged for function signatures
```python
def process_data(input_path: Path, threshold: float = 0.5) -> pd.DataFrame:
    """Process data from file."""
    ...
```

**Docstrings**: Required for public functions (Google-style)
```python
def generate_figure(data: pd.DataFrame, preset: str = "paper") -> Path:
    """Generate a publication figure from data.

    Args:
        data: Input DataFrame with columns ['x', 'y', 'category'].
        preset: Font size preset ('paper', 'poster', 'presentation').

    Returns:
        Path to generated figure file.

    Raises:
        ValueError: If preset is not valid.

    Example:
        >>> df = pd.read_csv("data.csv")
        >>> path = generate_figure(df, preset="poster")
    """
    ...
```

### Naming Conventions

**Files**:
- Scripts: `verb_noun.py` (e.g., `plot_gpu_costs.py`, `collect_data.py`)
- Modules: `noun.py` (e.g., `generator.py`, `parser.py`)
- Tests: `test_module.py` (e.g., `test_generator.py`)

**Functions**:
- Verbs for actions: `generate_diagram()`, `parse_terraform()`, `collect_data()`
- Nouns for getters: `get_config()`, `data_path()`

**Classes**:
- PascalCase: `LabLinkDiagramBuilder`, `TerraformParser`

**Constants**:
- SCREAMING_SNAKE_CASE: `FONT_PRESETS`, `DEFAULT_OUTPUT_DIR`

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Verbose output
uv run pytest -v

# Single file
uv run pytest tests/test_diagram_generation.py

# Single test
uv run pytest tests/test_diagram_generation.py::test_main_diagram_structure

# With coverage
uv run pytest --cov=src --cov-report=term-missing
```

### Writing Tests

**Test file location**: Mirror `src/` structure
```
src/diagram_gen/generator.py    →  tests/test_diagram_generation.py
src/terraform_parser/parser.py  →  tests/test_terraform_parser.py
```

**Test naming**: `test_<what_it_tests>()`
```python
def test_parse_terraform_file_with_ec2_instances():
    """Test parsing Terraform file with EC2 instances."""
    ...

def test_generate_diagram_raises_on_invalid_preset():
    """Test diagram generation raises ValueError for invalid preset."""
    ...
```

**Use fixtures for test data**:
```python
@pytest.fixture
def sample_config():
    """Sample Terraform configuration for testing."""
    return ParsedTerraformConfig(
        ec2_instances=[TerraformResource(...)],
        security_groups=[...],
    )

def test_diagram_builder(sample_config):
    """Test diagram builder initialization."""
    builder = LabLinkDiagramBuilder(sample_config)
    assert builder.config == sample_config
```

**Coverage target**: 80% minimum for `src/` modules

### What to Test

**DO test**:
- Core logic and algorithms
- Error handling and edge cases
- Data transformations
- Configuration parsing

**DON'T test**:
- Visual output (GraphViz rendering varies)
- External API responses (mock them instead)
- Trivial getters/setters

## Adding New Figures

### Workflow

1. **Explore** in Jupyter notebook
   ```
   notebooks/exploratory/<figure_name>.ipynb
   ```

2. **Extract** reusable logic to `src/` module
   ```python
   # src/<domain>/processor.py
   class DataProcessor:
       def process(self, data):
           ...
   ```

3. **Create** plotting script
   ```python
   # scripts/plotting/plot_<figure_name>.py
   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument("--preset", choices=["paper", "poster", "presentation"])
       parser.add_argument("--format", choices=["png", "pdf", "both", "all"])
       ...
   ```

4. **Add** data collection script (if needed)
   ```python
   # scripts/analysis/collect_<data>.py
   ```

5. **Document** data sources
   ```
   data/raw/<dataset>/README.md
   ```

6. **Test** the module
   ```
   tests/test_<module>.py
   ```

7. **Generate** final figures
   ```bash
   uv run python scripts/plotting/plot_<figure>.py --preset paper --output-dir figures/main
   ```

8. **Document** in `docs/figures/analysis-figures/<figure>.md`

### Script Template

```python
#!/usr/bin/env python
"""Generate <figure_name> figure for the LabLink paper.

This script generates <description> showing <what it shows>.

Usage:
    uv run python scripts/plotting/plot_<figure>.py --preset poster --format pdf

Data source:
    <data source description>
"""

import argparse
import logging
from pathlib import Path

import matplotlib.pyplot as plt

# Local imports
from src.<module>.<file> import <Class>

# Constants
FONT_PRESETS = {
    "paper": {"title": 14, "label": 12, "tick": 10},
    "poster": {"title": 20, "label": 16, "tick": 14},
    "presentation": {"title": 16, "label": 14, "tick": 12},
}

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--preset",
        choices=["paper", "poster", "presentation"],
        default="paper",
        help="Font size preset (default: paper)",
    )
    parser.add_argument(
        "--format",
        choices=["png", "pdf", "both", "all"],
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("figures/main"),
        help="Output directory (default: figures/main)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def generate_figure(data, preset: str, output_dir: Path, format: str) -> list[Path]:
    """Generate the figure.

    Args:
        data: Input data for plotting.
        preset: Font size preset name.
        output_dir: Directory to save figures.
        format: Output format(s).

    Returns:
        List of paths to generated figure files.
    """
    fonts = FONT_PRESETS[preset]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plotting code here
    ax.set_title("Figure Title", fontsize=fonts["title"])
    ax.set_xlabel("X Label", fontsize=fonts["label"])
    ax.set_ylabel("Y Label", fontsize=fonts["label"])
    ax.tick_params(labelsize=fonts["tick"])

    plt.tight_layout()

    # Save in requested formats
    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = []

    formats_to_save = []
    if format in ("png", "both", "all"):
        formats_to_save.append("png")
    if format in ("pdf", "both", "all"):
        formats_to_save.append("pdf")
    if format == "all":
        formats_to_save.append("svg")

    for fmt in formats_to_save:
        path = output_dir / f"<figure_name>.{fmt}"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved: {path}")
        output_paths.append(path)

    plt.close(fig)
    return output_paths


def main() -> None:
    """Main entry point."""
    args = parse_args()
    setup_logging(args.verbose)

    logger.info(f"Generating <figure_name> with preset={args.preset}")

    # Load data
    # data = load_data(...)

    # Generate figure
    paths = generate_figure(
        data=None,  # Replace with actual data
        preset=args.preset,
        output_dir=args.output_dir,
        format=args.format,
    )

    logger.info(f"Generated {len(paths)} figure(s)")


if __name__ == "__main__":
    main()
```

## Pull Request Process

### Before Submitting

1. **Format code**:
   ```bash
   uv run ruff format .
   ```

2. **Check linting**:
   ```bash
   uv run ruff check .
   ```

3. **Run tests**:
   ```bash
   uv run pytest
   ```

4. **Update documentation** (if applicable):
   - Add/update README in relevant directory
   - Update `docs/` if adding new figures or features

5. **Commit with clear message**:
   ```bash
   git commit -m "Add GPU reliance scoring figure

   - Implement scoring algorithm in src/gpu_costs/processor.py
   - Add plotting script scripts/plotting/plot_gpu_reliance.py
   - Document data sources in data/raw/gpu_reliance/README.md
   - Add tests with 85% coverage

   Closes #42"
   ```

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Bullet point list of specific changes
- Include file paths for significant changes

## Testing
- [ ] Tests pass locally (`uv run pytest`)
- [ ] Code formatted (`uv run ruff format .`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] New tests added for new functionality

## Documentation
- [ ] Updated relevant README files
- [ ] Added docstrings to new functions
- [ ] Updated docs/ if needed

## Screenshots
(If applicable, include before/after screenshots of figures)
```

### Review Criteria

PRs are reviewed for:

1. **Correctness**: Does it work as intended?
2. **Code quality**: Is it readable and maintainable?
3. **Testing**: Are new features tested?
4. **Documentation**: Are changes documented?
5. **Style**: Does it follow project conventions?

## OpenSpec Change Proposals

For **significant changes** (new features, breaking changes, architecture changes), use OpenSpec:

### When to Use OpenSpec

- Adding a new major figure category
- Changing the project structure
- Modifying the build/test workflow
- Breaking changes to existing APIs
- Large refactoring efforts

### Creating a Proposal

1. **Read the guide**:
   ```bash
   cat openspec/AGENTS.md
   ```

2. **Create proposal directory**:
   ```
   openspec/changes/<change-id>/
   ├── proposal.md      # Problem and solution overview
   ├── design.md        # Technical design details
   └── tasks.md         # Implementation tasks
   ```

3. **Validate**:
   ```bash
   openspec validate <change-id> --strict
   ```

4. **Apply** (after approval):
   ```bash
   openspec apply <change-id>
   ```

### Example Proposal

See `openspec/changes/consolidate-and-improve-documentation/` for a real example.

## Common Contribution Types

### Adding a New Analysis Figure

1. Create `scripts/plotting/plot_<figure>.py` following template
2. Add data to `data/raw/<dataset>/` with README.md
3. Add processing logic to `src/<domain>/`
4. Write tests in `tests/test_<module>.py`
5. Document in `docs/figures/analysis-figures/<figure>.md`
6. Update `docs/figures/analysis-figures/README.md`

### Fixing a Bug

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Add regression test if not covered
5. Document fix in commit message

### Improving Documentation

1. Read existing documentation in `docs/`
2. Make changes in appropriate `.md` file
3. Check internal links still work
4. Update cross-references if needed

### Adding a Dependency

```bash
# Production dependency
uv add <package>

# Development dependency
uv add --dev <package>

# Commit both files
git add pyproject.toml uv.lock
git commit -m "Add <package> for <purpose>"
```

## Getting Help

- **Documentation**: Start with `docs/README.md`
- **GraphViz issues**: See `docs/development/graphviz-reference.md`
- **Testing**: See `tests/README.md`
- **Questions**: Open a GitHub issue

## Code of Conduct

- Be respectful and constructive in reviews
- Focus on the code, not the person
- Assume good intent
- Ask clarifying questions before criticizing
- Help newcomers learn project conventions

## License

Contributions are made under the GPL-3.0-or-later license (see `LICENSE` file).

By contributing, you agree that your contributions will be licensed under the same license.
