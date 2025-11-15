# Proposal: Add SLEAP Dependency Network Visualization

## Why

SLEAP (Social LEAP Estimates Animal Poses) is a complex deep learning framework with extensive dependencies spanning scientific computing, machine learning, data processing, and visualization libraries. This complexity motivates the need for LabLink's dynamic VM allocation system - researchers need on-demand computational resources to run such sophisticated software stacks without manual environment setup.

A dependency network graph visualizing SLEAP's full transitive dependency tree will:
1. **Demonstrate ecosystem complexity** - Show the power-law distribution typical of modern software (many packages with few dependents, few packages with many dependents)
2. **Motivate LabLink's value proposition** - Illustrate why automated environment provisioning is essential for computational research
3. **Provide publication-quality figure** - Support the LabLink paper's argument about managing complex research software

This figure will be similar to the dependency network visualizations in [Phylum's analysis](https://blog.phylum.io/the-dependency-network-shows-the-complexity-of-the-software-ecosystem/) but focused on SLEAP as a representative computational biology workflow.

## What Changes

- Add new Python script `scripts/plotting/generate_sleap_dependency_graph.py` to extract and visualize SLEAP's dependency network
- Add dependency extraction module `src/dependency_graph/extractor.py` for parsing pyproject.toml and building transitive dependency trees
- Add graph visualization module `src/dependency_graph/visualizer.py` for creating publication-quality network diagrams
- Add required dependencies: `networkx`, `pipdeptree`, `toml` to pyproject.toml
- Create configurable presets matching existing repo conventions:
  - `paper` preset: 14pt fonts, 300 DPI for publication
  - `poster` preset: 20pt fonts, larger spacing for presentations
- Support multiple output formats: PNG, SVG, PDF
- Support configurable SLEAP source paths (local directory or GitHub URL)
- Generate figure showing:
  - Nodes representing Python packages (SLEAP + all transitive dependencies)
  - Edges representing dependency relationships
  - Visual encoding: node size by degree centrality, color by package category
  - Summary statistics: total packages, edges, degree distribution

## Impact

**Affected specs:**
- NEW: `sleap-dependency-visualization` - New capability for dependency network visualization

**Affected code:**
- `pyproject.toml` - Add networkx, pipdeptree, toml dependencies
- `scripts/plotting/` - New script for dependency graph generation
- `src/dependency_graph/` - New module for dependency extraction and visualization
- `figures/main/` - Output location for generated figures
- `README.md` - Documentation for generating dependency graphs

**Benefits:**
- Strengthens LabLink paper's motivation by visualizing software complexity
- Reusable framework for analyzing other scientific software dependencies
- Follows established repository patterns (configurable presets, multiple formats)
- No external API dependencies - can run offline with local SLEAP installation

**Risks:**
- Dependency tree extraction requires SLEAP to be installed or accessible
- Large dependency graphs may need layout optimization for readability
- Power-law distribution may require logarithmic scaling for visualization