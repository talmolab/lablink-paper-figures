# Design: GPU Hardware Reliance Analysis

## Overview

This change adds a time-series visualization showing how scientific software packages have become increasingly dependent on GPU hardware from 2010-2025. The implementation closely mirrors the successful `add-software-complexity-figure` architecture for consistency and code reuse.

## Key Design Decisions

### Decision 1: PyPI-Primary Data Collection Strategy

**Choice**: Use PyPI JSON API as primary source, with GitHub validation for key milestones

**Alternatives considered**:
1. conda-forge feedstocks (used in original software complexity design)
2. GitHub Archive / BigQuery analysis
3. Libraries.io API
4. Manual documentation review

**Rationale**:
- **Proven reliability**: The software complexity implementation already uses PyPI successfully
- **Historical completeness**: PyPI has complete version history with timestamps and dependency metadata
- **No rate limits**: Unlike GitHub (60 req/hr), PyPI has no authentication or rate limiting for basic queries
- **conda-forge limitation**: As discovered in software complexity work, conda-forge uses branch-based versioning instead of tags, making historical tag-based collection impossible
- **Consistency**: Matching the data source of software complexity reduces code duplication and learning curve

**Trade-offs**:
- PyPI `requires_dist` may not always explicitly list CUDA dependencies (some packages bundle CUDA in wheels)
- Requires supplementary scoring logic to detect GPU reliance beyond just parsing dependencies
- Pre-2015 metadata may be sparse

**Mitigation**:
- Implement GPU dependency scoring system (0-5) that combines multiple signals
- Manual validation via GitHub for 20-30 key milestone versions
- Keyword detection in package descriptions and dependency names

### Decision 2: GPU Dependency Scoring System (0-5 Scale)

**Choice**: Quantitative score from 0 (no GPU) to 5 (GPU-first design)

**Scoring rubric**:
| Score | Category | Definition | Example |
|-------|----------|------------|---------|
| 0 | No GPU | No GPU support whatsoever | scikit-image < 0.25 |
| 1 | Optional | GPU support available but entirely optional | Numba with CUDA extras |
| 2 | Recommended | Works without GPU but with severe performance degradation | Earlier TensorFlow versions |
| 3 | Practical Required | Technically optional but unusable for real workloads without GPU | Modern TensorFlow, PyTorch |
| 4 | Hard Required | Installation or core features fail without CUDA/GPU libraries | JAX (requires external CUDA) |
| 5 | GPU-First | Designed exclusively for GPU, no CPU fallback | CuPy, Rapids cuDF |

**Rationale**:
- **Nuance**: Binary "has GPU / no GPU" is insufficient - captures transition from optional → required
- **Interpretability**: 0-5 scale is intuitive for visualization and paper discussion
- **Flexibility**: Can be refined with manual review for ambiguous cases

**Alternative considered**: Binary indicator (0/1) - rejected as too coarse

**Detection logic**:
```python
# Automatic detection from PyPI metadata
if no_gpu_keywords_in_deps:
    score = 0
elif package_name in GPU_FIRST_PACKAGES:  # CuPy, cuDF, etc.
    score = 5
elif 'cudatoolkit' in required_deps:
    score = 4
elif package_name in BUNDLED_CUDA_PACKAGES:  # TensorFlow 2.x, PyTorch
    score = 3
elif 'cuda' in extras_require:
    score = 1-2  # Refine manually
else:
    score = 1  # GPU mentioned but unclear
```

### Decision 3: Package Selection (10 Packages, 3 Categories)

**Chosen packages**:

**Machine Learning / Deep Learning (4)**:
- TensorFlow (0.12+, 2016-present) - Separate `tensorflow-gpu` until 2.1, then unified
- PyTorch (0.1+, 2017-present) - GPU bundled from start
- JAX (0.1+, 2018-present) - Requires external CUDA installation
- Numba (0.12+, 2012-present) - JIT compiler, merged GPU support from NumbaPro in 2017

**Scientific Computing (3)**:
- CuPy (1.0+, 2017-present) - GPU-first NumPy-compatible arrays
- Rapids cuDF (2018+, PyPI 2024) - GPU DataFrame library
- scikit-image (0.14+, 2018-present) - Shows transition from CPU-only to optional GPU (cuCIM 2021)

**Molecular Dynamics / Bioinformatics (3)**:
- OpenMM (1.0+, 2010-present) - Built with GPU from inception
- GROMACS (Python wrappers, 2013+) - Traditional HPC that added GPU
- AlphaFold2 (2.0+, 2021-present) - Modern AI requiring high-end GPUs

**Rationale**:
- **Temporal coverage**: Spans 2010-2025, capturing GPU evolution from niche to mainstream
- **Domain diversity**: ML, scientific computing, biology - demonstrates broad trend
- **Dependency patterns**: Mix of GPU-optional, GPU-recommended, GPU-required, GPU-first
- **Data availability**: All available on PyPI with reasonable version history
- **Narrative value**: Tells story of GPU transition across scientific computing

**Alternative considered**: Include 15 packages - rejected to maintain visual clarity and reduce data collection time

### Decision 4: Visualization Style Matching Software Complexity

**Choice**: Reuse plot structure from `plot_software_complexity.py`

**Specific design elements**:
- **Main figure**: Connected scatter plot with all 10 packages, colored by category
- **Y-axis**: "GPU Dependency Level (0=None, 5=GPU-First)"
- **X-axis**: "Year" with only first and last years shown (avoid overlapping labels)
- **Category comparison**: Faceted plot (3 panels: ML, Scientific Computing, Biology)
- **Format presets**: paper (14pt, 300 DPI, 6.5"×5"), poster (20pt, 300 DPI, 12"×9"), presentation (16pt, 150 DPI, 10"×7.5")
- **Color palette**: Seaborn colorblind-friendly (same as software complexity)
- **Outputs**: PNG + PDF for each figure type

**Rationale**:
- **Consistency**: Matching style aids reader comprehension when figures appear in same paper
- **Code reuse**: Minimal new code, mostly parameter changes
- **Proven design**: Software complexity figures already validated and publication-ready

**Implementation approach**: Copy `plot_software_complexity.py` → `plot_gpu_reliance.py`, then adapt:
```python
# Change from:
ax.set_ylabel('Direct Dependencies', fontsize=...)

# To:
ax.set_ylabel('GPU Dependency Level (0=None, 5=GPU-First)', fontsize=...)
```

### Decision 5: Data Collection Methodology

**Phase 1: Automated PyPI Collection (2-3 days)**

```python
# Extend pattern from collect_dependency_data.py

GPU_PACKAGES = {
    # ML packages
    'tensorflow': 'pypi',
    'tensorflow-gpu': 'pypi',  # Separate package until TF 2.1
    'torch': 'pypi',
    'jax': 'pypi',
    'jaxlib': 'pypi',
    'numba': 'pypi',

    # Scientific computing
    'cupy': 'pypi',
    'cupy-cuda102': 'pypi',  # Multiple CUDA-specific variants
    'cupy-cuda110': 'pypi',
    'cupy-cuda11x': 'pypi',
    'cupy-cuda12x': 'pypi',
    'cudf': 'pypi',
    'scikit-image': 'pypi',

    # Biology/MD
    'openmm': 'pypi',
    'alphafold': 'pypi',
}

def collect_gpu_metadata(package_name: str) -> Dict:
    """Collect GPU-relevant metadata from PyPI."""
    # Get all versions (reuse existing logic)
    data = get_pypi_versions(package_name)

    for version_data in data['versions']:
        requires_dist = version_data.get('requires_dist', [])

        # Extract GPU-related dependencies
        gpu_deps = extract_gpu_dependencies(requires_dist)

        # Calculate GPU score
        gpu_score = calculate_gpu_score(
            requires_dist=requires_dist,
            package_name=package_name,
            version=version_data['version']
        )

        # Extract CUDA version requirements
        cuda_version = extract_cuda_version(requires_dist)

        version_data.update({
            'gpu_score': gpu_score,
            'gpu_dependencies': gpu_deps,
            'cuda_version': cuda_version,
            'requires_external_cuda': check_external_cuda_required(package_name)
        })
```

**Phase 2: Manual Validation (2-3 days)**

For 20-30 key milestone versions:
1. Clone GitHub repository
2. Checkout specific version tag
3. Review README, INSTALL, setup.py
4. Verify GPU requirements match automated scoring
5. Adjust scores if needed
6. Document rationale in validation CSV

**Phase 3: Data Processing (1 day)**

```python
# Output CSV format:
# package, version, date, gpu_score, cuda_version,
# gpu_deps_count, requires_external_cuda, source
```

**Phase 4: Visualization (1 day)**

Generate figures with three format presets, matching software complexity output structure.

### Decision 6: Folder Structure

**Choice**: Mirror `software_complexity/` structure

```
data/
  raw/
    gpu_reliance/
      pypi_metadata/
        tensorflow_versions.json
        torch_versions.json
        cupy_versions.json
        ...
      github_validation/
        validation_log.csv
  processed/
    gpu_reliance/
      gpu_timeseries.csv
      quality_report.txt
      source_attribution.csv
  gpu_reliance_README.md

scripts/
  analysis/
    collect_gpu_data.py
    process_gpu_data.py
  plotting/
    plot_gpu_reliance.py

figures/
  main/
    gpu_reliance_over_time.png
    gpu_reliance_over_time.pdf
    gpu_reliance_by_category.png
    gpu_reliance_by_category.pdf
    gpu_reliance_metadata.txt
```

**Rationale**:
- **Consistency**: Developers familiar with software complexity structure can navigate easily
- **Separation**: Raw vs processed data clearly distinguished
- **Documentation**: README at data level, metadata at figure level
- **Discoverability**: Predictable paths

## Metrics Tracked

| Metric | Description | Source | Use |
|--------|-------------|--------|-----|
| `gpu_score` | 0-5 scale quantifying GPU dependency | Automated + manual | Primary Y-axis |
| `cuda_version` | Minimum CUDA version required | PyPI `requires_dist` parsing | Secondary analysis |
| `gpu_deps_count` | Count of GPU-related dependencies | PyPI `requires_dist` | Validation |
| `requires_external_cuda` | Boolean: ships CUDA vs requires external | Package analysis | Narrative discussion |
| `package_variant` | Track `cupy` vs `cupy-cuda110` splits | Package naming | Data normalization |

## Testing Strategy

1. **Unit tests** for scoring logic:
   - Test `calculate_gpu_score()` with known packages
   - Test CUDA version extraction regex
   - Test GPU keyword detection

2. **Integration tests**:
   - Validate PyPI API response parsing
   - Check CSV output format
   - Verify figure generation runs without errors

3. **Data validation**:
   - Cross-check PyPI dates against GitHub release dates
   - Spot-check 5-10 versions by manual installation
   - Validate scoring with domain experts

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Script development | 1-2 days | Collection & processing scripts |
| Automated collection | 2-3 days | Raw PyPI metadata JSONs |
| Manual validation | 2-3 days | Validated GPU scores |
| Data processing | 1 day | Clean CSV dataset |
| Visualization | 1 day | Publication-ready figures |
| Documentation | 0.5 days | README and metadata |
| **Total** | **7-10 days** | Complete implementation |

## Open Questions

1. **CUDA-specific wheel handling**: How to aggregate `cupy-cuda102`, `cupy-cuda110`, `cupy-cuda12x` into single `cupy` timeline?
   - **Answer**: Treat as single package, track CUDA version separately, show highest score at each time point

2. **TensorFlow/TensorFlow-GPU split**: Two separate packages until TF 2.1, then unified - how to visualize?
   - **Answer**: Show both lines until 2.1, then single line; annotate unification event

3. **Score ambiguity**: What score for "works on CPU but 100x slower"?
   - **Answer**: Start at 2-3, refine with manual validation and community input

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PyPI metadata incomplete for old versions | High | Medium | Manual GitHub validation, focus on post-2015 |
| GPU requirements not in metadata | Medium | High | Keyword detection, README parsing, manual review |
| Subjective scoring disagreements | Medium | Low | Document rubric, get expert review, show examples |
| Package naming inconsistencies | Medium | Medium | Normalization mapping, variant tracking |
| Data collection time overrun | Low | Low | Parallelize collection, cache responses |

## Success Criteria

1. **Data completeness**: ≥50 versions per package (avg ~100 expected)
2. **Temporal coverage**: Data points spanning at least 2010-2025 for core packages
3. **Validation rate**: 100% of automatically assigned scores reviewed, 20-30 manually verified
4. **Figure quality**: Matches software complexity figures in style, resolution (300 DPI), format
5. **Reproducibility**: `uv run python collect_gpu_data.py` → `process_gpu_data.py` → `plot_gpu_reliance.py` generates figures in <30 minutes
6. **Documentation**: README explains methodology, metadata documents generation parameters