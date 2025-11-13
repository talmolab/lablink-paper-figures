# Scripts

This directory contains Python scripts for data processing and figure generation.

## Structure

- `analysis/` - Data analysis and processing scripts
- `plotting/` - Scripts to generate final figures

## Usage

Run scripts from the repository root:

```bash
python scripts/analysis/process_data.py
python scripts/plotting/generate_figure1.py
```

## Guidelines

- Scripts should be executable and include proper argument parsing
- Use `argparse` or `click` for command-line interfaces
- Save outputs to appropriate directories (`data/processed/` or `figures/`)
- Include docstrings and type hints