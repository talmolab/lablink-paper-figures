# Tasks: Add GPU Cost Trends Visualization

## Phase 1: Data Infrastructure (Serial)

- [x] Create `data/raw/gpu_prices/` directory structure
- [x] Write `data/raw/gpu_prices/README.md` with Epoch AI download instructions
  - Include direct URL: https://epoch.ai/data/machine-learning-hardware
  - Step-by-step download/extraction guide
  - Citation requirements (CC BY license)
  - Expected file: `ml_hardware.csv`
- [x] Create `src/gpu_costs/` module directory
- [x] Implement `src/gpu_costs/__init__.py` with public API exports
- [x] Implement `src/gpu_costs/loader.py` with CSV loading
  - `load_gpu_dataset(path)` function
  - Validate required columns: name, release_date, price, fp32_tflops
  - Parse dates to datetime objects
  - Handle missing values appropriately
  - Raise FileNotFoundError with helpful message if file missing
- [x] Add data schema validation tests in `tests/test_gpu_costs_loader.py`
  - Test loading valid dataset
  - Test missing file error handling
  - Test malformed CSV handling

## Phase 2: Data Processing (Serial, depends on Phase 1)

- [x] Implement `src/gpu_costs/filters.py` for GPU categorization
  - `is_ml_relevant(gpu_row)` function
  - `categorize_gpu(gpu_row)` → "professional" | "consumer" | "other"
  - Professional: Tesla, A100, H100, V100, P100 families
  - Consumer: RTX/GTX with fp32_tflops >= 5.0
  - Exclude: mobile, laptop, max-q variants
- [x] Implement `src/gpu_costs/processor.py` for data aggregation
  - `filter_ml_gpus(dataset)` function
  - `calculate_statistics(dataset)` → price ranges, medians, counts
  - `prepare_time_series(dataset, category)` → sorted by date
- [x] Add filtering tests in `tests/test_gpu_costs_filters.py`
  - Test professional GPU detection
  - Test consumer GPU filtering
  - Test mobile GPU exclusion
  - Test performance threshold filtering

## Phase 3: Visualization Core (Serial, depends on Phase 2)

- [x] Create `scripts/plotting/plot_gpu_cost_trends.py` skeleton
  - Add shebang and module docstring
  - Import required libraries (matplotlib, pandas, seaborn, numpy, scipy)
  - Add `sys.path.insert` for src module access
- [x] Define `FORMAT_PRESETS` dictionary matching existing patterns
  - paper: font 14pt, figsize (6.5, 5), dpi 300, line_width 2.0, marker_size 6
  - poster: font 20pt, figsize (12, 9), dpi 300, line_width 3.0, marker_size 10
  - presentation: font 16pt, figsize (10, 7.5), dpi 150, line_width 2.5, marker_size 8
- [x] Implement CLI argument parser
  - `--preset {paper,poster,presentation}` (default: paper)
  - `--output PATH` (default: figures/main/gpu_cost_trends.png)
  - `--format {png,pdf,both}` (default: both)
  - `--data PATH` (default: data/raw/gpu_prices/ml_hardware.csv)
  - `--include-performance` flag for price-performance subplot
  - `--verbose` for debug logging
- [x] Implement `setup_logging(verbose)` function
- [x] Implement `validate_data_quality(dataset)` function
  - Check >= 50 GPUs after filtering
  - Verify date range coverage (earliest <= 2010, latest >= 2023)
  - Check price data completeness (>= 70% have prices)
  - Log warnings for quality issues

## Phase 4: Price Trends Figure (Serial, depends on Phase 3)

- [x] Implement `plot_price_trends(dataset, preset, ax=None)` function
  - Set up matplotlib figure with preset dimensions
  - Apply seaborn style "whitegrid"
  - Filter to professional GPUs → plot solid line (dark blue)
  - Filter to consumer GPUs → plot dashed line (light blue)
  - Set axis labels: "Year", "Launch Price (USD)"
  - Set title: "GPU Cost Trends for Scientific Computing"
  - Add legend with categories
  - Configure font sizes from preset
- [x] Implement `add_gpu_annotations(ax, dataset, key_models)` function
  - Annotate V100 (2017)
  - Annotate RTX 2080 Ti (2018)
  - Annotate A100 (2020)
  - Annotate H100 (2022)
  - Use smart label placement to avoid overlap
- [x] Add trend line for professional GPUs (optional)
  - Linear regression or lowess smoothing
  - Show as faint line behind points

## Phase 5: Price-Performance Figure (Parallel with Phase 4)

- [x] Implement `calculate_price_performance(dataset)` function
  - Compute FLOP/s per dollar = fp32_tflops / price
  - Filter out GPUs missing price or performance data
  - Return dataset with new column
- [x] Implement `plot_price_performance(dataset, preset, ax=None)` function
  - Set up subplot with log scale Y-axis
  - Plot each GPU as scatter point
  - Color by category (professional/consumer)
  - Fit exponential trend line (y = a * exp(b*x))
  - Annotate doubling time (~2.5 years from Epoch AI research)
  - Set labels: "Year", "GFLOP/s per USD (log scale)"
- [x] Implement combined figure generation when `--include-performance` set
  - Create 1x2 subplot grid
  - Call both plot functions
  - Ensure consistent styling

## Phase 6: Metadata Generation (Parallel with Phase 4-5)

- [x] Implement `generate_metadata_file(dataset, output_path, statistics)` function
  - Create {stem}-metadata.txt adjacent to output file
  - Write header: "GPU COST TRENDS METADATA"
  - Section 1: DATA SOURCE
    - Epoch AI citation with URL
    - CC BY license notice
    - Download instructions
  - Section 2: GENERATION INFO
    - Timestamp
    - Preset used
    - Output format
  - Section 3: DATASET STATISTICS
    - Total GPUs in raw dataset
    - GPUs after ML-relevance filter
    - Professional GPU count
    - Consumer GPU count
    - Date range (min year - max year)
  - Section 4: PRICE STATISTICS
    - Professional: min, max, median prices
    - Consumer: min, max, median prices
    - Overall: price range
  - Section 5: DATA QUALITY
    - Percentage with pricing data
    - Percentage with performance data
    - Any gaps or warnings
- [x] Follow metadata format from `sleap-dependency-graph-metadata.txt` pattern
  - 70-character width separator lines
  - Left-aligned text
  - Clear section headers

## Phase 7: Output Generation (Serial, depends on Phase 4-6)

- [x] Implement `save_figure(fig, output_path, format, dpi)` function
  - Support PNG format with specified DPI
  - Support PDF format (vector)
  - Handle "both" format → generate both files
  - Use `bbox_inches="tight"` to trim whitespace
  - Log file paths and sizes
- [x] Integrate all components in main() function
  - Parse CLI arguments
  - Load dataset with loader.load_gpu_dataset()
  - Filter with filters.is_ml_relevant()
  - Validate with validate_data_quality()
  - Generate figure(s) based on flags
  - Generate metadata
  - Save outputs
  - Print success message with paths

## Phase 8: Documentation (Parallel, can start anytime)

- [x] Update `README.md` with GPU cost trends section
  - Add to main figure generation documentation
  - Include quick start example
  - Document preset options
  - Link to Epoch AI dataset
  - Show example output paths
- [x] Add inline documentation to all functions
  - Google-style docstrings
  - Type hints for all parameters
  - Examples in docstrings
- [x] Create example usage section in script docstring
  - Basic usage
  - Poster preset
  - With price-performance subplot
  - Custom data path

## Phase 9: Testing (Parallel with implementation)

- [x] Add unit tests for loader module
  - `tests/test_gpu_costs_loader.py`
  - Test valid CSV loading
  - Test missing file handling
  - Test schema validation
- [x] Add unit tests for filters module
  - `tests/test_gpu_costs_filters.py`
  - Test professional GPU detection
  - Test consumer GPU filtering
  - Test categorization logic
- [x] Add unit tests for processor module
  - `tests/test_gpu_costs_processor.py`
  - Test statistics calculation
  - Test time series preparation
- [x] Add integration test for full pipeline
  - `tests/test_gpu_cost_visualization.py`
  - Mock Epoch AI dataset with sample data
  - Test end-to-end figure generation
  - Validate output file creation
  - Validate metadata content
- [x] Add visual regression test (optional)
  - Generate reference figure
  - Compare pixel-wise or hash-based

## Phase 10: Polish (Serial, final phase)

- [x] Run script with real Epoch AI dataset
  - Download actual ml_hardware.csv
  - Generate all presets (paper, poster, presentation)
  - Generate with --include-performance
  - Review outputs for visual quality
- [x] Verify style consistency with existing figures
  - Compare colors to software_complexity figures
  - Check font sizes match presets
  - Verify file naming conventions
- [x] Run all tests and ensure 100% pass rate
  - pytest tests/test_gpu_costs*.py
  - pytest tests/ (full suite)
- [x] Validate against OpenSpec requirements
  - openspec validate add-gpu-cost-trends --strict
  - Fix any validation errors
- [x] Final review checklist:
  - [x] Figures readable at target sizes
  - [x] Annotations don't overlap
  - [x] Legend clear and positioned well
  - [x] Metadata file complete and accurate
  - [x] README documentation clear
  - [x] Code follows repository style (ruff clean)
  - [x] All tests passing
  - [x] Git-ignored data files properly excluded
