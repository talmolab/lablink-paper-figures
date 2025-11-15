# Implementation Tasks

## 1. Setup and Dependencies
- [ ] 1.1 Add `networkx>=3.0` to pyproject.toml dependencies
- [ ] 1.2 Add `toml>=0.10.0` to pyproject.toml dependencies
- [ ] 1.3 Run `uv sync` to install new dependencies
- [ ] 1.4 Create `src/dependency_graph/` module directory structure

## 2. Dependency Extraction Module
- [ ] 2.1 Create `src/dependency_graph/__init__.py`
- [ ] 2.2 Implement `src/dependency_graph/extractor.py` with functions:
  - [ ] 2.2.1 `parse_pyproject_toml(path)` - Extract dependencies from pyproject.toml
  - [ ] 2.2.2 `fetch_remote_pyproject(url)` - Download pyproject.toml from GitHub URL
  - [ ] 2.2.3 `build_dependency_graph(dependencies)` - Recursively build transitive dependency tree using PyPI JSON API
  - [ ] 2.2.4 `create_networkx_graph(dependency_dict)` - Convert dependency data to NetworkX DiGraph
- [ ] 2.3 Add package categorization (ML/scientific/data/visualization/utilities)
- [ ] 2.4 Add error handling for missing packages and network failures

## 3. Graph Visualization Module
- [ ] 3.1 Create `src/dependency_graph/visualizer.py` with functions:
  - [ ] 3.1.1 `calculate_graph_metrics(G)` - Compute degree distribution, centrality metrics
  - [ ] 3.1.2 `create_graph_layout(G, layout_type)` - Generate spring/hierarchical layout
  - [ ] 3.1.3 `visualize_dependency_graph(G, preset, output_path)` - Main visualization function
  - [ ] 3.1.4 `add_summary_statistics(fig, G)` - Add text box with node/edge counts
- [ ] 3.2 Implement preset configurations:
  - [ ] 3.2.1 `paper` preset: 14pt fonts, 300 DPI, compact spacing
  - [ ] 3.2.2 `poster` preset: 20pt fonts, 300 DPI, expanded spacing
- [ ] 3.3 Add color scheme for package categories (consistent with Seaborn palettes)
- [ ] 3.4 Add node sizing based on degree centrality
- [ ] 3.5 Support PNG, SVG, PDF output formats

## 4. Main Script
- [ ] 4.1 Create `scripts/plotting/generate_sleap_dependency_graph.py`
- [ ] 4.2 Implement command-line argument parser with options:
  - [ ] 4.2.1 `--sleap-source` - Path to local SLEAP directory or GitHub URL (default: env var or local path)
  - [ ] 4.2.2 `--output-dir` - Output directory for figures (default: figures/main)
  - [ ] 4.2.3 `--preset` - Font/spacing preset: paper or poster (default: paper)
  - [ ] 4.2.4 `--format` - Output format: png, svg, pdf (default: png)
  - [ ] 4.2.5 `--dpi` - Resolution for raster formats (default: 300)
  - [ ] 4.2.6 `--layout` - Graph layout algorithm: spring, kamada_kawai (default: spring)
  - [ ] 4.2.7 `--max-depth` - Maximum dependency tree depth (default: unlimited)
- [ ] 4.3 Add environment variable support for `SLEAP_PATH`
- [ ] 4.4 Implement main execution flow integrating extractor and visualizer
- [ ] 4.5 Add progress logging for long-running operations

## 5. Testing
- [ ] 5.1 Create `tests/test_dependency_extractor.py`
- [ ] 5.2 Add unit tests for pyproject.toml parsing
- [ ] 5.3 Add unit tests for graph construction
- [ ] 5.4 Create `tests/test_dependency_visualizer.py`
- [ ] 5.5 Add tests for layout generation and metric calculation
- [ ] 5.6 Add integration test generating sample graph with mock data

## 6. Documentation
- [ ] 6.1 Update `README.md` with dependency graph generation section
- [ ] 6.2 Add usage examples for both local and remote SLEAP sources
- [ ] 6.3 Document environment variables and configuration options
- [ ] 6.4 Add example commands for paper and poster outputs
- [ ] 6.5 Create `figures/README.md` entry explaining dependency graph figure

## 7. Data and Output
- [ ] 7.1 Create `data/processed/sleap_dependencies.json` for cached dependency data
- [ ] 7.2 Add `.gitignore` entry for large dependency cache files if needed
- [ ] 7.3 Generate initial figure with SLEAP dependencies
- [ ] 7.4 Verify figure quality at paper and poster presets
- [ ] 7.5 Add metadata file documenting generation parameters

## 8. Code Quality
- [ ] 8.1 Run `ruff format .` on all new code
- [ ] 8.2 Run `ruff check .` and fix any issues
- [ ] 8.3 Add docstrings to all public functions
- [ ] 8.4 Add type hints to function signatures
- [ ] 8.5 Run pytest and ensure all tests pass
