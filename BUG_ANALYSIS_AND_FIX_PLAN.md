# GPU Reliance Figure Bug: Comprehensive Analysis & Implementation Plan

## Executive Summary

**Critical Bug Confirmed**: The `_calculate_gpu_score()` method in `collect_gpu_data.py` has a logic ordering bug that causes GPU-first packages (CuPy, Numba) to be incorrectly scored as 0 instead of 5.

**Impact Scope**: 
- **254 CuPy versions**: ALL scored 0 (should be 5) = 100% misclassification
- **123 Numba versions**: ALL scored 0 (should be 1-3 depending on GPU features)
- **66 scikit-image versions**: ALL scored 0 (likely correct, but needs verification)
- Visual artifacts in figures appear as flat lines at score=0 instead of GPU-first (5)

**Root Cause**: Lines 178-179 return 0 immediately if no GPU keywords found in `requires_dist`, preventing GPU_FIRST_PACKAGES check on lines 182-184 from ever executing.

---

## 1. FULL SCOPE ANALYSIS

### 1.1 Scoring Logic Bug (Lines 162-216)

**Current (BROKEN) Order:**
```python
def _calculate_gpu_score(self, requires_dist, package_name, version):
    # Step 1: Check for GPU keywords in dependencies (WRONG FIRST!)
    if not any(kw in all_deps for kw in GPU_KEYWORDS):
        return 0  # ❌ EXITS EARLY - NEVER CHECKS GPU_FIRST_PACKAGES!
    
    # Step 2: GPU-first packages (UNREACHABLE for packages without deps)
    if any(pkg in base_package.lower() for pkg in GPU_FIRST_PACKAGES):
        return 5  # ❌ Never reached for CuPy (bundles CUDA, no PyPI deps)
```

**Packages Affected:**

1. **CuPy (all variants)**: 254 total versions
   - Base `cupy`: 147 versions → ALL scored 0 (should be 5)
   - `cupy-cuda102`: 40 versions → ALL scored 0 (should be 5)
   - `cupy-cuda110`: 32 versions → ALL scored 0 (should be 5)
   - `cupy-cuda11x`: 20 versions → ALL scored 0 (should be 5)
   - `cupy-cuda12x`: 15 versions → ALL scored 0 (should be 5)
   - **Why**: CuPy bundles CUDA in wheels, doesn't declare GPU deps in PyPI metadata

2. **Numba**: 123 versions → ALL scored 0 (should be 1-3)
   - Has optional GPU support via `numba.cuda` module
   - Doesn't declare CUDA in PyPI `requires_dist` (user must install CUDA toolkit)
   - **Correct score**: 1-2 (optional GPU, significant performance gain)

3. **scikit-image**: 66 versions → ALL scored 0 (CORRECT)
   - Has optional CUDA support for some operations
   - But primarily CPU-based, GPU is truly optional
   - **Verification needed**: Check if any versions have GPU dependencies

### 1.2 Correctly Scored Packages (Partial Success)

1. **PyTorch**: 44 versions
   - 24 scored 0 (early versions, pre-GPU)
   - 20 scored 3 (bundled CUDA, correct) ✓
   - **Why it worked**: PyTorch declares nvidia-* packages in `requires_dist` since v1.13

2. **TensorFlow**: 135 versions
   - 109 scored 0 (early versions or CPU-only)
   - 26 scored 3 (v2.1+ with bundled CUDA, correct) ✓
   - **Why it worked**: TensorFlow 2.x declares nvidia-cudnn dependencies

3. **JAX**: 183 versions
   - 149 scored 0 (CPU-only versions)
   - 34 scored 3 (GPU versions with jaxlib[cuda], correct) ✓

### 1.3 Edge Cases & Special Considerations

**Package Variants During Scoring:**
- CuPy variants (`cupy-cuda11x`, etc.) are handled via:
  ```python
  base_package = package_name.split('-')[0]  # Line 182
  ```
- This should work IF the GPU_FIRST_PACKAGES check was reached
- **Problem**: It's never reached due to early return on line 179

**Bundled CUDA Packages:**
- TensorFlow and PyTorch **ALSO bundle CUDA** but score correctly
- **Why**: They declare nvidia-* packages in `requires_dist` for compatibility
- CuPy doesn't declare these deps because it's a GPU-first package (assumes user has CUDA)

**Pre-release Versions:**
- CuPy: 64/147 versions (43.5%) are alpha/beta/rc
- Numba: 25/123 versions (20.3%) are rc versions
- scikit-image: 20/66 versions (30.3%) are dev/rc
- **Impact**: Add noise to time-series, but should retain for historical accuracy

---

## 2. CORRECT FIX DESIGN

### 2.1 Corrected Scoring Logic Order

**Principle**: Check intrinsic package identity BEFORE metadata dependencies

```python
def _calculate_gpu_score(self, requires_dist: List[str], package_name: str, version: str) -> int:
    """Calculate GPU dependency score (0-5) for package version.
    
    Score rubric:
    0: No GPU support
    1: Optional GPU (in extras)
    2: Recommended GPU (performance degradation without)
    3: Practical Required (bundled CUDA, unusable without GPU)
    4: Hard Required (installation fails without CUDA)
    5: GPU-First (designed exclusively for GPU)
    """
    # Convert to lowercase for matching
    deps_lower = [dep.lower() for dep in (requires_dist or [])]
    all_deps = ' '.join(deps_lower)
    base_package = package_name.split('-')[0]  # Handle cupy-cuda* variants
    
    # STEP 1: Check GPU-first packages FIRST (by design, not dependencies)
    if any(pkg in base_package.lower() for pkg in GPU_FIRST_PACKAGES):
        return 5
    
    # STEP 2: No GPU keywords → definitely no GPU support
    if not any(kw in all_deps for kw in GPU_KEYWORDS):
        return 0
    
    # STEP 3: Hard GPU requirements (cudatoolkit in required deps)
    required_cuda_packages = ['cudatoolkit', 'nvidia-cuda']
    if any(pkg in all_deps for pkg in required_cuda_packages):
        # Check if it's NOT in extras_require
        if 'extra' not in all_deps:
            return 4
    
    # STEP 4: Bundled CUDA packages (TensorFlow 2.x, PyTorch)
    if any(pkg in package_name.lower() for pkg in BUNDLED_CUDA_PACKAGES):
        # TensorFlow unified GPU support starting from 2.1.0
        if 'tensorflow' in package_name.lower() and 'tensorflow-gpu' not in package_name.lower():
            try:
                from packaging import version as pkg_version
                if pkg_version.parse(version) >= pkg_version.parse('2.1.0'):
                    return 3
            except:
                pass
        elif 'torch' in package_name.lower() or 'jax' in package_name.lower():
            return 3
    
    # STEP 5: TensorFlow-GPU (separate package, practical requirement)
    if 'tensorflow-gpu' in package_name.lower():
        return 3
    
    # STEP 6: Optional GPU (in extras or recommended)
    if 'extra' in all_deps or 'optional' in all_deps:
        return 1
    
    # STEP 7: GPU mentioned but unclear
    return 1
```

**Key Changes:**
1. ✅ GPU_FIRST_PACKAGES check moved to STEP 1 (before keyword check)
2. ✅ Early return (line 179) moved to STEP 2 (after GPU-first check)
3. ✅ All other logic preserved in same order

### 2.2 Special Handling for Numba

**Current Issue**: Numba has optional GPU via `numba.cuda`, not in PyPI deps

**Options:**
1. **Add to GPU_FIRST_PACKAGES** with score 2 (recommended)
   - Pros: Reflects reality (GPU is significant feature)
   - Cons: Not truly "GPU-first" (has CPU fallback)

2. **Create new OPTIONAL_GPU_PACKAGES list** with score 1-2
   - Pros: More accurate categorization
   - Cons: Adds complexity

3. **Keep at 0 with documentation**
   - Pros: Matches PyPI metadata strictly
   - Cons: Misleading (Numba DOES support GPU)

**Recommendation**: Option 2 - Create new constant:

```python
# Packages with significant optional GPU support (score 2)
OPTIONAL_GPU_PACKAGES = ['numba']

# Add to scoring logic after GPU_FIRST_PACKAGES check:
if any(pkg in base_package.lower() for pkg in OPTIONAL_GPU_PACKAGES):
    return 2  # Recommended GPU (performance benefit)
```

### 2.3 Data Quality Improvements

**1. Version Filtering Strategy:**

**DO NOT filter pre-release versions** because:
- Historical accuracy: Shows actual development timelines
- Academic rigor: Complete data set prevents cherry-picking
- CuPy 43.5% pre-releases: Filtering would lose significant history

**Instead: Add metadata flag**
```python
'is_prerelease': is_prerelease(version),  # Add to version_data
```

**2. PyPI Metadata Parsing Improvements:**

Current dependency extraction is crude (line 154):
```python
dep_name = req.split('[')[0].split(';')[0].split('>=')[0]...
```

**Enhancement**:
```python
from packaging.requirements import Requirement

def _extract_gpu_dependencies(self, requires_dist: List[str]) -> List[str]:
    """Extract GPU-related dependencies from requires_dist."""
    gpu_deps = set()
    
    for req_str in (requires_dist or []):
        if not req_str:
            continue
        try:
            req = Requirement(req_str)
            dep_name = req.name
            
            # Check if GPU-related
            if any(kw in dep_name.lower() for kw in GPU_KEYWORDS):
                gpu_deps.add(dep_name)
                
                # Also check environment markers for GPU extras
                if req.marker and 'extra' in str(req.marker):
                    gpu_deps.add(f"{dep_name} [extra]")
        except:
            # Fallback to crude parsing
            dep_name = req_str.split('[')[0].split(';')[0].split('>=')[0]...
    
    return list(gpu_deps)
```

**3. Validation Additions:**

Add to `GPUDataCollector` class:
```python
def _validate_scoring(self, package_name: str, version: str, gpu_score: int, requires_dist: List[str]) -> None:
    """Log warnings for suspicious scoring results."""
    base_package = package_name.split('-')[0]
    
    # Warn if GPU-first package scored low
    if any(pkg in base_package.lower() for pkg in GPU_FIRST_PACKAGES) and gpu_score < 5:
        logger.warning(f"GPU-first package {package_name} v{version} scored {gpu_score} (expected 5)")
    
    # Warn if bundled CUDA package scored 0
    if any(pkg in package_name.lower() for pkg in BUNDLED_CUDA_PACKAGES) and gpu_score == 0:
        logger.warning(f"Bundled CUDA package {package_name} v{version} scored 0 (unexpected)")
```

---

## 3. IMPLEMENTATION STEPS

### Phase 1: Code Fixes (30 minutes)

**Step 1.1: Fix scoring logic in collect_gpu_data.py**

```bash
# Backup original
cp scripts/analysis/collect_gpu_data.py scripts/analysis/collect_gpu_data.py.backup

# Apply fix (edit lines 162-216)
# See section 2.1 for corrected logic
```

**Specific changes:**
- Line 53: Add `OPTIONAL_GPU_PACKAGES = ['numba']`
- Lines 162-216: Reorder as shown in section 2.1
- Add `_validate_scoring()` method (lines 217-230)
- Call validation in `collect_pypi_gpu_data()` after line 110

**Step 1.2: Enhance dependency parsing**

```bash
# Add import
from packaging.requirements import Requirement

# Replace _extract_gpu_dependencies() method (lines 147-160)
```

**Step 1.3: Add pre-release detection**

```python
import re

def _is_prerelease(self, version: str) -> bool:
    """Check if version is a pre-release."""
    patterns = [r'a\d+$', r'b\d+$', r'rc\d+$', r'dev\d*$', r'\.post\d+$']
    return any(re.search(p, version, re.IGNORECASE) for p in patterns)

# Add to version_data dict (line 120):
'is_prerelease': self._is_prerelease(version),
```

### Phase 2: Data Re-collection (15-30 minutes)

**Option A: Re-collect all packages (RECOMMENDED)**
```bash
cd c:\repos\lablink-paper-figures

# Clear old data
rm -rf data/raw/gpu_reliance/pypi_metadata/*.json

# Re-collect with verbose logging
uv run python scripts/analysis/collect_gpu_data.py --verbose

# Expected output:
# - Collecting GPU data for tensorflow...
# - Collected 135 versions for tensorflow from PyPI
# - Collecting GPU data for cupy...
# - Collected 147 versions for cupy from PyPI
# - [etc for all packages]
# - Saved data to data/raw/gpu_reliance/pypi_metadata/cupy_versions.json
```

**Option B: Post-process existing data (FASTER, less accurate)**
```bash
# Create fix_scores.py script to update JSON files in-place
uv run python scripts/analysis/fix_scores.py

# Not recommended: Doesn't get new metadata improvements
```

**Time estimate**: 2-3 minutes per package × 15 packages ≈ 30-45 minutes

### Phase 3: Data Processing (5 minutes)

```bash
cd c:\repos\lablink-paper-figures

# Process raw data to time-series CSV
uv run python scripts/analysis/process_gpu_data.py --verbose

# Expected output:
# - Loading raw data files...
# - Loaded cupy_versions.json: 147 versions
# - [etc]
# - Processing data to time-series format...
# - Processed 960 data points for 8 packages
# - Saved processed data: data/processed/gpu_reliance/gpu_timeseries.csv
# - Saved quality report: data/processed/gpu_reliance/quality_report.txt
```

**Verification:**
```bash
# Check quality report
cat data/processed/gpu_reliance/quality_report.txt

# Expected: All packages INCLUDED (except alphafold, cudf with 1 version)

# Check CuPy scores in CSV
grep "^cupy," data/processed/gpu_reliance/gpu_timeseries.csv | head -5

# Expected: gpu_score column should show 5 (not 0)
```

### Phase 4: Figure Regeneration (2 minutes)

```bash
cd c:\repos\lablink-paper-figures

# Generate publication figures
uv run python scripts/plotting/plot_gpu_reliance.py --format paper --verbose

# Expected output:
# - Loading data from: data/processed/gpu_reliance/gpu_timeseries.csv
# - Using format preset: paper - Two-column journal layout
# - Generating main figure...
# - Saved: figures/main/gpu_reliance_over_time.png
# - Saved: figures/main/gpu_reliance_over_time.pdf
# - Generating category comparison figure...
# - Saved: figures/main/gpu_reliance_by_category.png
```

**Visual verification:**
- Open `figures/main/gpu_reliance_over_time.png`
- CuPy should appear at GPU score = 5 (top of chart)
- Should show clear progression from CPU-only (0) → Optional (1-2) → Required (3-5)
- No more "oscillating patterns" (was visual artifact from overlapping 0s)

### Phase 5: Documentation Update (10 minutes)

**Update README or methodology documentation:**

```markdown
## GPU Dependency Scoring Methodology

### Scoring Rubric (0-5 scale)

- **5 - GPU-First**: Packages designed exclusively for GPU (CuPy, cuDF)
- **4 - Hard Required**: Installation fails without CUDA toolkit
- **3 - Practical Required**: Bundled CUDA, unusable without GPU (TensorFlow 2.1+, PyTorch)
- **2 - Recommended**: Significant performance degradation without GPU (Numba)
- **1 - Optional**: GPU in extras_require only
- **0 - No GPU**: No GPU support

### Scoring Logic Order

1. **Intrinsic package identity** (GPU-first packages like CuPy)
2. **Absence of GPU keywords** (early return for non-GPU packages)
3. **Hard requirements** (cudatoolkit in required dependencies)
4. **Bundled CUDA** (TensorFlow, PyTorch, JAX)
5. **Optional GPU** (extras_require)

### Known Limitations

- **PyPI metadata incomplete**: Some packages (CuPy) bundle CUDA without declaring deps
- **Version-specific behavior**: TensorFlow GPU support unified in 2.1.0
- **Pre-release versions**: Included for historical completeness (43% of CuPy versions)
```

---

## 4. TESTING & VALIDATION

### 4.1 Automated Tests

Create `tests/test_gpu_scoring.py`:

```python
import pytest
from scripts.analysis.collect_gpu_data import GPUDataCollector

@pytest.fixture
def collector():
    return GPUDataCollector(output_dir=Path('/tmp'))

def test_gpu_first_packages_score_5(collector):
    """GPU-first packages should score 5 regardless of dependencies."""
    # CuPy with no dependencies (bundles CUDA)
    score = collector._calculate_gpu_score(
        requires_dist=[],
        package_name='cupy',
        version='10.0.0'
    )
    assert score == 5, "CuPy should score 5 (GPU-first)"
    
    # CuPy variant
    score = collector._calculate_gpu_score(
        requires_dist=[],
        package_name='cupy-cuda11x',
        version='10.0.0'
    )
    assert score == 5, "CuPy variant should score 5"

def test_bundled_cuda_scores_3(collector):
    """Bundled CUDA packages should score 3."""
    score = collector._calculate_gpu_score(
        requires_dist=['nvidia-cuda-runtime-cu11'],
        package_name='torch',
        version='2.0.0'
    )
    assert score == 3, "PyTorch should score 3 (bundled CUDA)"

def test_optional_gpu_scores_2(collector):
    """Optional GPU packages should score 2."""
    score = collector._calculate_gpu_score(
        requires_dist=[],
        package_name='numba',
        version='0.56.0'
    )
    assert score == 2, "Numba should score 2 (optional GPU)"

def test_no_gpu_scores_0(collector):
    """Non-GPU packages should score 0."""
    score = collector._calculate_gpu_score(
        requires_dist=['numpy >= 1.20'],
        package_name='pandas',
        version='1.5.0'
    )
    assert score == 0, "Pandas should score 0 (no GPU)"
```

**Run tests:**
```bash
uv run pytest tests/test_gpu_scoring.py -v
```

### 4.2 Data Validation Checks

```bash
# Check CuPy scores
uv run python -c "
import pandas as pd
df = pd.read_csv('data/processed/gpu_reliance/gpu_timeseries.csv')
cupy_scores = df[df['package'] == 'cupy']['gpu_score'].unique()
print(f'CuPy scores: {cupy_scores}')
assert list(cupy_scores) == [5], f'Expected [5], got {cupy_scores}'
print('✓ CuPy correctly scored as 5')
"

# Check Numba scores
uv run python -c "
import pandas as pd
df = pd.read_csv('data/processed/gpu_reliance/gpu_timeseries.csv')
numba_scores = df[df['package'] == 'numba']['gpu_score'].unique()
print(f'Numba scores: {numba_scores}')
assert 2 in numba_scores, f'Expected 2 in scores, got {numba_scores}'
print('✓ Numba correctly scored as 2')
"

# Verify no packages stuck at 0 inappropriately
uv run python -c "
import pandas as pd
df = pd.read_csv('data/processed/gpu_reliance/gpu_timeseries.csv')
for pkg in ['cupy', 'numba', 'tensorflow', 'torch', 'jax']:
    scores = df[df['package'] == pkg]['gpu_score'].unique()
    max_score = scores.max()
    assert max_score > 0, f'{pkg} has max score 0 (bug not fixed!)'
    print(f'✓ {pkg}: max score = {max_score}')
"
```

### 4.3 Visual Validation

**Before/After Comparison:**

1. Save current (buggy) figure:
   ```bash
   cp figures/main/gpu_reliance_over_time.png figures/main/gpu_reliance_BEFORE_FIX.png
   ```

2. After fix, compare side-by-side

**Expected differences:**
- CuPy line moves from y=0 to y=5
- Numba line moves from y=0 to y=2
- "Oscillating patterns" disappear (were overlapping 0-score packages)
- Clear stratification: GPU-first (5) > Bundled (3) > Optional (2) > None (0)

---

## 5. RISK ASSESSMENT & MITIGATION

### 5.1 Risks

**Risk 1: Breaking existing analysis**
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Keep backup of old data, version figures as v1 vs v2

**Risk 2: Incomplete fix (other packages misclassified)**
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Comprehensive testing (section 4), validation logging

**Risk 3: PyPI API rate limiting**
- **Likelihood**: Medium (15 packages × 100+ versions = 1500+ API calls)
- **Impact**: Low (just slower)
- **Mitigation**: Add retry logic, respect rate limits

**Risk 4: Version semantics change over time**
- **Likelihood**: High (TensorFlow GPU support changed at v2.1)
- **Impact**: Low (already handled in code)
- **Mitigation**: Version-specific logic already implemented (lines 197-202)

### 5.2 Rollback Plan

If fix causes problems:
```bash
# Restore original code
cp scripts/analysis/collect_gpu_data.py.backup scripts/analysis/collect_gpu_data.py

# Restore old figures
cp figures/main/gpu_reliance_BEFORE_FIX.png figures/main/gpu_reliance_over_time.png

# Document known issues
echo "Known issue: CuPy misclassified as score 0 (should be 5)" >> KNOWN_ISSUES.md
```

---

## 6. COMPLETE COMMAND SEQUENCE

**Full end-to-end execution (copy-paste ready):**

```bash
# Navigate to project root
cd c:\repos\lablink-paper-figures

# === PHASE 1: BACKUP ===
cp scripts/analysis/collect_gpu_data.py scripts/analysis/collect_gpu_data.py.backup
cp -r figures/main figures/main_BACKUP

# === PHASE 2: APPLY CODE FIX ===
# (Edit collect_gpu_data.py manually - see section 2.1)
# Key changes:
#   - Line 53: Add OPTIONAL_GPU_PACKAGES = ['numba']
#   - Lines 162-216: Reorder scoring logic (GPU_FIRST_PACKAGES first)
#   - Add _validate_scoring() method

# === PHASE 3: RE-COLLECT DATA ===
# Clear old data
rm -rf data/raw/gpu_reliance/pypi_metadata/*.json

# Re-collect with fixed scoring
uv run python scripts/analysis/collect_gpu_data.py --verbose

# === PHASE 4: PROCESS DATA ===
uv run python scripts/analysis/process_gpu_data.py --verbose

# === PHASE 5: VALIDATE SCORES ===
# Check CuPy scores
uv run python -c "import pandas as pd; df = pd.read_csv('data/processed/gpu_reliance/gpu_timeseries.csv'); print('CuPy scores:', df[df['package']=='cupy']['gpu_score'].unique()); assert df[df['package']=='cupy']['gpu_score'].unique()[0] == 5"

# Check Numba scores
uv run python -c "import pandas as pd; df = pd.read_csv('data/processed/gpu_reliance/gpu_timeseries.csv'); print('Numba scores:', df[df['package']=='numba']['gpu_score'].unique()); assert 2 in df[df['package']=='numba']['gpu_score'].unique()"

# === PHASE 6: REGENERATE FIGURES ===
uv run python scripts/plotting/plot_gpu_reliance.py --format paper --verbose

# === PHASE 7: VISUAL CHECK ===
# Open figures/main/gpu_reliance_over_time.png
# Verify CuPy appears at score=5 (top of chart)

# === PHASE 8: RUN TESTS (if created) ===
uv run pytest tests/test_gpu_scoring.py -v

# === CLEANUP ===
rm analyze_scores.py check_version_patterns.py
```

---

## 7. EXPECTED OUTCOMES

### 7.1 Quantitative Changes

**Score Distribution (Before → After):**

| Package | Versions | Before | After | Change |
|---------|----------|--------|-------|--------|
| cupy | 147 | All 0 | All 5 | ✅ Fixed |
| cupy-cuda* | 107 | All 0 | All 5 | ✅ Fixed |
| numba | 123 | All 0 | All 2 | ✅ Fixed |
| tensorflow | 135 | Mixed 0/3 | Mixed 0/3 | ✅ Unchanged (correct) |
| torch | 44 | Mixed 0/3 | Mixed 0/3 | ✅ Unchanged (correct) |
| jax | 183 | Mixed 0/3 | Mixed 0/3 | ✅ Unchanged (correct) |

**Total data points**: 960 (estimated after merging variants)
**Fixed data points**: 254 CuPy + 123 Numba = **377 (39% of dataset)**

### 7.2 Qualitative Improvements

**Figure Quality:**
1. ✅ Clear stratification by GPU reliance level
2. ✅ CuPy visible as GPU-first package (was invisible at 0)
3. ✅ No "oscillating patterns" (was overlapping 0s)
4. ✅ Accurate representation of GPU adoption timeline

**Scientific Accuracy:**
1. ✅ CuPy correctly classified as GPU-first (foundational for GPU computing in Python)
2. ✅ Numba correctly shows optional GPU support (major feature)
3. ✅ Clear distinction between bundled CUDA (TF/PyTorch) and GPU-first (CuPy)

**Documentation:**
1. ✅ Scoring methodology transparently documented
2. ✅ Known limitations acknowledged
3. ✅ Reproducible with explicit commands

---

## 8. FUTURE ENHANCEMENTS (Post-Fix)

### 8.1 Additional Packages to Consider

**GPU-first candidates:**
- cuML (RAPIDS machine learning)
- cuGraph (RAPIDS graph analytics)
- cuSignal (RAPIDS signal processing)
- CuCIM (RAPIDS medical imaging)

**Optional GPU candidates:**
- OpenCV (cv2.cuda module)
- Pillow-SIMD (GPU acceleration)
- Dask (dask-cuda integration)

### 8.2 Metadata Enhancements

**Parse extras_require:**
```python
# Check if package has [cuda] or [gpu] extras
if 'info' in version_data:
    extras = version_data['info'].get('extras_require', {})
    has_gpu_extra = any('cuda' in k.lower() or 'gpu' in k.lower() 
                       for k in extras.keys())
```

**Extract README content:**
```python
# Look for GPU mentions in package description
description = version_data['info'].get('description', '')
gpu_mentioned_in_docs = any(kw in description.lower() 
                            for kw in ['gpu', 'cuda', 'nvidia'])
```

### 8.3 Longitudinal Analysis

**Track score changes over time:**
- When did packages add GPU support? (0 → 1+)
- When did optional become required? (1 → 3)
- Correlation with CUDA releases?

---

## CONCLUSION

**This is a well-scoped, fixable bug with clear implementation path.**

**Confidence Level**: 95%
- Root cause confirmed via data inspection
- Fix is simple reordering of existing logic
- Validation strategy is comprehensive
- Rollback plan exists if needed

**Recommended Timeline**:
- Code changes: 30 minutes
- Data re-collection: 30 minutes  
- Testing & validation: 15 minutes
- Documentation: 10 minutes
- **Total: ~90 minutes**

**Next Steps**: Proceed with Phase 1 (code fixes) when ready.
