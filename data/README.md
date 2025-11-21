# Data Directory

This directory contains all data files used for figure generation, organized into raw (original) and processed (cleaned) data.

## Directory Structure

```
data/
├── raw/                    # Original, immutable data files (gitignored except READMEs)
│   ├── gpu_prices/         # Epoch AI ML Hardware Database (GPU pricing)
│   └── ...                 # Other external datasets
└── processed/              # Cleaned, transformed data ready for plotting
    ├── deployment_impact/  # Workshop timeline data
    ├── sleap_dependencies.json  # Cached SLEAP dependency data
    └── ...                 # Processed analysis results
```

## Data Organization Principles

### Raw Data (`data/raw/`)

**Purpose**: Store original, immutable data files exactly as downloaded/collected.

**Git status**: **Gitignored** (except README.md files)
- Raw data files are too large or change too frequently for git
- Each subdirectory should have a README.md documenting:
  - Data source (URL, API endpoint, manual collection)
  - Download/collection instructions
  - License and usage terms
  - Last updated date
  - File formats and schemas

**Example subdirectories**:
- `gpu_prices/` - Epoch AI ML Hardware Database CSV
- `software_complexity/` - conda-forge feedstock metadata (if cached)
- `survey_data/` - Workshop surveys, user feedback (if applicable)

### Processed Data (`data/processed/`)

**Purpose**: Store cleaned, transformed data ready for plotting.

**Git status**: **Selectively committed**
- Small processed files (<1MB) are committed for reproducibility
- Large processed files (>1MB) are gitignored, regenerate as needed
- Cached API responses are gitignored (can be refreshed)

**Characteristics**:
- Clean: Missing values handled, outliers addressed
- Standardized: Consistent formats, column names, units
- Aggregated: Summarized at appropriate granularity
- Documented: Metadata files describe processing steps

## Data Sources

### External Datasets

| Dataset | Location | Source | License | Download |
|---------|----------|--------|---------|----------|
| GPU Hardware Pricing | `raw/gpu_prices/` | Epoch AI | CC BY 4.0 | [epoch.ai/data/machine-learning-hardware](https://epoch.ai/data/machine-learning-hardware) |
| Software Dependencies | API calls | PyPI, conda-forge | Public APIs | Auto-fetched by scripts |
| SLEAP Dependencies | `processed/sleap_dependencies.json` | PyPI JSON API | Public API | Auto-fetched and cached |

### Manually Curated Data

| Dataset | Location | Purpose | Maintained By |
|---------|----------|---------|---------------|
| Workshop Timeline | `processed/deployment_impact/workshops.csv` | Deployment impact figure | Research team |

## Working with Data

### Downloading External Datasets

See individual `data/raw/<dataset>/README.md` files for download instructions.

**Example** (GPU pricing):
```bash
# 1. Visit https://epoch.ai/data/machine-learning-hardware
# 2. Click "Download Data" to get ZIP
# 3. Extract ml_hardware.csv to data/raw/gpu_prices/
ls data/raw/gpu_prices/ml_hardware.csv  # Verify
```

### Regenerating Processed Data

Most processed data can be regenerated from raw data:

```bash
# Software complexity
cd scripts/analysis
uv run python collect_dependency_data.py  # Fetch from APIs (20-40 min)
uv run python process_dependency_data.py  # Clean and aggregate
# Output: data/processed/dependency_data.csv

# SLEAP dependencies
cd ../plotting
uv run python generate_sleap_dependency_graph.py  # Auto-fetches and caches
# Output: data/processed/sleap_dependencies.json
```

### Using Cached Data

Many scripts cache expensive API calls:

```bash
# Use cached data (default, fast)
uv run python scripts/plotting/<script>.py

# Force refresh from APIs (slow, use when data is stale)
uv run python scripts/plotting/<script>.py --force-refresh
```

## Data Quality and Validation

### Raw Data Validation

Scripts validate raw data before processing:
- **Minimum record count**: Ensures sufficient data (e.g., ≥50 GPUs)
- **Date range**: Checks expected time span (e.g., 2006+)
- **Required fields**: Verifies essential columns present (price, date, name)
- **Data types**: Validates numeric fields, date formats

**Example** (GPU costs):
```
✓ Found 162 GPUs in dataset
✓ Date range: 2006-2025 (19 years)
✓ 127/162 (78%) have pricing data
```

### Processed Data Documentation

Each processed dataset should include:
- **Data file**: CSV, JSON, or Parquet format
- **Metadata file**: Processing date, script version, data sources
- **Schema documentation**: Column names, types, units, descriptions

## Privacy and Security

- **No credentials**: Never commit API tokens, passwords, or private keys
- **No PII**: Don't store personally identifiable information
- **Public data only**: Only use publicly available datasets or with proper licenses
- **Check licenses**: Verify usage rights for external datasets (CC BY, MIT, etc.)

## Adding New Data

When adding a new dataset:

1. **Create subdirectory**: `data/raw/<dataset-name>/`
2. **Add README**: Document source, license, download instructions
3. **Update .gitignore**: Add large files to `.gitignore`
4. **Process data**: Create script in `scripts/analysis/` to clean/transform
5. **Save processed**: Output to `data/processed/<dataset>.csv`
6. **Document processing**: Add metadata file with processing details
7. **Update this README**: Add row to data sources table

## Related Documentation

- [Analysis Figures](../docs/figures/analysis-figures/) - How data is used for figures
- [Development Guide](../docs/development/) - Contributing new analyses
- [Scripts README](../scripts/README.md) - Data processing scripts

## Data Size Guidelines

- **Raw data files**: Gitignore if >10MB
- **Processed files**: Commit if <1MB, gitignore if larger
- **API caches**: Always gitignore (can be regenerated)
- **Use git-lfs**: Consider for essential large files (>5MB)

## Subdirectory READMEs

Each data subdirectory should have its own README.md:
- [raw/gpu_prices/README.md](raw/gpu_prices/README.md) - GPU pricing dataset
- [processed/deployment_impact/README.md](processed/deployment_impact/README.md) - Workshop timeline
