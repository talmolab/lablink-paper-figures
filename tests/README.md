# Tests Directory

This directory contains unit tests and integration tests for the figure generation codebase.

## Directory Structure

```
tests/
├── __init__.py
├── test_terraform_parser.py       # Terraform HCL parsing tests
├── test_diagram_generation.py     # Architecture diagram generation tests
├── test_dependency_extractor.py   # Dependency graph extraction tests
├── test_dependency_visualizer.py  # Dependency visualization tests
└── test_qr_codes.py                # QR code generation tests
```

## Testing Framework

This project uses **pytest** for all testing:

- **Framework**: pytest 7.0+
- **Coverage**: pytest-cov for code coverage reporting
- **Test discovery**: Automatic discovery of `test_*.py` files
- **Fixtures**: Reusable test data and mock configurations

## Running Tests

### Run All Tests

```bash
# Basic test run
uv run pytest

# Verbose output
uv run pytest -v

# Show test output (print statements)
uv run pytest -s
```

### Run Specific Test Files

```bash
# Test Terraform parser only
uv run pytest tests/test_terraform_parser.py

# Test diagram generation only
uv run pytest tests/test_diagram_generation.py -v
```

### Run Specific Test Functions

```bash
# Run single test by name
uv run pytest tests/test_terraform_parser.py::test_parse_directory

# Run tests matching pattern
uv run pytest -k "terraform"
```

## Code Coverage

### Generate Coverage Report

```bash
# Terminal report
uv run pytest --cov=src --cov-report=term-missing

# HTML report (opens in browser)
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

- **Overall coverage**: Target ≥80%
- **Critical modules**: Target ≥90%
  - `src/diagram_gen/generator.py`
  - `src/terraform_parser/parser.py`
  - `src/dependency_graph/graph_builder.py`

## Test Structure

Tests mirror the `src/` directory structure:

```
src/diagram_gen/generator.py    →  tests/test_diagram_generation.py
src/terraform_parser/parser.py  →  tests/test_terraform_parser.py
src/dependency_graph/            →  tests/test_dependency_*.py
```

## Writing Tests

### Test File Template

```python
"""Tests for <module_name> module."""

import pytest
from src.<module>.<file> import MyClass, my_function

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}

def test_basic_functionality(sample_data):
    """Test basic functionality."""
    result = my_function(sample_data)
    assert result is not None

def test_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

### Pytest Fixtures

Fixtures provide reusable test data:

**Example** (from `test_terraform_parser.py`):
```python
@pytest.fixture
def sample_terraform_content():
    """Sample Terraform configuration content."""
    return '''
resource "aws_instance" "test_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.large"

  tags = {
    Name = "test-server"
  }
}
'''

def test_parse_terraform_file(sample_terraform_content, tmp_path):
    """Test parsing Terraform file."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    result = parse_terraform_file(tf_file)
    assert len(result.ec2_instances) == 1
    assert result.ec2_instances[0].name == "test_instance"
```

### Common Fixture Patterns

**Temporary directories** (for file I/O tests):
```python
def test_write_file(tmp_path):
    """Test file writing."""
    output_file = tmp_path / "output.txt"
    my_function(output_file)
    assert output_file.exists()
```

**Sample configurations** (for diagram tests):
```python
@pytest.fixture
def sample_config():
    """Create sample Terraform configuration."""
    config = ParsedTerraformConfig()
    config.ec2_instances.append(
        TerraformResource(
            resource_type="aws_instance",
            name="allocator_server",
            attributes={"instance_type": "t3.large"}
        )
    )
    return config
```

## Mocking External Dependencies

For tests that would call external APIs or services, use mocking:

### Mock API Calls

```python
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_fetch_data(mock_get):
    """Test data fetching with mocked API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"package": "sleap"}
    mock_get.return_value = mock_response

    result = fetch_package_data("sleap")
    assert result["package"] == "sleap"
    mock_get.assert_called_once()
```

### Mock File System

```python
from unittest.mock import mock_open, patch

@patch('builtins.open', mock_open(read_data='{"key": "value"}'))
def test_read_config():
    """Test config reading with mocked file."""
    result = read_json_config("config.json")
    assert result["key"] == "value"
```

## Testing Best Practices

### 1. Test Naming

- **Files**: `test_<module_name>.py`
- **Functions**: `test_<what_it_tests>()`
- **Classes**: `TestClassName`

**Good**:
```python
def test_parse_terraform_file_with_ec2_instances()
def test_diagram_generation_with_missing_resources()
```

**Bad**:
```python
def test1()
def test_stuff()
```

### 2. Test Organization

Group related tests:

```python
class TestTerraformParser:
    """Tests for Terraform parser."""

    def test_parse_ec2_instances(self):
        """Test EC2 instance parsing."""
        ...

    def test_parse_security_groups(self):
        """Test security group parsing."""
        ...
```

### 3. Assertions

Use clear, specific assertions:

**Good**:
```python
assert len(result.ec2_instances) == 2
assert result.ec2_instances[0].name == "allocator"
assert "ami" in result.ec2_instances[0].attributes
```

**Bad**:
```python
assert result  # Too vague
assert True    # Meaningless
```

### 4. Test Independence

Each test should be independent:

**Good**:
```python
def test_create_diagram(sample_config):
    """Test diagram creation."""
    builder = LabLinkDiagramBuilder(sample_config)
    diagram = builder.generate_main_architecture()
    assert diagram is not None

def test_validate_config(sample_config):
    """Test config validation."""
    # Uses fresh sample_config, not affected by previous test
    assert validate_terraform_config(sample_config)
```

**Bad**:
```python
# Global state shared between tests
global_builder = None

def test_create_diagram():
    global global_builder
    global_builder = LabLinkDiagramBuilder(config)
    ...

def test_use_diagram():
    # Depends on test_create_diagram running first!
    diagram = global_builder.generate()
    ...
```

### 5. Test Data

Use fixtures for test data, avoid hardcoding:

**Good**:
```python
@pytest.fixture
def sample_gpu_data():
    """Sample GPU pricing data."""
    return [
        {"name": "RTX 3090", "price": 1499, "year": 2020},
        {"name": "RTX 4090", "price": 1599, "year": 2022},
    ]

def test_process_gpu_data(sample_gpu_data):
    """Test GPU data processing."""
    result = process_gpu_pricing(sample_gpu_data)
    assert len(result) == 2
```

**Bad**:
```python
def test_process_gpu_data():
    """Test GPU data processing."""
    # Hardcoded data, hard to reuse
    result = process_gpu_pricing([
        {"name": "RTX 3090", "price": 1499, "year": 2020},
        {"name": "RTX 4090", "price": 1599, "year": 2022},
    ])
    assert len(result) == 2
```

## Testing Diagram Generation

Diagram tests focus on logic, not visual output:

```python
def test_diagram_builder_initialization(sample_config):
    """Test diagram builder initialization."""
    builder = LabLinkDiagramBuilder(sample_config, preset="paper")
    assert builder.config == sample_config
    assert builder.fonts["title_size"] == 14  # Paper preset

def test_main_diagram_structure(sample_config):
    """Test main diagram includes expected components."""
    builder = LabLinkDiagramBuilder(sample_config)
    # Test generates correct node structure, not visual rendering
    nodes = builder._get_main_architecture_nodes()
    assert "allocator" in [n.label for n in nodes]
```

**Why not test visual output?**
- PNG/PDF output is non-deterministic (GraphViz versions vary)
- Visual quality is subjective
- Logic and structure are what matter for correctness

## Continuous Integration

Tests run automatically on:
- Every commit (pre-commit hook, if configured)
- Every pull request (GitHub Actions)
- Before releases

**GitHub Actions example** (if `.github/workflows/test.yml` exists):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: uv sync --all-extras
      - run: uv run pytest --cov=src --cov-report=term-missing
```

## Test Coverage by Module

Current test coverage:

| Module | Test File | Coverage | Priority |
|--------|-----------|----------|----------|
| Terraform Parser | `test_terraform_parser.py` | ~85% | High |
| Diagram Generation | `test_diagram_generation.py` | ~75% | High |
| Dependency Graph | `test_dependency_*.py` | ~70% | Medium |
| QR Codes | `test_qr_codes.py` | ~90% | Low |

**High priority**: Core diagram and parsing logic
**Medium priority**: Analysis and visualization
**Low priority**: Simple utilities and one-off scripts

## Adding New Tests

When adding new functionality to `src/`:

1. **Create corresponding test file**: `tests/test_<module>.py`
2. **Write fixtures**: Provide sample data
3. **Test happy path**: Normal expected behavior
4. **Test edge cases**: Empty input, invalid data, missing files
5. **Test error handling**: Expected exceptions
6. **Run coverage**: `uv run pytest --cov=src/<module>`
7. **Aim for ≥80% coverage**: Focus on critical paths

**Example workflow**:
```bash
# 1. Write new function in src/
vim src/new_module/processor.py

# 2. Create test file
vim tests/test_processor.py

# 3. Run tests
uv run pytest tests/test_processor.py -v

# 4. Check coverage
uv run pytest tests/test_processor.py --cov=src/new_module --cov-report=term-missing

# 5. Fix uncovered lines
# (Repeat steps 2-4 until coverage ≥80%)
```

## Debugging Failed Tests

### Verbose Output

```bash
# Show full test output
uv run pytest -v -s

# Show local variables on failure
uv run pytest --showlocals
```

### Run Single Test

```bash
# Debug specific test
uv run pytest tests/test_diagram_generation.py::test_main_diagram_structure -v -s
```

### Use Python Debugger

```python
def test_complex_logic():
    """Test complex logic."""
    import pdb; pdb.set_trace()  # Breakpoint
    result = complex_function()
    assert result is not None
```

### Check Test Logs

```bash
# Capture logs
uv run pytest --log-cli-level=DEBUG
```

## Related Documentation

- [Source Code README](../src/README.md) - Module documentation
- [Scripts README](../scripts/README.md) - Script usage
- [Development Guide](../docs/development/contributing.md) - Contributing guidelines
- [pytest Documentation](https://docs.pytest.org/) - Official pytest docs

## Quick Command Reference

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific file
uv run pytest tests/test_terraform_parser.py

# Run specific test
uv run pytest tests/test_terraform_parser.py::test_parse_directory

# Verbose output
uv run pytest -v -s

# Coverage HTML report
uv run pytest --cov=src --cov-report=html
```
