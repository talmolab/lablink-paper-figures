# Corrected CRD Connection Workflow

## Current Diagram (WRONG)

```
User
  |
  | 1. Request VM
  v
Allocator
  |
  | 2. Assign VM, UPDATE vm_table
  v
VM Table (Database)
  |
  | TRIGGER fires
  v
pg_notify()
  |
  | 3. Notification (async)
  v
Client VM: subscribe.py
  |
  | 4. Execute CRD command
  v
Client VM: connect_crd.py
  |
  | 5. Authenticates & Connects
  v
Chrome Remote Desktop
  |
  | 6. Connection back
  v
User
```

**Problems**:
- Missing: Where user gets CRD code
- Missing: Flask web interface
- Wrong: Shows async push to subscribe.py
- Wrong: Implies subscribe.py starts after assignment
- Missing: User final access through browser

## Corrected Workflow

### Phase 1: User Gets CRD Code (BEFORE requesting VM)

```
User
  |
  | Navigate to website
  v
https://remotedesktop.google.com/headless
  |
  | Click "Begin" → "Next" → "Authorize"
  | (OAuth flow with Google account)
  v
Google Chrome Remote Desktop Server
  |
  | Returns authorization code
  v
User receives command:
  DISPLAY= /opt/google/chrome-remote-desktop/start-host \
    --code="4/0AanRJrjkgQ..." \
    --redirect-url="https://remotedesktop.google.com/_/oauthredirect" \
    --name=$(hostname)
```

### Phase 2: Client VM Waiting (ALREADY running, BEFORE user request)

```
Client VM boots
  |
  | Startup script runs
  v
Docker Container: lablink-client
  |
  | Container starts
  v
subscribe.py runs
  |
  | POST /vm_startup with hostname
  | TIMEOUT: 7 DAYS (604800 seconds)
  v
Allocator: Flask App
  |
  | Receives POST /vm_startup
  v
database.listen_for_notifications()
  |
  | PostgreSQL LISTEN 'vm_updates'
  | BLOCKING - waits indefinitely
  v
[WAITING... HTTP connection open, no response yet]
[Client VM blocked, Allocator endpoint blocked]
```

### Phase 3: User Requests VM

```
User (has CRD code from Phase 1)
  |
  | Navigate to allocator
  v
http://allocator-ip/
  |
  | Flask serves index.html
  v
Web Form
  - Email: user@example.com
  - CRD Command: [paste from Phase 1]
  |
  | Click "Submit"
  v
POST /api/request_vm
  |
  | Validate CRD command (must have --code)
  | Check available VMs
  v
database.assign_vm(email, crd_command, pin)
  |
  | SQL: UPDATE vms SET 
  |      useremail = 'user@example.com',
  |      crdcommand = '...',
  |      pin = '123456'
  |      WHERE hostname = 'lablink-client-1'
  v
Database TRIGGER: notify_crd_command_update()
  |
  | Fires on UPDATE OF CrdCommand
  v
pg_notify('vm_updates', JSON)
  |
  | JSON = {
  |   "HostName": "lablink-client-1",
  |   "CrdCommand": "...",
  |   "Pin": "123456"
  | }
  v
PostgreSQL sends notification on channel
```

### Phase 4: Client VM Unblocks and Configures

```
database.listen_for_notifications() [was waiting since Phase 2]
  |
  | Receives notification
  | Checks: HostName matches target
  v
Returns: {
  "status": "success",
  "pin": "123456",
  "command": "..."
}
  |
  | HTTP response sent
  v
subscribe.py receives response
  |
  | Parses JSON
  v
connect_to_crd(pin, command)
  |
  | Reconstruct full CRD command
  | Prepare PIN input (twice for verification)
  v
subprocess.run(
  "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=... --redirect-url=... --name=..."
)
  |
  | Executes CRD setup
  v
Chrome Remote Desktop Server (Google)
  |
  | Authenticates with code
  | Registers VM
  v
VM now accessible via Chrome Remote Desktop
```

### Phase 5: User Accesses VM

```
User sees success page
  - Hostname: lablink-client-1
  - PIN: 123456
  |
  | Navigate to access page
  v
https://remotedesktop.google.com/access/
  |
  | Google shows available remote machines
  | (VM appears automatically after Phase 4)
  v
User clicks on "lablink-client-1"
  |
  | Prompted for PIN
  v
User enters PIN: 123456
  |
  | Establishes connection
  v
Chrome Remote Desktop Connection
  |
  | Streaming VM desktop in browser
  v
User is working on remote VM
```

## Key Architecture Insights

### 1. Long Polling Pattern

This is NOT a push notification system. It's a **long polling** HTTP pattern:

```
Client makes request → Server holds connection open → 
Event occurs → Server responds → Client processes
```

### 2. Two Separate HTTP Connections

```
Connection 1 (Client VM → Allocator):
  POST /vm_startup → [BLOCKING] → 200 OK with CRD data

Connection 2 (User → Allocator):
  POST /api/request_vm → [Quick response] → Success page
```

Connection 1 blocks for up to 7 days.
Connection 2 responds immediately after database update.

### 3. Database as Event Bus

```
PostgreSQL LISTEN/NOTIFY is used as an event bus:
- Multiple client VMs can LISTEN simultaneously
- Each gets hostname-filtered notifications
- Unblocks only the matching VM's connection
```

### 4. External Dependencies

```
LabLink depends on two external Google services:
1. remotedesktop.google.com/headless - Get OAuth code
2. remotedesktop.google.com/access - Access configured VM
```

## Components and Their Roles

### User Actions (Manual)
1. Get CRD code from Google
2. Paste CRD code into LabLink form
3. Access VM via Chrome Remote Desktop

### Allocator Components
- **Flask Web App**: Serves UI, handles API requests
- **PostgreSQL Database**: Stores VM state, sends notifications
- **Terraform**: Provisions infrastructure (not shown in connection flow)

### Client VM Components
- **subscribe.py**: Makes blocking HTTP call, waits for assignment
- **connect_crd.py**: Executes CRD setup command

### External Services
- **Google Chrome Remote Desktop** (headless setup): Provides OAuth code
- **Google Chrome Remote Desktop** (access): Provides connection interface

## Timeline Example

```
T=0:     Admin creates 5 VMs via Terraform
T=+5min: VMs boot, all 5 run subscribe.py
T=+5min: All 5 POST to /vm_startup, all 5 are WAITING

[Hours pass, VMs are waiting...]

T=+2hr:  User Alice visits remotedesktop.google.com/headless
T=+2hr:  Alice gets code: --code="4/ABC123..."
T=+2hr:  Alice navigates to http://allocator-ip/
T=+2hr:  Alice pastes code and email, clicks Submit
T=+2hr:  Allocator assigns VM #1 to Alice
T=+2hr:  Database trigger fires
T=+2hr:  VM #1's subscribe.py unblocks (VMs #2-5 still waiting)
T=+2hr:  VM #1 configures Chrome Remote Desktop
T=+2hr:  Alice navigates to remotedesktop.google.com/access
T=+2hr:  Alice sees VM #1, clicks it, enters PIN
T=+2hr:  Alice is connected to VM #1

[VM #2-5 still waiting for their assignments...]

T=+3hr:  User Bob gets code, submits request
T=+3hr:  VM #2 assigned to Bob, unblocks, configures...
```

## Data Flow Sequence

### Request Flow
```
User Form → POST /api/request_vm → Flask Handler →
database.assign_vm() → SQL UPDATE → Trigger Function →
pg_notify() → [Notification in database]
```

### Response Flow
```
[Notification in database] → 
database.listen_for_notifications() receives → 
Flask /vm_startup returns → HTTP response to client →
subscribe.py receives → connect_to_crd() →
subprocess CRD setup → [VM configured]
```

## Why the Current Diagram is Wrong

### Misleading Aspects

1. **Shows user requesting VM as first step**
   - Reality: User must get CRD code BEFORE requesting VM

2. **Shows subscribe.py as passive listener**
   - Reality: subscribe.py makes active HTTP POST that blocks

3. **Shows pg_notify pushing to VM**
   - Reality: pg_notify unblocks a database connection on the allocator

4. **Omits Flask web interface**
   - Reality: Flask serves the form where users input CRD code

5. **Omits external Google services**
   - Reality: Two separate Google services are essential

6. **Shows async notification**
   - Reality: Synchronous unblocking of waiting connection

### What Needs to Change

1. Add Google Chrome Remote Desktop (headless) as first step
2. Add Flask Web UI component
3. Show subscribe.py → allocator as BLOCKING HTTP request
4. Relabel pg_notify as "unblocks waiting connection"
5. Add final user access via Chrome Remote Desktop web interface
6. Reorder steps to show CRD code acquisition first

## Diagram Update Recommendations

### New Component Boxes Needed
- External Service: "Google CRD\n(remotedesktop.google.com/headless)"
- Web Interface: "Flask Web UI\n(index.html form)"
- External Service: "Google CRD Access\n(remotedesktop.google.com/access)"

### New Edges Needed
- User → Google CRD (headless): "Get OAuth code"
- Google CRD → User: "Returns CRD command"
- User → Flask Web UI: "Submit email + CRD code"
- Flask Web UI → Allocator backend: "POST /api/request_vm"
- Client VM → Allocator: "POST /vm_startup [BLOCKS]" (style: dashed, color: blue)
- Allocator → Client VM: "Response with CRD data [UNBLOCKS]" (style: dashed, color: blue)
- User → Google CRD Access: "Access configured VM"

### Labels to Update
- pg_notify: Change from "Notification (async)" to "Notification (unblocks connection)"
- subscribe.py: Add note "WAITING since VM boot"
- Allocator /vm_startup: Add note "BLOCKING HTTP endpoint"

### Visual Improvements
- Use different colors for:
  - Setup phase (blue): VM waiting
  - User request phase (green): Form submission
  - Configuration phase (orange): CRD setup
  - Access phase (purple): Final connection
- Add timeline annotations showing sequence
- Group components by deployment location:
  - Allocator EC2
  - Client VM EC2
  - External (Google)
  - User's browser
