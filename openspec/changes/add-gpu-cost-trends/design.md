# Design: GPU Cost Trends Visualization

## Architecture

### Data Pipeline
```
Epoch AI Dataset (ZIP)
  → data/raw/gpu_prices/ml_hardware.csv
  → src/gpu_costs/loader.py (filter, clean, validate)
  → src/gpu_costs/processor.py (aggregate, interpolate)
  → scripts/plotting/plot_gpu_cost_trends.py (visualize)
  → figures/main/gpu_cost_*.{png,pdf}
```

### Module Structure
```
src/gpu_costs/
  __init__.py          # Public API
  loader.py            # Dataset loading and validation
  processor.py         # Data aggregation and statistics
  filters.py           # GPU categorization (ML-relevant, consumer, professional)

scripts/plotting/
  plot_gpu_cost_trends.py  # Main CLI script

data/raw/gpu_prices/
  ml_hardware.csv      # Epoch AI dataset (gitignored, user downloads)
  README.md            # Download instructions and citation
```

## Data Source Decision

### Selected: Epoch AI Machine Learning Hardware Database
**URL:** https://epoch.ai/data/machine-learning-hardware

**Rationale:**
- **Academic credibility**: Peer-reviewed methodology, widely cited in AI research
- **License**: CC BY (free to use, distribute, reproduce with attribution)
- **Coverage**: 160+ GPUs (2008-2025), comprehensive ML-focused dataset
- **Maintenance**: Actively updated (last: Nov 14, 2025)
- **Data quality**: Launch dates, pricing, FP32/FP16/FP64 performance metrics

**Citation:**
```
Epoch AI (2024), 'Data on Machine Learning Hardware',
Available at: https://epoch.ai/data/machine-learning-hardware
```

### Alternative Considered: Our World in Data
- **Pros**: Inflation-adjusted, polished visualizations
- **Cons**: Sources from same Epoch AI data, adds BLS inflation layer
- **Decision**: Use raw Epoch AI for direct control over processing

## Visualization Design

### Figure 1: GPU Price Trends (Primary)
**Type:** Line plot with annotated points
**X-axis:** Year (2006-2025)
**Y-axis:** Launch Price (USD, not inflation-adjusted to show nominal costs)
**Series:**
- Professional GPUs (Tesla, A100, H100) - solid line, dark blue
- Consumer GPUs suitable for ML (RTX series) - dashed line, light blue

**Annotations:**
- Key models: V100 (2017), RTX 2080 Ti (2018), A100 (2020), H100 (2022)
- SLEAP-compatible cards highlighted
- Trend lines showing price stability/increase

**Style matching:**
- Use seaborn `set_style("whitegrid")` like software complexity figures
- Colorblind-friendly palette
- Font sizes from FORMAT_PRESETS

### Figure 2: Price-Performance Evolution (Secondary/Optional)
**Type:** Scatter plot with trend line
**X-axis:** Year (2006-2025)
**Y-axis:** FLOP/s per dollar (log scale)
**Points:** Individual GPU releases, colored by category
**Trend line:** Exponential fit showing ~2.5 year doubling time

**Purpose:** Show efficiency improvements vs. absolute cost stagnation

## Data Processing Strategy

### GPU Filtering Logic
```python
def is_ml_relevant(gpu_row):
    """Filter to GPUs suitable for scientific ML/deep learning."""
    # Include professional datacenter GPUs
    if any(x in gpu_row['name'].lower()
           for x in ['tesla', 'a100', 'h100', 'v100', 'p100']):
        return True

    # Include consumer cards with sufficient VRAM (≥8GB typically)
    if 'rtx' in gpu_row['name'].lower() or 'gtx' in gpu_row['name'].lower():
        # Check VRAM or FP32 performance as proxy
        return gpu_row.get('fp32_tflops', 0) > 5.0

    # Exclude mobile/embedded GPUs
    if any(x in gpu_row['name'].lower()
           for x in ['mobile', 'laptop', 'max-q']):
        return False

    return False
```

### Time Series Handling
- **Sparse years**: Use all available data points, no interpolation for primary figure
- **Multiple releases per year**: Show all points, use transparency to handle overlap
- **Missing prices**: Exclude from dataset (some GPUs lack MSRP data)

### Statistics to Report in Metadata
- Total GPUs analyzed
- Date range
- Price range (min, max, median) for professional vs. consumer
- Average annual price change
- Data source and citation

## Configuration Design

### Preset System (matching existing patterns)
```python
FORMAT_PRESETS = {
    'paper': {
        'font_size': 14,
        'dpi': 300,
        'figsize': (6.5, 5),
        'line_width': 2.0,
        'marker_size': 6,
    },
    'poster': {
        'font_size': 20,
        'dpi': 300,
        'figsize': (12, 9),
        'line_width': 3.0,
        'marker_size': 10,
    },
    'presentation': {
        'font_size': 16,
        'dpi': 150,
        'figsize': (10, 7.5),
        'line_width': 2.5,
        'marker_size': 8,
    }
}
```

### CLI Interface
```bash
# Basic usage (downloads data if needed)
python scripts/plotting/plot_gpu_cost_trends.py \
    --preset paper \
    --output figures/main/gpu_cost_trends.png

# With price-performance subplot
python scripts/plotting/plot_gpu_cost_trends.py \
    --preset poster \
    --include-performance \
    --output figures/main/gpu_cost_analysis.pdf

# Specify data path
python scripts/plotting/plot_gpu_cost_trends.py \
    --data data/raw/gpu_prices/ml_hardware.csv \
    --preset paper \
    --format pdf
```

## Implementation Phases

### Phase 1: Data Infrastructure
1. Create `data/raw/gpu_prices/README.md` with download instructions
2. Implement `src/gpu_costs/loader.py` with CSV validation
3. Add data schema checks (required columns: name, release_date, price, fp32_tflops)

### Phase 2: Processing Logic
1. Implement filtering in `src/gpu_costs/filters.py`
2. Add price aggregation in `src/gpu_costs/processor.py`
3. Calculate statistics (median prices, trends)

### Phase 3: Visualization
1. Implement basic time series plot in `plot_gpu_cost_trends.py`
2. Add preset system matching existing patterns
3. Generate metadata file
4. Add price-performance subplot (optional feature)

### Phase 4: Integration
1. Update README.md with usage examples
2. Add tests for data loading and filtering
3. Validate against OpenSpec requirements

## Trade-offs

### Manual Download vs. Auto-Fetch
**Decision:** Manual download with clear instructions
**Rationale:**
- Epoch AI dataset is ~2MB ZIP (manageable size)
- Avoids API dependencies and rate limits
- Users see/verify data source directly
- Aligns with open science practices (data transparency)

### Inflation Adjustment
**Decision:** Show nominal prices (not inflation-adjusted)
**Rationale:**
- Nominal costs show actual researcher budget impact
- Complexity argument stronger with "sticker prices"
- Can add inflation note in figure caption
- Avoids dependency on BLS data

### GPU Selection Criteria
**Decision:** Include both professional and consumer ML-capable GPUs
**Rationale:**
- SLEAP runs on consumer cards (RTX series)
- Shows price range researchers face
- Highlights professional vs. consumer trade-offs
- More complete picture than datacenter-only

## Dependencies

**No new Python packages required:**
- matplotlib (existing)
- pandas (existing)
- seaborn (existing)
- numpy (existing)
- scipy (existing, for trend lines)

**Data dependency:**
- Epoch AI dataset (user downloads, ~2MB)

## Validation Strategy

### Data Validation
- Check required CSV columns exist
- Verify date range (2006-2025)
- Validate price > 0
- Ensure at least 50 GPUs after filtering

### Output Validation
- Generated figures exist at expected paths
- Metadata file contains required statistics
- PDF/PNG file sizes reasonable (<5MB)
- Visual inspection checklist in tests

## Open Questions
*None - design is complete based on existing patterns and research.*
