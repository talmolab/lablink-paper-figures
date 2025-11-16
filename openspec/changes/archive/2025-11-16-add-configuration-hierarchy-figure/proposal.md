# Add Configuration Hierarchy Figure

## Why

LabLink has extensive configurability across infrastructure, runtime, and application layers, but this flexibility is not currently visualized in the paper figures. A configuration hierarchy tree diagram would demonstrate LabLink's deployment versatility—showing how the same system can serve local development, workshop tutorials, and production research environments through configuration alone.

## What Changes

- Create configuration analysis document (`analysis/lablink-configuration-analysis.md`) documenting all 25+ configuration parameters
- Implement configuration hierarchy tree visualization script (`scripts/plotting/plot_configuration_hierarchy.py`)
- Generate multi-level tree diagram showing decision flow: Environment → SSL Strategy → Compute → Application → Scale
- Add new spec for configuration visualization capability

## Impact

- **Affected specs:** New capability `configuration-visualization`
- **Affected code:**
  - New: `scripts/plotting/plot_configuration_hierarchy.py`
  - New: `analysis/lablink-configuration-analysis.md`
  - New: `figures/main/lablink-configuration-hierarchy.{png,svg,pdf}`
- **Documentation:** Configuration hierarchy complements existing deployment impact, GPU reliance, and OS distribution figures
- **Research contribution:** Demonstrates LabLink's flexibility without overwhelming technical detail
