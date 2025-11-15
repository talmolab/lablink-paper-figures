# CRD Workflow Research: Code Analysis

This document contains the detailed code analysis that proves the CRD workflow uses a **blocking HTTP long-polling pattern** rather than async push notifications.

## Research Question

How does the LabLink CRD connection workflow actually work at the code level?

## Key Finding

The workflow uses **synchronous blocking HTTP with long-polling**, NOT async push notifications. The client VM makes a single HTTP POST request that blocks for up to 7 days waiting for a response.

## Code Evidence

### 1. Client VM: Blocking HTTP Request

The client VM's subscribe.py uses a standard blocking HTTP POST with a 7-day timeout.

**Pattern**: Synchronous long-polling HTTP request

**Expected behavior**: The HTTP request will not complete until either:
1. A response is received from the allocator (VM assigned)
2. The 7-day timeout expires
3. Network error occurs

This is the classic long-polling pattern used for real-time updates without WebSockets.

### 2. Allocator: Blocking Endpoint

The allocator's `/vm_startup` endpoint holds the HTTP connection open by calling a blocking database listener function.

**Pattern**: HTTP endpoint that doesn't return immediately

**Expected behavior**: When the client POST arrives:
1. Store initial data in database
2. Call `listen_for_notifications()` which blocks the thread
3. Thread waits until PostgreSQL notification received
4. Return HTTP response with CRD command
5. HTTP connection finally completes

This is server-side long-polling implementation.

### 3. PostgreSQL LISTEN/NOTIFY: Internal Event Bus

The allocator uses PostgreSQL's LISTEN/NOTIFY as an internal event mechanism to know when to unblock waiting HTTP requests.

**Pattern**: Database pub/sub used internally by server

**Expected behavior**:
1. Allocator opens PostgreSQL connection
2. Executes `LISTEN vm_updates_{vm_id}`
3. Enters polling loop checking for notifications
4. When notification received, parse payload and return
5. This unblocks the Flask endpoint
6. Flask endpoint returns HTTP response

**Critical insight**: The client VM never talks to PostgreSQL directly. The pg_notify() mechanism is entirely internal to the allocator service.

### 4. User Workflow: Flask Web Interface

Users request VMs through a Flask web form, not through subscribe.py.

**Pattern**: Traditional web form submission

**Expected behavior**:
1. User navigates to allocator's Flask web UI
2. User fills form with email and CRD command (obtained from Google)
3. User submits form
4. Flask POST handler processes request
5. Database UPDATE triggers pg_notify()
6. User receives success page immediately

The user's HTTP request completes quickly. It's the VM's HTTP request that was blocking.

### 5. Database Trigger: Event Publisher

When a VM is assigned to a user, the database trigger fires and publishes a notification.

**Pattern**: Database trigger with NOTIFY

**Expected behavior**:
1. User request causes UPDATE to vm_table
2. Trigger function executes after UPDATE
3. Trigger calls pg_notify() with channel name and JSON payload
4. All connections LISTENing on that channel receive notification
5. This unblocks the specific VM's waiting allocator thread

### 6. Google Chrome Remote Desktop: External OAuth

Users must visit Google's CRD website BEFORE requesting a VM to obtain the OAuth code.

**Pattern**: External OAuth flow

**Expected flow**:
1. User visits https://remotedesktop.google.com/headless
2. User authenticates with Google account
3. User authorizes Chrome Remote Desktop
4. Google provides OAuth code (starts with "4/0...")
5. User copies this code
6. User pastes code into LabLink Flask form

This step is REQUIRED and happens FIRST, but is completely missing from the current diagram.

## Workflow Sequence (Correct)

```
PHASE 0: VM Initialization (automated, happens first)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T=0:    Terraform provisions Client VM
T=+2m:  VM boots, cloud-init runs
T=+3m:  Docker container starts
T=+3m:  subscribe.py executes
T=+3m:  → HTTP POST to allocator /vm_startup
T=+3m:  → Allocator calls listen_for_notifications()
T=+3m:  → PostgreSQL LISTEN vm_updates_{vm_id}
T=+3m:  ⏳ HTTP REQUEST BLOCKING (waiting up to 7 days)


PHASE 1: User Gets CRD Code (manual, happens later)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T=+30m: User opens browser
T=+30m: User navigates to https://remotedesktop.google.com/headless
T=+31m: User clicks "Begin" → "Next" → "Authorize"
T=+31m: Google OAuth flow completes
T=+31m: Google returns CRD command with OAuth code
T=+32m: User copies the command


PHASE 2: User Requests VM (manual)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T=+33m: User navigates to http://{allocator-ip}/
T=+33m: Flask serves index.html form
T=+34m: User fills form:
        - Email: researcher@university.edu
        - CRD Command: [pastes from Phase 1]
T=+34m: User clicks "Submit"
T=+34m: → POST /api/request_vm
T=+34m: Flask handler calls assign_vm()
T=+34m: → UPDATE vm_table SET useremail=..., crdcommand=...
T=+34m: Database trigger fires
T=+34m: → pg_notify('vm_updates_{vm_id}', {...})
T=+34m: User sees success page with PIN


PHASE 3: VM Unblocks and Configures (automated)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T=+34m: listen_for_notifications() receives pg notification
T=+34m: Function returns CRD command data
T=+34m: /vm_startup endpoint returns HTTP 200
T=+34m: ✓ HTTP REQUEST UNBLOCKS (after 31 minutes of waiting)
T=+34m: subscribe.py receives response
T=+34m: subscribe.py calls connect_to_crd()
T=+35m: → subprocess executes CRD setup command
T=+35m: → Authenticates with Google CRD servers
T=+36m: VM registered with Google CRD
T=+36m: ✓ VM ready for remote access


PHASE 4: User Connects (manual)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T=+37m: User navigates to https://remotedesktop.google.com/access
T=+37m: User sees VM in list of available machines
T=+37m: User clicks on VM
T=+37m: User enters PIN from success page
T=+38m: Chrome Remote Desktop connection established
T=+38m: ✓ User working on remote VM
```

## Architectural Patterns Identified

### Long-Polling HTTP

**What it is**: Client makes HTTP request, server holds connection open until event occurs, then responds.

**Why LabLink uses it**: 
- Simpler than WebSockets
- Works through firewalls
- Reliable delivery (HTTP retry logic)
- No need for persistent connection management

**Tradeoff**: Ties up one thread per waiting VM on allocator. For dozens of VMs this is fine, for thousands would need different approach.

### Database as Event Bus

**What it is**: Using PostgreSQL LISTEN/NOTIFY for pub/sub messaging.

**Why LabLink uses it**:
- Already using PostgreSQL for VM state
- LISTEN/NOTIFY is built-in, no additional infrastructure
- Guaranteed delivery within database transaction
- Multiple listeners can receive same notification

**Tradeoff**: Not suitable for high-throughput scenarios, but perfect for occasional VM assignments.

### Blocking Synchronous Design

**What it is**: Using blocking calls instead of async/await or callbacks.

**Why LabLink uses it**:
- Simpler code, easier to understand
- Flask default is synchronous
- VM assignment is infrequent (not high-throughput)
- 7-day timeout means no retry logic needed

**Tradeoff**: Blocks a thread per waiting VM, but acceptable for small-scale deployments.

## What Current Diagram Gets Wrong

### 1. Missing External OAuth Step

**Current diagram**: Starts with "User requests VM"

**Reality**: User must first visit Google CRD website to get OAuth code, THEN request VM

**Fix needed**: Add Google CRD website as step 1, show user getting code before requesting VM

### 2. Wrong Notification Pattern

**Current diagram**: Shows pg_notify() sending async notification to subscribe.py

**Reality**: pg_notify() unblocks a waiting database connection on the ALLOCATOR, which then returns HTTP response to subscribe.py

**Fix needed**: Show subscribe.py → allocator as blocking HTTP request, pg_notify() as internal allocator mechanism

### 3. Missing Flask Web Interface

**Current diagram**: No web UI shown

**Reality**: User interacts with Flask web form to submit VM request with CRD code

**Fix needed**: Add Flask Web UI component showing form submission

### 4. Wrong Timing

**Current diagram**: Implies subscribe.py reacts to notification

**Reality**: subscribe.py is already waiting (blocking) when user makes request. User request unblocks the waiting subscribe.py

**Fix needed**: Show VM waiting state BEFORE user action

### 5. Missing Final Access Step

**Current diagram**: Ends with "Chrome Remote Desktop connection"

**Reality**: After VM is configured, user must visit Chrome Remote Desktop web interface to actually connect

**Fix needed**: Add final step showing user accessing VM through browser

## Component Roles (Corrected)

### Client VM Components
- **subscribe.py**: Makes blocking HTTP POST to `/vm_startup`, waits for response with CRD command
- **connect_crd.py**: Executes CRD setup command received from subscribe.py
- **Docker container**: Provides environment for above scripts

### Allocator Components (all on same EC2 instance)
- **Flask web app**: Serves UI for user VM requests
- **Flask API /vm_startup**: Blocking endpoint for VM initialization requests
- **Flask API /api/request_vm**: User-facing endpoint for VM assignment requests
- **PostgreSQL database**: Stores VM state, provides LISTEN/NOTIFY event bus
- **database.listen_for_notifications()**: Blocking function that waits for pg notifications

### External Services
- **Google CRD (headless)**: https://remotedesktop.google.com/headless - Provides OAuth codes
- **Google CRD (access)**: https://remotedesktop.google.com/access - Browser-based VM access

### User Touchpoints
1. Google CRD headless website (get OAuth code)
2. LabLink Flask web form (request VM with code)
3. LabLink success page (see PIN and hostname)
4. Google CRD access website (connect to VM)

## Database Schema Analysis

### VM Table Columns Relevant to CRD Workflow

```sql
CREATE TABLE vms (
    hostname VARCHAR PRIMARY KEY,        -- e.g., "lablink-client-1"
    useremail VARCHAR,                   -- Set when VM assigned
    crdcommand TEXT,                     -- CRD command from user
    pin VARCHAR,                         -- Auto-generated PIN
    status VARCHAR,                      -- 'available', 'assigned', etc.
    ... other columns ...
);
```

### State Transitions

```
1. VM created by Terraform:
   hostname='lablink-client-1', useremail=NULL, crdcommand=NULL, status='provisioning'

2. VM boots and subscribe.py runs:
   status='available'
   (subscribe.py POST blocked, waiting...)

3. User requests VM:
   useremail='user@example.com', crdcommand='DISPLAY= /opt/...', pin='123456', status='assigned'
   (Trigger fires → pg_notify → subscribe.py unblocks)

4. VM configured:
   status='active'

5. User releases VM:
   useremail=NULL, crdcommand=NULL, pin=NULL, status='available'
```

## References for Diagram Update

The following code locations should be referenced when updating the diagram:

1. **Blocking HTTP timeout**: 604800 seconds (7 days)
2. **Database notification channel**: `vm_updates_{vm_id}`
3. **Flask web form**: `templates/index.html`
4. **User-facing endpoint**: `POST /api/request_vm`
5. **VM-facing endpoint**: `POST /vm_startup`
6. **Google CRD headless**: https://remotedesktop.google.com/headless
7. **Google CRD access**: https://remotedesktop.google.com/access

## Conclusion

The current CRD connection diagram fundamentally misrepresents the architecture by:
1. Omitting the external Google OAuth step
2. Omitting the Flask web interface
3. Showing async push instead of blocking HTTP
4. Missing the correct timing (VM waits BEFORE user acts)
5. Missing the final browser access step

The corrected diagram must show:
1. Google CRD website for OAuth code (first)
2. VM initialization and blocking HTTP wait (automated, before user)
3. Flask web form for user request (manual, later)
4. Database trigger unblocking allocator's internal listener
5. Allocator returning HTTP response to unblock subscribe.py
6. CRD configuration on VM
7. User accessing VM through Google CRD web interface (last)
