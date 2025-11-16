# Implementation Tasks

## 1. Data Collection Infrastructure Setup
- [ ] 1.1 Create directory structure: `data/raw/gpu_reliance/pypi_metadata/`, `data/processed/gpu_reliance/`, `data/raw/gpu_reliance/github_validation/`
- [ ] 1.2 Create `scripts/analysis/collect_gpu_data.py` with argument parsing and logging (copy structure from `collect_dependency_data.py`)
- [ ] 1.3 Define `GPU_PACKAGES` dictionary mapping 10 packages to PyPI source
- [ ] 1.4 Implement `collect_pypi_gpu_data(package_name)` function to fetch all versions from PyPI JSON API
- [ ] 1.5 Add GPU-specific keyword detection (`GPU_KEYWORDS = ['cuda', 'cudnn', 'gpu', 'nvidia', 'cupy']`)
- [ ] 1.6 Add progress indicators and error handling for API calls

## 2. GPU Dependency Scoring Logic
- [ ] 2.1 Implement `calculate_gpu_score(requires_dist, package_name, version)` function with 0-5 scoring rubric
- [ ] 2.2 Define `GPU_FIRST_PACKAGES` list (cupy, cudf, cucim, rapids packages)
- [ ] 2.3 Define `BUNDLED_CUDA_PACKAGES` list (tensorflow>=2.1, torch, jax)
- [ ] 2.4 Implement keyword-based detection for CUDA requirements
- [ ] 2.5 Implement `extract_cuda_version(requires_dist)` using regex to find CUDA version requirements
- [ ] 2.6 Implement `check_external_cuda_required(package_name)` to identify packages needing external CUDA installation

## 3. Package Variant Handling
- [ ] 3.1 Create mapping for CuPy variants: `cupy-cuda102`, `cupy-cuda110`, `cupy-cuda11x`, `cupy-cuda12x` → base `cupy`
- [ ] 3.2 Handle TensorFlow/TensorFlow-GPU split: collect both packages, mark unification at TF 2.1.0
- [ ] 3.3 Implement normalization logic to aggregate variants under base package name
- [ ] 3.4 Track CUDA version separately from base package

## 4. Manual Validation Infrastructure
- [ ] 4.1 Create `data/raw/gpu_reliance/github_validation/validation_log.csv` template with columns: package, version, date, auto_score, manual_score, rationale, validator, validation_date
- [ ] 4.2 Identify 20-30 key milestone versions across 10 packages for manual review
- [ ] 4.3 Document validation procedure in `data/gpu_reliance_README.md`

## 5. Data Processing Pipeline
- [ ] 5.1 Create `scripts/analysis/process_gpu_data.py` (adapt from `process_dependency_data.py`)
- [ ] 5.2 Implement loading and aggregation of all PyPI JSON files
- [ ] 5.3 Implement package variant normalization (merge CuPy variants, TensorFlow variants)
- [ ] 5.4 Apply minimum data point filter (exclude packages with <5 versions)
- [ ] 5.5 Generate `data/processed/gpu_reliance/gpu_timeseries.csv` with schema: package, version, date, gpu_score, cuda_version, gpu_deps_count, requires_external_cuda, source
- [ ] 5.6 Generate quality report: `data/processed/gpu_reliance/quality_report.txt`
- [ ] 5.7 Generate source attribution: `data/processed/gpu_reliance/source_attribution.csv`

## 6. Visualization Script Foundation
- [ ] 6.1 Create `scripts/plotting/plot_gpu_reliance.py` (copy structure from `plot_software_complexity.py`)
- [ ] 6.2 Implement `--format` argument with choices: paper, poster, presentation
- [ ] 6.3 Implement `--output-dir` argument for custom output paths
- [ ] 6.4 Load processed GPU time-series CSV data
- [ ] 6.5 Set up matplotlib/seaborn styling matching software complexity figures
- [ ] 6.6 Define format-specific configurations (matching software complexity presets)

## 7. Main Figure Generation
- [ ] 7.1 Implement `plot_main_figure(output_path)` method in `GpuReliancePlotter` class
- [ ] 7.2 Create connected scatter plot for all packages
- [ ] 7.3 Apply distinct colors per package from colorblind-friendly palette
- [ ] 7.4 Set Y-axis label: "GPU Dependency Level (0=None, 5=GPU-First)"
- [ ] 7.5 Set X-axis label: "Year" with only first and last years shown
- [ ] 7.6 Set title: "GPU Hardware Reliance in Scientific Software Over Time"
- [ ] 7.7 Add legend with package names
- [ ] 7.8 Add grid lines for readability
- [ ] 7.9 Save to `figures/main/gpu_reliance_over_time.{png,pdf}` with appropriate DPI

## 8. Category Comparison Figure
- [ ] 8.1 Implement `plot_category_comparison(output_path)` method
- [ ] 8.2 Define package categories: ML/Deep Learning, Scientific Computing, Biology
- [ ] 8.3 Create 3 faceted subplots (one per category)
- [ ] 8.4 Plot packages within each category with consistent styling
- [ ] 8.5 Share X-axis across subplots
- [ ] 8.6 Label each panel with category name
- [ ] 8.7 Set overall title: "GPU Dependency Growth by Scientific Domain"
- [ ] 8.8 Save to `figures/main/gpu_reliance_by_category.{png,pdf}`

## 9. Documentation and Metadata
- [ ] 9.1 Create `data/gpu_reliance_README.md` documenting methodology, data sources, GPU scoring rubric, and reproduction instructions
- [ ] 9.2 Implement `generate_metadata(output_path, data_file)` method in plotting script
- [ ] 9.3 Generate `figures/main/gpu_reliance_metadata.txt` with generation timestamp, format preset, data source, package list, data point counts, date range
- [ ] 9.4 Update main `README.md` with new "Generating GPU Hardware Reliance Figure" section
- [ ] 9.5 Add quick start guide matching software complexity section style
- [ ] 9.6 Document all three format presets and example commands

## 10. Testing and Validation
- [ ] 10.1 Write unit test for `calculate_gpu_score()` with known packages (CuPy=5, scikit-image=0, TensorFlow 2.x=3)
- [ ] 10.2 Write unit test for `extract_cuda_version()` regex
- [ ] 10.3 Write unit test for GPU keyword detection
- [ ] 10.4 Test PyPI API response parsing with mock data
- [ ] 10.5 Validate CSV output format matches expected schema
- [ ] 10.6 Test figure generation runs without errors for all three formats
- [ ] 10.7 Verify PNG and PDF outputs are created
- [ ] 10.8 Check figure quality (fonts readable, labels not overlapping, colors distinguishable)

## 11. Data Collection Execution
- [ ] 11.1 Run `collect_gpu_data.py` for all 10 packages
- [ ] 11.2 Verify data collection completes without errors
- [ ] 11.3 Check raw JSON files created in `data/raw/gpu_reliance/pypi_metadata/`
- [ ] 11.4 Verify version counts are reasonable (expect 50-200 versions per package)
- [ ] 11.5 Spot-check JSON structure for correctness

## 12. Manual Validation Execution
- [ ] 12.1 Review first GPU support version for TensorFlow (v0.12.0, Dec 2016)
- [ ] 12.2 Review first GPU support version for PyTorch (v0.1.1, 2017)
- [ ] 12.3 Review CuPy as GPU-first package (v1.0.0, June 2017)
- [ ] 12.4 Review JAX CUDA requirements (v0.1.0, 2018)
- [ ] 12.5 Review OpenMM GPU-first design (v1.0, Jan 2010)
- [ ] 12.6 Review AlphaFold2 GPU requirements (v2.0, 2021)
- [ ] 12.7 Review TensorFlow/TensorFlow-GPU unification (TF 2.1.0, Jan 2020)
- [ ] 12.8 Review Numba GPU support transition (NumbaPro merge ~2017)
- [ ] 12.9 Review scikit-image transition to optional GPU (cuCIM 2021, backend dispatch 0.25)
- [ ] 12.10 Review GROMACS Python wrapper GPU support
- [ ] 12.11 Document all validation findings in `validation_log.csv`
- [ ] 12.12 Adjust GPU scores based on validation insights

## 13. Data Processing Execution
- [ ] 13.1 Run `process_gpu_data.py` on collected raw data
- [ ] 13.2 Verify `gpu_timeseries.csv` is created with expected columns
- [ ] 13.3 Check data point counts match expectations (expect 500-1000 total)
- [ ] 13.4 Review quality report for excluded packages (if any)
- [ ] 13.5 Verify source attribution shows correct package counts
- [ ] 13.6 Spot-check CSV data for correctness (dates, scores, package names)

## 14. Figure Generation Execution
- [ ] 14.1 Generate paper format figures: `uv run python plot_gpu_reliance.py --format paper --verbose`
- [ ] 14.2 Verify main figure shows clear GPU dependency trends
- [ ] 14.3 Verify category comparison shows domain-specific patterns
- [ ] 14.4 Check X-axis shows only first and last years
- [ ] 14.5 Check Y-axis label is clear and accurate
- [ ] 14.6 Generate poster format: `uv run python plot_gpu_reliance.py --format poster --verbose`
- [ ] 14.7 Generate presentation format: `uv run python plot_gpu_reliance.py --format presentation --verbose`
- [ ] 14.8 Verify all output files exist (6 files: 3 formats × 2 figure types for main, or PNG+PDF for each)

## 15. Code Quality and Reproducibility
- [ ] 15.1 Run `ruff check scripts/analysis/collect_gpu_data.py scripts/analysis/process_gpu_data.py scripts/plotting/plot_gpu_reliance.py`
- [ ] 15.2 Run `ruff format scripts/analysis/ scripts/plotting/`
- [ ] 15.3 Fix any linting errors or style issues
- [ ] 15.4 Add docstrings to all public functions
- [ ] 15.5 Add type hints where appropriate
- [ ] 15.6 Test end-to-end reproduction from clean state
- [ ] 15.7 Verify completion time is under 30 minutes
- [ ] 15.8 Verify no new dependencies were added

## 16. Final Review and Polishing
- [ ] 16.1 Review all generated figures for publication quality
- [ ] 16.2 Check that figure style matches software complexity figures
- [ ] 16.3 Verify documentation is complete and clear
- [ ] 16.4 Ensure all metadata files are generated correctly
- [ ] 16.5 Test README instructions are accurate
- [ ] 16.6 Get peer review from domain expert on GPU scoring
- [ ] 16.7 Address any feedback or corrections
- [ ] 16.8 Create final commit and prepare for archival