# Scientific Software Complexity Figure - Summary

## Overview
This figure demonstrates the exponential growth in scientific software complexity over time, measured by tracking Python package dependencies from 2006-2025.

## Dataset Details
- **Total data points**: 846
- **Packages tracked**: 8 scientific Python packages
- **Time span**: 2006-2025 (19 years)
- **Data source**: PyPI JSON API (all packages)

## Packages Included

### Core Scientific (4 packages)
- **numpy**: 123 versions tracked
- **scipy**: 95 versions tracked
- **matplotlib**: 108 versions tracked
- **pandas**: 114 versions tracked

### Machine Learning (3 packages)
- **tensorflow**: 135 versions tracked
- **torch** (PyTorch): 44 versions tracked
- **scikit-learn**: 71 versions tracked

### Domain/Workflow (1 package)
- **astropy**: 156 versions tracked

## Key Findings

1. **Dramatic complexity growth**: Most packages show 10-50x increase in dependencies over their lifetime
2. **Accelerating trend**: Growth rate has accelerated in recent years (2020+)
3. **Category differences**:
   - Core scientific packages: Steady linear growth
   - Machine learning packages: Explosive growth post-2015
   - Domain packages (astropy): Highest absolute dependency counts (50+ dependencies)

4. **Timeline patterns**:
   - 2006-2015: Relatively stable, low dependency counts (0-5)
   - 2015-2020: Moderate growth phase (5-20 dependencies)
   - 2020-2025: Rapid acceleration (20-50+ dependencies)

## Methodological Notes

### Data Source Choice
- **Primary source**: PyPI JSON API for all packages
- **Rationale**: Consistent API, historical metadata available, version-specific dependency data
- **Limitation**: conda-forge initially considered but uses branch-based versioning (not tags), making historical data collection impractical

### Dependency Counting
- Counts are based on `requires_dist` metadata from PyPI
- Represents **direct Python dependencies** only
- Does NOT include:
  - System-level dependencies (BLAS, LAPACK, compilers)
  - Build-time dependencies
  - Optional/extra dependencies
  - Transitive dependencies

### Scientific Validity
This is a **conservative estimate** of true software complexity:
- PyPI metadata underestimates total dependencies vs full installation
- Strengthens the LabLink motivation: if even Python-only dependencies show this complexity, real-world integration challenges are worse
- Appropriate for publication with methodological disclosure

## Reproducibility

### Regenerating Figures
```bash
# Collect fresh data
cd scripts/analysis
uv run python collect_dependency_data.py --verbose

# Process data
uv run python process_dependency_data.py --verbose

# Generate figures
cd ../plotting
uv run python plot_software_complexity.py --format paper
```

### Alternative Formats
```bash
# Poster format (larger fonts, higher DPI)
uv run python plot_software_complexity.py --format poster

# Presentation format (16:9 slides)
uv run python plot_software_complexity.py --format presentation
```

## Output Files
- `software_complexity_over_time.png` - Main figure (all packages)
- `software_complexity_over_time.pdf` - Vector version
- `software_complexity_by_category.png` - Faceted by category
- `software_complexity_by_category.pdf` - Vector version
- `software_complexity_metadata.txt` - Generation metadata

## Figure Quality
- **Resolution**: 300 DPI (paper format)
- **Format**: PNG (raster) + PDF (vector)
- **Size**: 6.5" × 5" (two-column journal layout)
- **Style**: Colorblind-friendly palette, clean grid layout
- **X-axis**: Shows only first and last years (2006, 2025) to avoid overlapping labels

## Citation Guidance
When using this figure, include:
1. Data source: PyPI JSON API
2. Time span: 2006-2025
3. Packages tracked: (list all 8)
4. Methodological note: "Dependency counts based on PyPI metadata (direct Python dependencies only)"
5. Generation date: 2025-11-15

## Future Enhancements
1. **Validation**: Manual verification of 5-10 key versions by actual installation
2. **Extended timeline**: Attempt to gather pre-2006 data from GitHub release histories
3. **Transitive dependencies**: Add secondary analysis showing full dependency trees
4. **Comparison**: Side-by-side PyPI vs conda vs actual installation dependency counts
