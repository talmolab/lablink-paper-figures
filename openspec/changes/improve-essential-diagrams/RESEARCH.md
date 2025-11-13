# Research Documentation: Essential Diagram Improvements

## Overview

This document captures research findings that informed the design decisions for improving the 4 essential architecture diagrams (lablink-architecture, lablink-crd-connection, lablink-logging-pipeline, lablink-vm-provisioning).

## Technical Accuracy Research

### WebRTC Verification for Chrome Remote Desktop

**Question**: Does Chrome Remote Desktop actually use WebRTC protocol?

**Research Method**: Web search for "does Chrome Remote Desktop use WebRTC protocol"

**Findings** (2025-11-13):
- **CONFIRMED**: Chrome Remote Desktop does use WebRTC protocol
- Chrome Remote Desktop is "built on Google's secure infrastructure using the latest open web technologies like WebRTC"
- Browser must support WebRTC and other "modern web platform features" to use Chrome Remote Desktop
- Implementation is nuanced: CRD leverages both WebRTC for P2P multimedia streaming AND Google's proprietary Chromoting protocol
- Chromoting protocol stacks on top to handle remote input synchronization, encryption, and authentication
- For networking layer, P2P connections are established using ICE (Interactive Connectivity Establishment) protocol and WebRTC
- WebRTC handles peer-to-peer connections and video streaming, while Chromoting provides complete remote desktop functionality

**Sources**:
- Multiple web sources from 2025 search results
- Chrome Remote Desktop documentation
- Developer discussions on WebRTC forums

**Conclusion**: 
- ✅ Current diagram label "WebRTC Connection" is technically accurate
- ✅ Improvement to "WebRTC P2P Connection" adds precision without being incorrect
- ✅ No conceptual error on WebRTC claim - verified as correct

**Recommendation**: Update label to "WebRTC P2P Connection" for technical precision, add note about Google Chromoting protocol if space permits.

---

## GraphViz Edge Label Positioning Research

**Question**: How can we achieve consistent edge label positioning "a few pixels above arrow lines"?

**Research Method**: Web search for "graphviz edge label positioning labeldistance labelangle consistent placement above line"

**Findings**:

### Key Limitations Discovered

1. **labeldistance and labelangle limitations**:
   - These attributes work in polar coordinates with origin at edge endpoint
   - They ONLY affect `headlabel` and `taillabel` (labels at edge endpoints)
   - They DO NOT affect regular `label` attribute (middle of edge)
   - 0-degree ray goes back along edge, positive angles = counterclockwise, negative = clockwise

2. **No horizontal label placement control**:
   - GraphViz doesn't let you choose horizontal label placement relative to edge
   - All solutions are "somewhat hacky" according to Stack Overflow discussions
   - `labelangle` does not rotate label text itself, only defines where to place it (text stays horizontal)

3. **Text rotation not supported**:
   - Labels cannot be rotated to align parallel with edges
   - Workarounds involve printing characters one-per-line or using rotated image files as labels

4. **Fundamental limitation**:
   - "GraphViz has no native way to consistently place labels 'above' edges" (Stack Overflow consensus)
   - "No native way to rotate text to align parallel with edges"

### Available Workarounds

1. **xlabel attribute**:
   - Places labels AFTER coordinates for nodes/edges have been decided
   - Better for avoiding overlaps, but still no "above edge" guarantee

2. **labelfloat attribute**:
   - Allows labels to "float" away from edges for clarity
   - GraphViz intelligently positions to avoid overlaps
   - Best available option for "good enough" positioning

3. **Post-processing with gvpr**:
   - Can reposition edge labels after layout
   - Complex, requires external processing step
   - Rejected as overly complex for marginal benefit

**Sources**:
- Stack Overflow: "How to place edge labels ON edge in graphviz"
- Stack Overflow: "Graphviz: Place edge label on the other side"
- Official GraphViz documentation on edge attributes
- GraphViz forum discussions on label spacing

**Conclusion**:
- ❌ Perfect "always N pixels above line" positioning is NOT possible in GraphViz
- ✅ Best available solution: `labelfloat=true` + increased fontsize
- ✅ This provides "good enough" improvement over default random positioning
- ⚠️ User expectations must be managed: "Consistent positioning" means "consistently better", not "perfectly above line"

**Recommendation**: 
- Use `labelfloat=true` in edge_attr for all diagrams
- Document GraphViz limitation in code comments
- Consider `xlabel` for specific problematic labels if needed
- Accept that some labels may still be suboptimal due to GraphViz constraints

---

## Diagrams Library Icon Availability Research

**Question**: What icons are available in the Python diagrams library for replacing Blank nodes?

**Research Method**: Web searches + documentation review at diagrams.mingrammer.com

**Findings**:

### AWS Icons Available

From `diagrams.aws.management`:
- ✅ **Cloudwatch** - Generic CloudWatch icon
- ✅ **CloudwatchAlarm** - Alarms
- ✅ **CloudwatchLogs** - Log groups (already in use)
- ✅ **CloudwatchRule** - Event rules
- ✅ **CloudwatchEventEventBased** - Event-based triggers ← **PERFECT for Subscription Filter**
- ✅ **CloudwatchEventTimeBased** - Time-based events

From `diagrams.aws.compute`:
- ✅ **Lambda** - Lambda functions (already in use)
- ✅ **LambdaFunction** - Alternative Lambda icon
- ✅ **EC2** - EC2 instances (already in use)

From `diagrams.aws.database`:
- ✅ **RDS** - Generic RDS icon ← **Good for database TRIGGER representation**
- ✅ **RDS variants** - MySQL, PostgreSQL, Oracle, MariaDB, SQL Server
- ✅ **Aurora**, **DynamoDB**, **Redshift**, etc.

### On-Premises Icons Available

From `diagrams.onprem.client`:
- ✅ **User** - Individual user icon (already in use)
- ✅ **Users** - Group of users
- ✅ **Client** - Generic client application icon

From `diagrams.onprem.container`:
- ✅ **Docker** - Docker logo/icon ← **PERFECT for Phase 2 in VM provisioning**
- ✅ **Containerd**, **Crio**, **Firecracker**, **K3S**, **Lxc**, **Rkt**

From `diagrams.onprem.database`:
- ✅ **Postgresql** - PostgreSQL logo ← **PERFECT for pg_notify()**
- ✅ **MySQL**, **MongoDB**, **Cassandra**, **Oracle**, **Neo4J**, etc. (15+ database icons)

From `diagrams.programming.language`:
- ✅ **Python** - Python logo ← **PERFECT for subscribe.py and connect_crd.py**
- ✅ **Java**, **JavaScript**, **Go**, **Rust**, etc.

From `diagrams.onprem.monitoring`:
- ✅ **Prometheus** - Monitoring service
- ✅ **Grafana**, **Datadog**, **New Relic**, **Splunk**, etc.

### Custom Icons Support

The library supports custom icons via:
- **diagrams.custom.Custom** class
- Can use local PNG files
- Can use remote URLs (download with urlretrieve)
- Icons should be ~256x256px for consistency

**Extensions available**:
- ExtendedDiagramIcons package provides additional icons
- autonode-diagrams can auto-generate icons from label text

### Icon Availability Summary

| Component | Current (Blank) | Available Replacement | Source |
|-----------|----------------|----------------------|---------|
| CloudWatch Agent | ❌ Blank | ✅ `Cloudwatch` | `diagrams.aws.management.Cloudwatch` |
| Subscription Filter | ❌ Blank | ✅ `CloudwatchEventEventBased` | `diagrams.aws.management.CloudwatchEventEventBased` |
| Database TRIGGER | ❌ Blank | ✅ `RDS` + label | `diagrams.aws.database.RDS` |
| pg_notify() | ❌ Blank | ✅ `Postgresql` | `diagrams.onprem.database.Postgresql` |
| subscribe.py | ❌ Blank | ✅ `Python` | `diagrams.programming.language.Python` |
| connect_crd.py | ❌ Blank | ✅ `Python` | `diagrams.programming.language.Python` |
| Terraform subprocess | ❌ Blank | ⚠️ Custom or library? | Check for `diagrams.onprem.iac.Terraform` OR custom terraform.png |
| Phase 1 (Cloud-init) | ❌ Blank | ⚠️ Keep Blank or generic | No obvious icon |
| Phase 2 (Docker) | ❌ Blank | ✅ `Docker` | `diagrams.onprem.container.Docker` |
| Phase 3 (Application) | ❌ Blank | ⚠️ Keep Blank or generic | No obvious icon |

**Terraform Icon Investigation** (requires additional check):
- Need to verify if diagrams library has Terraform icon in `diagrams.onprem.iac.*` or similar
- If not available in library, download official Terraform logo from terraform.io
- Terraform logo is open source and free to use
- Resize to ~256x256px and use with `diagrams.custom.Custom`

**Sources**:
- https://diagrams.mingrammer.com/docs/nodes/aws
- https://diagrams.mingrammer.com/docs/nodes/onprem
- diagrams library documentation and GitHub repository

**Conclusion**:
- ✅ 6 out of 10 Blank nodes have PERFECT library icon replacements
- ⚠️ 1 (Terraform) may need custom icon (pending verification)
- ⚠️ 3 (Phase 1, 3, and potentially Terraform) acceptable to keep as Blank if no good alternative

**Recommendation**:
- Replace all 6 with confirmed library icons immediately
- Investigate Terraform icon availability in library
- If no Terraform library icon: download official logo and use Custom node
- Keep Phase 1 and 3 as Blank nodes (no semantically appropriate icons)

---

## Title Placement Research

**Question**: How to move diagram titles from bottom to top in Python diagrams library?

**Research Method**: Web search for "Python diagrams library title placement top bottom graph_attr"

**Findings**:

### GraphViz labelloc Attribute

From official GraphViz documentation (graphviz.org/docs/attrs/labelloc/):

- **For graphs and clusters**: Only `labelloc=t` (top) and `labelloc=b` (bottom) are allowed
- **Default behavior**:
  - Root graph labels go on the **bottom** (labelloc=b default)
  - Cluster labels go on the **top** (labelloc=t default)
- **To place root graph title on top**: Set `labelloc="t"` in graph_attr

### Python diagrams Library Integration

- diagrams library uses GraphViz as rendering engine
- `graph_attr` parameter accepts GraphViz attributes dictionary
- Can set any valid GraphViz attribute: `graph_attr={"labelloc": "t", ...}`

### Implementation

```python
graph_attr = {
    "fontsize": "32",
    "bgcolor": "white",
    "dpi": "300",
    "labelloc": "t",  # Place title at top
    # ... other attributes
}

with Diagram(
    "My Title",
    graph_attr=graph_attr,
    # ...
):
    # diagram components
```

**Sources**:
- GraphViz official documentation: https://graphviz.org/docs/attrs/labelloc/
- Python diagrams library documentation
- Stack Overflow: "Graphviz (DOT) Captions"

**Conclusion**:
- ✅ Simple one-line fix: Add `"labelloc": "t"` to graph_attr dictionary
- ✅ Works for all diagram types
- ✅ No side effects or complications

**Recommendation**: Add `labelloc="t"` to `_create_graph_attr()` helper method with parameter to control (default True for top placement).

---

## Font Size Selection Research

**Question**: What font sizes are appropriate for publication-quality diagrams at 300 DPI?

**Analysis Method**: Typography best practices + empirical testing needs

**Findings**:

### Current Sizes (Before Improvement)
- Node labels: 11pt
- Edge labels: 12pt
- Cluster/title labels: 32pt

### Proposed Sizes
- Node labels: 14pt (27% increase)
- Edge labels: 14pt (17% increase)
- Cluster/title labels: 32pt (unchanged)

### Rationale

1. **11pt is too small for print**:
   - Standard body text in papers is 10-12pt
   - Diagram labels should be at least 12-14pt for comfortable reading
   - At 6-8 inch width (typical figure size), 11pt is borderline illegible

2. **14pt is minimum recommended**:
   - Typography guides suggest 12-14pt minimum for technical diagrams
   - 14pt provides comfortable reading without magnification
   - Maintains balance with 32pt titles (2.3:1 ratio)

3. **32pt titles are appropriate**:
   - Provides clear visual hierarchy
   - Large enough to serve as section headers
   - Proportional to diagram size at 300 DPI

### Testing Strategy

- Generate diagrams with 14pt
- Print at realistic size (6-8 inches wide)
- Verify readability at arm's length (~18-24 inches viewing distance)
- If text overlaps or layout is cramped, try 13pt
- If text still too small, try 15pt
- Iterate to find optimal balance

**Conclusion**:
- ✅ 14pt is reasonable starting point for both node and edge labels
- ✅ Maintains visual hierarchy (32pt title > 14pt labels)
- ⚠️ May need adjustment based on actual layout results

**Recommendation**: Start with 14pt, parameterize in helper methods to allow easy adjustment during testing.

---

## Summary of Research Findings

| Research Question | Finding | Impact on Design |
|------------------|---------|------------------|
| WebRTC in CRD? | ✅ Confirmed - CRD uses WebRTC + Chromoting | Update label to "WebRTC P2P Connection" for precision |
| Edge label positioning? | ❌ No perfect solution in GraphViz | Use `labelfloat=true` as "good enough", document limitation |
| Icon availability? | ✅ 6/10 have perfect replacements, 1 needs custom, 3 keep Blank | Replace where possible, document rationale |
| Title placement? | ✅ Simple: `labelloc="t"` | Add to graph_attr helper method |
| Font sizes? | ✅ 14pt recommended for print | Update node_attr and edge_attr helpers |

## Outstanding Investigations

1. **Terraform Icon**: Need to check if diagrams library has built-in Terraform icon or requires custom
2. **Print Testing**: After implementation, print diagrams at realistic size to validate font sizes
3. **Layout Testing**: After font size increase, verify no text overlap or layout overflow
4. **Code Validation**: Cross-reference all diagram flows with actual LabLink codebase for accuracy

## References

- GraphViz Official Documentation: https://graphviz.org/docs/
- Python diagrams Library: https://diagrams.mingrammer.com/
- Stack Overflow GraphViz discussions (multiple threads)
- Chrome Remote Desktop technical documentation
- Typography best practices for technical diagrams
