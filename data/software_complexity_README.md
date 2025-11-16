# Scientific Software Complexity Data

This directory contains data for analyzing dependency growth in scientific Python packages over time (2000-2025).

## Overview

The analysis tracks 8-10 representative scientific Python packages across three categories:
- **Core Scientific Stack**: NumPy, SciPy, matplotlib, pandas
- **Machine Learning**: TensorFlow, PyTorch, scikit-learn
- **Domain/Workflow**: AstroPy, Jupyter

## Data Sources

### conda-forge (for compiled packages)
Used for: NumPy, SciPy, matplotlib, pandas, scikit-learn, AstroPy

**Why**: conda-forge metadata includes complete system-level dependencies (BLAS, LAPACK, compilers) that PyPI omits, providing accurate complexity metrics for compiled scientific packages.

**Access**:
- Feedstock repositories: `https://github.com/conda-forge/{package}-feedstock`
- Parse `meta.yaml` files from git history for dependency metadata

**Example**:
```bash
# NumPy feedstock
https://github.com/conda-forge/numpy-feedstock
```

### PyPI (for pure-Python packages)
Used for: TensorFlow, PyTorch, Jupyter

**Why**: These packages have simpler PyPI distributions (pre-compiled wheels) where PyPI metadata is sufficient and authoritative.

**Access**:
- PyPI JSON API: `https://pypi.org/pypi/{package}/{version}/json`
- Extract `requires_dist` field for dependency lists

### GitHub (for validation)
Spot-check 5-10 key versions across packages to validate data quality.

**Access**:
- Direct analysis of `requirements.txt`, `setup.py`, `pyproject.toml` from tagged releases

## Directory Structure

```
data/
├── raw/software_complexity/
│   ├── conda_forge_metadata/      # conda-forge package metadata
│   │   ├── numpy_meta.json
│   │   ├── scipy_meta.json
│   │   └── ...
│   ├── pypi_metadata/             # PyPI version metadata
│   │   ├── tensorflow_versions.json
│   │   ├── torch_versions.json    # PyPI name for PyTorch
│   │   └── ...
│   └── github_validation/         # GitHub validation results
│       └── validation_results.json
│
└── processed/software_complexity/
    ├── dependency_timeseries.csv  # Cleaned time-series data
    ├── quality_report.txt         # Data quality assessment
    └── source_attribution.csv     # Tracks data source per package
```

## Data Collection

### Step 1: Collect Raw Data

```bash
# Collect data for all packages (requires internet connection)
cd scripts/analysis
python collect_dependency_data.py

# Collect for specific packages
python collect_dependency_data.py --packages numpy scipy matplotlib

# Use GitHub token for higher rate limits (optional but recommended)
python collect_dependency_data.py --github-token YOUR_TOKEN_HERE

# The token can be generated at: https://github.com/settings/tokens
# Required scopes: public_repo (read-only)
```

**Expected runtime**: 20-40 minutes depending on internet speed and API rate limits

**Output**: JSON files in `data/raw/software_complexity/`

### Step 2: Process Data

```bash
# Process raw JSON files into cleaned CSV
cd scripts/analysis
python process_dependency_data.py

# With custom settings
python process_dependency_data.py --min-data-points 10
```

**Output**:
- `dependency_timeseries.csv` - Main time-series data
- `quality_report.txt` - Data quality assessment
- `source_attribution.csv` - Source tracking

## Data Files

### dependency_timeseries.csv

Columns:
- `package` (str): Package name
- `date` (datetime): Release date
- `version` (str): Package version
- `total_dependencies` (int): Total dependency count (direct + transitive)
- `source` (str): Data source (`conda-forge` or `pypi`)

### quality_report.txt

Contains:
- Packages included/excluded
- Reason for exclusion (insufficient data points)
- Data point counts per package

### source_attribution.csv

Tracks which data source was used for each package:
- `package` (str): Package name
- `source` (str): Data source
- `count` (int): Number of versions from this source

## Data Quality Notes

### Completeness
- **conda-forge**: Complete data since ~2016 (when conda-forge launched)
- **Pre-2016**: Limited conda-forge data; may need supplementing with PyPI or GitHub
- **PyPI**: Variable historical metadata quality; improved significantly after 2015

### Known Limitations
1. **Early 2000s data**: May be sparse for some packages due to poor historical metadata
2. **Transitive dependencies**: Calculated from direct dependencies listed in metadata; may not capture full installation tree
3. **System dependencies**: Only captured for conda-forge packages; PyPI data underestimates true complexity
4. **Package exclusions**: Packages with <5 data points excluded by default

### Validation
- Spot-check key versions against actual installations
- Cross-reference with academic literature on dependency evolution
- Compare conda-forge vs PyPI counts for packages available in both

## Citation

If using this data in publications, please cite:
- Libraries.io dataset (for background research): Decan et al. (2017)
- conda-forge project: https://conda-forge.org
- PyPI: Python Package Index, https://pypi.org

## Reproducibility

To ensure reproducibility:
1. Raw JSON files should be archived with collection timestamps
2. Document conda-forge commit SHAs for feedstock repositories
3. Record PyPI API access dates
4. Preserve processing scripts with exact dependency versions

## Contact

For questions about this data collection methodology, please refer to the main repository README or open an issue.
