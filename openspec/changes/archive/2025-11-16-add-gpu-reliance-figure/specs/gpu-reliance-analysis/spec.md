# Specification: gpu-reliance-analysis

## Purpose

Track and visualize the evolution of GPU hardware dependency in scientific Python packages from 2010-2025, demonstrating the transition from optional GPU acceleration to practical hardware requirements. This analysis quantifies GPU reliance trends across machine learning, scientific computing, and biology domains to support the LabLink paper's argument about reproducibility challenges in modern computational research.

---

## ADDED Requirements

### Requirement: GPU Dependency Data Collection from PyPI

The system SHALL collect historical GPU dependency metadata from PyPI JSON API for 10 representative scientific packages spanning 2010-2025.

#### Scenario: Collect TensorFlow GPU metadata across all versions

**Given** the package name "tensorflow"
**When** collecting GPU metadata via PyPI JSON API
**Then** the system retrieves all released versions with timestamps
**And** extracts GPU-related dependencies from `requires_dist` field for each version
**And** identifies CUDA version requirements where specified
**And** saves raw data to `data/raw/gpu_reliance/pypi_metadata/tensorflow_versions.json`

#### Scenario: Handle CUDA-specific package variants

**Given** the base package "cupy" with variants "cupy-cuda102", "cupy-cuda110", "cupy-cuda11x", "cupy-cuda12x"
**When** collecting data for the cupy family
**Then** the system collects metadata for all variants
**And** tracks which CUDA version each variant supports
**And** normalizes variant data to aggregate under base package "cupy"
**And** records the CUDA version requirement separately

#### Scenario: Extract GPU dependencies using keyword detection

**Given** a package version with `requires_dist` containing "cudatoolkit >=11.2"
**When** analyzing dependencies for GPU content
**Then** the system identifies "cudatoolkit" as a GPU dependency
**And** extracts minimum CUDA version "11.2"
**And** increments GPU dependency count
**And** flags package as requiring external CUDA installation

#### Scenario: Collect TensorFlow vs TensorFlow-GPU split history

**Given** TensorFlow had separate "tensorflow" and "tensorflow-gpu" packages until version 2.1.0
**When** collecting TensorFlow data
**Then** the system collects both package histories
**And** identifies the unification point at TensorFlow 2.1.0 (Jan 2020)
**And** marks pre-2.1 versions as having separate GPU variant
**And** marks post-2.1 versions as unified with bundled GPU support

---

### Requirement: GPU Dependency Scoring System

The system SHALL calculate a GPU dependency score (0-5) for each package version quantifying the level of GPU reliance.

#### Scenario: Score package with no GPU support (score 0)

**Given** a package version of scikit-image 0.18.0
**When** calculating GPU score
**Then** the system finds no GPU-related keywords in dependencies
**And** finds no CUDA dependencies
**And** assigns score 0 (No GPU support)

#### Scenario: Score GPU-first package (score 5)

**Given** a package version of CuPy 13.0.0
**When** calculating GPU score
**Then** the system identifies "cupy" as a GPU-first package
**And** verifies CUDA is required (not optional)
**And** assigns score 5 (GPU-First design)

#### Scenario: Score package with hard GPU requirement (score 4)

**Given** a package version of JAX 0.4.0 with required CUDA dependencies
**When** calculating GPU score
**Then** the system detects "cudatoolkit" in required dependencies (not extras)
**And** verifies installation fails without CUDA
**And** assigns score 4 (Hard Required)

#### Scenario: Score package with bundled GPU support (score 3)

**Given** a package version of PyTorch 2.0.0
**When** calculating GPU score
**Then** the system identifies package as bundling CUDA in wheels
**And** recognizes GPU is practical requirement for real workloads
**And** assigns score 3 (Practical Required)

#### Scenario: Score package with optional GPU via extras (score 1-2)

**Given** a package version of Numba 0.56.0 with CUDA support in extras_require
**When** calculating GPU score
**Then** the system detects "cuda" in optional dependencies
**And** verifies CPU fallback exists
**And** assigns score 1-2 (Optional GPU, flagged for manual review)

---

### Requirement: Manual Validation of Key Milestone Versions

The system SHALL support manual validation and refinement of GPU scores for 20-30 key milestone versions across packages.

#### Scenario: Validate first GPU support version for TensorFlow

**Given** TensorFlow 0.12.0 (Dec 2016) was first version with separate tensorflow-gpu package
**When** performing manual validation
**Then** developer reviews GitHub release notes for v0.12.0
**And** confirms separate tensorflow-gpu package required external CUDA 8.0
**And** verifies automatic score assignment is appropriate
**And** documents validation in `data/raw/gpu_reliance/github_validation/validation_log.csv`

#### Scenario: Refine ambiguous GPU score

**Given** a package version automatically assigned score 2 (Optional GPU)
**When** performing manual validation via GitHub documentation review
**Then** developer reads installation instructions and README
**And** determines if GPU is truly optional or practically required
**And** adjusts score up/down if evidence contradicts automatic assignment
**And** records rationale in validation log

#### Scenario: Identify GPU-first design from repository analysis

**Given** OpenMM 1.0 (Jan 2010) claimed GPU support from inception
**When** validating via GitHub repository
**Then** developer checks for `.cu` CUDA files in early commits
**And** reviews architecture documentation
**And** confirms GPU-first design (score 5)
**And** validates earliest version date matches repository tag

---

### Requirement: Data Processing and Quality Control

The system SHALL process raw GPU metadata into clean time-series CSV format with quality validation.

#### Scenario: Aggregate and normalize package data

**Given** raw JSON files for all 10 packages in `data/raw/gpu_reliance/pypi_metadata/`
**When** processing data
**Then** the system loads all JSON files
**And** normalizes package variant names (cupy-cuda* → cupy)
**And** aggregates TensorFlow and TensorFlow-GPU histories
**And** exports to `data/processed/gpu_reliance/gpu_timeseries.csv` with columns: package, version, date, gpu_score, cuda_version, gpu_deps_count, requires_external_cuda, source

#### Scenario: Filter packages with insufficient data

**Given** a package with only 3 versions collected
**When** applying quality filters (minimum 5 versions required)
**Then** the system excludes the package from final dataset
**And** logs exclusion reason in `data/processed/gpu_reliance/quality_report.txt`
**And** reports excluded package name and version count

#### Scenario: Generate source attribution report

**Given** processed data from multiple packages
**When** generating metadata reports
**Then** the system creates `data/processed/gpu_reliance/source_attribution.csv`
**And** lists each package with version count and data source (pypi)
**And** calculates total data points across all packages
**And** identifies date range (earliest to latest version)

---

### Requirement: Visualization with Configurable Format Presets

The system SHALL generate publication-quality time-series figures showing GPU dependency evolution with three format presets (paper, poster, presentation).

#### Scenario: Generate main figure in paper format

**Given** processed GPU time-series data in CSV format
**When** generating main figure with `--format paper`
**Then** the system creates a connected scatter plot
**And** plots all 10 packages with distinct colors (colorblind-friendly palette)
**And** uses Y-axis label "GPU Dependency Level (0=None, 5=GPU-First)"
**And** uses X-axis label "Year" with only first and last years shown
**And** applies font size 14pt, DPI 300, figure size 6.5" × 5"
**And** saves to `figures/main/gpu_reliance_over_time.png` and `.pdf`

#### Scenario: Generate category comparison figure

**Given** packages categorized into ML/Deep Learning, Scientific Computing, and Biology domains
**When** generating category comparison figure
**Then** the system creates 3 faceted subplots (one per category)
**And** plots packages within each category with consistent styling
**And** shares X-axis across all subplots
**And** labels each panel with category name
**And** saves to `figures/main/gpu_reliance_by_category.png` and `.pdf`

#### Scenario: Generate poster format with larger fonts

**Given** the same processed data
**When** generating main figure with `--format poster`
**Then** the system applies font size 20pt, DPI 300, figure size 12" × 9"
**And** maintains same plot structure with larger, more readable text
**And** overwrites previous outputs with poster-sized versions
**And** updates `figures/main/gpu_reliance_metadata.txt` with format preset "poster"

#### Scenario: Support presentation format for slides

**Given** the same processed data
**When** generating main figure with `--format presentation`
**Then** the system applies font size 16pt, DPI 150, figure size 10" × 7.5" (16:9 aspect)
**And** optimizes for projection and screen viewing
**And** generates both PNG and PDF outputs

---

### Requirement: Comprehensive Documentation and Metadata

The system SHALL generate documentation explaining methodology, data provenance, and figure generation parameters.

#### Scenario: Generate data collection methodology README

**Given** completion of data collection
**When** creating documentation
**Then** the system generates `data/gpu_reliance_README.md`
**And** documents PyPI JSON API as primary data source
**And** explains GPU scoring rubric (0-5 scale)
**And** lists all 10 tracked packages with categories
**And** provides reproduction instructions
**And** notes limitations (PyPI metadata may not capture all GPU requirements)

#### Scenario: Generate figure metadata file

**Given** successful figure generation
**When** saving figures
**Then** the system creates `figures/main/gpu_reliance_metadata.txt`
**And** records generation timestamp
**And** documents format preset used
**And** lists data source file path
**And** includes package list and data point counts
**And** shows date range (earliest to latest)
**And** reports source breakdown (all from pypi)

#### Scenario: Update main repository README

**Given** new GPU reliance analysis capability added
**When** updating documentation
**Then** the system adds new section to main `README.md`
**And** provides quick start guide matching software complexity section style
**And** explains three-step process: collect → process → visualize
**And** documents all three format presets
**And** shows example commands with `uv run python` prefix

---

### Requirement: Reproducibility and Code Quality

The system SHALL ensure full reproducibility of GPU reliance analysis with clean, maintainable code following project conventions.

#### Scenario: End-to-end reproduction in single session

**Given** a fresh clone of the repository
**When** running the complete pipeline:
```bash
cd scripts/analysis
uv run python collect_gpu_data.py --verbose
uv run python process_gpu_data.py --verbose
cd ../plotting
uv run python plot_gpu_reliance.py --format paper --verbose
```
**Then** the system completes without errors
**And** generates all expected output files
**And** produces bit-identical figures (within float precision)
**And** completes in under 30 minutes

#### Scenario: Code style matches project conventions

**Given** newly created Python scripts
**When** running `ruff check` and `ruff format`
**Then** all scripts pass linting with no errors
**And** formatting is Black-compatible (88 char line length)
**And** imports are properly ordered (stdlib, third-party, local)
**And** functions have docstrings
**And** type hints are used where appropriate

#### Scenario: Reuse existing dependencies (no new packages)

**Given** the project's current dependency set
**When** implementing GPU reliance analysis
**Then** the system uses only existing packages (requests, pandas, matplotlib, seaborn)
**And** requires no additions to `pyproject.toml`
**And** follows same import patterns as software complexity scripts
