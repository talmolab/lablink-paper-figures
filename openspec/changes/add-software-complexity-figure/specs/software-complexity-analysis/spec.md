# Software Complexity Analysis Specification

## ADDED Requirements

### Requirement: Data Collection from Multiple Sources
The system SHALL collect historical dependency data for scientific Python packages using source-specific strategies optimized for scientific software accuracy.

#### Scenario: Collect from conda-forge for compiled scientific packages
- **GIVEN** a compiled scientific package (NumPy, SciPy, matplotlib, pandas, scikit-learn, AstroPy)
- **WHEN** the data collection script runs with conda-forge as the source
- **THEN** dependency metadata is extracted from conda-forge feedstock repositories
- **AND** the data includes Python dependencies AND system-level dependencies (BLAS, compilers, etc.)
- **AND** historical data is obtained by parsing `meta.yaml` files from git history
- **AND** the data is saved to `data/raw/software_complexity/conda_forge_metadata/{package}_meta.json`

#### Scenario: Collect from PyPI for pure-Python packages
- **GIVEN** a pure-Python or ML package with simpler distribution (TensorFlow, PyTorch, Jupyter)
- **WHEN** the data collection script runs with PyPI as the source
- **THEN** release dates and version metadata are fetched via the PyPI JSON API
- **AND** dependency lists are extracted from the `requires_dist` field for each version
- **AND** the data is saved to `data/raw/software_complexity/pypi_metadata/{package}_versions.json`

#### Scenario: Validate with GitHub repository analysis
- **GIVEN** 5-10 key package versions selected for validation
- **WHEN** the validation script analyzes historical releases
- **THEN** requirements files are parsed from tagged releases on GitHub
- **AND** dependency counts are compared against conda-forge/PyPI data for quality assessment
- **AND** validation results are saved to `data/raw/software_complexity/github_validation/validation_results.json`

### Requirement: Representative Package Selection
The system SHALL track a curated set of 8-10 representative scientific Python packages that span different eras, domains, and dependency patterns.

#### Scenario: Core scientific computing packages
- **GIVEN** the need to establish a baseline
- **WHEN** selecting packages for the core category
- **THEN** NumPy, SciPy, matplotlib, and pandas are included
- **AND** these packages represent the foundational scientific stack (2001-2010 era)

#### Scenario: Modern machine learning packages
- **GIVEN** the need to show recent complexity growth
- **WHEN** selecting packages for the ML category
- **THEN** TensorFlow, PyTorch, and scikit-learn are included
- **AND** these packages represent the deep learning era (2015-present)

#### Scenario: Domain-specific packages
- **GIVEN** the need to show domain diversity
- **WHEN** selecting packages for domain-specific analysis
- **THEN** at least one package from bioinformatics, astronomy, or related domains is included
- **AND** Jupyter is included to represent notebook-based workflows

### Requirement: Data Processing Pipeline
The system SHALL process raw dependency data into cleaned time-series format suitable for visualization.

#### Scenario: Aggregate dependency counts by release date
- **GIVEN** raw dependency data from conda-forge and PyPI sources
- **WHEN** the processing script runs
- **THEN** dependency counts are aggregated by package and release date
- **AND** duplicates and conflicts are resolved using a priority order (GitHub validation > conda-forge > PyPI)
- **AND** the output includes columns: package, date, version, total_dependencies, direct_dependencies, source
- **AND** a source attribution file tracks which data source was used for each data point

#### Scenario: Handle missing or incomplete data
- **GIVEN** some packages have incomplete historical data
- **WHEN** processing the raw data
- **THEN** missing dependency counts are flagged for manual investigation
- **AND** packages with insufficient data points (<5 releases) are excluded from analysis
- **AND** a data quality report is generated in `data/processed/software_complexity/quality_report.txt`

#### Scenario: Save processed time-series data
- **GIVEN** aggregated and cleaned dependency data
- **WHEN** processing is complete
- **THEN** the final dataset is saved to `data/processed/software_complexity/dependency_timeseries.csv`
- **AND** the file is UTF-8 encoded with comma separators
- **AND** the file includes a header row with column names

### Requirement: Configurable Visualization Output
The system SHALL generate publication-quality figures with configurable formatting for different contexts (paper, poster, presentation).

#### Scenario: Generate figure for paper publication
- **GIVEN** processed dependency time-series data
- **WHEN** the plotting script runs with `--format paper`
- **THEN** the figure uses 14pt font sizes
- **AND** the output is saved as both PNG (300 DPI) and PDF (vector)
- **AND** the figure dimensions are optimized for two-column journal layout (6.5" width)

#### Scenario: Generate figure for poster presentation
- **GIVEN** processed dependency time-series data
- **WHEN** the plotting script runs with `--format poster`
- **THEN** the figure uses 20pt font sizes for readability at distance
- **AND** the output is saved as both PNG (300 DPI) and PDF (vector)
- **AND** the figure dimensions are larger (12" width)

#### Scenario: Generate figure for slide presentation
- **GIVEN** processed dependency time-series data
- **WHEN** the plotting script runs with `--format presentation`
- **THEN** the figure uses 16pt font sizes
- **AND** the output is saved as both PNG (150 DPI) and PDF (vector)
- **AND** the figure dimensions match standard slide aspect ratio (10" x 7.5")

### Requirement: Time-Series Visualization Design
The system SHALL generate a connected scatter plot showing dependency growth over time with clear visual encoding.

#### Scenario: Plot individual package trajectories
- **GIVEN** processed time-series data for multiple packages
- **WHEN** generating the main figure
- **THEN** each package is plotted as a connected scatter plot
- **AND** each package has a distinct color from a colorblind-friendly palette
- **AND** data points represent individual releases with markers
- **AND** lines connect points chronologically to show trajectory

#### Scenario: Add trend lines for clarity
- **GIVEN** individual package trajectories
- **WHEN** generating the main figure
- **THEN** LOESS smoothed trend lines are overlaid on scatter points
- **AND** trend lines are semi-transparent to avoid obscuring data points
- **AND** trend lines help visualize overall growth patterns

#### Scenario: Format axes and labels
- **GIVEN** the complete plot
- **WHEN** finalizing the figure
- **THEN** the x-axis shows years from 2000 to 2025
- **AND** the y-axis shows total dependency count
- **AND** the y-axis uses logarithmic scale if the range spans more than 2 orders of magnitude
- **AND** grid lines are included for readability
- **AND** a legend identifies all packages with category grouping

#### Scenario: Add contextual annotations
- **GIVEN** the plotted trends
- **WHEN** finalizing the figure
- **THEN** key inflection points are annotated (e.g., "Deep Learning Era 2015+")
- **AND** annotations use arrows or text boxes that don't obscure data
- **AND** annotations provide narrative context for observed trends

### Requirement: Supplementary Breakdown Figures
The system SHALL generate supplementary figures showing per-package details and category comparisons.

#### Scenario: Generate per-category comparison
- **GIVEN** packages grouped into categories (core, ML, domain-specific)
- **WHEN** generating supplementary figures
- **THEN** a faceted plot shows each category in a separate panel
- **AND** all panels use consistent axis ranges for comparison
- **AND** the output is saved to `figures/supplementary/software_complexity_by_category.*`

#### Scenario: Generate individual package trend details
- **GIVEN** individual package time-series data
- **WHEN** generating supplementary figures
- **THEN** a multi-panel figure shows each package separately
- **AND** each panel includes both direct and transitive dependencies
- **AND** the output is saved to `figures/supplementary/software_complexity_individual_packages.*`

### Requirement: Reproducibility and Documentation
The system SHALL ensure all data collection, processing, and visualization steps are reproducible and well-documented.

#### Scenario: Command-line interface for data collection
- **GIVEN** the data collection script
- **WHEN** a user runs the script
- **THEN** clear help text explains all parameters using `--help`
- **AND** the script accepts `--packages` to specify which packages to analyze
- **AND** the script accepts `--sources` to choose data sources (conda-forge, pypi, github, all)
- **AND** the script automatically selects appropriate source per package (conda-forge for compiled, PyPI for pure-Python)
- **AND** the script provides progress output during execution

#### Scenario: Command-line interface for visualization
- **GIVEN** the plotting script
- **WHEN** a user runs the script
- **THEN** clear help text explains all parameters using `--help`
- **AND** the script accepts `--format` with choices (paper, poster, presentation)
- **AND** the script accepts `--output-dir` to specify where figures are saved
- **AND** the script provides confirmation of generated files

#### Scenario: Include metadata with outputs
- **GIVEN** generated figures
- **WHEN** the plotting script completes
- **THEN** a metadata file is created alongside figures
- **AND** the metadata includes generation timestamp, data sources used (conda-forge commit SHAs, PyPI access dates), and package list
- **AND** the metadata documents which source was used for each package
- **AND** the metadata is saved as `figures/main/software_complexity_metadata.txt`
