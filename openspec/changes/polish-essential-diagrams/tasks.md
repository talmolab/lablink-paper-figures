# Tasks: Polish Essential Architecture Diagrams

## Phase 1: Add Dynamic Spacing to Font Presets ⏱️ 30 min

- [ ] 1.1 Update `_create_graph_attr()` method in generator.py
  - [ ] 1.1.1 Add spacing dictionary with paper/poster/presentation values
  - [ ] 1.1.2 Update `nodesep` to use `spacing["nodesep"]`
  - [ ] 1.1.3 Update `ranksep` to use `spacing["ranksep"]`
- [ ] 1.2 Test spacing with all presets
  - [ ] 1.2.1 Generate test diagram with paper preset - measure spacing
  - [ ] 1.2.2 Generate test diagram with poster preset - verify no overlap
  - [ ] 1.2.3 Generate test diagram with presentation preset - verify intermediate spacing

## Phase 2: Refactor build_main_diagram() to Use Helpers ⏱️ 1 hour

- [ ] 2.1 Add `fontsize_preset` parameter to method signature
  - [ ] 2.1.1 Add parameter with default value "paper"
  - [ ] 2.1.2 Update docstring to document new parameter
- [ ] 2.2 Replace inline graph_attr with helper call
  - [ ] 2.2.1 Delete inline `graph_attr = {...}` dictionary (lines ~230-239)
  - [ ] 2.2.2 Add `graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)`
- [ ] 2.3 Replace inline node_attr with helper call
  - [ ] 2.3.1 Delete inline `node_attr = {...}` dictionary (lines ~241-244)
  - [ ] 2.3.2 Add `node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)`
- [ ] 2.4 Replace inline edge_attr with helper call
  - [ ] 2.4.1 Delete inline `edge_attr = {...}` dictionary (lines ~246-249)
  - [ ] 2.4.2 Add `edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)`
- [ ] 2.5 Add edge_fontsize variable for inline labels
  - [ ] 2.5.1 Add `edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])`
- [ ] 2.6 Update all inline edge label fontsize references
  - [ ] 2.6.1 Find all `fontsize="12"` in edge labels (lines ~265-316)
  - [ ] 2.6.2 Replace with `fontsize=edge_fontsize`
- [ ] 2.7 Validate refactoring
  - [ ] 2.7.1 Generate main diagram with paper preset
  - [ ] 2.7.2 Compare with previous version - verify only title position and font size changed
  - [ ] 2.7.3 Generate main diagram with poster preset - verify no overlap

## Phase 3: Add Terraform Icon ⏱️ 1 hour

- [ ] 3.1 Download official Terraform logo
  - [ ] 3.1.1 Visit https://www.hashicorp.com/brand
  - [ ] 3.1.2 Download Terraform logo in PNG format
  - [ ] 3.1.3 Create `assets/icons/` directory if not exists
  - [ ] 3.1.4 Save logo as `assets/icons/terraform.png`
- [ ] 3.2 Verify and resize icon if needed
  - [ ] 3.2.1 Check icon dimensions (should be ~256x256px)
  - [ ] 3.2.2 If larger than 512x512, resize to 256x256 using PIL or ImageMagick
  - [ ] 3.2.3 Verify PNG format and transparency
- [ ] 3.3 Update build_vm_provisioning_diagram() method
  - [ ] 3.3.1 Add `from diagrams.custom import Custom` to imports
  - [ ] 3.3.2 Add `from pathlib import Path` if not already imported
  - [ ] 3.3.3 Replace Blank terraform node (line ~517) with Custom node
  - [ ] 3.3.4 Add icon path calculation relative to generator.py
  - [ ] 3.3.5 Add existence check with fallback to Blank
- [ ] 3.4 Test Terraform icon rendering
  - [ ] 3.4.1 Generate VM provisioning diagram - verify Terraform icon appears
  - [ ] 3.4.2 Temporarily rename icon file - verify fallback to Blank works
  - [ ] 3.4.3 Restore icon file - verify icon reappears

## Phase 4: Update CRD Edge Label ⏱️ 15 min

- [ ] 4.1 Update build_crd_connection_diagram() method
  - [ ] 4.1.1 Locate edge label "Authenticates & Connects to" (line ~631)
  - [ ] 4.1.2 Change to "Authenticates & Connects" (remove "to")
- [ ] 4.2 Validate label update
  - [ ] 4.2.1 Generate CRD connection diagram
  - [ ] 4.2.2 Verify label reads "Authenticates & Connects"
  - [ ] 4.2.3 Verify label positioning still correct

## Phase 5: Update Wrapper Function and Script ⏱️ 15 min

- [ ] 5.1 Update generate_main_diagram() wrapper function
  - [ ] 5.1.1 Add `fontsize_preset: str = "paper"` parameter (line ~1227)
  - [ ] 5.1.2 Pass `fontsize_preset=fontsize_preset` to builder.build_main_diagram() call
  - [ ] 5.1.3 Update function docstring if present
- [ ] 5.2 Update generate_architecture_diagram.py script
  - [ ] 5.2.1 Locate main diagram generation call (line ~206)
  - [ ] 5.2.2 Add `fontsize_preset=args.fontsize_preset` to generate_main_diagram() call
- [ ] 5.3 Validate wrapper and script changes
  - [ ] 5.3.1 Run script with --diagram-type main --fontsize-preset paper
  - [ ] 5.3.2 Run script with --diagram-type main --fontsize-preset poster
  - [ ] 5.3.3 Verify both generate successfully

## Phase 6: Comprehensive Testing ⏱️ 1 hour

- [ ] 6.1 Generate all diagrams with paper preset
  - [ ] 6.1.1 Run: `python scripts/plotting/generate_architecture_diagram.py --diagram-type all-essential --fontsize-preset paper`
  - [ ] 6.1.2 Verify all 4 diagrams generate without errors
  - [ ] 6.1.3 Check file sizes (should be ~400-600KB for 300 DPI PNG)
- [ ] 6.2 Generate all diagrams with poster preset
  - [ ] 6.2.1 Run: `python scripts/plotting/generate_architecture_diagram.py --diagram-type all-essential --fontsize-preset poster`
  - [ ] 6.2.2 Verify all 4 diagrams generate without errors
  - [ ] 6.2.3 Check for text overlap - none should exist
- [ ] 6.3 Visual inspection checklist
  - [ ] 6.3.1 Main diagram: Title at top ✅
  - [ ] 6.3.2 Main diagram: Fonts 14pt (paper) / 20pt (poster) ✅
  - [ ] 6.3.3 VM provisioning: Terraform icon visible ✅
  - [ ] 6.3.4 CRD connection: Label "Authenticates & Connects" ✅
  - [ ] 6.3.5 Poster preset: No text overlap ✅
  - [ ] 6.3.6 All diagrams: 300 DPI quality ✅
- [ ] 6.4 Regression testing
  - [ ] 6.4.1 Generate legacy diagrams (detailed, network-flow)
  - [ ] 6.4.2 Verify no unexpected changes
  - [ ] 6.4.3 Verify all still render correctly

## Phase 7: Documentation and Cleanup ⏱️ 30 min

- [ ] 7.1 Update README.md
  - [ ] 7.1.1 Add note about Terraform icon asset requirement
  - [ ] 7.1.2 Update examples to show poster preset usage
  - [ ] 7.1.3 Document spacing formula for future reference
- [ ] 7.2 Git commit changes
  - [ ] 7.2.1 Stage modified generator.py
  - [ ] 7.2.2 Stage modified generate_architecture_diagram.py
  - [ ] 7.2.3 Stage new terraform.png asset
  - [ ] 7.2.4 Commit with descriptive message
- [ ] 7.3 Create before/after comparison
  - [ ] 7.3.1 Generate diagrams with old code (git stash)
  - [ ] 7.3.2 Generate diagrams with new code (git stash pop)
  - [ ] 7.3.3 Document improvements in commit message

## Phase 8: Validation and Sign-off ⏱️ 30 min

- [ ] 8.1 Run OpenSpec validation
  - [ ] 8.1.1 Run: `openspec validate polish-essential-diagrams --strict`
  - [ ] 8.1.2 Fix any validation errors
  - [ ] 8.1.3 Re-run until passing
- [ ] 8.2 Final quality check
  - [ ] 8.2.1 Print diagrams at actual paper size (6-8 inches wide)
  - [ ] 8.2.2 Verify text readable at arm's length
  - [ ] 8.2.3 Verify Terraform icon clear and recognizable
- [ ] 8.3 Archive proposal
  - [ ] 8.3.1 Create COMPLETED.md in proposal directory
  - [ ] 8.3.2 Document completion date and final metrics
  - [ ] 8.3.3 List any deviations from original plan

## Timeline Summary

| Phase | Duration | Dependency |
|-------|----------|------------|
| Phase 1: Dynamic Spacing | 30 min | None |
| Phase 2: Refactor Main Diagram | 1 hour | Phase 1 complete |
| Phase 3: Terraform Icon | 1 hour | None (can parallel Phase 1-2) |
| Phase 4: CRD Label | 15 min | None (can parallel all) |
| Phase 5: Wrapper/Script | 15 min | Phase 2 complete |
| Phase 6: Testing | 1 hour | Phases 1-5 complete |
| Phase 7: Documentation | 30 min | Phase 6 complete |
| Phase 8: Validation | 30 min | Phase 7 complete |

**Total Sequential Time**: 4.5 hours
**Total with Parallelization**: 3.5 hours

## Critical Path

```
Phase 1 (30m) → Phase 2 (1h) → Phase 5 (15m) → Phase 6 (1h) → Phase 7 (30m) → Phase 8 (30m)
       ↘
        Phase 3 (1h) can run in parallel
        Phase 4 (15m) can run in parallel
```

## Notes

- Phases 1-2 must be sequential (spacing before main diagram refactor)
- Phase 3 (Terraform icon) can be done in parallel with Phases 1-2
- Phase 4 (CRD label) can be done any time
- Phase 5 depends on Phase 2 (wrapper needs refactored method)
- Phases 6-8 must be sequential at the end

## Blockers and Risks

- **Terraform icon download**: Requires internet access and HashiCorp site availability
  - **Mitigation**: Fallback to Blank if icon unavailable
- **Spacing calibration**: May need iteration if overlap still occurs
  - **Mitigation**: Parameterized values easy to adjust
- **Main diagram complexity**: Refactoring 40+ lines carries slight risk
  - **Mitigation**: Helper methods already proven in 3 diagrams
