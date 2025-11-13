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

TODO: Add instructions for generating figures

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