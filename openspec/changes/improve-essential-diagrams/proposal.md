# Improve Essential Architecture Diagrams

## Why

The 4 essential architecture diagrams for the LabLink paper have **critical quality and accuracy issues** that will reduce publication impact and reader comprehension:

### Visual Quality Issues (All 4 Diagrams)
1. **Title placement**: Titles are at the bottom (GraphViz default), reducing professional appearance and making diagrams harder to scan
2. **Text size**: All text except titles is too small for publication quality at 300 DPI, reducing readability in printed papers
3. **Edge label positioning**: Labels are randomly positioned by GraphViz's layout algorithm, sometimes overlapping edges or being placed far from their associated connections, creating visual confusion

### Accuracy and Completeness Issues (Per Diagram)

**lablink-architecture.png** (Main System Overview)
- ✅ Overall structure is excellent
- Only needs: Global fixes (title, text size, edge labels)

**lablink-crd-connection.png** (Chrome Remote Desktop Connection)
- **Missing graphics**: Using generic Blank nodes for TRIGGER, pg_notify(), subscribe.py, connect_crd.py
- **Conceptual error**: "Launches" CRD is misleading - CRD authenticates and establishes WebRTC connection, but doesn't "launch" the application
- **Accuracy issue**: Need to verify WebRTC claim (Research confirms: ✅ CRD does use WebRTC for P2P connections + Google's Chromoting protocol)
- **Missing context**: CRD command authenticates user for Google CRD access to VM (not explained)
- **Missing context**: VMs are pre-launched by admin (not shown in this figure, should clarify in label)

**lablink-logging-pipeline.png** (CloudWatch Logging)
- **Missing graphics**: CloudWatch Agent and Subscription Filter are Blank nodes
- **Unclear mechanism**: What subscription filter does (should show it triggers Lambda, not just passes through)
- **Missing endpoint**: Admin viewing logs from browser (logs are accessible via web UI, should show this)
- **Missing detail**: Subscription filter pattern and how it matches log events

**lablink-vm-provisioning.png** (VM Provisioning & Lifecycle)
- **Missing graphics**: Terraform subprocess, all 3 cloud-init phase nodes, Docker phase, Application ready - all Blank nodes
- **Missing critical flow**: APIs used by VM to connect back to allocator (client feedback that updates database with startup status)
- **Title issue**: Remove "Lifecycle" from title (diagram doesn't show complete lifecycle - no teardown, monitoring, or data collection)
- **Missing timing context**: Phase durations are shown but no indication of total provisioning time (~105 seconds)

### Research Findings

**WebRTC Investigation**: Chrome Remote Desktop does use WebRTC protocol for establishing P2P connections and handling video streaming, combined with Google's proprietary Chromoting protocol for complete remote desktop functionality. This is technically accurate.

**Available Diagrams Library Icons**:
- ✅ CloudWatch: CloudwatchLogs, CloudwatchEventEventBased, Cloudwatch (all available)
- ✅ Database: RDS with PostgreSQL variant available
- ✅ Containers: Docker icon available in onprem.container
- ✅ Client: Client icon available in onprem.client
- ✅ Programming: Python icon available for .py scripts
- ⚠️ Custom needed: PostgreSQL TRIGGER and pg_notify() require custom approach (no native icon)

## What Changes

### Global Improvements (All 4 Diagrams)

1. **Title Placement**: Add `labelloc="t"` to graph_attr to place titles at top
2. **Text Size Increase**: Increase node_attr fontsize from 11 to 14-16 (keep title at 32)
3. **Edge Label Strategy**: 
   - Increase edge label fontsize from 12 to 14
   - Add `labelfloat=true` to allow labels to move away from edges for clarity
   - Consider using `xlabel` attribute for critical labels (positions after layout)
   - Document GraphViz limitation: No native "always above line" positioning exists

### Diagram-Specific Improvements

**1. lablink-architecture.png**
- Apply global improvements only
- No structural changes (diagram is excellent)

**2. lablink-crd-connection.png**
- Replace `Blank("TRIGGER\n(on CrdCommand)")` with RDS icon + label "Database TRIGGER"
- Replace `Blank("pg_notify()")` with small custom icon or use onprem.database.Postgresql with label "pg_notify()"
- Replace `Blank("subscribe.py\n(LISTEN)")` with Python icon + label "subscribe.py (LISTEN)"
- Replace `Blank("connect_crd.py")` with Python icon + label "connect_crd.py"
- Change edge label "5. Launches" → "5. Authenticates & Connects to"
- Change edge label "6. WebRTC Connection" → "6. WebRTC P2P Connection (Google Chromoting)"
- Add annotation to Client VM: "Client VM (Admin-provisioned)"
- Add note explaining: "CRD command authenticates user's Google account for remote access"

**3. lablink-logging-pipeline.png**
- Replace `Blank("CloudWatch\nAgent")` with onprem.container.Docker or custom monitoring icon
- Replace `Blank("Subscription\nFilter")` with CloudwatchEventEventBased icon
- Change subscription filter edge label to clearly show: "3. Triggers (on pattern match)"
- Add Admin viewing logs: User icon + edge from database → admin with label "7. View logs (web UI)"
- Add annotation showing subscription filter pattern: "(pattern: all events)"

**4. lablink-vm-provisioning.png**
- Replace `Blank("Terraform\nSubprocess")` with custom Terraform logo icon (use Custom node with terraform.png)
- Replace cloud-init phase Blank nodes with numbered cluster showing:
  - Phase 1: Use onprem.container.Docker or custom icon
  - Phase 2: Use onprem.container.Docker icon
  - Phase 3: Use generic.blank.Blank with checkmark or custom icon
- Add feedback flow: Client VM → Allocator with label "4. Status updates (POST /api/vm-metrics)"
- Change title: "LabLink VM Provisioning & Lifecycle" → "LabLink VM Provisioning"
- Add edge showing: allocator → database with label "5. Store provisioning metrics"
- Add annotation: "Total provisioning time: ~105 seconds"

### Code Changes

**Modified**: `src/diagram_gen/generator.py`
- Update `_create_graph_attr()` helper method (new):
  ```python
  def _create_graph_attr(self, dpi=300, title_on_top=True):
      """Create consistent graph attributes for all diagrams."""
      return {
          "fontsize": "32",
          "fontname": "Helvetica",
          "bgcolor": "white",
          "dpi": str(dpi),
          "pad": "0.5",
          "nodesep": "0.6",
          "ranksep": "0.8",
          "splines": "ortho",
          "labelloc": "t" if title_on_top else "b",  # NEW: Title at top
      }
  ```
- Update `_create_node_attr()` helper method (new):
  ```python
  def _create_node_attr(self, fontsize=14):
      """Create consistent node attributes."""
      return {
          "fontsize": str(fontsize),  # Increased from 11
          "fontname": "Helvetica",
      }
  ```
- Update `_create_edge_attr()` helper method (new):
  ```python
  def _create_edge_attr(self, fontsize=14):
      """Create consistent edge attributes."""
      return {
          "fontsize": str(fontsize),  # Increased from 12
          "fontname": "Helvetica",
          "labeldistance": "2.0",
          "labelangle": "0",
          "labelfloat": "true",  # NEW: Allow labels to float for clarity
      }
  ```
- Refactor all 4 diagram methods to use these helpers
- Update `build_crd_connection_diagram()`: Replace Blank nodes with proper icons
- Update `build_logging_pipeline_diagram()`: Replace Blank nodes, add admin viewing
- Update `build_vm_provisioning_diagram()`: Replace Blank nodes, add feedback flow, update title

**New**: `assets/icons/terraform.png` (if custom icon needed)
- Download official Terraform logo for custom node
- Resize to appropriate dimensions for diagram

### Documentation Changes

**Modified**: `figures/main/diagram_metadata.txt`
- Update metadata with improvement details
- Document icon choices and rationale

**New**: `openspec/changes/improve-essential-diagrams/RESEARCH.md`
- Document WebRTC verification research
- Document available diagrams library icons
- Document GraphViz edge label positioning limitations
- Document icon selection rationale

## Impact

### Affected Components
- **Modified**: `src/diagram_gen/generator.py` - Refactor to use helper methods, update 4 diagram methods (~200 lines changed)
- **Modified**: All 4 essential diagrams regenerated with improvements
- **New**: Helper methods for consistent styling
- **Potentially new**: Custom Terraform icon asset

### External Dependencies
- **diagrams library**: Already installed, using existing icons
- **Custom icons**: May need to download Terraform logo (free, open source)
- **No new Python dependencies**: All improvements use existing packages

### Breaking Changes
- **None**: Generated diagrams are outputs, not APIs
- All changes are visual improvements, not behavioral changes

### User-Visible Changes
- Diagrams have titles at top (more professional)
- Text is more readable (larger font sizes)
- Edge labels are clearer (larger, better positioning)
- Missing icons replaced with proper graphics (more accurate)
- Conceptual errors corrected (more accurate)
- Missing context added (more complete)

### Publication Impact
- **High priority**: These 4 diagrams are for the main paper figures
- Improved visual quality increases publication acceptance likelihood
- Corrected accuracy issues prevent reviewer questions/concerns
- Better readability ensures printed copies are clear at typical paper sizes

### Quality Metrics
- **Before**: Title at bottom, 11pt node text, 12pt edge text, 8 Blank placeholder nodes, 2 conceptual errors
- **After**: Title at top, 14-16pt node text, 14pt edge text, 0-2 Blank nodes (only where truly no icon exists), 0 conceptual errors

## Risk Assessment

### Low Risk
- Global styling changes (labelloc, fontsize) are simple GraphViz attributes
- Icon replacements use well-documented diagrams library APIs
- Changes are isolated to diagram generation (no runtime code affected)

### Medium Risk
- Edge label positioning: GraphViz has fundamental limitations (no "always above" option)
- Custom icons: May need to create/download additional assets
- Text size: Too large may cause layout issues (need to test and adjust)

### Mitigation Strategies
1. **Test iteratively**: Generate each diagram after changes, verify layout looks correct
2. **Icon fallback**: If custom icons don't work, document why Blank nodes are needed
3. **Font size tuning**: Start with 14pt, adjust up/down based on visual results
4. **Edge label workaround**: Use `labelfloat=true` + manual `xlabel` positioning for critical labels if needed
5. **Validate with maintainers**: Review diagrams with LabLink team before finalizing

## Success Criteria

1. ✅ All 4 diagrams have titles at top
2. ✅ Text is readable at 14-16pt (node labels) and 14pt (edge labels)
3. ✅ Edge labels are positioned clearly (even if not perfectly "above line" due to GraphViz limitations)
4. ✅ All reasonable icon replacements completed (TRIGGER, pg_notify, subscribe.py, connect_crd.py, CloudWatch Agent, Subscription Filter, phases)
5. ✅ Conceptual errors corrected ("Launches" → "Authenticates & Connects", "Lifecycle" → "Provisioning")
6. ✅ Missing context added (CRD authentication, admin viewing logs, VM feedback flow, provisioning time)
7. ✅ Diagrams maintain 300 DPI publication quality
8. ✅ No layout breakage (all nodes and edges still visible and clear)

## Alternatives Considered

### Alternative 1: Use different diagramming library (e.g., PlantUML, Mermaid)
- **Rejected**: Too much rework, existing diagrams are good quality
- **Why**: Only need incremental improvements, not complete rewrite

### Alternative 2: Manually edit PNG files in image editor
- **Rejected**: Not reproducible, violates "diagrams as code" principle
- **Why**: Code-based diagrams ensure reproducibility and version control

### Alternative 3: Keep Blank nodes, don't replace with icons
- **Rejected**: Reduces visual quality and professionalism
- **Why**: Proper icons significantly improve diagram clarity and aesthetics

### Alternative 4: Create custom edge label positioning via post-processing
- **Rejected**: Too complex for marginal improvement
- **Why**: GraphViz labelfloat + increased fontsize provides "good enough" solution

## Dependencies

### Upstream
- Requires `expand-diagram-suite` to be completed (provides the 4 essential diagrams)

### Downstream
- None: This is a leaf change (improves existing diagrams, doesn't affect other components)

## Timeline Estimate

- **Day 1** (4 hours): 
  - Create helper methods for graph_attr, node_attr, edge_attr
  - Apply global improvements to all 4 diagrams
  - Test layout with larger font sizes
- **Day 2** (4 hours):
  - Replace Blank nodes with proper icons in CRD and Logging diagrams
  - Correct conceptual errors and add missing context
  - Test and adjust
- **Day 3** (4 hours):
  - Replace Blank nodes in VM Provisioning diagram
  - Add feedback flows and update title
  - Final testing and validation
- **Day 4** (2 hours):
  - Create research documentation
  - Update metadata
  - Final review and polish

**Total**: ~2-3 days (14 hours)

## Notes

- GraphViz edge label positioning is fundamentally limited (no native "above line" option)
- Using `labelfloat=true` allows labels to move for clarity, which is best available solution
- WebRTC verification research confirms CRD technical accuracy
- Priority is publication-ready quality for main paper figures
- Supplementary diagrams will be addressed in separate proposal if needed
