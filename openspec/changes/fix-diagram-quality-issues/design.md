# Design: Systematic Diagram Quality Improvements

## Design Rationale

### Why This Approach?

**Research-driven solutions:**
- Documented root causes in `analysis/graphviz-settings-reference.md`
- Proven fix pattern from API architecture diagram (95% success rate)
- Systematic review identified common problems across diagrams

**Key insight:** GraphViz's orthogonal edge routing works best with TB (top-to-bottom) direction. LR + clusters + ortho = routing failure.

### Design Principles

1. **Use proven patterns** - TB direction + minlen pattern from API architecture
2. **Minimal changes** - Only change what's necessary to fix issues
3. **Consistency** - All diagrams use same helper methods and spacing approach
4. **Backward compatibility** - Existing diagrams still generate, just with better quality

## Architectural Analysis

### Current State: LabLinkDiagramBuilder Class

```
src/diagram_gen/generator.py (1416 lines)
├── Helper Methods (lines 93-177)
│   ├── _create_graph_attr() - Graph-level attributes with preset support
│   ├── _create_node_attr() - Node-level attributes with preset support
│   ├── _create_edge_attr() - Edge-level attributes with preset support
│   └── _adjust_label_for_preset() - Font size scaling
├── Diagram Generation Methods (11 total)
│   ├── build_main_diagram() - ❌ LR + clusters = broken arrows
│   ├── build_detailed_diagram() - ❌ Hardcoded fonts, no preset support
│   ├── build_network_flow_diagram() - ❌ Hardcoded fonts
│   ├── build_vm_provisioning_diagram() - ⚠️ LR + clusters = cramped
│   ├── build_crd_connection_diagram() - ⚠️ Insufficient spacing for workflow
│   ├── build_logging_pipeline_diagram() - ⚠️ Horizontal compression
│   ├── build_cicd_workflow_diagram() - ❌ Hardcoded fonts, Blank nodes
│   ├── build_api_architecture_diagram() - ✅ Reference implementation
│   ├── build_network_flow_enhanced_diagram() - ❌ Hardcoded fonts
│   ├── build_monitoring_diagram() - ❌ Hardcoded fonts
│   └── build_data_collection_diagram() - ❌ Hardcoded fonts
```

### Problem Patterns Identified

#### Pattern A: LR Direction + Clusters = Broken Arrows
**Affected:** architecture (1), vm-provisioning (5)

**Technical explanation:**
- GraphViz's orthogonal routing algorithm (`splines="ortho"`) optimized for TB layouts
- LR direction with clusters creates over-constrained layout graphs
- Cross-cluster edges fail to find valid routing paths

**Solution:**
```python
# BEFORE (broken)
direction="LR"  # Horizontal
user >> external_cluster_component  # Broken arrow

# AFTER (working)
direction="TB"  # Vertical
user >> Edge(minlen="2") >> external_cluster_component  # Proper routing
```

**Evidence:** API architecture changed from LR to TB, all arrows now render correctly

#### Pattern B: Insufficient Spacing for Poster Preset
**Affected:** crd-connection (2), architecture-detailed (3), logging-pipeline (6)

**Technical explanation:**
- Poster preset: 20pt fonts (43% larger than 14pt paper preset)
- Default spacing: `nodesep=1.0`, `ranksep=1.5` designed for paper
- Large fonts + default spacing = text overlap and cramping

**Current spacing values:**
```python
spacing = {
    "paper": {"nodesep": "1.0", "ranksep": "1.5"},
    "poster": {"nodesep": "1.8", "ranksep": "2.5"},
}
```

**Problem:** `ranksep=2.5` still insufficient for:
- TB workflows with 15+ vertical steps
- Complex clusters with 3+ nested components

**Solution:** Workflow-specific overrides
```python
# CRD connection (15 steps, TB direction)
graph_attr["ranksep"] = "3.0"  # +20% vs default poster

# Detailed architecture (many clusters)
graph_attr["nodesep"] = "1.2"
graph_attr["ranksep"] = "2.0"
```

#### Pattern C: Hardcoded Fonts (No Preset Support)
**Affected:** detailed (3), network-flow (4), cicd (7), enhanced (9), monitoring (10), data-collection (11)

**Technical explanation:**
- Early diagrams written before `FONT_PRESETS` system established
- Hardcoded `fontsize`, `nodesep`, `ranksep` values
- Cannot generate both poster and paper versions

**Current pattern:**
```python
# OLD (hardcoded)
graph_attr = {
    "fontsize": "32",      # Hardcoded title size
    "nodesep": "0.8",      # Hardcoded spacing
    "ranksep": "1.5",      # Hardcoded spacing
    "fontname": "Sans-Serif",
    "splines": "ortho",
}
node_attr = {"fontsize": "11"}  # Hardcoded node label size
```

**New pattern (from API architecture):**
```python
# NEW (preset-driven)
graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)
```

## Diagram-Specific Fix Designs

### Fix 1: Main Architecture Diagram
**File:** `generator.py` lines 245-315

**Current issues:**
- Direction: LR
- Cross-cluster edges from Admin/Allocator/CloudWatch
- No minlen parameters

**Changes:**
```python
# Line 274: Change direction
direction="TB",  # Was "LR"

# Lines 302-316: Add minlen to cross-cluster edges
admin >> Edge(color="red", minlen="2") >> iam  # Was: no minlen
allocator >> Edge(minlen="2") >> client_vm     # Was: no minlen
cloudwatch >> Edge(minlen="2") >> lambda_fn    # Was: no minlen
# ... apply to all cross-cluster edges
```

**Expected result:** All arrows render correctly with clean orthogonal routing

### Fix 2: CRD Connection Diagram
**File:** `generator.py` lines 592-786

**Current issues:**
- Direction: TB (correct)
- 15-step workflow vertically stacked
- `ranksep=2.5` insufficient for poster preset
- Text overlap on edge labels

**Changes:**
```python
# After line 635: Override ranksep for complex workflow
graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
graph_attr["ranksep"] = "3.0"  # Increase from 2.5 to 3.0
graph_attr["sep"] = "+35,35"   # Increase from +25,25 for edge clearance

# Consider: Reduce to paper preset for this diagram
# fontsize_preset = "paper"  # Override in CLI for 15-step workflow
```

**Expected result:** Clear vertical flow with no label overlap

### Fix 3: Detailed Architecture Diagram
**File:** `generator.py` lines 317-433

**Current issues:**
- No `fontsize_preset` parameter
- Hardcoded `graph_attr` (line 327)
- Fixed font sizes (11pt, too small for poster)
- No minlen on cross-cluster edges

**Changes:**
```python
# Line 318: Add fontsize_preset parameter
def build_detailed_diagram(
    self,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper",  # ADD THIS
) -> None:

# Lines 327-350: Replace hardcoded attrs with helpers
graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
graph_attr["nodesep"] = "1.2"  # Override for dense clusters
graph_attr["ranksep"] = "2.0"  # Override for many layers
node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)

# Lines 370+: Add minlen to cross-cluster edges
# (Identify and add minlen="2" to edges crossing cluster boundaries)
```

**Expected result:** Readable layout with consistent preset support

### Fix 4: VM Provisioning Diagram
**File:** `generator.py` lines 481-590

**Current issues:**
- Direction: LR
- "3-Phase Startup Sequence" cluster cramped
- Cross-cluster edges to startup phases

**Option A: Change to TB direction**
```python
# Line 520: Change direction
direction="TB",  # Was "LR"
# Add minlen to cross-cluster edges
```

**Option B: Keep LR, increase spacing**
```python
# Line 520: Keep LR but increase ranksep
direction="LR",
graph_attr["ranksep"] = "2.5"  # Increase horizontal spacing
```

**Recommendation:** Option A (TB direction) for consistency with other clustered diagrams

### Fix 5: Logging Pipeline Diagram
**File:** `generator.py` lines 788-863

**Current issue:**
- Direction: LR (works for linear flow)
- "Observability" cluster horizontally compressed
- `ranksep=1.5` insufficient for cluster width

**Changes:**
```python
# After line 813: Override ranksep for LR layout
graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
graph_attr["ranksep"] = "2.5"  # Increase horizontal spacing
graph_attr["nodesep"] = "1.0"  # Maintain vertical spacing
```

**Expected result:** More horizontal space for 6-step pipeline

### Fix 6: CI/CD Workflow Diagram
**File:** `generator.py` lines 865-974

**Current issues:**
- Hardcoded fonts (lines 891, 902, 907)
- Blank nodes as placeholders (lines 927-929, 938, 943, 948)
- No `fontsize_preset` parameter

**Changes:**
```python
# Line 866: Add fontsize_preset parameter
def build_cicd_workflow_diagram(
    self,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper",  # ADD THIS
) -> None:

# Lines 891-907: Replace hardcoded attrs
graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)

# Lines 927-948: Replace Blank nodes with visible text or icons
# Option 1: Use existing icons (GitHub, Docker, etc.)
# Option 2: Use Custom() nodes with text labels
# Recommendation: Option 1 for visual consistency
```

### Fixes 7-10: Add Preset Support (4 diagrams)
**Files:** network-flow (435-479), network-flow-enhanced (1125-1238), monitoring (1240-1329), data-collection (1331-1416)

**Pattern (apply to all 4):**
```python
# Add fontsize_preset parameter
def build_X_diagram(
    self,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper",  # ADD THIS
) -> None:
    # Replace hardcoded attrs with helpers
    graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
    node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
    edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)
```

## Font Preset Strategy

### Decision Matrix: When to Use Poster vs Paper

| Diagram | Preset | Rationale |
|---------|--------|-----------|
| architecture | **poster** | Main figure, high visibility needed |
| architecture-detailed | **paper** | Too complex for large fonts |
| network-flow | **paper** | Simple flow, compact OK |
| vm-provisioning | **poster** | Important workflow |
| crd-connection | **paper** | 15 steps, need information density |
| logging-pipeline | **poster** | Key observability diagram |
| cicd-workflow | **paper** | Complex parallel flows |
| api-architecture | **poster** | Reference implementation |
| network-flow-enhanced | **paper** | 3 configurations, detailed |
| monitoring | **paper** | 3 parallel services |
| data-collection | **paper** | Linear flow, compact OK |

### Rationale:
- **Poster**: Simple topologies (≤5 major components), high visibility for presentations
- **Paper**: Complex workflows (>10 steps or >3 clusters), information density for publications

## Testing Strategy

### Validation Levels

**Level 1: Visual Inspection**
- Open all 11 regenerated PNGs
- Check for: broken arrows, text overlap, readability at 100% zoom
- Compare against API architecture reference

**Level 2: Preset Validation**
- Generate each diagram with both poster and paper presets
- Verify spacing scales appropriately
- Confirm text remains readable in both versions

**Level 3: Pattern Validation**
- Verify all clustered diagrams use TB direction
- Verify all cross-cluster edges have `minlen="2"`
- Verify all diagrams use helper methods (no hardcoded attrs)

### Test Commands

```bash
# Generate all diagrams with poster preset
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type all \
  --fontsize-preset poster

# Generate specific diagram with paper preset
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type crd-connection \
  --fontsize-preset paper
```

## Alternative Approaches Considered

### Alternative 1: Split Complex Diagrams
**Idea:** Split detailed architecture into 2 diagrams (Infrastructure + Observability)

**Pros:**
- Simpler layouts, easier to understand
- Less cramping per diagram

**Cons:**
- More diagrams to maintain
- May not be desired for publication (single comprehensive view preferred)

**Decision:** Rejected - Try spacing adjustments first, split only if necessary

### Alternative 2: Use Polyline Splines Instead of Ortho
**Idea:** Change `splines="polyline"` to avoid orthogonal routing issues with LR

**Pros:**
- More flexible routing, works with LR direction
- Less likely to fail

**Cons:**
- Loses clean orthogonal (right-angle) aesthetic
- Not consistent with other diagrams
- TB + ortho is the proven pattern

**Decision:** Rejected - TB direction is better solution

### Alternative 3: Manually Adjust Each Diagram Individually
**Idea:** Fine-tune spacing for each diagram without systematic pattern

**Pros:**
- Maximum control per diagram

**Cons:**
- Not maintainable
- No reusable patterns
- Future diagrams won't benefit

**Decision:** Rejected - Systematic approach with documented patterns is essential

## Implementation Sequence

### Phase 1: Quick Wins (Day 1, 2-3 hours)
**Goal:** Fix most visible critical issues

1. Architecture diagram (LR→TB + minlen) - 1 hour
2. Logging pipeline (spacing only) - 30 min
3. VM provisioning (LR→TB) - 30 min

**Rationale:** High-impact fixes with low complexity

### Phase 2: Complex Fixes (Day 2, 4-6 hours)
**Goal:** Address technical debt and complex layouts

4. CRD connection (spacing + testing) - 2 hours
5. Detailed architecture (preset refactor OR split) - 2-3 hours
6. CI/CD workflow (preset refactor + Blank nodes) - 2 hours

**Rationale:** These require more testing and potential iteration

### Phase 3: Consistency Pass (Day 3, 2-3 hours)
**Goal:** Ensure all diagrams follow patterns

7. Add preset support to 4 remaining diagrams - 2 hours
8. Final visual review of all 11 diagrams - 30 min
9. Update documentation - 30 min

**Rationale:** Low-risk improvements for long-term maintainability

## Documentation Updates

### Update 1: GraphViz Settings Reference
**File:** `analysis/graphviz-settings-reference.md`

**Add section:** "Workflow-Specific Spacing Guidelines"
```markdown
### Workflow-Specific Spacing Guidelines

**TB Workflows (15+ vertical steps):**
- `ranksep="3.0"` or higher
- Example: CRD connection (15 steps)

**LR Workflows with Clusters:**
- `ranksep="2.5"` for horizontal spacing
- Example: Logging pipeline (6 steps + cluster)

**Dense Cluster Layouts:**
- `nodesep="1.2"` minimum
- `ranksep="2.0"` minimum
- Example: Detailed architecture (6+ clusters)
```

### Update 2: README or Diagram Guide
**File:** `README.md` or new `docs/diagram-generation.md`

**Add section:** "Generating Publication-Quality Diagrams"
```markdown
## Font Presets

- **Poster preset** (`--fontsize-preset poster`): 20pt fonts for presentations
- **Paper preset** (`--fontsize-preset paper`): 14pt fonts for publications

### Recommended Presets by Diagram

- **Poster**: architecture, vm-provisioning, logging-pipeline, api-architecture
- **Paper**: architecture-detailed, crd-connection, cicd-workflow, network diagrams
```

## Success Metrics

### Quantitative:
- 11 of 11 diagrams generate without errors
- 0 broken arrows across all diagrams
- 0 text overlap instances
- 100% diagrams use preset system

### Qualitative:
- All diagrams meet publication standards
- Consistent visual style across suite
- Maintainable pattern for future diagrams
- Positive user review for poster presentation

## Rollback Strategy

If fixes introduce new issues:

1. **Git revert** to previous commit (current diagrams work, just with issues)
2. **Selective rollback** - Keep fixes that work, revert problematic ones
3. **Reference implementation** - API architecture diagram always works as fallback pattern

**Confidence:** High - All fixes based on proven API architecture pattern
