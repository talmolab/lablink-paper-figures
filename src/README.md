# Source Modules (`src/`)

This directory contains reusable Python modules for figure generation. Code here is imported by scripts in `scripts/` and tested in `tests/`.

## Directory Structure

```
src/
├── diagram_gen/         # Infrastructure diagram generation logic
│   ├── generator.py            # LabLinkDiagramBuilder class
│   ├── font_presets.py         # Font preset system
│   └── helpers.py              # Diagram helper methods
├── terraform_parser/    # Terraform HCL parsing utilities
│   ├── parser.py               # Parse .tf files
│   └── resource_extractor.py  # Extract AWS resources
├── dependency_graph/    # Network analysis for dependencies
│   ├── graph_builder.py        # Build NetworkX graphs
│   └── categorization.py      # Package categorization
└── gpu_costs/           # GPU pricing data processing
    └── processor.py            # Clean and validate GPU data
```

## Module Purposes

### `diagram_gen/` - Infrastructure Diagram Generation

**Purpose**: Generate architecture diagrams from Terraform configurations using the Python `diagrams` library.

**Key exports**:
- `LabLinkDiagramBuilder` - Main class for diagram generation
- `FONT_PRESETS` - Paper/poster/presentation font configurations
- Helper methods for consistent diagram styling

**Used by**: `scripts/plotting/generate_architecture_diagram.py`

**Example**:
```python
from src.diagram_gen.generator import LabLinkDiagramBuilder

builder = LabLinkDiagramBuilder(terraform_config, preset="poster")
builder.generate_main_architecture()
```

### `terraform_parser/` - Terraform HCL Parsing

**Purpose**: Parse Terraform `.tf` files to extract AWS resource configurations.

**Key exports**:
- `TerraformParser` - Parse HCL syntax
- `ResourceExtractor` - Extract resource blocks
- Resource type identification

**Used by**: `diagram_gen/generator.py`

**Example**:
```python
from src.terraform_parser.parser import TerraformParser

parser = TerraformParser(terraform_dir)
resources = parser.parse_all_files()
```

### `dependency_graph/` - Dependency Network Analysis

**Purpose**: Build and analyze dependency networks for software packages.

**Key exports**:
- `GraphBuilder` - Construct NetworkX directed graphs
- `PackageCategorizer` - Categorize packages (ML/scientific/data/etc.)
- Centrality calculations

**Used by**: `scripts/plotting/generate_sleap_dependency_graph.py`

**Example**:
```python
from src/dependency_graph.graph_builder import GraphBuilder

builder = GraphBuilder()
graph = builder.build_from_pypi("sleap")
```

### `gpu_costs/` - GPU Pricing Data Processing

**Purpose**: Process and validate GPU pricing datasets.

**Key exports**:
- `GPUDataProcessor` - Clean Epoch AI dataset
- Validation functions
- Filtering by GPU type

**Used by**: `scripts/plotting/plot_gpu_cost_trends.py`

## Code Organization Principles

### What Belongs in `src/`

- **Reusable logic**: Code used by multiple scripts
- **Complex algorithms**: Non-trivial processing logic
- **Class definitions**: Builders, parsers, processors
- **Configuration**: Constants, presets, schemas
- **Utilities**: Helper functions used across scripts

### What Belongs in `scripts/`

- **Entry points**: CLI scripts with argument parsing
- **Orchestration**: Combining `src/` modules for specific tasks
- **I/O operations**: File reading/writing, API calls
- **Visualization**: Matplotlib/seaborn plotting code
- **One-off logic**: Script-specific code not reused elsewhere

### Example: Where Code Goes

**Good** (in `src/diagram_gen/generator.py`):
```python
class LabLinkDiagramBuilder:
    def __init__(self, terraform_config, preset="paper"):
        self.config = terraform_config
        self.fonts = FONT_PRESETS[preset]
    
    def generate_main_architecture(self):
        # Reusable diagram generation logic
        ...
```

**Good** (in `scripts/plotting/generate_architecture_diagram.py`):
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--terraform-dir", required=True)
    parser.add_argument("--preset", default="paper")
    args = parser.parse_args()
    
    # Parse Terraform
    config = TerraformParser(args.terraform_dir).parse()
    
    # Build diagram
    builder = LabLinkDiagramBuilder(config, args.preset)
    builder.generate_main_architecture()
```

## Testing

All code in `src/` should have corresponding tests in `tests/`:

```
src/diagram_gen/generator.py    →  tests/test_diagram_gen/test_generator.py
src/terraform_parser/parser.py  →  tests/test_terraform_parser/test_parser.py
```

Run tests:
```bash
uv run pytest tests/
uv run pytest --cov=src --cov-report=term-missing
```

## Code Style

- **Formatting**: `uv run ruff format src/`
- **Linting**: `uv run ruff check src/`
- **Line length**: 88 characters (Black-compatible)
- **Type hints**: Encouraged for function signatures
- **Docstrings**: Required for public functions (Google-style)

## Adding New Modules

1. **Create module directory**: `src/<module_name>/`
2. **Add `__init__.py`**: Export public API
3. **Write tests**: `tests/test_<module_name>/`
4. **Document**: Add section to this README
5. **Import in scripts**: Use from scripts

**Example structure**:
```
src/new_module/
├── __init__.py          # from .main import MyClass
├── main.py              # Core logic
├── helpers.py           # Utility functions
└── constants.py         # Configuration
```

## Related Documentation

- [Development Guide](../docs/development/) - Contributing guidelines
- [Scripts README](../scripts/README.md) - Script usage
- [Testing](../tests/README.md) - Testing strategy
