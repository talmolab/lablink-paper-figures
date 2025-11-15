# Specification: Corrected CRD Connection Workflow Diagram

## Overview

This specification defines the requirements for the corrected CRD connection diagram that accurately represents the blocking HTTP long-polling architecture pattern with Google Chrome Remote Desktop integration.

## Requirements

### Requirement: CRD diagram SHALL show Google Chrome Remote Desktop OAuth as first step

The system SHALL generate a CRD connection diagram that shows the Google Chrome Remote Desktop website (remotedesktop.google.com/headless) as the first step in the user workflow, where the user obtains the OAuth code.

#### Scenario: User gets OAuth code from Google CRD website

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows a component labeled "Google CRD OAuth" or "Google CRD (remotedesktop.google.com/headless)"
**And** the diagram shows user interacting with this component as step 1
**And** the diagram shows the component returning an OAuth code/CRD command to the user
**And** this step occurs BEFORE the user submits a VM request

**Code references**:
- [src/diagram_gen/generator.py](src/diagram_gen/generator.py) - build_crd_connection_diagram() method
- [analysis/crd-workflow-research.md:329-340](analysis/crd-workflow-research.md#L329-L340) - Phase 3: User Gets CRD Code

**Acceptance Criteria**:
- Google CRD OAuth component exists in diagram
- User → Google CRD edge exists and is labeled as step 1
- Google CRD → User edge shows "Returns OAuth code" or similar
- Component uses Saas icon type (external service)

---

### Requirement: CRD diagram SHALL show Flask web interface

The system SHALL generate a CRD connection diagram that shows the Flask web interface (index.html) where users submit their email and CRD command to request a VM.

#### Scenario: User submits request via Flask web form

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows a component labeled "Flask Web UI" or "Flask Web UI (index.html)"
**And** the component is in the "LabLink Infrastructure" cluster
**And** the diagram shows user navigating to Flask UI (step 2)
**And** the diagram shows user submitting request via Flask UI (step 3)
**And** the diagram shows Flask UI posting to Allocator backend

**Code references**:
- [lablink/packages/allocator/src/lablink_allocator_service/templates/index.html:40-50](../../../../../lablink/packages/allocator/src/lablink_allocator_service/templates/index.html#L40-L50) - Form with email and crd_command fields
- [lablink/packages/allocator/src/lablink_allocator_service/main.py:64](../../../../../lablink/packages/allocator/src/lablink_allocator_service/main.py#L64) - POST /api/request_vm endpoint

**Acceptance Criteria**:
- Flask Web UI component exists in diagram
- User → Flask UI edge exists (step 2)
- Flask UI → User edge shows form fields
- User → Flask UI → Allocator flow clearly shown (step 3)
- Component uses Flask icon type

---

### Requirement: CRD diagram SHALL show blocking HTTP pattern not async push

The system SHALL generate a CRD connection diagram that accurately represents the blocking HTTP long-polling pattern where the client VM makes a blocking POST request that waits for an HTTP response, NOT an async push notification pattern.

#### Scenario: subscribe.py makes blocking HTTP POST to allocator

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows subscribe.py → allocator edge labeled "POST /vm_startup [BLOCKS]" or similar
**And** the edge style is dashed (indicates HTTP request)
**And** the edge color distinguishes it from other edges (e.g., blue)
**And** the edge label includes "BLOCKS" or "waits" or "7 days timeout"
**And** this edge is shown as step 0 (happens before user actions)

**Code references**:
- [lablink/packages/client/src/lablink_client_service/subscribe.py:176-180](../../../../../lablink/packages/client/src/lablink_client_service/subscribe.py#L176-L180) - requests.post() with timeout=(30, 604800)
- [analysis/crd-workflow-research.md:155-198](analysis/crd-workflow-research.md#L155-L198) - Section 5: Client VM Startup - The Blocking Wait

**Acceptance Criteria**:
- subscribe.py → allocator edge exists and is labeled step 0
- Edge style is dashed
- Label includes "BLOCKS" or similar blocking indicator
- Label includes timeout information (7 days or 604800 seconds)
- Edge color is blue or otherwise distinguished

---

#### Scenario: Allocator returns HTTP response to unblock subscribe.py

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows allocator → subscribe.py edge labeled "Response [UNBLOCKS]" or similar
**And** the edge style is dashed (indicates HTTP response)
**And** the edge color matches the blocking request edge (e.g., blue)
**And** the edge label includes "UNBLOCKS" or "returns CRD data"
**And** this edge is shown after database notification (step 7 or later)

**Code references**:
- [lablink/packages/allocator/src/lablink_allocator_service/main.py:218-223](../../../../../lablink/packages/allocator/src/lablink_allocator_service/main.py#L218-L223) - /vm_startup endpoint returns JSON response
- [analysis/crd-workflow-research.md:199-277](analysis/crd-workflow-research.md#L199-L277) - Section 6: Allocator - The Blocking Endpoint and Section 7: Database - The LISTEN/NOTIFY Wait

**Acceptance Criteria**:
- Allocator → subscribe.py edge exists and is labeled step 7 (or similar)
- Edge style is dashed
- Label includes "UNBLOCKS" or "response" indicator
- Edge color matches blocking request edge
- Shows bidirectional HTTP pattern (request + response)

---

#### Scenario: pg_notify() unblocks allocator connection not client VM

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows pg_notify() → allocator edge (NOT pg_notify() → client VM)
**And** the edge label says "Unblocks listen_for_notifications()" or similar
**And** the diagram does NOT show direct database → client VM notification
**And** pg_notify() component is in "LabLink Infrastructure" cluster (internal mechanism)

**Code references**:
- [lablink/packages/allocator/src/lablink_allocator_service/database.py:237-273](../../../../../lablink/packages/allocator/src/lablink_allocator_service/database.py#L237-L273) - listen_for_notifications() receives pg_notify() within allocator process
- [analysis/crd-workflow-research.md:232-277](analysis/crd-workflow-research.md#L232-L277) - Section 7: Database - The LISTEN/NOTIFY Wait

**Acceptance Criteria**:
- pg_notify() → allocator edge exists
- NO direct pg_notify() → client VM edge
- Label clarifies this unblocks allocator's database connection
- pg_notify() in same cluster as allocator (internal mechanism)

---

### Requirement: CRD diagram SHALL show correct sequence with VM waiting first

The system SHALL generate a CRD connection diagram that shows the correct sequence where the client VM is already waiting (step 0) BEFORE the user takes any action (steps 1-9).

#### Scenario: Step 0 shows VM waiting before user actions

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows step 0 labeled "POST /vm_startup [BLOCKS]" or similar
**And** steps 1-9 show the user workflow (get code, submit request, etc.)
**And** step 0 is visually or textually indicated as a pre-condition
**And** annotations clarify that step 0 happens during VM boot, before user acts

**Code references**:
- [analysis/crd-workflow-corrected.md:69-96](analysis/crd-workflow-corrected.md#L69-L96) - Phase 2: Client VM Waiting (ALREADY running, BEFORE user request)
- [analysis/crd-workflow-research.md:316-327](analysis/crd-workflow-research.md#L316-L327) - Phase 2: Client VM Registration (Automatic on Boot)

**Acceptance Criteria**:
- Step 0 exists and shows VM → allocator blocking request
- Steps 1-9 show user workflow chronologically
- subscribe.py component has annotation like "[WAITING since boot]"
- Diagram makes clear that step 0 is ongoing when step 1 begins

---

#### Scenario: Steps 1-9 show complete user workflow

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows 10 distinct steps (0-9) covering:
- 0: VM blocks waiting
- 1: User gets OAuth code from Google CRD
- 2-3: User submits request via Flask UI
- 4-6: Allocator updates database, trigger fires, notification sent
- 7: Allocator responds to VM's blocking request
- 8: VM executes CRD command
- 9: User accesses configured VM

**Code references**:
- [analysis/crd-workflow-corrected.md:44-381](analysis/crd-workflow-corrected.md#L44-L381) - Complete corrected workflow with all phases
- [analysis/crd-workflow-research.md:314-377](analysis/crd-workflow-research.md#L314-L377) - Complete workflow sections

**Acceptance Criteria**:
- All 10 steps (0-9) are visible in diagram
- Each step has clear label describing action
- Sequence is logical and chronological
- No steps are missing from end-to-end flow

---

### Requirement: CRD diagram SHALL show final user access via Google CRD access page

The system SHALL generate a CRD connection diagram that shows the final step where the user accesses the configured VM through the Google Chrome Remote Desktop access page (remotedesktop.google.com/access).

#### Scenario: User accesses VM via Google CRD access page

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows a component labeled "Google CRD Access" or "Google CRD (remotedesktop.google.com/access)"
**And** the diagram shows user accessing this component as step 9 (final step)
**And** the edge is labeled with "Access VM" or "Enter PIN" or similar
**And** this step occurs AFTER CRD configuration on VM (step 8)

**Code references**:
- [analysis/crd-workflow-corrected.md:182-209](analysis/crd-workflow-corrected.md#L182-L209) - Phase 5: User Accesses VM
- [analysis/crd-workflow-research.md:366-377](analysis/crd-workflow-research.md#L366-L377) - Phase 7: User Accesses VM (Chrome Remote Desktop)

**Acceptance Criteria**:
- Google CRD Access component exists in diagram
- User → Google CRD Access edge exists and is labeled as step 9
- Edge label mentions accessing VM or entering PIN
- Component uses Saas icon type (external service)
- This is the final step in the workflow

---

### Requirement: CRD diagram SHALL group components by deployment location

The system SHALL generate a CRD connection diagram that uses clusters to group components by their deployment location (Allocator EC2, Client VM, External Services).

#### Scenario: Components grouped in deployment-based clusters

**Given** the CRD connection diagram is generated
**When** the user views the diagram
**Then** the diagram shows a cluster labeled "LabLink Infrastructure" or "Allocator EC2"
**And** this cluster contains: Flask Web UI, Allocator, PostgreSQL Database, Database Trigger, pg_notify()
**And** the diagram shows a cluster labeled "Client VM" or "Separate EC2"
**And** this cluster contains: subscribe.py, connect_crd.py
**And** the diagram shows a cluster labeled "External Services" or "Google"
**And** this cluster contains: Google CRD OAuth, Google CRD Access
**And** the User component is outside all clusters

**Code references**:
- [design.md:Decision 5](design.md#decision-5-component-grouping-by-deployment-location) - Component grouping by deployment location
- [lablink-template/lablink-infrastructure](../../../../../lablink-template/lablink-infrastructure) - Terraform infrastructure showing EC2 deployments

**Acceptance Criteria**:
- Three clusters exist: LabLink Infrastructure, Client VM, External Services
- Each component is in the correct cluster based on where it runs
- User component is not in any cluster
- Cluster labels clearly indicate deployment location

---

### Requirement: CRD diagram SHALL accurately label all edges with code-verified descriptions

The system SHALL generate a CRD connection diagram where all edge labels accurately describe the actual code behavior, verified against source code references.

#### Scenario: Database UPDATE edge matches actual SQL

**Given** the CRD connection diagram is generated
**When** the user views the edge from allocator to database
**Then** the edge label says "UPDATE vm_table SET crdcommand=..." or similar
**And** the label matches the actual SQL in database.py:141-148

**Code references**:
- [lablink/packages/allocator/src/lablink_allocator_service/database.py:141-148](../../../../../lablink/packages/allocator/src/lablink_allocator_service/database.py#L141-L148) - UPDATE vms SET useremail, crdcommand, pin

**Acceptance Criteria**:
- Edge label mentions UPDATE or SQL or SET crdcommand
- Label is concise but accurate (< 50 characters)
- Label matches actual code behavior

---

#### Scenario: pg_notify edge label matches actual PostgreSQL call

**Given** the CRD connection diagram is generated
**When** the user views the edge from trigger to pg_notify()
**Then** the edge label says "pg_notify('vm_updates', JSON)" or similar
**And** the label matches the actual trigger code in generate_init_sql.py:103-109

**Code references**:
- [lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py:103-109](../../../../../lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py#L103-L109) - PERFORM pg_notify('vm_updates', json_build_object(...))

**Acceptance Criteria**:
- Edge label mentions pg_notify and channel name 'vm_updates'
- Label mentions JSON payload or similar
- Label matches actual trigger function code

---

#### Scenario: Blocking timeout label matches actual code timeout

**Given** the CRD connection diagram is generated
**When** the user views the edge from subscribe.py to allocator (blocking request)
**Then** the edge label mentions "7 days" or "604800 seconds" timeout
**And** the timeout matches the actual code in subscribe.py:179

**Code references**:
- [lablink/packages/client/src/lablink_client_service/subscribe.py:179](../../../../../lablink/packages/client/src/lablink_client_service/subscribe.py#L179) - timeout=(30, 604800)

**Acceptance Criteria**:
- Edge label mentions 7 days or 604800 or "up to 7 days"
- Timeout value matches actual code
- Label clearly indicates this is a blocking timeout

---

### Requirement: CRD diagram SHALL pass peer review test

The system SHALL generate a CRD connection diagram that enables a peer reviewer unfamiliar with LabLink to correctly answer questions about the architecture after viewing the diagram.

#### Scenario: Peer reviewer understands where user gets CRD code

**Given** a peer reviewer unfamiliar with LabLink views the CRD connection diagram
**When** asked "Where does the user get the CRD code?"
**Then** the reviewer answers "Google Chrome Remote Desktop website" or "remotedesktop.google.com/headless" or similar
**And** the answer is considered correct

**Acceptance Criteria**:
- 75% or more of peer reviewers answer correctly
- Diagram clearly shows Google CRD OAuth component as step 1
- User interaction with Google CRD is visually obvious

---

#### Scenario: Peer reviewer understands blocking pattern

**Given** a peer reviewer unfamiliar with LabLink views the CRD connection diagram
**When** asked "How does the client VM know when it's been assigned?"
**Then** the reviewer answers mentioning "blocking HTTP request" or "waiting for HTTP response" or "POST request that blocks"
**And** the answer demonstrates understanding of blocking pattern (NOT push notifications)

**Acceptance Criteria**:
- 75% or more of peer reviewers answer correctly
- Diagram clearly shows bidirectional HTTP edges with BLOCKS/UNBLOCKS labels
- Peer reviewer does NOT say "push notification" or "async notification"

---

#### Scenario: Peer reviewer understands database trigger role

**Given** a peer reviewer unfamiliar with LabLink views the CRD connection diagram
**When** asked "What role does the database trigger play?"
**Then** the reviewer answers mentioning "unblocks the allocator" or "sends notification to allocator" or "internal notification"
**And** the answer demonstrates understanding that trigger notifies allocator, NOT client VM directly

**Acceptance Criteria**:
- 75% or more of peer reviewers answer correctly
- Diagram clearly shows pg_notify → allocator edge (NOT pg_notify → client VM)
- Label "Unblocks listen_for_notifications()" or similar is clear

---

### Requirement: CRD diagram SHALL support paper and poster presets without overlap

The system SHALL generate the CRD connection diagram with both paper (14pt fonts) and poster (20pt fonts) presets without any text overlapping graphics or other text.

#### Scenario: Paper preset renders without overlap

**Given** the CRD connection diagram is generated with paper preset (14pt fonts)
**When** the diagram is rendered to PNG at 300 DPI
**Then** no edge labels overlap with node graphics
**And** no edge labels overlap with other edge labels
**And** all text is readable at publication scale (6-8 inches wide)

**Code references**:
- [src/diagram_gen/generator.py](src/diagram_gen/generator.py) - _create_graph_attr() with fontsize_preset="paper"

**Acceptance Criteria**:
- Visual inspection shows no overlapping text
- All components and labels visible
- Diagram renders successfully without GraphViz errors

---

#### Scenario: Poster preset renders without overlap

**Given** the CRD connection diagram is generated with poster preset (20pt fonts)
**When** the diagram is rendered to PNG at 300 DPI
**Then** no edge labels overlap with node graphics (despite 43% larger fonts)
**And** no edge labels overlap with other edge labels
**And** spacing (nodesep, ranksep) is sufficient for larger fonts
**And** minlen on edges prevents crowding

**Code references**:
- [src/diagram_gen/generator.py](src/diagram_gen/generator.py) - _create_graph_attr() with fontsize_preset="poster"

**Acceptance Criteria**:
- Visual inspection shows no overlapping text
- All components and labels visible with larger fonts
- Spacing automatically increases for poster preset
- Diagram renders successfully without GraphViz errors

---

## MODIFIED Requirements

None. All requirements are new for the corrected CRD workflow diagram.

## ADDED Requirements

All requirements in this specification are new additions to correct the fundamental architectural misrepresentations in the current CRD connection diagram.

## REMOVED Requirements

None. No existing requirements are being removed. The current diagram requirements are being replaced with these corrected requirements.

---

## Summary of Requirements

1. ✅ Google CRD OAuth shown as step 1 (where user gets code)
2. ✅ Flask Web UI shown (where user submits request)
3. ✅ Blocking HTTP pattern shown (NOT async push)
4. ✅ subscribe.py → allocator edge labeled "BLOCKS"
5. ✅ Allocator → subscribe.py edge labeled "UNBLOCKS"
6. ✅ pg_notify() → allocator (NOT pg_notify() → client VM)
7. ✅ Correct sequence (step 0 = VM waiting, steps 1-9 = user workflow)
8. ✅ Google CRD Access shown as final step 9
9. ✅ Components grouped by deployment location (3 clusters)
10. ✅ All edge labels match actual code behavior
11. ✅ Peer review test passes (> 75% correct answers on 3 questions)
12. ✅ Both paper and poster presets render without overlap

---

## Validation Methods

### Code Reference Validation
- Every edge label MUST have a corresponding code reference in comments
- Code references MUST include file path and line numbers
- Labels MUST accurately describe the code behavior

### Peer Review Validation
- Minimum 2 peer reviewers unfamiliar with LabLink internals
- 3 standard questions (see Requirement: peer review)
- 75% pass rate required (6 out of 8 question-reviewer combinations)
- If failed, iterate on diagram and re-test

### Visual Inspection Validation
- Generate with both paper and poster presets
- Check for text overlap (none allowed)
- Check for missing components (all 9 required)
- Check for missing edges (all 12+ required)
- Check for correct cluster grouping (3 clusters)

### Regression Testing
- Generate all other diagrams (main, vm-provisioning, logging-pipeline)
- Verify no unexpected changes
- Verify all still render correctly
