# Design: SLEAP Dependency Network Visualization

## Context

The LabLink paper needs to demonstrate the complexity of modern computational research software to motivate the need for automated VM provisioning and environment management. SLEAP (Social LEAP Estimates Animal Poses) serves as an excellent case study - it's a real-world deep learning framework used by the target audience (computational researchers) with a complex dependency tree spanning ML frameworks, scientific computing, data processing, and visualization libraries.

This visualization will create a publication-quality network graph showing SLEAP's full transitive dependency tree, similar to ecosystem analyses like [Phylum's dependency network visualization](https://blog.phylum.io/the-dependency-network-shows-the-complexity-of-the-software-ecosystem/).

**Stakeholders:**
- Paper authors need publication-quality figures
- Poster presenters need larger, more readable versions
- Researchers interested in reproducible dependency analysis

**Constraints:**
- Must work with local SLEAP installation (`C:\repos\sleap`) or remote GitHub URL
- Must follow existing repo conventions (presets, output formats)
- Must generate high-quality static figures (not interactive visualizations)
- Should run offline after initial data collection

## Goals / Non-Goals

**Goals:**
- ✅ Generate publication-quality static dependency network graphs
- ✅ Show full transitive dependency tree (emphasize complexity)
- ✅ Support configurable presets (paper 14pt, poster 20pt)
- ✅ Support multiple output formats (PNG 300 DPI, SVG, PDF)
- ✅ Accept configurable SLEAP source (local path or GitHub URL)
- ✅ Visualize power-law distribution characteristics
- ✅ Provide summary statistics (total packages, edges, degree distribution)
- ✅ Use standard visualization libraries (matplotlib, seaborn, networkx)

**Non-Goals:**
- ❌ Interactive HTML visualizations (PyVis) - not needed for paper
- ❌ Real-time dependency monitoring or updates
- ❌ Vulnerability scanning or security analysis
- ❌ Support for non-Python ecosystems
- ❌ Dynamic dependency resolution at runtime
- ❌ Package recommendation or optimization

## Decisions

### Decision 1: Dependency Extraction Strategy

**Chosen approach:** Parse pyproject.toml + PyPI JSON API for transitive dependencies

**Rationale:**
- **Why not pipdeptree:** Requires SLEAP to be installed in current environment, creates circular dependency issues, and may conflict with existing packages in this repo
- **Why not conda/pip resolver:** Too slow for large dependency trees, requires package installation
- **Why PyPI JSON API:** Fast, no installation required, provides reliable dependency metadata via `https://pypi.org/pypi/{package}/json`
- **Why parse pyproject.toml:** Direct access to SLEAP's declared dependencies without installation

**Implementation:**
```python
# 1. Parse SLEAP's pyproject.toml to get direct dependencies
# 2. For each dependency, fetch PyPI JSON API: https://pypi.org/pypi/{package}/json
# 3. Recursively extract dependencies from "requires_dist" field
# 4. Build NetworkX DiGraph with packages as nodes, dependencies as edges
```

**Trade-offs:**
- ✅ Works without installing SLEAP
- ✅ Fast - only fetches metadata
- ✅ Handles both local files and GitHub URLs
- ⚠️ Requires internet for PyPI API (one-time, results can be cached)
- ⚠️ May include optional dependencies - need filtering logic

### Decision 2: Graph Layout Algorithm

**Chosen approach:** Force-directed spring layout (NetworkX `spring_layout` with `k` parameter tuning)

**Alternatives considered:**
- Hierarchical layout: Good for showing dependency levels but doesn't emphasize power-law distribution
- Circular layout: Too cluttered for large graphs (100+ nodes)
- Kamada-Kawai: Similar to spring but slower for large graphs

**Rationale:**
- Spring layout naturally clusters highly connected packages (PyTorch, NumPy) in center
- Visualizes hub-and-spoke pattern characteristic of power-law distributions
- Computationally efficient for graphs with 100-200 nodes
- Industry standard for dependency visualizations (see Phylum reference)

**Implementation:**
```python
pos = nx.spring_layout(G, k=0.15, iterations=50, seed=42)
# k controls spacing, iterations for convergence, seed for reproducibility
```

### Decision 3: Visual Encoding

**Node size:** Scaled by degree centrality (total connections)
- Emphasizes "hub" packages like PyTorch, NumPy that many depend on
- Formula: `size = 100 + 2000 * degree_centrality`

**Node color:** Categorized by package domain
- ML/DL: Red/orange (PyTorch, TensorFlow, etc.)
- Scientific computing: Blue (NumPy, SciPy, pandas)
- Data processing: Green (PIL, h5py, opencv)
- Visualization: Purple (matplotlib, seaborn)
- Utilities: Gray (packaging, typing, etc.)
- Uses Seaborn color palettes for consistency

**Edge style:**
- Directed arrows showing dependency direction
- Gray with 50% opacity to reduce visual clutter
- Thinner edges for clarity with many connections

**Layout presets:**
- Paper: Figure size 12x10 inches, 14pt fonts, 300 DPI
- Poster: Figure size 18x15 inches, 20pt fonts, 300 DPI (43% larger)

### Decision 4: Package Categorization

**Approach:** Hard-coded mapping with fallback heuristics

```python
CATEGORIES = {
    'ml': ['torch', 'tensorflow', 'keras', 'scikit-learn', 'sleap'],
    'scientific': ['numpy', 'scipy', 'pandas', 'sympy'],
    'data': ['pillow', 'h5py', 'opencv-python', 'imageio'],
    'viz': ['matplotlib', 'seaborn', 'plotly'],
    'utilities': ['packaging', 'typing-extensions', 'importlib-metadata']
}
# Fallback: categorize by common prefixes (py*, lib*, etc.)
```

**Rationale:**
- Manual categorization ensures accuracy for key packages
- Fallback prevents uncategorized nodes
- Categories align with paper narrative (ML complexity)

### Decision 5: Data Caching

**Approach:** Optional JSON cache in `data/processed/sleap_dependencies.json`

**Rationale:**
- PyPI API calls can be slow for 100+ packages (1-2 minutes)
- Cached data enables offline use and faster iteration
- Cache invalidation controlled by `--force-refresh` flag
- Cache includes timestamp and SLEAP version for tracking

**Trade-offs:**
- ✅ Fast subsequent runs (< 5 seconds vs. 1-2 minutes)
- ✅ Reproducible - same data for same SLEAP version
- ✅ Enables offline work
- ⚠️ Cache may become stale if SLEAP dependencies change
- ⚠️ Cache file size ~50-100 KB (negligible)

## Risks / Trade-offs

### Risk 1: Graph Readability with 100+ Nodes

**Risk:** Transitive dependency graphs can have 100-200+ nodes, making labels unreadable.

**Mitigation:**
1. Only label top-N most central packages (degree centrality > threshold)
2. Provide `--max-depth` parameter to limit transitive depth
3. Use larger figure sizes for poster preset (18x15 inches)
4. Consider separate "full graph" and "core dependencies" views

**Monitoring:** Manual review of generated figures for readability

### Risk 2: PyPI API Rate Limiting

**Risk:** PyPI may rate-limit requests if fetching 100+ package metadata entries rapidly.

**Mitigation:**
1. Implement exponential backoff on 429 errors
2. Cache results to avoid repeated API calls
3. Add `time.sleep(0.1)` between requests (polite crawling)
4. Document that initial run may take 1-2 minutes

### Risk 3: Optional Dependencies Inflating Graph

**Risk:** SLEAP has optional dependencies (e.g., `[dev]`, `[nn]`) that may not be relevant.

**Mitigation:**
1. Parse `project.optional-dependencies` separately
2. Add `--include-optional` flag (default: False for main dependencies only)
3. Document which dependencies are included
4. For LabLink paper, include all to maximize complexity visualization

### Risk 4: Cross-Platform Path Handling

**Risk:** Default path `C:\repos\sleap` is Windows-specific.

**Mitigation:**
1. Use `pathlib.Path` for cross-platform compatibility
2. Support environment variable `SLEAP_PATH`
3. Provide both local path and GitHub URL options
4. Document path configuration in README

**Example:**
```python
from pathlib import Path
import os

sleap_path = Path(args.sleap_source or os.getenv('SLEAP_PATH', 'C:/repos/sleap'))
```

## Migration Plan

**N/A** - This is a new capability, no existing code to migrate.

**Deployment steps:**
1. Implement changes according to tasks.md
2. Generate initial figures for review
3. Iterate on layout/visual encoding based on feedback
4. Update README with usage examples
5. Commit final figures to `figures/main/`

**Rollback:** Delete new files if visualization doesn't meet requirements.

## Open Questions

1. **Should we include SLEAP's development dependencies?**
   - Leaning toward: Include all to maximize complexity visualization for paper motivation
   - Can add `--exclude-dev` flag for cleaner view if needed

2. **What degree centrality threshold for labeling?**
   - Proposal: Label top 20 packages or those with degree > 5
   - Need to test with actual SLEAP graph to determine optimal value

3. **Should we show degree distribution histogram as inset?**
   - Proposal: Add optional `--show-stats-inset` flag for log-log plot
   - May clutter main figure - recommend separate supplementary figure

4. **Color scheme - categorical or continuous?**
   - Chosen: Categorical by package domain (more informative)
   - Alternative: Continuous color scale by centrality (less visually distinct)

5. **Should we support comparison with other frameworks?**
   - Out of scope for MVP
   - Could be future enhancement: overlay multiple frameworks' dependency graphs