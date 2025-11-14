# Specification: Diagram Polish and Completion

## Overview

This specification defines the requirements to polish and complete the 4 essential architecture diagrams (lablink-architecture, lablink-crd-connection, lablink-logging-pipeline, lablink-vm-provisioning) to publication quality by completing refactoring, adding dynamic spacing, and replacing placeholder icons.

## MODIFIED Requirements

### Requirement: Main diagram SHALL support font size presets

The system SHALL generate the main architecture diagram with configurable font size presets (paper, poster, presentation) with appropriate title positioning and spacing.

#### Scenario: Generate main diagram with paper preset for publication
**Given** the diagram generation system is available
**When** user runs:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type main \
  --fontsize-preset paper
```
**Then** the main diagram is generated with:
- Title positioned at top of diagram (not bottom)
- Node labels at 14pt font size
- Edge labels at 14pt font size
- Title at 32pt font size
- Node spacing (nodesep) of 0.6
- Rank spacing (ranksep) of 0.8
- 300 DPI output quality

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder.build_main_diagram()`
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_graph_attr()`
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_node_attr()`
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_edge_attr()`

---

#### Scenario: Generate main diagram with poster preset for presentations
**Given** the diagram generation system is available
**When** user runs:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type main \
  --fontsize-preset poster
```
**Then** the main diagram is generated with:
- Title positioned at top of diagram
- Node labels at 20pt font size (43% larger than paper)
- Edge labels at 20pt font size
- Title at 48pt font size
- Node spacing (nodesep) of 0.9 (50% more than paper)
- Rank spacing (ranksep) of 1.2 (50% more than paper)
- No text overlap or clipping
- 300 DPI output quality

**And** the increased spacing prevents overlap:
- 20pt fonts are 43% larger than 14pt fonts
- Spacing increased 50% to provide comfortable margin
- Rounded values (0.9, 1.2) easier to remember than proportional (0.86, 1.14)

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder.build_main_diagram()` - fontsize_preset parameter
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_graph_attr()` - dynamic spacing logic

---

#### Scenario: Main diagram wrapper function passes preset to builder
**Given** the `generate_main_diagram()` wrapper function is called
**When** the wrapper receives a `fontsize_preset` parameter
**Then** the wrapper passes the preset to `LabLinkDiagramBuilder.build_main_diagram()`
**And** the diagram is generated with the specified preset

**Code references**:
- `src/diagram_gen/generator.py::generate_main_diagram()` wrapper function (lines ~1223-1239)
- `scripts/plotting/generate_architecture_diagram.py` - passes args.fontsize_preset

---

### Requirement: Font preset spacing SHALL scale dynamically

The system SHALL adjust node spacing (nodesep) and rank spacing (ranksep) based on the selected font preset to prevent text overlap with larger fonts.

#### Scenario: Paper preset uses baseline spacing
**Given** a diagram is generated with paper preset (14pt fonts)
**When** the `_create_graph_attr()` helper method is called with `fontsize_preset="paper"`
**Then** the graph attributes include:
- `nodesep="0.6"` - baseline spacing
- `ranksep="0.8"` - baseline spacing
- Sufficient space for 14pt node labels

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_graph_attr()` - spacing dictionary

---

#### Scenario: Poster preset uses increased spacing for larger fonts
**Given** a diagram is generated with poster preset (20pt fonts)
**When** the `_create_graph_attr()` helper method is called with `fontsize_preset="poster"`
**Then** the graph attributes include:
- `nodesep="0.9"` - 50% more than paper (0.6 × 1.5 = 0.9)
- `ranksep="1.2"` - 50% more than paper (0.8 × 1.5 = 1.2)
- Sufficient space for 20pt node labels without overlap

**And** the spacing increase is justified by:
- 20pt fonts are 43% larger than 14pt (20 / 14 = 1.43)
- 50% spacing increase provides comfortable margin (1.5× safety factor)
- Prevents text overlap observed with fixed spacing

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_graph_attr()` - spacing calculation

---

#### Scenario: Presentation preset uses interpolated spacing
**Given** a diagram is generated with presentation preset (16pt fonts)
**When** the `_create_graph_attr()` helper method is called with `fontsize_preset="presentation"`
**Then** the graph attributes include:
- `nodesep="0.75"` - between paper (0.6) and poster (0.9)
- `ranksep="1.0"` - between paper (0.8) and poster (1.2)
- Sufficient space for 16pt node labels

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder._create_graph_attr()` - spacing dictionary

---

### Requirement: VM provisioning diagram SHALL use Terraform official icon

The system SHALL display the Terraform subprocess in the VM provisioning diagram using the official HashiCorp Terraform logo instead of a generic blank placeholder.

#### Scenario: Terraform icon renders when asset available
**Given** the Terraform icon file exists at `assets/icons/terraform.png`
**When** the VM provisioning diagram is generated
**Then** the Terraform subprocess node uses the Custom icon from the asset file
**And** the icon is displayed with label "Terraform\nSubprocess"
**And** the icon is visually consistent with other cloud provider icons (AWS, etc.)

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder.build_vm_provisioning_diagram()` - Terraform node (line ~517)
- `assets/icons/terraform.png` - official logo asset (256x256px PNG)

---

#### Scenario: Terraform icon falls back to Blank when asset missing
**Given** the Terraform icon file does NOT exist at `assets/icons/terraform.png`
**When** the VM provisioning diagram is generated
**Then** the Terraform subprocess node uses a Blank placeholder with label "Terraform\nSubprocess"
**And** the diagram generation completes successfully (does not fail)
**And** a fallback message is logged (optional)

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder.build_vm_provisioning_diagram()` - existence check and fallback

---

#### Scenario: Terraform icon path is calculated relative to generator module
**Given** the diagram generator module is located at `src/diagram_gen/generator.py`
**When** the Terraform icon path is calculated
**Then** the path is constructed as:
```python
terraform_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "terraform.png"
```
**And** the path resolves correctly regardless of working directory
**And** the path is cross-platform (works on Windows, Linux, macOS)

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder.build_vm_provisioning_diagram()` - path calculation using `__file__`

---

### Requirement: CRD connection edge label SHALL be concise

The CRD connection diagram SHALL use concise, accurate edge label text that clearly conveys the authentication and connection action without redundant prepositions.

#### Scenario: CRD connector label reads "Authenticates & Connects"
**Given** the CRD connection diagram is generated
**When** the edge from `connect_crd.py` to Chrome Remote Desktop application is rendered
**Then** the edge label reads "5. Authenticates & Connects" (without "to")
**And** the label is concise (25 characters vs 28 with "to")
**And** the label maintains technical accuracy (both authentication and connection concepts)
**And** the destination is clear from the arrow (no need for "to")

**Code references**:
- `src/diagram_gen/generator.py::LabLinkDiagramBuilder.build_crd_connection_diagram()` - edge label (line ~631)

---

## ADDED Requirements

None. All requirements are modifications to existing diagram generation behavior.

## REMOVED Requirements

None. No functionality is being removed.
