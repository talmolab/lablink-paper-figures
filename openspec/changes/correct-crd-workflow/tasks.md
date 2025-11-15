# Tasks: Correct CRD Connection Workflow Diagram

## Phase 1: Update Component Definitions ⏱️ 1 hour

- [ ] 1.1 Read current build_crd_connection_diagram() method
  - [ ] 1.1.1 Locate method in src/diagram_gen/generator.py
  - [ ] 1.1.2 Identify current components (6 nodes)
  - [ ] 1.1.3 Identify current edges (6 edges)
  - [ ] 1.1.4 Document current structure for comparison
- [ ] 1.2 Add deployment-based cluster structure
  - [ ] 1.2.1 Create "LabLink Infrastructure (Allocator EC2)" cluster
  - [ ] 1.2.2 Create "Client VM (Separate EC2)" cluster
  - [ ] 1.2.3 Create "External Services (Google)" cluster
  - [ ] 1.2.4 Keep User node outside clusters
- [ ] 1.3 Add Google CRD components
  - [ ] 1.3.1 Add google_crd_oauth = Saas("Google CRD\nOAuth\n(remotedesktop.google.com/headless)")
  - [ ] 1.3.2 Add google_crd_access = Saas("Google CRD\nAccess\n(remotedesktop.google.com/access)")
  - [ ] 1.3.3 Place both in "External Services" cluster
- [ ] 1.4 Add Flask Web UI component
  - [ ] 1.4.1 Add flask_ui = Flask("Flask Web UI\n(index.html)")
  - [ ] 1.4.2 Place in "LabLink Infrastructure" cluster
  - [ ] 1.4.3 Add comment noting Flask UI runs on same EC2 as Allocator
- [ ] 1.5 Update existing components
  - [ ] 1.5.1 Update subscribe_service label to "subscribe.py\n[WAITING since boot]"
  - [ ] 1.5.2 Update allocator to show both /vm_startup and /api/request_vm endpoints
  - [ ] 1.5.3 Keep connect_crd.py component
  - [ ] 1.5.4 Add alignment edge between subscribe.py and connect_crd.py (invisible)
- [ ] 1.6 Add internal allocator components
  - [ ] 1.6.1 Add trigger = RDS("Database\nTRIGGER")
  - [ ] 1.6.2 Add pg_notify = Postgresql("pg_notify()")
  - [ ] 1.6.3 Place both in "LabLink Infrastructure" cluster
  - [ ] 1.6.4 Add annotation "Internal to Allocator" on these components

## Phase 2: Restructure Edges for Blocking Pattern ⏱️ 1.5 hours

- [ ] 2.1 Remove old async notification edge
  - [ ] 2.1.1 Delete pg_notify >> subscribe_service edge
  - [ ] 2.1.2 Verify no other direct database → client VM edges
- [ ] 2.2 Add blocking HTTP edges (subscribe.py ↔ allocator)
  - [ ] 2.2.1 Add subscribe_service >> Edge(label="0. POST /vm_startup\n[BLOCKS up to 7 days]", style="dashed", color="blue", minlen="3") >> allocator
  - [ ] 2.2.2 Add allocator >> Edge(label="7. Response with CRD data\n[UNBLOCKS]", style="dashed", color="blue", minlen="3") >> subscribe_service
- [ ] 2.3 Add user → Google CRD OAuth flow
  - [ ] 2.3.1 Add user >> Edge(label="1. Navigate to website") >> google_crd_oauth
  - [ ] 2.3.2 Add google_crd_oauth >> Edge(label="Returns OAuth code\n(CRD command)") >> user
- [ ] 2.4 Add user → Flask UI → allocator flow
  - [ ] 2.4.1 Add user >> Edge(label="2. Navigate to\nLabLink web interface") >> flask_ui
  - [ ] 2.4.2 Add flask_ui >> Edge(label="Shows form:\nemail + CRD code") >> user
  - [ ] 2.4.3 Add user >> Edge(label="3. Submit request") >> flask_ui
  - [ ] 2.4.4 Add flask_ui >> Edge(label="POST /api/request_vm") >> allocator
- [ ] 2.5 Add allocator → database → trigger → pg_notify chain
  - [ ] 2.5.1 Add allocator >> Edge(label="4. UPDATE vm_table\nSET crdcommand=...", fontsize=edge_fontsize) >> database
  - [ ] 2.5.2 Add database >> Edge(label="Trigger fires\nON UPDATE OF CrdCommand") >> trigger
  - [ ] 2.5.3 Add trigger >> Edge(label="5. pg_notify('vm_updates',\nJSON payload)") >> pg_notify
  - [ ] 2.5.4 Add pg_notify >> Edge(label="6. Unblocks\nlisten_for_notifications()", style="dashed", color="orange") >> allocator
- [ ] 2.6 Add subscribe.py → connect_crd.py flow
  - [ ] 2.6.1 Add subscribe_service >> Edge(label="8. Execute\nCRD command") >> crd_connector
- [ ] 2.7 Add connect_crd.py → Google CRD OAuth flow
  - [ ] 2.7.2 Add crd_connector >> Edge(label="Authenticates with\nOAuth code", color="green") >> google_crd_oauth
- [ ] 2.8 Add final user access flow
  - [ ] 2.8.1 Add user >> Edge(label="9. Access configured VM\n(enter PIN)", color="purple") >> google_crd_access

## Phase 3: Test Component and Edge Rendering ⏱️ 30 min

- [ ] 3.1 Generate diagram with paper preset
  - [ ] 3.1.1 Run: python scripts/plotting/generate_architecture_diagram.py --diagram-type crd-connection --fontsize-preset paper
  - [ ] 3.1.2 Verify all 9 components render
  - [ ] 3.1.3 Verify all 12+ edges render
  - [ ] 3.1.4 Check for GraphViz errors
- [ ] 3.2 Visual inspection of layout
  - [ ] 3.2.1 Check cluster grouping (3 clusters visible)
  - [ ] 3.2.2 Check edge crossings (minimize if possible)
  - [ ] 3.2.3 Check label overlap (none should overlap graphics)
  - [ ] 3.2.4 Check sequence numbers (0-9 visible and logical)
- [ ] 3.3 Generate with poster preset
  - [ ] 3.3.1 Run with --fontsize-preset poster
  - [ ] 3.3.2 Verify no text overlap with larger fonts
  - [ ] 3.3.3 Check spacing is adequate

## Phase 4: Refine Labels and Annotations ⏱️ 45 min

- [ ] 4.1 Update edge labels for accuracy
  - [ ] 4.1.1 Verify "POST /vm_startup [BLOCKS up to 7 days]" matches code (subscribe.py:179)
  - [ ] 4.1.2 Verify "UPDATE vm_table SET crdcommand=..." matches code (database.py:141-148)
  - [ ] 4.1.3 Verify "pg_notify('vm_updates', JSON)" matches code (generate_init_sql.py:103-109)
  - [ ] 4.1.4 Verify "Unblocks listen_for_notifications()" matches code (database.py:237-273)
  - [ ] 4.1.5 Verify "POST /api/request_vm" matches code (main.py:64)
- [ ] 4.2 Add component annotations
  - [ ] 4.2.1 Add note on subscribe.py: "[WAITING since boot]"
  - [ ] 4.2.2 Add note on Flask UI: "(same EC2 as Allocator)"
  - [ ] 4.2.3 Add note on pg_notify: "(internal notification)"
- [ ] 4.3 Add helpful diagram annotations (optional)
  - [ ] 4.3.1 Consider adding timeline note: "Step 0 happens BEFORE step 1"
  - [ ] 4.3.2 Consider adding note: "Blocking wait: up to 7 days"
  - [ ] 4.3.3 Consider color-coding phases (blue=blocking, green=user, orange=config, purple=access)

## Phase 5: Layout Tuning and Optimization ⏱️ 45 min

- [ ] 5.1 Adjust edge lengths to prevent label overlap
  - [ ] 5.1.1 Set minlen="3" on long blocking HTTP edges
  - [ ] 5.1.2 Set minlen="2" on database → trigger → pg_notify chain
  - [ ] 5.1.3 Test rendering, adjust as needed
- [ ] 5.2 Align Python scripts horizontally
  - [ ] 5.2.1 Add invisible edge: subscribe_service >> Edge(style="invis") >> crd_connector
  - [ ] 5.2.2 Verify horizontal alignment in rendered diagram
- [ ] 5.3 Optimize cluster positioning
  - [ ] 5.3.1 Check if clusters overlap or crowd diagram
  - [ ] 5.3.2 Adjust graph_attr spacing if needed (nodesep, ranksep)
  - [ ] 5.3.3 Consider rank constraints if layout suboptimal
- [ ] 5.4 Test with both paper and poster presets
  - [ ] 5.4.1 Generate both versions
  - [ ] 5.4.2 Check spacing works for both font sizes
  - [ ] 5.4.3 Adjust if poster preset shows overlap

## Phase 6: Code Reference Validation ⏱️ 30 min

- [ ] 6.1 Trace edge 0: POST /vm_startup [BLOCKS]
  - [ ] 6.1.1 Check subscribe.py:176-180 for HTTP POST with timeout=(30, 604800)
  - [ ] 6.1.2 Verify label accuracy
- [ ] 6.2 Trace edge 1: Get OAuth code
  - [ ] 6.2.1 Check README or docs for Google CRD instructions
  - [ ] 6.2.2 Verify URL: remotedesktop.google.com/headless
- [ ] 6.3 Trace edge 3: Submit request
  - [ ] 6.3.1 Check templates/index.html:40-50 for form fields
  - [ ] 6.3.2 Verify POST /api/request_vm endpoint (main.py:64)
- [ ] 6.4 Trace edge 4: UPDATE vm_table
  - [ ] 6.4.1 Check database.py:141-148 for assign_vm SQL
  - [ ] 6.4.2 Verify UPDATE statement matches label
- [ ] 6.5 Trace edge 5: pg_notify
  - [ ] 6.5.1 Check generate_init_sql.py:100-113 for trigger function
  - [ ] 6.5.2 Verify pg_notify call and JSON payload
- [ ] 6.6 Trace edge 6: Unblocks listen_for_notifications
  - [ ] 6.6.1 Check database.py:237-273 for LISTEN loop
  - [ ] 6.6.2 Verify notification unblocks and returns data
  - [ ] 6.6.3 Check main.py:218-221 for /vm_startup endpoint blocking call
- [ ] 6.7 Trace edge 8: Execute CRD command
  - [ ] 6.7.1 Check subscribe.py:189 for connect_to_crd() call
  - [ ] 6.7.2 Check connect_crd.py:96-118 for subprocess execution

## Phase 7: Peer Review Testing ⏱️ 1 hour

- [ ] 7.1 Prepare peer review materials
  - [ ] 7.1.1 Generate final diagram (paper preset)
  - [ ] 7.1.2 Prepare 3 test questions (see design.md peer review section)
  - [ ] 7.1.3 Find reviewer unfamiliar with LabLink internals
- [ ] 7.2 Conduct peer review
  - [ ] 7.2.1 Show diagram to reviewer (no explanation)
  - [ ] 7.2.2 Ask: "Where does the user get the CRD code?"
    - Expected answer: "Google Chrome Remote Desktop website"
  - [ ] 7.2.3 Ask: "How does the client VM know when it's been assigned?"
    - Expected answer: "It's been waiting on a blocking HTTP request"
  - [ ] 7.2.4 Ask: "What role does the database trigger play?"
    - Expected answer: "Sends notification that unblocks the allocator's waiting connection"
- [ ] 7.3 Collect feedback and adjust
  - [ ] 7.3.1 Document any misunderstandings
  - [ ] 7.3.2 Identify confusing labels or edges
  - [ ] 7.3.3 Make adjustments based on feedback
  - [ ] 7.3.4 Re-test with reviewer if major changes made

## Phase 8: Side-by-Side Comparison ⏱️ 30 min

- [ ] 8.1 Generate both old and new versions
  - [ ] 8.1.1 Git stash current changes
  - [ ] 8.1.2 Generate old version diagram (save as lablink-crd-old.png)
  - [ ] 8.1.3 Git stash pop
  - [ ] 8.1.4 Generate new version diagram (save as lablink-crd-new.png)
- [ ] 8.2 Visual comparison checklist
  - [ ] 8.2.1 Old: Shows 6 components → New: Shows 9 components ✅
  - [ ] 8.2.2 Old: Shows async push → New: Shows blocking HTTP ✅
  - [ ] 8.2.3 Old: Missing Google CRD → New: Shows both OAuth and Access ✅
  - [ ] 8.2.4 Old: Missing Flask UI → New: Shows web interface ✅
  - [ ] 8.2.5 Old: 6 steps → New: 10 steps (0-9) ✅
  - [ ] 8.2.6 Old: User first → New: VM waiting first ✅
- [ ] 8.3 Document improvements
  - [ ] 8.3.1 Create comparison doc showing before/after
  - [ ] 8.3.2 List all corrected misrepresentations
  - [ ] 8.3.3 Highlight accuracy improvements (40% → 95%)

## Phase 9: Documentation Updates ⏱️ 45 min

- [ ] 9.1 Update README.md
  - [ ] 9.1.1 Update CRD connection diagram description
  - [ ] 9.1.2 Add note about blocking HTTP pattern
  - [ ] 9.1.3 Add note about Google CRD dependencies
  - [ ] 9.1.4 Update diagram type description in examples
- [ ] 9.2 Update diagram metadata
  - [ ] 9.2.1 Update diagram_metadata.txt with new component count
  - [ ] 9.2.2 Add notes about architectural accuracy improvements
  - [ ] 9.2.3 Reference analysis documents (crd-workflow-research.md)
- [ ] 9.3 Check for related documentation
  - [ ] 9.3.1 Search for "CRD connection" in docs
  - [ ] 9.3.2 Search for "async notification" or "push notification"
  - [ ] 9.3.3 Update any references that contradict corrected diagram

## Phase 10: Final Validation and Commit ⏱️ 30 min

- [ ] 10.1 Run comprehensive tests
  - [ ] 10.1.1 Generate all essential diagrams (verify no regression)
  - [ ] 10.1.2 Generate CRD diagram with paper preset
  - [ ] 10.1.3 Generate CRD diagram with poster preset
  - [ ] 10.1.4 Verify file sizes reasonable (~400-800KB for PNG)
- [ ] 10.2 Final quality checklist
  - [ ] 10.2.1 All 9 components render correctly ✅
  - [ ] 10.2.2 All 12+ edges render correctly ✅
  - [ ] 10.2.3 No label overlap with graphics ✅
  - [ ] 10.2.4 Blocking pattern clearly shown ✅
  - [ ] 10.2.5 Google CRD integration shown ✅
  - [ ] 10.2.6 Flask web UI shown ✅
  - [ ] 10.2.7 Correct sequence (0-9) ✅
  - [ ] 10.2.8 Peer review passed (> 75% understanding) ✅
- [ ] 10.3 Git commit
  - [ ] 10.3.1 Stage modified generator.py
  - [ ] 10.3.2 Stage OpenSpec proposal files (proposal.md, design.md, tasks.md, spec.md)
  - [ ] 10.3.3 Stage updated README.md
  - [ ] 10.3.4 Stage analysis documents if updated
  - [ ] 10.3.5 Commit with message: "Correct CRD connection diagram to show blocking HTTP pattern"
  - [ ] 10.3.6 Include reference to OpenSpec proposal in commit message

## Timeline Summary

| Phase | Duration | Dependency |
|-------|----------|------------|
| Phase 1: Component Definitions | 1 hour | None |
| Phase 2: Restructure Edges | 1.5 hours | Phase 1 complete |
| Phase 3: Test Rendering | 30 min | Phase 2 complete |
| Phase 4: Refine Labels | 45 min | Phase 3 complete |
| Phase 5: Layout Tuning | 45 min | Phase 4 complete |
| Phase 6: Code Validation | 30 min | Phase 5 complete |
| Phase 7: Peer Review | 1 hour | Phase 6 complete |
| Phase 8: Comparison | 30 min | Phase 7 complete |
| Phase 9: Documentation | 45 min | Phase 8 complete |
| Phase 10: Final Validation | 30 min | Phase 9 complete |

**Total Sequential Time**: 7 hours 45 minutes
**Critical Path**: Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10

## Notes

- **Most Critical Phase**: Phase 2 (restructuring edges) - this is where blocking pattern is implemented
- **Quality Gate**: Phase 7 (peer review) - must pass before proceeding to commit
- **Risk Mitigation**: Phase 8 (comparison) - ensures changes are improvements, not regressions
- **User Requirement**: User explicitly requested this correction: "ok I still think we need to work on this figure"

## Blockers and Risks

- **Diagram Complexity**: 9 components and 12+ edges might be too dense
  - **Mitigation**: Use clustering to group components logically
  - **Backup Plan**: Consider splitting into 2 diagrams if single diagram too complex after Phase 3

- **Layout Issues**: GraphViz might struggle with optimal layout for this many edges
  - **Mitigation**: Use minlen, invisible edges, and rank constraints
  - **Backup Plan**: Manual adjustment of specific edge routing if needed

- **Peer Review Failure**: If reviewer can't understand diagram (Phase 7)
  - **Mitigation**: Iterate on labels and annotations based on feedback
  - **Escalation**: If 2+ reviewers fail, reconsider diagram structure

- **Performance**: Rendering time might increase significantly
  - **Mitigation**: Measure generation time, ensure < 5 seconds
  - **Acceptable**: Up to 10 seconds is still reasonable for complex diagram
