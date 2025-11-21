# LabLink Key Workflows

This document describes the critical workflows in the LabLink system, focusing on the Chrome Remote Desktop (CRD) connection process and VM provisioning.

## CRD Connection Workflow

The CRD connection workflow enables users to access remote VMs through Google Chrome Remote Desktop. This is the **primary user-facing workflow** in LabLink.

### Architecture Pattern: Long-Polling HTTP

**Key insight**: This workflow uses **synchronous blocking HTTP with long-polling**, NOT async push notifications or WebSockets. The client VM makes a single HTTP POST request that blocks for up to 7 days waiting for a response.

### Complete Workflow (5 Phases)

#### Phase 1: User Gets CRD Code (BEFORE requesting VM)

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

**User action required**: User must obtain OAuth code from Google BEFORE requesting VM from LabLink.

#### Phase 2: Client VM Waiting (ALREADY running, BEFORE user request)

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

**Key technical detail**: The VM's HTTP POST request stays open (blocking) for up to 7 days. This is long-polling, not async messaging.

#### Phase 3: User Requests VM

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

**User action required**: User pastes CRD code from Phase 1 into LabLink web form.

#### Phase 4: Client VM Unblocks and Configures

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

**Automatic**: VM configures itself once user submits request. No further user action needed until access.

#### Phase 5: User Accesses VM

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

**User action required**: User navigates to Google CRD access page and enters PIN shown on LabLink success page.

### Timeline Example

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

### Key Architecture Insights

#### 1. Long Polling Pattern

This is NOT a push notification system. It's a **long polling** HTTP pattern:

```
Client makes request → Server holds connection open →
Event occurs → Server responds → Client processes
```

**Why long-polling?**
- Simpler than WebSockets
- Works through firewalls/NAT
- No persistent connection management
- Python requests library handles it natively

**Trade-offs**:
- One thread per waiting VM (acceptable for small-scale)
- 7-day timeout prevents infinite waiting
- Network interruptions require retry logic

#### 2. Two Separate HTTP Connections

```
Connection 1 (Client VM → Allocator):
  POST /vm_startup → [BLOCKING] → 200 OK with CRD data

Connection 2 (User → Allocator):
  POST /api/request_vm → [Quick response] → Success page
```

Connection 1 blocks for up to 7 days.
Connection 2 responds immediately after database update.

#### 3. Database as Event Bus

```
PostgreSQL LISTEN/NOTIFY is used as an event bus:
- Multiple client VMs can LISTEN simultaneously
- Each gets hostname-filtered notifications
- Unblocks only the matching VM's connection
```

**Why PostgreSQL LISTEN/NOTIFY?**
- Built-in pub/sub mechanism
- No additional message broker needed
- Transactional consistency (notification only if UPDATE commits)
- Lightweight for small-scale deployments

#### 4. External Dependencies

```
LabLink depends on two external Google services:
1. remotedesktop.google.com/headless - Get OAuth code
2. remotedesktop.google.com/access - Access configured VM
```

**Security consideration**: Google OAuth ensures only authenticated users can access VMs.

### Components and Their Roles

#### User Actions (Manual)
1. Get CRD code from Google (Phase 1)
2. Paste CRD code into LabLink form (Phase 3)
3. Access VM via Chrome Remote Desktop (Phase 5)

#### Allocator Components
- **Flask Web App**: Serves UI, handles API requests
- **PostgreSQL Database**: Stores VM state, sends notifications
- **Terraform**: Provisions infrastructure (not shown in connection flow)

#### Client VM Components
- **subscribe.py**: Makes blocking HTTP call, waits for assignment
- **connect_crd.py**: Executes CRD setup command

#### External Services
- **Google Chrome Remote Desktop** (headless setup): Provides OAuth code
- **Google Chrome Remote Desktop** (access): Provides connection interface

### Data Flow Sequence

#### Request Flow
```
User Form → POST /api/request_vm → Flask Handler →
database.assign_vm() → SQL UPDATE → Trigger Function →
pg_notify() → [Notification in database]
```

#### Response Flow
```
[Notification in database] →
database.listen_for_notifications() receives →
Flask /vm_startup returns → HTTP response to client →
subscribe.py receives → connect_to_crd() →
subprocess CRD setup → [VM configured]
```

## VM Provisioning Workflow

The VM provisioning workflow is how administrators create new VM instances for users to access.

### Provisioning Steps

```
Admin
  |
  | Navigate to /admin
  | HTTP Basic Auth required
  v
Admin Dashboard
  |
  | Click "Create VMs"
  v
VM Creation Form
  - Number of instances: 5
  - Instance type: g4dn.xlarge
  |
  | Click "Launch"
  v
POST /api/launch
  |
  | Authenticated with HTTP Basic Auth
  v
Terraform subprocess
  |
  | terraform apply -auto-approve
  | -var="num_instances=5"
  | -var="instance_type=g4dn.xlarge"
  v
AWS API Calls
  |
  | Create EC2 instances
  | Create security groups
  | Attach IAM roles
  | Configure CloudWatch logging
  v
VMs booting
  |
  | User data script executes
  | Docker container starts
  | subscribe.py runs
  v
VMs waiting for assignment (enters CRD workflow Phase 2)
```

### Terraform Resources Created

For each VM, Terraform provisions:

1. **EC2 Instance** (g4dn.xlarge or similar)
2. **Security Group** (SSH, RDP, CRD ports)
3. **IAM Instance Profile** (CloudWatch Logs permissions)
4. **CloudWatch Log Group** (VM application logs)
5. **Elastic IP** (optional, based on configuration)

See [infrastructure.md](infrastructure.md) for complete resource inventory.

### VM Startup Sequence

```
1. EC2 instance boots
2. User data script runs:
   - Install Docker
   - Pull lablink-client container
   - Start container
3. Container starts:
   - Run subscribe.py
   - POST /vm_startup (enters blocking state)
4. VM now waiting for assignment
```

**Duration**: Typically 3-5 minutes from Terraform apply to VM waiting state.

## VM Destruction Workflow

The VM destruction workflow removes VMs from the pool.

### Destruction Steps

```
Admin
  |
  | Navigate to /admin
  v
Admin Dashboard
  |
  | Click "Destroy All VMs"
  | Confirmation prompt
  v
POST /destroy
  |
  | HTTP Basic Auth required
  v
Terraform subprocess
  |
  | terraform destroy -auto-approve
  v
AWS API Calls
  |
  | Terminate EC2 instances
  | Delete security groups
  | Delete IAM roles
  | Delete CloudWatch log groups
  v
VMs terminated
  |
  | Database records marked as destroyed
  v
No VMs available
```

**Warning**: Destructive operation. All user data on VMs is lost.

## Logging Workflow

The logging workflow captures VM logs and makes them available to administrators.

### Log Flow

```
Client VM
  |
  | Application writes to stdout/stderr
  v
Docker container logs
  |
  | Docker logging driver: awslogs
  v
CloudWatch Logs
  |
  | Log stream: /aws/ec2/lablink-client-1
  v
CloudWatch Subscription Filter
  |
  | Filter pattern: [all]
  | Destination: Lambda function
  v
Lambda: log-processor
  |
  | Parse log entries
  | Extract structured data
  v
POST /api/vm-logs
  |
  | Send logs to allocator
  v
Allocator Database
  |
  | INSERT INTO vm_logs
  v
Admin View
  |
  | GET /admin/logs/<hostname>
  | Renders logs in web UI
  v
Admin sees VM logs
```

**Latency**: Typically 30-60 seconds from log write to admin visibility.

**Retention**: CloudWatch logs retained for 7 days, database logs retained indefinitely (or until VM destroyed).

## Related Documentation

- [API Endpoints](api-endpoints.md) - All 22 Flask endpoints with details
- [Database Schema](database-schema.md) - PostgreSQL tables and triggers
- [Infrastructure](infrastructure.md) - Complete AWS resource inventory
- [Configuration](configuration.md) - LabLink configuration options

## Diagram Generation

To regenerate workflow diagrams:

```bash
# CRD connection workflow
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type crd-connection \
  --preset poster

# VM provisioning workflow
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type vm-provisioning \
  --preset poster

# Logging pipeline
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type logging-pipeline \
  --preset poster
```
