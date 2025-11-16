# Design Document: Scientific Software Complexity Figure

## Context

Scientific software has grown increasingly complex over the past 20+ years, with modern packages accumulating hundreds of dependencies. This trend has significant implications for reproducibility, maintenance burden, and highlights the motivation for tools like LabLink that provide controlled computational environments. This figure will provide empirical evidence for these trends by visualizing dependency growth across representative scientific Python packages from 2000-2025.

**Background Research:** Extensive research was conducted on:
- Scientific software packages spanning multiple domains and eras
- Data sources for historical dependency tracking (conda-forge, PyPI, GitHub)
- Academic literature on dependency evolution and software bloat
- Best practices for time-series visualization in academic publications
- Comparative analysis of PyPI vs conda-forge metadata completeness for scientific packages

**Stakeholders:**
- Paper authors who need compelling empirical evidence for the reproducibility crisis
- Readers who need to understand the context and motivation for LabLink
- Reviewers who will scrutinize data collection methodology and visualization choices

## Goals / Non-Goals

**Goals:**
- Generate publication-quality figure showing dependency growth over time (2000-2025)
- Track 8-10 representative scientific Python packages across multiple domains
- Support configurable output formats (paper, poster, presentation) with appropriate styling
- Ensure reproducibility through automated data collection and processing pipeline
- Provide both aggregate trends (main figure) and detailed breakdowns (supplementary)
- Validate findings against existing academic literature on dependency evolution

**Non-Goals:**
- Analyzing dependency networks or relationships between packages (out of scope)
- Real-time dependency tracking or monitoring (historical analysis only)
- Coverage of non-Python ecosystems (focus on Python scientific stack only)
- Automated dependency resolution or management (visualization only)
- Interactive or web-based visualizations (static figures for publication)
- Comprehensive coverage of all distribution channels (focused on conda-forge + PyPI as most relevant)

## Decisions

### Decision 1: conda-forge-First Data Collection Strategy

**What:** Collect dependency data using a source-per-package strategy optimized for scientific software:

**Primary Sources by Package Type:**
1. **conda-forge repodata** (for compiled scientific packages): NumPy, SciPy, matplotlib, pandas, scikit-learn, AstroPy
   - Access via conda-forge feedstock repositories: `https://github.com/conda-forge/{package}-feedstock`
   - Parse `meta.yaml` files from git history for complete dependency metadata including system libraries
   - Query conda repodata.json API for structured version/dependency data

2. **PyPI JSON API** (for pure-Python packages): TensorFlow, PyTorch, Jupyter
   - Official package registry with version-specific dependency metadata
   - Endpoint: `https://pypi.org/pypi/{package}/{version}/json`
   - Extract `requires_dist` field for dependency lists

3. **GitHub releases** (validation): Spot-check 5-10 key versions across packages
   - Direct analysis of `requirements.txt`, `setup.py`, or `pyproject.toml` from tagged releases
   - Ground truth for data quality assessment

**Why conda-forge for Scientific Packages:**
- **Complete system-level dependencies**: Captures compiled libraries (BLAS, LAPACK, compilers) that PyPI metadata omits
- **Accurate for scientific reality**: Most scientific users install via conda, not pip
- **Better historical metadata**: conda-forge `meta.yaml` files have complete dependency specs since ~2016
- **Tells the right story**: Shows true complexity including system dependencies, aligning with LabLink's motivation (reproducibility, containerization)

**Example - SciPy 1.7.0 metadata comparison:**
- PyPI `requires_dist`: `["numpy>=1.16.5"]` (1 Python dependency)
- conda-forge `meta.yaml`: `numpy>=1.16.5, python>=3.7, blas, libopenblas, libgfortran` (5+ dependencies including system libs)
- **Reality**: Installing SciPy brings in dozens of transitive dependencies

**Why PyPI for ML/Pure-Python Packages:**
- TensorFlow and PyTorch have simpler PyPI distributions (pre-compiled wheels)
- Jupyter and pure-Python packages don't have significant compiled dependency differences
- PyPI metadata is sufficient and authoritative for these cases

**Alternatives considered:**
- **Libraries.io dataset**: Indexes primarily PyPI; misses conda-specific dependencies and system libraries critical for scientific packages
- **PyPI-only approach**: Severely underestimates complexity for compiled scientific packages (NumPy, SciPy, matplotlib)
- **conda-forge-only**: Some packages (especially newer ML frameworks) have better PyPI distribution metadata
- **BigQuery PyPI dataset**: Comprehensive but requires Google Cloud setup, costs, and still misses conda ecosystem

**Priority order for conflicts:** GitHub (ground truth) > conda-forge (for compiled packages) > PyPI (for pure-Python packages)

**Data Collection Implementation:**
```python
PACKAGE_SOURCES = {
    # Compiled scientific packages - use conda-forge
    'numpy': 'conda-forge',
    'scipy': 'conda-forge',
    'matplotlib': 'conda-forge',
    'pandas': 'conda-forge',
    'scikit-learn': 'conda-forge',
    'astropy': 'conda-forge',

    # Pure-Python or simpler PyPI distributions
    'tensorflow': 'pypi',
    'pytorch': 'pypi',
    'jupyter': 'pypi',
}
```

### Decision 2: Dependency Counting Methodology

**What:** Track **total dependencies** (direct + transitive) rather than direct dependencies only.

**Why:**
- Total dependencies better represent the true complexity burden on users
- Illustrates the "dependency hell" problem where transitive deps grow exponentially
- Academic literature (Decan et al. 2017) shows transitive deps are major source of fragility
- More compelling narrative for motivating LabLink's controlled environments

**Alternatives considered:**
- **Direct dependencies only**: Simpler to collect but underestimates true complexity
- **Both direct and transitive**: More complete but clutters visualization; relegated to supplementary figures

**Implementation:** Use package metadata to count all required packages for a given version.

### Decision 3: Package Selection Strategy

**What:** Select 8-10 packages across three categories:

**Core Scientific Stack (4 packages):**
- NumPy (2006+): Foundation of scientific Python
- SciPy (2001+): Scientific computing algorithms
- matplotlib (2003+): Visualization foundation
- pandas (2008+): Data analysis framework

**Modern ML (3 packages):**
- TensorFlow (2015+): Industrial ML framework
- PyTorch (2016+): Research-focused ML framework
- scikit-learn (2007+): Classical ML algorithms

**Domain-Specific/Workflow (2-3 packages):**
- Jupyter (2014+): Notebook-based workflows (92% YoY growth)
- AstroPy or BioPython: Domain-specific example

**Why:**
- Spans different eras (2001-2025) showing evolution over time
- Covers multiple domains demonstrating breadth of scientific computing
- Includes both lightweight (NumPy) and heavyweight (TensorFlow) packages
- Well-documented packages with reliable historical data
- Mix of "old" (SciPy) and "new" (PyTorch) shows inflection points

**Alternatives considered:**
- **More packages (15-20)**: Too cluttered for main figure; better for supplementary
- **Fewer packages (3-5)**: Insufficient to show diversity and trends
- **Domain-specific only**: Misses foundational stack and ML revolution

### Decision 4: Visualization Approach

**What:** Connected scatter plot with LOESS trend lines.

**Design elements:**
- **X-axis:** Years (2000-2025)
- **Y-axis:** Total dependency count (logarithmic scale if range >100x)
- **Encoding:** One color per package (colorblind-friendly palette)
- **Points:** Individual releases as scatter markers
- **Lines:** Connected chronologically to show trajectory
- **Trends:** LOESS smoothed overlay (semi-transparent)
- **Annotations:** Key inflection points (e.g., "Deep Learning Era 2015+")

**Why:**
- Scatter points show actual data (transparency and reproducibility)
- Connected lines show evolution trajectory for each package
- Trend lines smooth noisy release schedules for clearer patterns
- Annotations provide narrative context for observed trends
- Logarithmic scale accommodates wide range (NumPy ~20 deps vs TensorFlow ~200 deps)

**Alternatives considered:**
- **Line plot only**: Obscures individual release data points
- **Stacked area chart**: Shows aggregate but loses per-package detail
- **Heatmap**: Good for many packages but less intuitive for trends
- **Small multiples**: Better for detailed comparison; used in supplementary figures

**Reference:** "Line Graph or Scatter Plot? Automatic Selection of Methods for Visualizing Trends in Time Series" recommends scatter + trend lines for this use case.

### Decision 5: Configurable Format Presets

**What:** Three format presets with different styling:

| Preset | Font Size | DPI | Dimensions | Use Case |
|--------|-----------|-----|------------|----------|
| `paper` | 14pt | 300 | 6.5" width | Two-column journal layout |
| `poster` | 20pt | 300 | 12" width | Conference poster (readable at distance) |
| `presentation` | 16pt | 150 | 10" × 7.5" | Slide deck (16:9 aspect ratio) |

**Why:**
- Different contexts have different readability requirements
- Font sizes from established visualization best practices
- DPI values match publication standards (300 for print, 150 for screen)
- Dimensions optimize for common layout constraints

**Implementation:** Use command-line flag `--format {paper,poster,presentation}` to select preset.

**Alternatives considered:**
- **Separate scripts per format**: Code duplication and maintenance burden
- **Manual configuration**: Error-prone and not reproducible
- **Single format only**: Inflexible; requires regeneration for different contexts

### Decision 6: Data Storage and Processing Workflow

**What:** Three-stage pipeline:

```
1. Raw Data Collection
   └─> data/raw/software_complexity/
       ├── conda_forge_metadata/
       │   ├── numpy_meta.json
       │   ├── scipy_meta.json
       │   └── ... (one per conda package)
       ├── pypi_metadata/
       │   ├── tensorflow_versions.json
       │   ├── pytorch_versions.json
       │   └── ... (one per PyPI package)
       └── github_validation/
           ├── validation_results.json
           └── sample_requirements.txt

2. Data Processing
   └─> data/processed/software_complexity/
       ├── dependency_timeseries.csv
       ├── quality_report.txt
       └── source_attribution.csv (tracks which source used per data point)

3. Visualization
   └─> figures/main/
       ├── software_complexity_over_time.{png,pdf}
       └── software_complexity_metadata.txt
   └─> figures/supplementary/
       ├── software_complexity_by_category.{png,pdf}
       └── software_complexity_individual_packages.{png,pdf}
```

**Why:**
- Clear separation of concerns (collect → process → visualize)
- Raw data preserved for reproducibility and re-analysis
- Intermediate processing step allows data quality validation
- Follows project conventions (`data/raw/`, `data/processed/`, `figures/`)

**Implementation:**
- `scripts/analysis/collect_dependency_data.py` → raw data
- Processing logic integrated into collection script → processed data
- `scripts/plotting/plot_software_complexity.py` → figures

## Risks / Trade-offs

### Risk 1: Data Availability and Quality
- **Risk:** Historical dependency data may be incomplete or inaccurate for older package versions, especially pre-2016 for conda-forge
- **Mitigation:** conda-forge launched in 2016; for earlier data (2000-2016), supplement with PyPI or GitHub historical analysis. Multi-source validation, data quality report generation, exclude packages with <5 data points
- **Trade-off:** May need to exclude some interesting packages due to data gaps; early 2000s data may be less complete but still show directional trends

### Risk 2: API Rate Limits
- **Risk:** PyPI and GitHub APIs have rate limits that could slow data collection
- **Mitigation:** Implement exponential backoff, cache responses, allow GitHub token for authentication
- **Trade-off:** Initial data collection may take several hours; acceptable for one-time analysis

### Risk 3: Visualization Complexity
- **Risk:** Plotting 8-10 packages on one figure may become cluttered
- **Mitigation:** Use LOESS smoothing, semi-transparent trend lines, clear color palette, supplement with faceted plots
- **Trade-off:** Main figure shows aggregate trends; detailed analysis in supplementary figures

### Risk 4: Dependency Counting Methodology Variability
- **Risk:** conda-forge and PyPI count dependencies differently (conda includes system libs, PyPI often doesn't); mixing sources may create inconsistencies
- **Mitigation:** Document methodology clearly, use consistent source per package category (conda for compiled, PyPI for pure-Python), validate against actual installations, include source attribution in processed data
- **Trade-off:** Absolute counts not directly comparable between conda/PyPI packages, but this reflects real-world complexity differences; relative trends within each source remain valid and informative

### Risk 5: Reproducibility Over Time
- **Risk:** Data sources may change or become unavailable (conda-forge feedstocks reorganized, PyPI API changes)
- **Mitigation:** Archive raw metadata JSON files in repository (likely <10MB total), document exact conda-forge commit SHAs and PyPI API access dates, preserve data collection scripts
- **Trade-off:** Modest repository size increase (~10-20MB) but ensures long-term reproducibility

## Migration Plan

Not applicable (new capability, no existing implementation to migrate).

**Deployment steps:**
1. Implement data collection and processing pipeline
2. Run initial data collection and validate quality
3. Generate figures in all three formats
4. Review figures with paper authors for accuracy and clarity
5. Iterate on visualization design based on feedback
6. Archive final data and figures in repository

**Rollback:** Not applicable (no production dependencies).

## Open Questions

1. **Data archiving:** Should we commit raw conda-forge/PyPI metadata to the repository?
   - **Consideration:** Raw JSON files likely <10-20MB total (much smaller than Libraries.io dataset)
   - **Recommendation:** Commit raw metadata JSONs to ensure reproducibility; include conda-forge commit SHAs and collection timestamps

2. **Package selection finalization:** Should we include SLEAP as a domain-specific modern package?
   - **Consideration:** SLEAP is related to LabLink and shows modern ML dependency patterns
   - **Recommendation:** Include if data is available; otherwise use AstroPy or BioPython

3. **Annotation specificity:** How many annotations should we add to the main figure?
   - **Consideration:** Too many annotations clutter; too few miss context
   - **Recommendation:** Start with 2-3 key annotations (Deep Learning Era, NumPy 1.0, etc.) and adjust based on author feedback

4. **Supplementary figure necessity:** Are both category comparison and individual breakdown needed?
   - **Consideration:** Supplementary figures add value but require additional work
   - **Recommendation:** Implement both; authors can decide which to include in publication

5. **Color palette selection:** Which colorblind-friendly palette should we use?
   - **Consideration:** Need distinct colors for 8-10 packages
   - **Recommendation:** Use seaborn "colorblind" palette or Okabe-Ito palette (both support 8+ colors)