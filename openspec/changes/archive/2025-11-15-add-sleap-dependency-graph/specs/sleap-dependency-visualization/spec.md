# Specification: SLEAP Dependency Network Visualization

## ADDED Requirements

### Requirement: Dependency Data Extraction

The system SHALL extract Python package dependency data from SLEAP's pyproject.toml file and build a complete transitive dependency graph using PyPI metadata APIs.

#### Scenario: Extract from local SLEAP installation

- **WHEN** user provides a local path to SLEAP repository (e.g., `C:\repos\sleap`)
- **THEN** the system SHALL parse the pyproject.toml file and extract all dependencies from `project.dependencies` section
- **AND** the system SHALL recursively fetch dependency metadata from PyPI JSON API for each package
- **AND** the system SHALL build a NetworkX DiGraph with packages as nodes and dependencies as directed edges

#### Scenario: Extract from GitHub URL

- **WHEN** user provides a GitHub raw URL to pyproject.toml (e.g., `https://github.com/talmolab/sleap/blob/develop/pyproject.toml`)
- **THEN** the system SHALL download the file content via HTTP request
- **AND** the system SHALL parse dependencies and build the transitive graph as with local files

#### Scenario: Handle optional dependencies

- **WHEN** SLEAP's pyproject.toml contains optional dependency groups (e.g., `[project.optional-dependencies]`)
- **THEN** the system SHALL include these by default to maximize complexity visualization
- **AND** the system SHALL support a `--exclude-optional` flag to exclude optional dependencies if specified

#### Scenario: Cache dependency data

- **WHEN** dependency graph is successfully built
- **THEN** the system SHALL save the graph data to `data/processed/sleap_dependencies.json` with timestamp and SLEAP version metadata
- **AND** on subsequent runs SHALL use cached data unless `--force-refresh` flag is provided

#### Scenario: Handle missing or unavailable packages

- **WHEN** a package is not found in PyPI metadata API
- **THEN** the system SHALL log a warning with the package name
- **AND** SHALL continue processing other dependencies without crashing
- **AND** SHALL include the package node without its transitive dependencies

### Requirement: Package Categorization

The system SHALL categorize packages into semantic domains (ML/DL, scientific computing, data processing, visualization, utilities) for visual encoding.

#### Scenario: Categorize well-known packages

- **WHEN** processing packages like PyTorch, NumPy, matplotlib, or pillow
- **THEN** the system SHALL assign categories based on a predefined mapping:
  - ML/DL: `torch`, `tensorflow`, `keras`, `scikit-learn`, `sleap`
  - Scientific: `numpy`, `scipy`, `pandas`, `sympy`
  - Data: `pillow`, `h5py`, `opencv-python`, `imageio`
  - Visualization: `matplotlib`, `seaborn`, `plotly`
  - Utilities: `packaging`, `typing-extensions`, `importlib-metadata`

#### Scenario: Categorize unknown packages with heuristics

- **WHEN** a package is not in the predefined mapping
- **THEN** the system SHALL apply heuristic categorization based on package name prefixes or fallback to "utilities" category

### Requirement: Graph Metrics Calculation

The system SHALL calculate network analysis metrics to identify important packages and characterize the dependency structure.

#### Scenario: Calculate degree centrality

- **WHEN** dependency graph is built
- **THEN** the system SHALL compute degree centrality for each node (proportion of total possible connections)
- **AND** SHALL use centrality values to scale node sizes in visualization

#### Scenario: Calculate summary statistics

- **WHEN** generating the visualization
- **THEN** the system SHALL compute and display:
  - Total number of packages (nodes)
  - Total number of dependencies (edges)
  - Mean degree (average connections per package)
  - Maximum degree (most-connected package)

### Requirement: Publication-Quality Visualization

The system SHALL generate static network graph visualizations using matplotlib and networkx with configurable presets for paper and poster outputs.

#### Scenario: Generate paper preset visualization

- **WHEN** user specifies `--preset paper` (or uses default)
- **THEN** the system SHALL create a figure with:
  - Figure size: 12 x 10 inches
  - Font sizes: 14pt for labels, 12pt for annotations
  - DPI: 300 for PNG output
  - Node sizes: 100-2100 points scaled by degree centrality
  - Compact spacing: spring layout with k=0.15

#### Scenario: Generate poster preset visualization

- **WHEN** user specifies `--preset poster`
- **THEN** the system SHALL create a figure with:
  - Figure size: 18 x 15 inches (50% larger than paper)
  - Font sizes: 20pt for labels, 18pt for annotations (43% larger)
  - DPI: 300 for PNG output
  - Node sizes: 150-3000 points (proportionally larger)
  - Expanded spacing: spring layout with k=0.22 (47% more space)

#### Scenario: Apply visual encoding scheme

- **WHEN** rendering the graph
- **THEN** the system SHALL apply:
  - Node colors by category using Seaborn color palette (colorblind-friendly)
  - Node sizes proportional to degree centrality (hub packages are larger)
  - Directed edges with arrows showing dependency direction
  - Edge opacity: 50% to reduce visual clutter
  - Labels only for top-N most central packages or those with degree > threshold

#### Scenario: Include summary statistics on figure

- **WHEN** rendering the visualization
- **THEN** the system SHALL add a text box containing:
  - Total packages count
  - Total dependencies count
  - Top 5 most-connected packages with their degree counts
- **AND** position the text box in an unoccupied corner of the figure

### Requirement: Multiple Output Formats

The system SHALL support exporting dependency graphs in PNG, SVG, and PDF formats for different publication needs.

#### Scenario: Export PNG for paper submission

- **WHEN** user specifies `--format png` (or uses default)
- **THEN** the system SHALL save a raster image at specified DPI (default 300)
- **AND** SHALL use lossless compression
- **AND** SHALL create filename: `sleap-dependency-graph.png`

#### Scenario: Export SVG for presentations

- **WHEN** user specifies `--format svg`
- **THEN** the system SHALL save a vector graphics file
- **AND** SHALL preserve all text as editable paths
- **AND** SHALL create filename: `sleap-dependency-graph.svg`

#### Scenario: Export PDF for LaTeX papers

- **WHEN** user specifies `--format pdf`
- **THEN** the system SHALL save a vector graphics PDF
- **AND** SHALL embed all fonts
- **AND** SHALL create filename: `sleap-dependency-graph.pdf`

### Requirement: Configurable SLEAP Source

The system SHALL accept SLEAP source location via command-line argument, environment variable, or default path with cross-platform compatibility.

#### Scenario: Use command-line argument

- **WHEN** user runs script with `--sleap-source C:\repos\sleap`
- **THEN** the system SHALL use the provided path to locate pyproject.toml

#### Scenario: Use environment variable

- **WHEN** user sets `SLEAP_PATH` environment variable and does not provide `--sleap-source`
- **THEN** the system SHALL use the environment variable value as the SLEAP source path

#### Scenario: Use default path

- **WHEN** no `--sleap-source` argument is provided and no `SLEAP_PATH` environment variable is set
- **THEN** the system SHALL use default path `C:/repos/sleap` (converted to pathlib for cross-platform compatibility)

#### Scenario: Accept GitHub URL

- **WHEN** user provides `--sleap-source https://github.com/talmolab/sleap/blob/develop/pyproject.toml`
- **THEN** the system SHALL detect URL pattern and download the file instead of reading from local filesystem

### Requirement: Graph Layout Algorithms

The system SHALL support multiple graph layout algorithms to optimize visualization readability.

#### Scenario: Use spring layout (default)

- **WHEN** user specifies `--layout spring` or uses default
- **THEN** the system SHALL use NetworkX spring_layout with force-directed algorithm
- **AND** SHALL configure parameters: iterations=50, k=0.15 (paper) or k=0.22 (poster), seed=42 for reproducibility

#### Scenario: Use Kamada-Kawai layout

- **WHEN** user specifies `--layout kamada_kawai`
- **THEN** the system SHALL use NetworkX kamada_kawai_layout for more uniform edge lengths

### Requirement: Depth Limiting

The system SHALL support limiting transitive dependency depth to control graph complexity.

#### Scenario: Unlimited depth (default)

- **WHEN** user does not specify `--max-depth` or specifies `--max-depth 0`
- **THEN** the system SHALL include all transitive dependencies regardless of depth

#### Scenario: Limited depth

- **WHEN** user specifies `--max-depth 2`
- **THEN** the system SHALL only include dependencies up to 2 levels deep from SLEAP
- **AND** SHALL mark truncated branches with annotation or different node style

### Requirement: Command-Line Interface

The system SHALL provide a comprehensive command-line interface following repository conventions.

#### Scenario: Display help documentation

- **WHEN** user runs `python scripts/plotting/generate_sleap_dependency_graph.py --help`
- **THEN** the system SHALL display usage information including all parameters and their defaults

#### Scenario: Run with minimal arguments

- **WHEN** user runs script without arguments
- **THEN** the system SHALL use all default values and generate PNG in `figures/main/` using paper preset

#### Scenario: Validate mutually exclusive options

- **WHEN** user provides invalid combination of options
- **THEN** the system SHALL display clear error message and exit with non-zero status code

### Requirement: Progress Logging

The system SHALL provide informative logging during long-running operations.

#### Scenario: Log dependency extraction progress

- **WHEN** extracting dependencies from PyPI API
- **THEN** the system SHALL log progress messages like "Fetching package 45/120: numpy"
- **AND** SHALL estimate remaining time based on average fetch duration

#### Scenario: Log visualization steps

- **WHEN** generating the graph layout and rendering
- **THEN** the system SHALL log major steps: "Computing graph layout...", "Calculating metrics...", "Rendering visualization..."

#### Scenario: Log cache usage

- **WHEN** using cached dependency data
- **THEN** the system SHALL log: "Using cached dependency data from YYYY-MM-DD HH:MM"

### Requirement: Error Handling and Validation

The system SHALL validate inputs and provide actionable error messages.

#### Scenario: Invalid SLEAP source path

- **WHEN** user provides a path that does not exist or does not contain pyproject.toml
- **THEN** the system SHALL display error: "pyproject.toml not found at {path}. Please verify SLEAP source path."
- **AND** SHALL exit with status code 1

#### Scenario: Network failure fetching PyPI data

- **WHEN** PyPI API request fails with network error
- **THEN** the system SHALL retry up to 3 times with exponential backoff
- **AND** if all retries fail SHALL log warning and continue with partial data

#### Scenario: Invalid output directory

- **WHEN** user specifies `--output-dir` that cannot be created (permission error)
- **THEN** the system SHALL display error with permission details
- **AND** SHALL exit with status code 1