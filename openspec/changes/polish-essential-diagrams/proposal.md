# Polish Essential Architecture Diagrams

## Why

The 4 essential architecture diagrams have **critical quality and completeness issues** that reduce publication readiness:

### Main Architecture Diagram (lablink-architecture.png)
- **Title position**: Title at bottom (GraphViz default) instead of top
- **Font sizes**: Using hardcoded 11pt/12pt fonts instead of helper methods with 14pt
- **No poster preset support**: `build_main_diagram()` doesn't accept `fontsize_preset` parameter
- **Cramped spacing**: Hardcoded `nodesep=0.6`, `ranksep=0.8` too tight for larger fonts

### CRD Connection Diagram (lablink-crd-connection.png)
- **Edge label precision**: Should be "Authenticates & Connects" (remove "to" for conciseness)
- **Font overlap**: Poster preset (20pt) causes text to overlap with icons
- **Layout alignment**: Graphics appear scattered, need better visual flow

### VM Provisioning Diagram (lablink-vm-provisioning.png)
- **Missing Terraform icon**: Using generic `Blank` node - unacceptable for infrastructure-as-code system
- **Incomplete**: All improvements from improve-essential-diagrams proposal not yet applied
- **API endpoint clarity**: Using `/api/vm-metrics` but needs verification

### Global Issues (All Diagrams)
- **Poster preset spacing**: `nodesep` and `ranksep` not adjusted for 20pt fonts
- **Incomplete refactoring**: Main diagram not using helper methods created in improve-essential-diagrams

## What Changes

### 1. Refactor build_main_diagram() to Use Helper Methods

**Current State** (lines 218-260 in generator.py):
- Hardcoded `graph_attr`, `node_attr`, `edge_attr` dictionaries
- Hardcoded font sizes (32pt title, 11pt nodes, 12pt edges)
- No `labelloc="t"` for title positioning
- No `fontsize_preset` parameter

**Proposed Changes**:
```python
def build_main_diagram(
    self,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper",  # NEW PARAMETER
) -> None:
    """Generate main LabLink architecture diagram.

    Args:
        fontsize_preset: Font size preset: "paper" (14pt), "poster" (20pt), "presentation" (16pt)
    """
    # Use helper methods instead of inline dictionaries
    graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)
    node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
    edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)

    # Get edge fontsize for consistency
    edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])
```

### 2. Add Dynamic Spacing for Font Presets

**Current State** (_create_graph_attr lines 106-123):
- Hardcoded `nodesep="0.6"` and `ranksep="0.8"`
- No adjustment for larger fonts in poster/presentation presets

**Proposed Changes**:
```python
def _create_graph_attr(
    self, dpi: int = 300, title_on_top: bool = True, fontsize_preset: str = "paper"
) -> dict:
    """Create graph attributes with dynamic spacing based on font preset."""
    fonts = self.FONT_PRESETS[fontsize_preset]

    # Adjust spacing based on font size to prevent overlap
    spacing = {
        "paper": {"nodesep": "0.6", "ranksep": "0.8"},       # 14pt fonts
        "poster": {"nodesep": "0.9", "ranksep": "1.2"},      # 20pt fonts - need MORE space
        "presentation": {"nodesep": "0.75", "ranksep": "1.0"}, # 16pt fonts
    }[fontsize_preset]

    return {
        "fontsize": str(fonts["title"]),
        "fontname": "Helvetica",
        "bgcolor": "white",
        "dpi": str(dpi),
        "pad": "0.5",
        "nodesep": spacing["nodesep"],  # DYNAMIC
        "ranksep": spacing["ranksep"],  # DYNAMIC
        "splines": "ortho",
        "labelloc": "t" if title_on_top else "b",
    }
```

### 3. Add Terraform Icon Using Custom Node

**Current State** (line 517 in generator.py):
```python
terraform = Blank("Terraform\nSubprocess")
```

**Proposed Solution**:
1. Download official Terraform logo from HashiCorp (open source, permissible use)
2. Save to `assets/icons/terraform.png` at 256x256px
3. Use `diagrams.custom.Custom` node:

```python
from diagrams.custom import Custom
from pathlib import Path

# Get path to Terraform icon
terraform_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "terraform.png"

if terraform_icon_path.exists():
    terraform = Custom("Terraform\nSubprocess", str(terraform_icon_path))
else:
    # Fallback to Blank if icon not found
    terraform = Blank("Terraform\nSubprocess")
```

### 4. Update CRD Edge Label for Conciseness

**Current State** (line 631):
```python
label="5. Authenticates & Connects to"
```

**Proposed Change**:
```python
label="5. Authenticates & Connects"  # Remove "to" for conciseness
```

### 5. Update generate_main_diagram() Wrapper Function

**Current State** (lines 1223-1239):
```python
def generate_main_diagram(
    config: ParsedTerraformConfig,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
):
    builder = LabLinkDiagramBuilder(config, show_iam=False, show_security_groups=False)
    builder.build_main_diagram(output_path, format=format, dpi=dpi)
```

**Proposed Change**:
```python
def generate_main_diagram(
    config: ParsedTerraformConfig,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper",  # NEW PARAMETER
):
    builder = LabLinkDiagramBuilder(config, show_iam=False, show_security_groups=False)
    builder.build_main_diagram(output_path, format=format, dpi=dpi, fontsize_preset=fontsize_preset)
```

### 6. Update Script to Pass Preset to Main Diagram

**Current State** (line 206 in generate_architecture_diagram.py):
```python
generate_main_diagram(config, output_path, format=fmt, dpi=args.dpi)
```

**Proposed Change**:
```python
generate_main_diagram(config, output_path, format=fmt, dpi=args.dpi, fontsize_preset=args.fontsize_preset)
```

## Impact

### Affected Components
- **Modified**: `src/diagram_gen/generator.py`
  - `_create_graph_attr()` - Add dynamic spacing (5 lines)
  - `build_main_diagram()` - Refactor to use helpers (~40 lines changed)
  - `build_vm_provisioning_diagram()` - Add Terraform icon (~8 lines changed)
  - `build_crd_connection_diagram()` - Update edge label (1 line changed)
  - `generate_main_diagram()` wrapper - Add parameter (2 lines changed)
- **Modified**: `scripts/plotting/generate_architecture_diagram.py` - Pass preset parameter (1 line changed)
- **New**: `assets/icons/terraform.png` - Official Terraform logo (256x256px)

### External Dependencies
- **Terraform logo**: Download from https://www.terraform.io/brand (permissible use under HashiCorp brand guidelines)
- **diagrams.custom.Custom**: Already available in diagrams library

### Breaking Changes
- **None**: All changes are additive with backwards-compatible defaults

### User-Visible Changes
- Main diagram now has title at top
- Main diagram supports poster preset (20pt fonts)
- Poster preset has appropriate spacing to prevent overlap
- Terraform shown with official icon (professional appearance)
- CRD label more concise ("Authenticates & Connects")

### Quality Metrics
- **Before**: Title at bottom, 11pt fonts, Blank Terraform icon, cramped poster layout
- **After**: Title at top, configurable fonts (14-20pt), Terraform icon, spacious poster layout

## Risk Assessment

### Low Risk
- Helper method refactoring: Well-tested pattern already used in 3 other diagrams
- Spacing adjustments: Simple numeric parameter changes
- Edge label update: Single-word removal

### Medium Risk
- **Terraform icon**: Requires downloading external asset
  - **Mitigation**: Fallback to Blank if icon file not found
  - **Validation**: Check HashiCorp brand guidelines for permissible use

### Testing Strategy
1. Generate all diagrams with paper preset (default) - verify no regression
2. Generate all diagrams with poster preset - verify no overlap
3. Verify Terraform icon renders correctly
4. Compare before/after screenshots for visual quality

## Success Criteria

1. ✅ Main diagram title appears at top
2. ✅ Main diagram uses 14pt fonts (paper preset) by default
3. ✅ Main diagram supports poster preset with 20pt fonts
4. ✅ Poster preset has sufficient spacing (no text overlap)
5. ✅ Terraform icon appears in VM provisioning diagram
6. ✅ CRD label reads "Authenticates & Connects"
7. ✅ All diagrams maintain 300 DPI publication quality
8. ✅ No layout breakage or text clipping

## Alternatives Considered

### Alternative 1: Keep Blank Terraform Icon
- **Rejected**: User feedback: "blank looks awful" and "entire infra is based off terraform"
- **Why**: Terraform is core to LabLink architecture, deserves proper visual representation

### Alternative 2: Use Text-Only Custom Node
- **Rejected**: Less professional than official logo
- **Why**: Custom icon provides visual consistency with other AWS/cloud icons

### Alternative 3: Fixed Spacing for All Presets
- **Rejected**: Causes overlap with larger fonts
- **Why**: Dynamic spacing ensures quality across all font sizes

### Alternative 4: Remove Poster Preset
- **Rejected**: Already implemented and used
- **Why**: Needed for presentations and posters

## Dependencies

### Upstream
- Requires `improve-essential-diagrams` changes to be in place (helper methods exist)

### Downstream
- None: These are output diagrams, not consumed by other code

## Timeline Estimate

- **Phase 1** (1 hour): Refactor build_main_diagram() to use helpers
- **Phase 2** (30 min): Add dynamic spacing to _create_graph_attr()
- **Phase 3** (1 hour): Download Terraform icon, implement Custom node with fallback
- **Phase 4** (15 min): Update CRD edge label
- **Phase 5** (15 min): Update wrapper function and script
- **Phase 6** (1 hour): Test all combinations (paper/poster × 4 diagrams)

**Total**: 4 hours

## Notes

- HashiCorp Terraform logo is available under permissible use guidelines for technical documentation
- Terraform icon fallback to Blank ensures robustness if asset missing
- Dynamic spacing formula: poster needs ~50% more space than paper due to 43% larger fonts (20pt vs 14pt)
- CRD label change aligns with proposal decision documented in improve-essential-diagrams
