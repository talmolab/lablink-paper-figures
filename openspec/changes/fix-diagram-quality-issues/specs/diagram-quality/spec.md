# Capability: Diagram Quality and Rendering

## Overview

Ensure all 11 architecture diagrams render with publication-quality output based on actual visual inspection: fix missing arrows in API architecture, fix broken arrows and text overlap in detailed architecture, correct icon usage in VM provisioning, and ensure consistent font preset support.

## MODIFIED Requirements

### Requirement: Fix missing database edges in API architecture diagram

The system SHALL render all edges from API functional groups to the PostgreSQL database within the Allocator cluster.

**Previous behavior**: Edges from the 5 API group nodes (User Interface, Query API, Admin Management, VM Callbacks, Lambda Callback) to the PostgreSQL database were defined in code but not rendering visually.

**New behavior**: All database edges render correctly, either through spacing adjustments or repositioning the database node.

#### Scenario: Render edges from all API groups to database

**Given** the diagram type is `api-architecture`
**And** the diagram contains 5 API functional group nodes inside the Allocator cluster
**And** the PostgreSQL database is inside the same Allocator cluster
**When** the diagram is generated
**Then** edges from User Interface → Database must be visible (line 1076)
**And** edges from Query API → Database must be visible (line 1078)
**And** edges from Admin Management → Database must be visible (line 1086)
**And** edges from VM Callbacks → Database must be visible (line 1094)
**And** edges from Lambda Callback → Database must be visible (line 1109)
**And** all database edges must use gray color (#6c757d)

**Code location**: `src/diagram_gen/generator.py` lines 1076-1109

**Potential solutions**:
1. Add `nodesep` or `ranksep` override to increase intra-cluster spacing
2. Move database outside Allocator cluster (separate node)
3. Add `constraint="false"` to database edges to allow more routing freedom

---

### Requirement: Fix broken arrows and text overlap in detailed architecture

The system SHALL ensure all edges render correctly and no text overlaps in the detailed architecture diagram.

**Previous behavior**: Many edges broken or missing, text overlapping, hardcoded font sizes prevent poster preset support.

**New behavior**: All edges render, no text overlap, supports both poster and paper presets with proper spacing.

#### Scenario: Render all edges in detailed architecture

**Given** the diagram type is `architecture-detailed`
**And** the diagram contains 6+ clusters with complex nesting
**When** the diagram is generated
**Then** all edges must render completely (no broken/missing arrows)
**And** edge routing must be clear and unambiguous
**And** no edges may overlap with nodes or labels

**Code location**: `src/diagram_gen/generator.py` lines 317-433

#### Scenario: Add preset support to detailed architecture

**Given** the diagram type is `architecture-detailed`
**When** the diagram generation method is called
**Then** it must accept a `fontsize_preset` parameter (default `"paper"`)
**And** it must use `self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)`
**And** it must use `self._create_node_attr(fontsize_preset=fontsize_preset)`
**And** it must use `self._create_edge_attr(fontsize_preset=fontsize_preset)`
**And** it must NOT contain hardcoded `fontsize="11"` (line ~350)

**Code location**: `src/diagram_gen/generator.py` lines 318-350

#### Scenario: Prevent text overlap in detailed architecture

**Given** the diagram type is `architecture-detailed`
**And** the diagram uses poster preset (20pt fonts)
**When** the diagram is generated
**Then** `nodesep` must be at least `"1.2"` for cluster spacing
**And** `ranksep` must be at least `"2.0"` for layer spacing
**And** no cluster labels may overlap with contained nodes
**And** no edge labels may overlap with nodes or other labels

---

### Requirement: Use correct icon for application software in VM provisioning

The system SHALL display a generic Python or application icon for "Application Software ready" step, not Flask icon.

**Previous behavior**: VM provisioning startup sequence showed Flask icon for "3. Application Software ready", which is incorrect (Flask only runs on Allocator, not client VMs).

**New behavior**: Shows Python icon or generic application icon with proper fallback handling.

#### Scenario: Use Python icon as fallback for application software

**Given** the diagram type is `vm-provisioning`
**And** the "3-Phase Startup Sequence" cluster shows application readiness
**And** the custom application.png icon file does not exist
**When** the diagram is generated
**Then** the system must use Python icon as fallback (from `diagrams.programming.language import Python`)
**And** the label must remain "3. Application\nSoftware ready"
**And** the icon must NOT be Flask (Flask is only on Allocator)

**Code location**: `src/diagram_gen/generator.py` lines 554-559

**Current code**:
```python
# Phase 3: Application ready with app icon
app_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "application.png"
if app_icon_path.exists():
    phase3 = Custom("3. Application\nSoftware ready", str(app_icon_path))
else:
    phase3 = Blank("3. Application\nSoftware ready")  # ← PROBLEM: Blank fallback
```

**Required change**: Use Python icon as fallback instead of Blank.

---

### Requirement: Increase spacing for CRD connection workflow

The system SHALL provide adequate spacing in the CRD connection diagram to prevent edge label overlap.

**Previous behavior**: Some edge labels overlap with nodes or other labels in the 15-step workflow when using poster preset.

**New behavior**: Adequate spacing ensures no overlap with poster preset.

#### Scenario: Prevent label overlap in CRD workflow with poster preset

**Given** the diagram type is `crd-connection`
**And** the workflow contains 15 numbered steps across 4 phases
**And** the fontsize_preset is `"poster"`
**When** the diagram is generated
**Then** `ranksep` should be at least `"3.0"` for vertical spacing
**And** `sep` should be at least `"+30,30"` for edge clearance
**And** no edge labels shall overlap with nodes
**And** all 15 step numbers must be clearly readable

**Code location**: `src/diagram_gen/generator.py` lines 635-650

**Suggested override** (after line 637):
```python
# Override spacing for complex 15-step workflow if using poster preset
if fontsize_preset == "poster":
    graph_attr["ranksep"] = "3.0"  # Increase from default 2.5
    graph_attr["sep"] = "+30,30"   # Adjust edge clearance
```

---

### Requirement: Support consistent font presets across remaining diagrams

The system SHALL ensure diagrams using hardcoded fonts support the font preset system for both poster and paper generation.

**Previous behavior**: 6 diagrams (architecture-detailed, network-flow, cicd-workflow, network-flow-enhanced, monitoring, data-collection) used hardcoded font sizes, preventing consistent poster/paper generation.

**New behavior**: All diagrams use `_create_graph_attr()`, `_create_node_attr()`, and `_create_edge_attr()` helper methods with `fontsize_preset` parameter.

#### Scenario: Refactor network-flow to use preset system

**Given** the diagram type is `network-flow`
**When** the diagram generation method is called
**Then** it must accept a `fontsize_preset` parameter (default `"paper"`)
**And** it must use helper methods for graph, node, and edge attributes
**And** it must NOT contain hardcoded `fontsize="32"`, `fontsize="11"`, or `fontsize="12"`

**Code location**: `src/diagram_gen/generator.py` lines 435-479

#### Scenario: Refactor CI/CD workflow to use preset system

**Given** the diagram type is `cicd-workflow`
**When** the diagram generation method is called
**Then** it must accept a `fontsize_preset` parameter (default `"paper"`)
**And** it must use helper methods for attributes
**And** it must NOT contain hardcoded fontsize values (lines 891, 902, 907)

**Code location**: `src/diagram_gen/generator.py` lines 865-974

#### Scenario: Refactor network-flow-enhanced to use preset system

**Given** the diagram type is `network-flow-enhanced`
**When** the diagram generation method is called
**Then** it must accept a `fontsize_preset` parameter
**And** it must use helper methods for attributes

**Code location**: `src/diagram_gen/generator.py` lines 1125-1238

#### Scenario: Refactor monitoring diagram to use preset system

**Given** the diagram type is `monitoring`
**When** the diagram generation method is called
**Then** it must accept a `fontsize_preset` parameter
**And** it must use helper methods for attributes

**Code location**: `src/diagram_gen/generator.py` lines 1240-1329

#### Scenario: Refactor data-collection diagram to use preset system

**Given** the diagram type is `data-collection`
**When** the diagram generation method is called
**Then** it must accept a `fontsize_preset` parameter
**And** it must use helper methods for attributes

**Code location**: `src/diagram_gen/generator.py` lines 1331-1416

---

## ADDED Requirements

None. This change fixes existing capabilities.

---

## REMOVED Requirements

None. This change enhances existing behavior without removing functionality.

---

## Dependencies

- Python `diagrams` library (existing)
- GraphViz backend (existing)
- Font preset system: `LabLinkDiagramBuilder.FONT_PRESETS` (existing)
- Helper methods: `_create_graph_attr()`, `_create_node_attr()`, `_create_edge_attr()` (existing)
- Python icon: `from diagrams.programming.language import Python` (available)

---

## Testing Notes

### Visual Validation

Generate diagrams and verify fixes:

```bash
# API architecture - check database edges
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type api-architecture \
  --fontsize-preset poster

# Detailed architecture - check edges and preset support
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type architecture-detailed \
  --fontsize-preset paper

# VM provisioning - check Python icon
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type vm-provisioning \
  --fontsize-preset poster

# CRD connection - check spacing
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type crd-connection \
  --fontsize-preset poster
```

### Specific Validation Points

**API Architecture**:
- [ ] All 5 API groups have visible arrows to PostgreSQL database (gray color)
- [ ] User Interface → Database edge renders
- [ ] Query API → Database edge renders
- [ ] Admin Management → Database edge renders
- [ ] VM Callbacks → Database edge renders
- [ ] Lambda Callback → Database edge renders

**Detailed Architecture**:
- [ ] Uses fontsize_preset parameter
- [ ] No hardcoded font sizes
- [ ] All edges render (no broken arrows)
- [ ] No text overlap
- [ ] Supports both poster and paper presets

**VM Provisioning**:
- [ ] "3. Application Software ready" shows Python icon (NOT Flask)
- [ ] Startup sequence clear and readable

**CRD Connection**:
- [ ] No edge label overlap with poster preset
- [ ] All 15 step numbers visible

**All Diagrams**:
- [ ] Support both poster and paper presets
- [ ] Use helper methods (no hardcoded attrs in 6 refactored diagrams)
- [ ] Consistent styling

---

## Success Metrics

**Quantitative:**
- 11/11 diagrams generate without errors
- 5/5 database edges visible in API architecture
- 0 broken arrows in detailed architecture
- 0 text overlap instances
- 6/6 diagrams refactored to use preset system

**Qualitative:**
- Pass visual review for publication quality
- Accurate icon usage (Python not Flask for client VMs)
- Consistent visual style across suite