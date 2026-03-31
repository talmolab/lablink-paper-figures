# LabLink API Architecture Analysis

## Overview

This document provides a comprehensive analysis of the LabLink Flask API architecture, documenting all endpoints with their HTTP methods, authentication requirements, and functional categorization.

**Updated:** 2026-03-31 (Bearer token auth, new endpoints for scheduled destruction and reboot, logging changes)

## Complete API Endpoint Inventory

### Total: 28+ Endpoints

**Breakdown by category:**
- User Interface: 2 endpoints (public)
- Admin Management: 16 endpoints (HTTP Basic Auth or Bearer token)
- VM-to-Allocator API: 5 endpoints (Bearer token auth)
- Query API: 4 endpoints (public or auth required)
- Log Shipper Callback: 1 endpoint (Bearer token required)

**Authentication model (updated 2026-03):**
- HTTP Basic Auth: Admin UI and admin API endpoints
- Bearer token: Auto-generated at allocator startup for VM-to-allocator and log shipper calls
- `require_auth()` decorator accepts either Basic or Bearer auth

**New endpoints since Nov 2025:**
- `POST /api/schedule-destruction` — Schedule automated VM destruction
- `GET /api/schedule-destruction` — List scheduled destructions
- `DELETE /api/schedule-destruction/<id>` — Cancel scheduled destruction
- `POST /api/reboot-vm` — Reboot a client VM
- `GET /api/reboot-vm/<hostname>` — Check reboot status
- `GET /admin/scheduled-destruction` — View scheduled destructions UI

## Category 1: User Interface (2 endpoints - Public)

These are the user-facing endpoints for the web interface.

### GET /
- **Line**: 137
- **Purpose**: Home page with VM request form
- **Security**: Public
- **Returns**: Renders `index.html` template
- **Notes**: Main entry point for users

### POST /api/request_vm
- **Line**: 245
- **Purpose**: User requests VM assignment with CRD code
- **Security**: Public (validates CRD code format)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "crd_command": "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=...",
    "pin": "123456"
  }
  ```
- **Validation**:
  - CRD command must contain `--code=`
  - PIN must be provided
  - Email format validated
- **Returns**: Success page with assigned VM hostname
- **Notes**: Creates VM assignment, triggers database notification

## Category 2: Admin Management (10 endpoints - HTTP Basic Auth)

All admin endpoints use the `@auth.login_required` decorator (lines 96-106). Authentication verified via `verify_password()` function using bcrypt password hashing.

### VM Provisioning Endpoints (6)

#### GET /admin
- **Line**: 148
- **Decorator**: `@auth.login_required`
- **Purpose**: Admin dashboard overview
- **Returns**: Renders admin dashboard template
- **Security**: HTTP Basic Auth (bcrypt)

#### GET /admin/create
- **Line**: 142
- **Decorator**: `@auth.login_required`
- **Purpose**: Page for creating new VMs
- **Returns**: Renders VM creation form
- **Security**: HTTP Basic Auth (bcrypt)

#### POST /api/launch
- **Line**: 291
- **Decorator**: `@auth.login_required`
- **Purpose**: Provision new VMs via Terraform
- **Request Body**:
  ```json
  {
    "num_instances": 5,
    "instance_type": "g4dn.xlarge"
  }
  ```
- **Returns**: Launch status and VM identifiers
- **Security**: HTTP Basic Auth (bcrypt)
- **Notes**: Triggers Terraform subprocess

#### POST /destroy
- **Line**: 418
- **Decorator**: `@auth.login_required`
- **Purpose**: Destroy all VMs
- **Returns**: Destruction status
- **Security**: HTTP Basic Auth (bcrypt)
- **Notes**: Destructive operation, requires confirmation

#### GET /admin/instances
- **Line**: 232
- **Decorator**: `@auth.login_required`
- **Purpose**: View all VM instances
- **Returns**: List of all VMs with status
- **Security**: HTTP Basic Auth (bcrypt)

#### GET /admin/instances/delete
- **Line**: 239
- **Decorator**: `@auth.login_required`
- **Purpose**: Page for deleting specific VMs
- **Returns**: Renders deletion interface
- **Security**: HTTP Basic Auth (bcrypt)

### AWS Credentials Endpoints (2)

#### POST /api/admin/set-aws-credentials
- **Line**: 193
- **Decorator**: `@auth.login_required`
- **Purpose**: Set AWS credentials for Terraform
- **Request Body**:
  ```json
  {
    "aws_access_key_id": "AKIA...",
    "aws_secret_access_key": "...",
    "aws_region": "us-east-1"
  }
  ```
- **Returns**: Success/error status
- **Security**: HTTP Basic Auth (bcrypt)
- **Notes**: Stores credentials securely

#### POST /api/admin/unset-aws-credentials
- **Line**: 180
- **Decorator**: `@auth.login_required`
- **Purpose**: Unset/clear AWS credentials
- **Returns**: Success status
- **Security**: HTTP Basic Auth (bcrypt)

### Monitoring & Data Endpoints (2)

#### GET /admin/logs/<hostname>
- **Line**: 723
- **Decorator**: `@auth.login_required`
- **Purpose**: View VM logs page for specific hostname
- **URL Parameters**: `hostname` (VM identifier)
- **Returns**: Renders logs viewing page
- **Security**: HTTP Basic Auth (bcrypt)

#### GET /api/scp-client
- **Line**: 469
- **Decorator**: `@auth.login_required`
- **Purpose**: Download data from VMs via SCP
- **Returns**: File download or status
- **Security**: HTTP Basic Auth (bcrypt)
- **Notes**: Used for collecting experiment data

## Category 3: VM-to-Allocator API (5 endpoints - Public with validation)

These endpoints are called by Client VMs. While technically "public" (no HTTP Basic Auth), they validate the calling VM exists in the database.

### POST /vm_startup
- **Line**: 449
- **Purpose**: **BLOCKING** endpoint for VM startup notification
- **Security**: Public (validates hostname exists)
- **Request Body**:
  ```json
  {
    "hostname": "lablink-client-1",
    "crd_code": "..."
  }
  ```
- **Behavior**:
  - **BLOCKS for up to 7 days** (604,800 seconds)
  - Uses PostgreSQL LISTEN/NOTIFY to wait for assignment
  - Returns CRD command when VM assigned
- **Returns**:
  ```json
  {
    "status": "success",
    "pin": "123456",
    "command": "DISPLAY= /opt/..."
  }
  ```
- **Notes**: Long-polling pattern, critical for CRD workflow

### POST /api/update_inuse_status
- **Line**: 579
- **Purpose**: VM reports whether it's in use
- **Security**: Public (validates hostname exists)
- **Request Body**:
  ```json
  {
    "hostname": "lablink-client-1",
    "inuse": true,
    "last_activity": "2025-01-15T14:30:00Z"
  }
  ```
- **Returns**: Success status
- **Notes**: Used for idle detection

### POST /api/gpu_health
- **Line**: 599
- **Purpose**: VM reports GPU health metrics
- **Security**: Public (validates hostname exists)
- **Request Body**:
  ```json
  {
    "hostname": "lablink-client-1",
    "gpu_utilization": 85.5,
    "gpu_memory_used": 7890,
    "gpu_temperature": 72
  }
  ```
- **Returns**: Success status
- **Notes**: Stored for monitoring dashboard

### POST /api/vm-status
- **Line**: 617
- **Purpose**: VM updates its status
- **Security**: Public (validates hostname exists)
- **Request Body**:
  ```json
  {
    "hostname": "lablink-client-1",
    "status": "active",
    "uptime": 3600
  }
  ```
- **Returns**: Success status

### POST /api/vm-metrics/<hostname>
- **Line**: 734
- **Purpose**: VM sends performance metrics
- **Security**: Public (validates hostname exists)
- **URL Parameters**: `hostname` (VM identifier)
- **Request Body**:
  ```json
  {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_usage": 35.8
  }
  ```
- **Returns**: Success status
- **Notes**: Stored in database for monitoring

## Category 4: Query API (4 endpoints - Public GET)

These are read-only endpoints for querying VM status and logs.

### GET /api/vm-status
- **Line**: 648
- **Purpose**: Get status of all VMs
- **Security**: Public
- **Returns**:
  ```json
  {
    "vms": [
      {
        "hostname": "lablink-client-1",
        "status": "active",
        "user": "user@example.com"
      }
    ]
  }
  ```

### GET /api/vm-status/<hostname>
- **Line**: 635
- **Purpose**: Get status of specific VM
- **Security**: Public
- **URL Parameters**: `hostname` (VM identifier)
- **Returns**:
  ```json
  {
    "hostname": "lablink-client-1",
    "status": "active",
    "user": "user@example.com",
    "uptime": 3600
  }
  ```

### GET /api/vm-logs/<hostname>
- **Line**: 700
- **Purpose**: Get logs for specific VM
- **Security**: Public
- **URL Parameters**: `hostname` (VM identifier)
- **Returns**:
  ```json
  {
    "logs": [
      {
        "timestamp": "2025-01-15T14:30:00Z",
        "level": "INFO",
        "message": "Application started"
      }
    ]
  }
  ```

### GET /api/unassigned_vms_count
- **Line**: 572
- **Purpose**: Get count of available VMs
- **Security**: Public
- **Returns**:
  ```json
  {
    "count": 5
  }
  ```
- **Notes**: Used by frontend to show availability

## Category 5: Log Shipper Callback (1 endpoint - Bearer token required)

> **Updated 2026-03 (PR #279):** This endpoint was previously called by Lambda (CloudWatch log processor). It is now called by the self-hosted `log_shipper.sh` running on each client VM.

### POST /api/vm-logs
- **Purpose**: Receive batched logs from client VM log shipper
- **Security**: Bearer token required (auto-generated API token)
- **Request Body**:
  ```json
  {
    "hostname": "sleap-lablink-client-prod-1",
    "log_type": "cloudinit",
    "messages": ["log line 1", "log line 2", "..."]
  }
  ```
- **Returns**: Success status
- **Notes**: Called by `log_shipper.sh` (two instances per VM: cloud-init + Docker logs). Batches of 50 lines or 15-second flush intervals.

## Category 6: New Endpoints (Added 2026-03)

### POST /api/schedule-destruction
- **Purpose**: Schedule automated VM destruction at a future time
- **Security**: HTTP Basic Auth or Bearer token
- **Returns**: JSON with schedule details

### GET /api/schedule-destruction
- **Purpose**: List all scheduled destructions
- **Security**: HTTP Basic Auth or Bearer token
- **Returns**: JSON array of scheduled destructions

### DELETE /api/schedule-destruction/<id>
- **Purpose**: Cancel a scheduled destruction
- **Security**: HTTP Basic Auth or Bearer token
- **Returns**: JSON confirmation

### POST /api/reboot-vm
- **Purpose**: Reboot a client VM
- **Security**: HTTP Basic Auth or Bearer token
- **Request Body**: `{"hostname": "..."}`
- **Returns**: JSON with reboot status

### GET /api/reboot-vm/<hostname>
- **Purpose**: Check reboot status for a VM
- **Security**: HTTP Basic Auth or Bearer token
- **Returns**: JSON with reboot status

### GET /admin/scheduled-destruction
- **Purpose**: Admin UI for viewing scheduled destructions
- **Security**: HTTP Basic Auth
- **Returns**: HTML page

## Authentication & Security

### Dual Authentication Model (Updated 2026-03)

LabLink supports two authentication methods, and the `require_auth()` decorator accepts either:

1. **HTTP Basic Auth** — For admin UI access and admin API calls
2. **Bearer Token Auth** — For VM-to-allocator communication and log shipper

### HTTP Basic Auth Implementation

**Authentication flow:**
1. Client sends HTTP request with `Authorization: Basic <base64(username:password)>`
2. Flask-HTTPAuth decorator intercepts request
3. Calls `verify_password(username, password)` function
4. Password verified using bcrypt hashing
5. Request allowed or denied (401 Unauthorized)

### Bearer Token Auth (New)

**Authentication flow:**
1. Allocator generates API token at startup
2. Token passed to client VMs via Terraform variables (`api_token`)
3. Client VMs and log shippers include `Authorization: Bearer <token>` in requests
4. `require_auth()` checks for valid Bearer token if Basic auth fails

**Decorator usage:**
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Check username exists
    # Verify password with bcrypt.checkpw()
    return True or False

@app.route('/admin')
@auth.login_required
def admin_panel():
    # Only accessible with valid credentials
    pass
```

**Protected endpoints:**
- All 10 admin endpoints use `@auth.login_required`
- Credentials stored in environment variables
- Passwords hashed with bcrypt

### Public Endpoint Validation

While 12 endpoints are "public" (no HTTP Basic Auth), they still validate requests:

**Hostname validation** (VM-to-Allocator endpoints):
- Checks hostname exists in `vm_table`
- Returns 404 if VM not found
- Prevents unauthorized VMs from sending data

**CRD code validation** (/api/request_vm):
- Validates CRD command contains `--code=`
- Ensures OAuth code present
- Prevents invalid requests

**VM existence check** (/api/vm-logs from Lambda):
- Validates VM exists before storing logs
- Prevents log spam for non-existent VMs

## Data Flow Patterns

### Pattern 1: User Request Flow
```
User → GET / → Renders form
User → POST /api/request_vm → Database UPDATE → Trigger → pg_notify()
```

### Pattern 2: Admin Provisioning Flow
```
Admin → HTTP Basic Auth → POST /api/launch → Terraform → AWS → New VMs
```

### Pattern 3: VM Startup Flow (Long-Polling)
```
VM boots → POST /vm_startup → BLOCKS (up to 7 days)
User → POST /api/request_vm → Database trigger → pg_notify()
/vm_startup UNBLOCKS → Returns CRD command → VM configures CRD
```

### Pattern 4: VM Monitoring Flow
```
VM → POST /api/gpu_health → Database INSERT
VM → POST /api/vm-metrics → Database INSERT
Admin → GET /admin/logs/<hostname> → Database SELECT → Render page
```

### Pattern 5: Lambda Log Flow
```
VM → CloudWatch Logs → Subscription Filter → Lambda
Lambda → POST /api/vm-logs → Database INSERT
```

## Response Codes

### Success Codes
- **200 OK**: Successful GET/POST
- **201 Created**: Resource created (VM provisioned)
- **204 No Content**: Successful DELETE

### Error Codes
- **400 Bad Request**: Invalid request body or parameters
- **401 Unauthorized**: Missing or invalid HTTP Basic Auth
- **404 Not Found**: VM hostname not found
- **503 Service Unavailable**: No VMs available for assignment

## API Versioning

**Current version**: No versioning (v1 implicit)

**Endpoints with `/api/` prefix**: Modern endpoints (RESTful)
**Endpoints without `/api/`**: Legacy/web interface endpoints

**Future consideration**: Version endpoints as `/api/v2/...` when breaking changes needed

## Rate Limiting

**Current implementation**: None

**Future consideration**:
- Rate limit public endpoints (prevent abuse)
- Rate limit VM endpoints (prevent log spam)
- No rate limit for admin endpoints (trusted users)

## Diagram Representation

The API architecture diagram shows:

1. **Actors**:
   - User (public access)
   - Admin (HTTP Basic Auth)
   - Client VM (hostname validated)
   - Lambda (log processor)

2. **Endpoint clusters**:
   - User Interface (2 endpoints)
   - Admin Management (16 endpoints, authenticated)
   - VM-to-Allocator API (5 endpoints, Bearer token)
   - Query API (4 endpoints, public or auth)
   - Log Shipper Callback (1 endpoint, Bearer token)
   - Scheduled Operations (3 endpoints, authenticated)
   - VM Reboot (2 endpoints, authenticated)

3. **Color coding**:
   - Green: User flows
   - Yellow: Admin operations (authenticated)
   - Red: Destroy operations
   - Blue: VM monitoring/status
   - Purple: Log shipper
   - Gray: Query operations
   - Orange: Scheduled operations

4. **Visual indicators**:
   - IAM icon: HTTP Basic Auth with bcrypt
   - Key icon: Bearer token auth
   - Endpoint labels: HTTP method + path
   - Edge labels: Purpose/data flow
   - Blocking indicator: [BLOCKING 7 days] on /vm_startup

## Key Architectural Insights

### Long-Polling Pattern
- `/vm_startup` uses long-polling (blocks up to 7 days)
- Simpler than WebSockets, works through firewalls
- Uses PostgreSQL LISTEN/NOTIFY internally
- One thread per waiting VM (acceptable for small-scale)

### Separation of Concerns
- User endpoints: Web interface for researchers
- Admin endpoints: Infrastructure management
- VM endpoints: Machine-to-machine status updates
- Query endpoints: Read-only data access
- Lambda endpoints: Asynchronous log processing

### Security Model
- **Admin endpoints**: HTTP Basic Auth (bcrypt)
- **Public endpoints**: Validation-based (hostname, CRD code, VM existence)
- **No API keys**: Simple auth model for small-scale deployment
- **Future**: Could add JWT tokens for API access

### Blocking vs Non-Blocking
- **Blocking**: `/vm_startup` (long-polling)
- **Non-blocking**: All other endpoints (immediate response)

## References

- **Source code**: `lablink/packages/allocator/src/lablink_allocator_service/main.py`
- **Authentication**: Flask-HTTPAuth library with bcrypt
- **Database**: PostgreSQL with LISTEN/NOTIFY
- **Deployment**: Flask development server (future: Gunicorn/uWSGI)

## Related Analysis Documents

- [CRD Workflow Research](./crd-workflow-research.md) - Detailed analysis of the CRD connection workflow
- [CRD Workflow Corrected](./crd-workflow-corrected.md) - Visual representation of corrected CRD workflow

## Diagram Generation

To regenerate the API architecture diagram:

```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type api-architecture \
  --format png \
  --fontsize-preset poster
```

Outputs to: `figures/run_<timestamp>/diagrams/lablink-api-architecture.png`
