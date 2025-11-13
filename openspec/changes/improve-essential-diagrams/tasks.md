# Implementation Tasks: Improve Essential Diagrams

## 1. Create Helper Methods for Consistent Styling

- [ ] 1.1 Create `_create_graph_attr()` helper method in `LabLinkDiagramBuilder` class
  - [ ] 1.1.1 Add parameters: `dpi=300`, `title_on_top=True`, `cluster_fontsize=32`
  - [ ] 1.1.2 Set `labelloc="t"` when `title_on_top=True` (KEY CHANGE for title placement)
  - [ ] 1.1.3 Maintain existing styling: fontsize, fontname, bgcolor, pad, nodesep, ranksep, splines
  - [ ] 1.1.4 Add docstring documenting all parameters

- [ ] 1.2 Create `_create_node_attr()` helper method
  - [ ] 1.2.1 Add parameter: `fontsize=14` (increased from 11)
  - [ ] 1.2.2 Set fontname="Helvetica" for consistency
  - [ ] 1.2.3 Add docstring documenting parameters

- [ ] 1.3 Create `_create_edge_attr()` helper method
  - [ ] 1.3.1 Add parameter: `fontsize=14` (increased from 12)
  - [ ] 1.3.2 Add `labelfloat="true"` (NEW for better label positioning)
  - [ ] 1.3.3 Maintain existing: labeldistance, labelangle, fontname
  - [ ] 1.3.4 Add docstring documenting parameters and GraphViz limitation

## 2. Apply Global Improvements to All 4 Diagrams

- [ ] 2.1 Update `build_main_diagram()` (lablink-architecture.png)
  - [ ] 2.1.1 Replace inline graph_attr with `self._create_graph_attr(dpi=dpi)`
  - [ ] 2.1.2 Replace inline node_attr with `self._create_node_attr(fontsize=14)`
  - [ ] 2.1.3 Replace inline edge_attr with `self._create_edge_attr(fontsize=14)`
  - [ ] 2.1.4 Test: Generate diagram and verify title at top
  - [ ] 2.1.5 Test: Verify text size increased and readable
  - [ ] 2.1.6 Test: Check for layout overflow or text overlap issues

- [ ] 2.2 Update `build_crd_connection_diagram()` 
  - [ ] 2.2.1 Replace inline graph_attr with helper method
  - [ ] 2.2.2 Replace inline node_attr with helper method
  - [ ] 2.2.3 Replace inline edge_attr with helper method
  - [ ] 2.2.4 Test: Generate and verify styling improvements

- [ ] 2.3 Update `build_logging_pipeline_diagram()`
  - [ ] 2.3.1 Replace inline graph_attr with helper method
  - [ ] 2.3.2 Replace inline node_attr with helper method
  - [ ] 2.3.3 Replace inline edge_attr with helper method
  - [ ] 2.3.4 Test: Generate and verify styling improvements

- [ ] 2.4 Update `build_vm_provisioning_diagram()`
  - [ ] 2.4.1 Replace inline graph_attr with helper method
  - [ ] 2.4.2 Replace inline node_attr with helper method
  - [ ] 2.4.3 Replace inline edge_attr with helper method
  - [ ] 2.4.4 Test: Generate and verify styling improvements

## 3. Improve CRD Connection Diagram (lablink-crd-connection.png)

- [ ] 3.1 Replace Blank nodes with proper icons
  - [ ] 3.1.1 Replace `Blank("TRIGGER\n(on CrdCommand)")` with RDS node labeled "Database TRIGGER"
  - [ ] 3.1.2 Replace `Blank("pg_notify()")` with `onprem.database.Postgresql` labeled "pg_notify()"
  - [ ] 3.1.3 Replace `Blank("subscribe.py\n(LISTEN)")` with `programming.language.Python` labeled "subscribe.py (LISTEN)"
  - [ ] 3.1.4 Replace `Blank("connect_crd.py")` with `programming.language.Python` labeled "connect_crd.py"
  - [ ] 3.1.5 Test: Generate diagram and verify icons display correctly

- [ ] 3.2 Correct conceptual errors in edge labels
  - [ ] 3.2.1 Change "5. Launches" → "5. Authenticates & Connects to"
  - [ ] 3.2.2 Update "6. WebRTC Connection" → "6. WebRTC P2P Connection"
  - [ ] 3.2.3 Test: Generate and verify label text updated

- [ ] 3.3 Add missing context annotations
  - [ ] 3.3.1 Add annotation to Client VM: "Client VM (Admin-provisioned)"
  - [ ] 3.3.2 Add note in diagram or documentation explaining CRD authentication
  - [ ] 3.3.3 Test: Generate and verify annotations visible

- [ ] 3.4 Validate technical accuracy
  - [ ] 3.4.1 Verify WebRTC claim is correct (research: ✅ confirmed)
  - [ ] 3.4.2 Cross-reference with LabLink codebase for accuracy
  - [ ] 3.4.3 Document any remaining uncertainties

## 4. Improve Logging Pipeline Diagram (lablink-logging-pipeline.png)

- [ ] 4.1 Replace Blank nodes with proper icons
  - [ ] 4.1.1 Replace `Blank("CloudWatch\nAgent")` with appropriate monitoring icon (try `aws.management.Cloudwatch`)
  - [ ] 4.1.2 Replace `Blank("Subscription\nFilter")` with `CloudwatchEventEventBased` from `diagrams.aws.management`
  - [ ] 4.1.3 Test: Generate diagram and verify icons display correctly

- [ ] 4.2 Clarify subscription filter mechanism
  - [ ] 4.2.1 Update edge label: "3. Triggers" → "3. Triggers (on pattern match)"
  - [ ] 4.2.2 Add annotation showing pattern: "(pattern: all events)" or similar
  - [ ] 4.2.3 Test: Generate and verify clarification visible

- [ ] 4.3 Add missing admin viewing flow
  - [ ] 4.3.1 Add `User("Admin")` node
  - [ ] 4.3.2 Add edge: Database → Admin with label "7. View logs (web UI)"
  - [ ] 4.3.3 Position admin node appropriately in layout
  - [ ] 4.3.4 Test: Generate and verify complete logging story (collect → store → view)

## 5. Improve VM Provisioning Diagram (lablink-vm-provisioning.png)

- [ ] 5.1 Replace Blank nodes with proper icons
  - [ ] 5.1.1 Investigate if diagrams library has Terraform icon
  - [ ] 5.1.2 If no library icon: Download Terraform logo, resize to ~256x256px, save to `assets/icons/terraform.png`
  - [ ] 5.1.3 Replace `Blank("Terraform\nSubprocess")` with Custom node using terraform.png OR library icon
  - [ ] 5.1.4 Test: Generate and verify Terraform icon displays correctly

- [ ] 5.2 Improve phase representation
  - [ ] 5.2.1 Consider creating sub-cluster "3-Phase Startup Sequence" to group phases
  - [ ] 5.2.2 For Phase 2: Replace Blank with `onprem.container.Docker` icon
  - [ ] 5.2.3 For Phase 1 and 3: Evaluate if keeping as Blank is acceptable or use generic icons
  - [ ] 5.2.4 Test: Generate and verify phase visualization is clear

- [ ] 5.3 Add missing VM feedback flow
  - [ ] 5.3.1 Add edge: Client VM → Allocator with label "4. Status updates (POST /api/vm-metrics)"
  - [ ] 5.3.2 Add edge: Allocator → Database with label "5. Store provisioning metrics"
  - [ ] 5.3.3 Adjust edge numbering to accommodate new flows
  - [ ] 5.3.4 Test: Generate and verify two-way communication shown

- [ ] 5.4 Correct title and add timing context
  - [ ] 5.4.1 Change title: "LabLink VM Provisioning & Lifecycle" → "LabLink VM Provisioning"
  - [ ] 5.4.2 Add annotation: "Total provisioning time: ~105 seconds" (sum of phase times)
  - [ ] 5.4.3 Test: Generate and verify title and annotation updated

## 6. Testing and Validation

- [ ] 6.1 Visual inspection of all 4 diagrams
  - [ ] 6.1.1 Verify titles at top (not bottom)
  - [ ] 6.1.2 Verify text size increased and readable
  - [ ] 6.1.3 Verify edge labels positioned clearly (not overlapping edges excessively)
  - [ ] 6.1.4 Verify no layout overflow or text overlap issues
  - [ ] 6.1.5 Verify all icons replaced (or documented why Blank kept)

- [ ] 6.2 Technical accuracy validation
  - [ ] 6.2.1 Cross-reference CRD diagram with LabLink codebase (subscribe.py, connect_crd.py, TRIGGER)
  - [ ] 6.2.2 Cross-reference Logging diagram with CloudWatch setup code
  - [ ] 6.2.3 Cross-reference VM Provisioning diagram with Terraform and startup scripts
  - [ ] 6.2.4 Document any discovered inaccuracies

- [ ] 6.3 Print quality testing
  - [ ] 6.3.1 Verify all diagrams maintain 300 DPI resolution
  - [ ] 6.3.2 Print test pages at typical paper size (6-8 inches wide)
  - [ ] 6.3.3 Verify text readable in print at realistic viewing distance
  - [ ] 6.3.4 Adjust font sizes if needed based on print test

- [ ] 6.4 File size and format validation
  - [ ] 6.4.1 Verify PNG files generated correctly
  - [ ] 6.4.2 Check file sizes reasonable (100-300KB per diagram)
  - [ ] 6.4.3 Verify transparency/background correct (white background)

## 7. Documentation

- [ ] 7.1 Create research documentation
  - [ ] 7.1.1 Create `openspec/changes/improve-essential-diagrams/RESEARCH.md`
  - [ ] 7.1.2 Document WebRTC verification research (sources, findings)
  - [ ] 7.1.3 Document diagrams library icon investigation
  - [ ] 7.1.4 Document GraphViz edge label positioning limitations
  - [ ] 7.1.5 Document icon selection rationale for each replacement

- [ ] 7.2 Update diagram metadata
  - [ ] 7.2.1 Update `figures/main/diagram_metadata.txt` with improvement details
  - [ ] 7.2.2 Add generation timestamp
  - [ ] 7.2.3 List specific improvements applied
  - [ ] 7.2.4 Document any known limitations or trade-offs

- [ ] 7.3 Update code documentation
  - [ ] 7.3.1 Add docstrings to all new helper methods
  - [ ] 7.3.2 Add comments explaining GraphViz attribute choices
  - [ ] 7.3.3 Document known limitations (edge label positioning)
  - [ ] 7.3.4 Add code references to relevant LabLink codebase files

- [ ] 7.4 Update README (if needed)
  - [ ] 7.4.1 Add section on diagram improvements if appropriate
  - [ ] 7.4.2 Document how to regenerate diagrams with improvements
  - [ ] 7.4.3 Explain diagram quality criteria

## 8. Final Review and Polish

- [ ] 8.1 Side-by-side comparison
  - [ ] 8.1.1 Compare new diagrams with original versions
  - [ ] 8.1.2 Document visual improvements
  - [ ] 8.1.3 Confirm all issues from user feedback addressed

- [ ] 8.2 Code review
  - [ ] 8.2.1 Review helper method implementation for correctness
  - [ ] 8.2.2 Review icon replacements for semantic accuracy
  - [ ] 8.2.3 Review edge label changes for technical accuracy
  - [ ] 8.2.4 Check for code duplication or inconsistencies

- [ ] 8.3 Final validation
  - [ ] 8.3.1 Run all diagram generation tests
  - [ ] 8.3.2 Verify no regressions in existing functionality
  - [ ] 8.3.3 Confirm all success criteria met (see proposal.md)
  - [ ] 8.3.4 Get approval from paper authors if possible

- [ ] 8.4 Prepare for merge
  - [ ] 8.4.1 Commit all changes with descriptive messages
  - [ ] 8.4.2 Update OpenSpec proposal with final results
  - [ ] 8.4.3 Mark tasks as complete
  - [ ] 8.4.4 Ready for code review and merge

## Notes

- **Priority**: Tasks 1-5 are implementation, 6-8 are validation/documentation
- **Dependencies**: Task 1 must complete before Task 2; Tasks 3-5 can run in parallel after Task 2
- **Testing**: Test after each major change, don't wait until the end
- **Iteration**: If font sizes cause layout issues, iterate on sizes (try 13pt, 15pt, etc.)
- **Fallback**: If custom icons don't work, document and keep as Blank nodes
- **GraphViz limitations**: Accept "good enough" edge label positioning, don't over-engineer
