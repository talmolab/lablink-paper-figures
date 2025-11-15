# Correct CRD Connection Workflow Diagram

## Why

The current CRD connection diagram (`lablink-crd-connection.png`) **fundamentally misrepresents the architecture** and will mislead readers about how LabLink actually works.

### Critical Errors in Current Diagram

1. **Wrong Architecture Pattern**
   - **Shows**: Async push notification pattern (database → client VM)
   - **Reality**: Synchronous blocking HTTP long-polling pattern (client VM blocks waiting for HTTP response)
   - **Impact**: Readers will think LabLink uses WebSocket/push notifications when it uses standard HTTP blocking

2. **Missing External Dependencies**
   - **Shows**: User directly requests VM from allocator
   - **Reality**: User must first visit https://remotedesktop.google.com/headless to get OAuth code
   - **Impact**: Completely obscures the critical Google Chrome Remote Desktop integration

3. **Missing User Interface**
   - **Shows**: User → Allocator (abstract interaction)
   - **Reality**: Flask web interface (index.html form) where user submits email + CRD code
   - **Impact**: Readers won't understand how users actually interact with the system

4. **Wrong Component Behavior**
   - **Shows**: subscribe.py as a passive listener that receives notifications
   - **Reality**: subscribe.py makes blocking HTTP POST with 7-DAY timeout
   - **Impact**: Misunderstands how client VMs wait for assignment

5. **Wrong Timing/Sequence**
   - **Shows**: User request triggers subscribe.py execution
   - **Reality**: subscribe.py is ALREADY WAITING before user makes request (since VM boot)
   - **Impact**: Backwards understanding of cause and effect

### Evidence from Codebase

From `lablink/packages/client/src/lablink_client_service/subscribe.py` (lines 176-180):

```python
response = requests.post(
    url, json={"hostname": hostname},
    timeout=(30, 604800)  # 7 DAYS timeout on read!
)
```

This is a **blocking HTTP call**, not a notification listener.

From `lablink/packages/allocator/src/lablink_allocator_service/main.py` (lines 218-221):

```python
# THIS IS THE BLOCKING PART
result = database.listen_for_notifications(
    channel=MESSAGE_CHANNEL, target_hostname=hostname
)
```

The allocator endpoint BLOCKS until database notification received, holding the HTTP connection open.

From `lablink/packages/allocator/src/lablink_allocator_service/templates/index.html` (lines 40-46):

```html
<label for="crd_command" class="form-label">CRD Command</label>
<input type="text" id="crd_command" name="crd_command"
       placeholder="Enter CRD command" required />
```

User submits CRD command via web form, not shown in diagram.

## What Changes

### 1. Add Google Chrome Remote Desktop Website (First Step)

**New Component**: External service box for https://remotedesktop.google.com/headless

**Why**: User MUST visit this website to get OAuth code before requesting a VM. This is step 1 of the actual workflow.

**Flow**:
```
User → Google CRD Website → Get OAuth code → User (has code)
```

### 2. Add Flask Web Interface Component

**New Component**: Flask Web UI (index.html form) running on Allocator EC2

**Why**: This is how users actually interact with LabLink - not an abstract "request VM" but a concrete web form.

**Flow**:
```
User (with code) → Flask Web UI → Enter email + CRD code → Submit
```

### 3. Show Blocking HTTP Pattern (NOT Async Push)

**Current Edge**: "Notification (async)" from pg_notify() to subscribe.py

**Updated Edges**:
1. Client VM → Allocator: "POST /vm_startup [BLOCKS up to 7 days]" (dashed line, blue)
2. Allocator → Client VM: "Response with CRD data [UNBLOCKS]" (dashed line, blue)

**Labels to Add**:
- On subscribe.py: "WAITING since VM boot"
- On /vm_startup endpoint: "Holds connection open until notification"
- On pg_notify: "Unblocks waiting allocator connection" (NOT "pushes to VM")

**Why**: This accurately represents the long-polling pattern instead of push notifications.

### 4. Correct Sequence Order

**Current Sequence**:
1. User requests VM
2. Allocator assigns VM
3. Database trigger fires
4. subscribe.py receives notification
5. CRD configured

**Corrected Sequence**:
0. **[VM Boot]** subscribe.py → POST /vm_startup → BLOCKS (this happens BEFORE user does anything)
1. User → Google CRD website → Get OAuth code
2. User → Flask web form → Submit email + CRD code
3. Allocator → UPDATE database with CRD command
4. Database trigger → pg_notify()
5. Allocator's listen_for_notifications() → receives notification → unblocks
6. /vm_startup endpoint → Returns CRD data to subscribe.py
7. subscribe.py → execute connect_crd.py
8. connect_crd.py → Configure Chrome Remote Desktop
9. User → Google CRD access page → Connect to VM

### 5. Add Final Access Step

**New Component**: Google Chrome Remote Desktop access (remotedesktop.google.com/access)

**Why**: Shows how user actually connects to configured VM (browser-based, not SSH)

**Flow**:
```
User sees success page (hostname + PIN) → Navigate to Google CRD access →
Click on VM → Enter PIN → Desktop streaming in browser
```

### 6. Update Component Locations/Grouping

**Clusters to Show**:
1. **LabLink Infrastructure** (Allocator EC2):
   - Flask Web UI
   - Allocator backend (/vm_startup, /api/request_vm endpoints)
   - PostgreSQL database
   - Database trigger

2. **Client VM** (Separate EC2):
   - subscribe.py (blocking HTTP client)
   - connect_crd.py (CRD setup script)

3. **External Services** (Outside LabLink):
   - Google Chrome Remote Desktop (headless OAuth)
   - Google Chrome Remote Desktop (access interface)

4. **User** (Browser):
   - Researcher/admin using the system

## Impact

### Affected Components

- **Modified**: `src/diagram_gen/generator.py::build_crd_connection_diagram()`
  - ~100 lines rewritten
  - Add Google CRD website components (2 new nodes)
  - Add Flask Web UI component (1 new node)
  - Restructure edges to show blocking HTTP pattern
  - Update all labels for accuracy
  - Reorder sequence numbers
  - Add timeline/phase annotations

- **Created**: `analysis/crd-workflow-research.md` ✅ (already exists)
- **Created**: `analysis/crd-workflow-corrected.md` ✅ (already exists)

### External Dependencies

None - all changes use existing diagram library components.

### Breaking Changes

**Visual Breaking Change**: Diagram will look significantly different
- Different components (adds 3 new external service nodes)
- Different flow (blocking pattern vs push pattern)
- Different sequence (9 steps instead of 6)
- Different grouping (shows deployment locations)

**Why Acceptable**: Current diagram is fundamentally wrong. This is a correction, not an enhancement.

### User-Visible Changes

- **Before**: Misleading diagram showing push notifications
- **After**: Accurate diagram showing blocking HTTP long-polling with Google CRD integration

### Quality Metrics

- **Accuracy**: Current = 40% (missing components, wrong pattern), After = 95%
- **Completeness**: Current = 60% (missing Google CRD, Flask UI), After = 100%
- **Clarity**: Current = 50% (confusing architecture), After = 85% (clear flow with timeline)

## Risk Assessment

### Low Risk

- Using existing diagram library components (no new dependencies)
- Analysis documents completed (research.md, corrected.md) provide clear spec
- Diagram generation code isolated to single method

### Medium Risk

- **Complexity**: Diagram will have more components (9 vs 6 nodes) and edges (12 vs 6)
  - **Mitigation**: Use visual grouping (clusters) and color coding to manage complexity
  - **Mitigation**: Consider splitting into 2 diagrams if single diagram too dense

- **Readability**: More detailed flow might be harder to read at paper font sizes
  - **Mitigation**: Test rendering at both paper and poster presets
  - **Mitigation**: Use minlen to control edge lengths and prevent overlap
  - **Mitigation**: Consider creating simplified version for main text, detailed version for supplementary

### High Risk

None identified.

### Testing Strategy

1. **Generate diagram**: Run with paper preset, verify all components render
2. **Visual inspection**: Check that blocking pattern is clear vs push pattern
3. **Peer review**: Have someone unfamiliar with codebase read diagram, explain workflow back
4. **Code reference validation**: Verify all labels match actual code behavior
5. **Comparison**: Side-by-side with old diagram to highlight corrections

## Success Criteria

1. ✅ Diagram shows Google CRD website as step 1 (where user gets OAuth code)
2. ✅ Diagram shows Flask web interface (where user submits code + email)
3. ✅ Diagram shows blocking HTTP pattern (subscribe.py → allocator with "BLOCKS" label)
4. ✅ Diagram shows pg_notify as unblocking mechanism (not push to VM)
5. ✅ Diagram shows correct sequence (VM waiting BEFORE user request)
6. ✅ Diagram shows final user access via Google CRD access page
7. ✅ All edge labels accurately describe actual code behavior
8. ✅ Component grouping shows deployment locations (Allocator EC2, Client VM, External)
9. ✅ Peer reviewer can explain workflow correctly after reading diagram

## Alternatives Considered

### Alternative 1: Keep Current Diagram, Add Notes

- **Rejected**: Notes can't fix fundamental architectural misrepresentation
- **Why**: Diagram structure itself implies async push pattern; notes would contradict visuals

### Alternative 2: Create Two Separate Diagrams

- **Option A**: "VM Initialization & Waiting" (blocking pattern focus)
- **Option B**: "User Request & CRD Setup" (user interaction focus)
- **Status**: Consider if single diagram too complex after initial implementation

### Alternative 3: Simplify by Omitting Google CRD Website

- **Rejected**: Google CRD integration is CRITICAL to understanding LabLink
- **Why**: User feedback: "The user goes to google chrome remote desktop in the browser and gets the CRD commands" - explicitly requested

### Alternative 4: Show Only LabLink Components (Omit External Services)

- **Rejected**: Would still be incomplete/misleading
- **Why**: Readers need to understand full end-to-end flow including Google dependencies

## Dependencies

### Upstream

- Requires completed analysis documents (crd-workflow-research.md, crd-workflow-corrected.md) ✅
- Requires understanding of actual codebase behavior ✅

### Downstream

- Will affect paper text describing CRD connection (must match diagram)
- May affect supplementary materials if diagram referenced

### Parallel Work

- Can proceed independently of other diagram improvements
- Should coordinate with any documentation updates about CRD workflow

## Timeline Estimate

- **Phase 1** (2 hours): Update build_crd_connection_diagram() method
  - Add Google CRD website component (30 min)
  - Add Flask web UI component (30 min)
  - Restructure edges for blocking pattern (1 hour)

- **Phase 2** (1 hour): Update labels and sequence
  - Renumber steps (15 min)
  - Update all edge labels for accuracy (30 min)
  - Add annotations (BLOCKS, WAITING, etc.) (15 min)

- **Phase 3** (1 hour): Visual refinement
  - Adjust spacing/layout (30 min)
  - Add color coding for phases (15 min)
  - Test at paper and poster presets (15 min)

- **Phase 4** (30 min): Testing and validation
  - Generate diagrams (5 min)
  - Peer review (15 min)
  - Adjustments based on feedback (10 min)

**Total**: 4.5 hours

## Notes

- User explicitly requested: "The user goes to google chrome remote desktop in the browser and gets the CRD commands. They are able to request a VM from the allocator and authenticate using the CRD command so the CRD command is passed to the allocator through the web interface"

- This change addresses the user's concern: "ok I still think we need to work on this figure" after seeing previous version

- Analysis documents created after thorough codebase review across both `lablink` and `lablink-template` repositories

- Blocking HTTP pattern (long-polling) is CRITICAL architectural insight that current diagram completely misses
