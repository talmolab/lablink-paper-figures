# Proposal: Add GPU Cost Trends Visualization

## Why

GPU acceleration is essential for SLEAP and other deep learning pose estimation tools, but GPU costs represent a significant barrier for computational biology researchers. While GPU price-performance improves (~2.5 year doubling time per Epoch AI research), absolute purchase costs for scientific GPUs have remained high ($5,000-$40,000 range) over the past 15+ years.

A GPU cost trends visualization will:
1. **Demonstrate hardware cost barriers** - Show why cloud-based solutions like LabLink are economically attractive compared to purchasing dedicated hardware
2. **Motivate on-demand GPU access** - Illustrate the sustained high cost of ownership that makes pay-per-use models compelling
3. **Provide publication-quality figure** - Support the LabLink paper's economic argument with authoritative data

This figure will use Epoch AI's Machine Learning Hardware Database (2006-2025, CC BY licensed) showing price trends for GPUs relevant to scientific computing and pose estimation workloads.

## What Changes

- Add new Python script `scripts/plotting/plot_gpu_cost_trends.py` to visualize GPU pricing over time
- Add GPU cost data module `src/gpu_costs/` for loading and processing Epoch AI dataset
- Download and cache Epoch AI ML Hardware Database to `data/raw/gpu_prices/`
- Create configurable presets matching existing repo conventions:
  - `paper` preset: 14pt fonts, 6.5"x5" for two-column journals
  - `poster` preset: 20pt fonts, 12"x9" for conference posters
  - `presentation` preset: 16pt fonts, 10"x7.5" for slides
- Support multiple output formats: PNG, PDF
- Generate two complementary figures:
  - **GPU price trends over time**: Launch MSRP of key scientific GPUs (2006-2025)
  - **Price-performance evolution**: FLOP/s per dollar showing efficiency improvements
- Auto-generate metadata file documenting data sources and statistics
- Follow established patterns from `plot_software_complexity.py` and `generate_sleap_dependency_graph.py`

## Impact

**Affected specs:**
- NEW: `gpu-cost-visualization` - New capability for GPU cost trend visualization

**Affected code:**
- `pyproject.toml` - No new dependencies (uses existing matplotlib, pandas, seaborn)
- `scripts/plotting/` - New script `plot_gpu_cost_trends.py`
- `src/gpu_costs/` - New module for data loading and processing
- `data/raw/gpu_prices/` - Epoch AI dataset cache
- `figures/main/` - Output location for generated figures
- `README.md` - Documentation for generating GPU cost figures

**Benefits:**
- Strengthens LabLink paper's economic motivation
- Uses authoritative, peer-reviewed data source (Epoch AI)
- Proper academic citation (CC BY license)
- Reusable framework for GPU cost analysis
- Follows established repository patterns

**Risks:**
- Dataset requires manual download from Epoch AI (160+ GPUs, ~2MB)
- Time series may need smoothing/interpolation for visual clarity
- Need to filter to ML-relevant GPUs (exclude gaming-only cards)
