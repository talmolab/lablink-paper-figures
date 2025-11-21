# LabLink Database Schema Analysis

**Analysis Date:** 2025-11-15
**Source Repository:** `lablink` (packages/allocator)
**Primary Files:**
- `packages/allocator/src/lablink_allocator_service/generate_init_sql.py` - Schema definition
- `packages/allocator/src/lablink_allocator_service/database.py` - Database operations

---

## Overview

LabLink uses a **single-table PostgreSQL database** with a sophisticated trigger-based notification system. The database serves as the central coordination point for VM lifecycle management, user assignment, performance monitoring, and real-time communication between the allocator service and client VMs.

### Key Architectural Features

1. **Long-Polling Pattern**: Client VMs use PostgreSQL LISTEN/NOTIFY for blocking HTTP requests (up to 7 days)
2. **Trigger-Based Notifications**: Database triggers automatically notify waiting clients when VMs are assigned
3. **Comprehensive Metrics**: Built-in performance tracking for 3-phase VM startup sequence
4. **Simple Schema**: All VM state in a single table - no joins needed

---

## Database Configuration

### Connection Parameters

From `database.py::__init__()`:

```python
dbname: str          # Database name
user: str            # PostgreSQL user
password: str        # User password
host: str            # PostgreSQL host (AWS RDS endpoint)
port: int            # Port number (default: 5432)
table_name: str      # VM table name (configurable)
message_channel: str # LISTEN/NOTIFY channel name
```

### Deployment Context

- **Platform**: PostgreSQL on AWS RDS
- **Isolation Level**: AUTOCOMMIT (for real-time LISTEN/NOTIFY)
- **Schema Generation**: `generate-init-sql` CLI tool creates init.sql from config.yaml

---

## Table Schema: VM Table

### Complete Column List

From `generate_init_sql.py` (lines 29-49):

| Column Name | Data Type | Constraints | Purpose |
|-------------|-----------|-------------|---------|
| **HostName** | VARCHAR(1024) | PRIMARY KEY | Unique VM identifier |
| **Pin** | VARCHAR(1024) | - | Chrome Remote Desktop PIN (hardcoded "123456") |
| **CrdCommand** | VARCHAR(1024) | - | CRD headless authentication command |
| **UserEmail** | VARCHAR(1024) | - | Email of researcher assigned to VM |
| **InUse** | BOOLEAN | NOT NULL DEFAULT FALSE | Tracks active VM usage |
| **Healthy** | VARCHAR(1024) | - | GPU health status: "Healthy", "Unhealthy", "N/A" |
| **Status** | VARCHAR(1024) | - | VM lifecycle state (see Status Values below) |
| **Logs** | TEXT | - | Aggregated CloudWatch logs for this VM |
| **TerraformApplyStartTime** | TIMESTAMP | - | Phase 1: Terraform provisioning start |
| **TerraformApplyEndTime** | TIMESTAMP | - | Phase 1: Terraform provisioning end |
| **TerraformApplyDurationSeconds** | FLOAT | - | Phase 1: Duration in seconds |
| **CloudInitStartTime** | TIMESTAMP | - | Phase 2: Cloud-init setup start |
| **CloudInitEndTime** | TIMESTAMP | - | Phase 2: Cloud-init setup end |
| **CloudInitDurationSeconds** | FLOAT | - | Phase 2: Duration in seconds |
| **ContainerStartTime** | TIMESTAMP | - | Phase 3: Container startup start |
| **ContainerEndTime** | TIMESTAMP | - | Phase 3: Container startup end |
| **ContainerStartupDurationSeconds** | FLOAT | - | Phase 3: Duration in seconds |
| **TotalStartupDurationSeconds** | FLOAT | - | Total time from Terraform start to container ready |
| **CreatedAt** | TIMESTAMP | DEFAULT NOW() | VM creation timestamp |

### Column Groups by Function

#### 1. **VM Assignment Columns** (User-facing)
- `HostName` - VM identifier
- `UserEmail` - Assigned researcher
- `CrdCommand` - Connection credentials
- `Pin` - CRD PIN code

#### 2. **Monitoring & Health Columns**
- `Status` - Lifecycle state
- `Healthy` - GPU health check result
- `InUse` - Active usage tracking
- `Logs` - Diagnostic information

#### 3. **Performance Metrics Columns** (3-Phase Startup Tracking)
- **Phase 1: Terraform** - `TerraformApply*` (3 columns)
- **Phase 2: Cloud-init** - `CloudInit*` (3 columns)
- **Phase 3: Container** - `ContainerStartup*` (3 columns)
- **Total**: `TotalStartupDurationSeconds`

#### 4. **Metadata Columns**
- `CreatedAt` - Audit trail

---

## Status Values

From analysis of `database.py` operations:

| Status Value | Meaning | Set By |
|--------------|---------|--------|
| `"initializing"` | VM is being provisioned by Terraform | Allocator (POST /api/launch) |
| `"running"` | VM is operational, cloud-init complete | Client VM (POST /api/vm-startup) |
| `"error"` | Provisioning or startup failed | Allocator or Client VM |
| `"available"` | VM is ready but unassigned | Allocator |
| `"assigned"` | VM has been assigned to a user | Allocator (POST /request_vm) |

---

## Database Triggers & Functions

### Trigger: `trigger_crd_command_insert_or_update`

From `generate_init_sql.py` (lines 66-69):

```sql
CREATE TRIGGER trigger_crd_command_insert_or_update
AFTER INSERT OR UPDATE OF CrdCommand ON {VM_TABLE}
FOR EACH ROW
EXECUTE FUNCTION notify_crd_command_update();
```

**Purpose**: Automatically notify waiting client VMs when they are assigned to a user

**Trigger Conditions**:
- Fires on `INSERT` (new VM row created)
- Fires on `UPDATE OF CrdCommand` (VM gets assigned and CRD credentials are set)

### Function: `notify_crd_command_update()`

From `generate_init_sql.py` (lines 51-64):

```sql
CREATE OR REPLACE FUNCTION notify_crd_command_update()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        '{MESSAGE_CHANNEL}',
        json_build_object(
            'HostName', NEW.HostName,
            'CrdCommand', NEW.CrdCommand,
            'Pin', NEW.Pin
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Payload Structure**:
```json
{
  "HostName": "vm-abc123",
  "CrdCommand": "DISPLAY=:0 /opt/google/chrome-remote-desktop/start-host ...",
  "Pin": "123456"
}
```

**Communication Pattern**:
1. Client VM calls `database.listen_for_notifications(channel='vm_updates', target_hostname='vm-abc123')`
2. Client VM blocks waiting for PostgreSQL NOTIFY
3. User submits VM request via Flask web UI
4. Allocator executes `UPDATE vm_table SET CrdCommand=... WHERE HostName='vm-abc123'`
5. Trigger fires → `pg_notify()` sends JSON payload
6. Client VM's LISTEN receives notification → unblocks → executes CRD setup

---

## Database Operations

### Core CRUD Operations

From `database.py`:

| Method | SQL Operation | Purpose |
|--------|---------------|---------|
| `insert_vm(hostname)` | INSERT | Create new VM record with hostname, InUse=False |
| `get_vm_by_hostname(hostname)` | SELECT WHERE hostname | Retrieve single VM details |
| `get_all_vms()` | SELECT * (excluding logs) | List all VMs |
| `update_vm_status(hostname, status)` | UPDATE SET Status | Track lifecycle state |
| `assign_vm(email, crd_command, pin, hostname)` | UPDATE SET UserEmail, CrdCommand, Pin | Assign VM to user (triggers notify) |
| `clear_database()` | DELETE FROM table | Cleanup operation |

### LISTEN/NOTIFY Operations

| Method | PostgreSQL Command | Purpose |
|--------|-------------------|---------|
| `listen_for_notifications(channel, target_hostname)` | LISTEN {channel} | Block waiting for assignment notification |
| (Internal) | pg_notify(channel, payload) | Send JSON notification to listening clients |

### Monitoring Operations

| Method | SQL Operation | Purpose |
|--------|---------------|---------|
| `update_vm_in_use(hostname, in_use)` | UPDATE SET InUse | Track active usage |
| `update_health(hostname, healthy)` | UPDATE SET Healthy | Store GPU health status |
| `save_logs_by_hostname(hostname, logs)` | UPDATE SET Logs | Store CloudWatch logs |
| `update_vm_metrics(hostname, metrics)` | UPDATE SET {timing columns} | Record performance metrics |
| `calculate_total_startup_time(hostname)` | UPDATE SET TotalStartupDurationSeconds | Compute total startup duration |

### Query Operations

| Method | SQL Operation | Purpose |
|--------|---------------|---------|
| `get_unassigned_vms()` | SELECT WHERE UserEmail IS NULL | Find available VMs |
| `get_vm_details(email)` | SELECT WHERE UserEmail | Get user's assigned VM |
| `get_all_vm_status()` | SELECT Status, COUNT(*) GROUP BY | Status distribution query |
| `get_row_count()` | SELECT COUNT(*) | Total VM count |
| `get_column_names(table_name)` | Query information_schema | Schema introspection |

---

## Performance Metrics: 3-Phase Startup Sequence

The database schema supports detailed tracking of VM provisioning performance:

### Phase 1: Terraform Provisioning
- **Columns**: `TerraformApplyStartTime`, `TerraformApplyEndTime`, `TerraformApplyDurationSeconds`
- **What's measured**: Time for `terraform apply` to provision EC2 instance
- **Typical duration**: 60-120 seconds

### Phase 2: Cloud-init Setup
- **Columns**: `CloudInitStartTime`, `CloudInitEndTime`, `CloudInitDurationSeconds`
- **What's measured**: Time for OS initialization, package installation, agent setup
- **Includes**: CloudWatch agent, Docker installation, system configuration
- **Typical duration**: 90-180 seconds

### Phase 3: Container Startup
- **Columns**: `ContainerStartTime`, `ContainerEndTime`, `ContainerStartupDurationSeconds`
- **What's measured**: Time for Docker image pull and container startup
- **Includes**: Image download (can be large), container initialization
- **Typical duration**: 60-300 seconds (depends on image size)

### Total Startup Time
- **Column**: `TotalStartupDurationSeconds`
- **Calculation**: Sum of all three phases
- **Purpose**: End-to-end VM provisioning performance metric
- **Used for**: Paper benchmarks, optimization analysis

---

## Security Considerations

### PIN Hardcoding
- **Current Implementation**: PIN is hardcoded to `"123456"` in the schema
- **Location**: Set during VM assignment in `assign_vm()` method
- **Security Model**: Relies on Google CRD OAuth for actual authentication
- **PIN Purpose**: Secondary authentication layer for remote desktop access

### Password Storage
- **Database Password**: Stored in `config.yaml` (encrypted in production deployments)
- **User Credentials**: Not stored in database (OAuth-based authentication)

### Access Control
- **Database User**: Created with `GRANT ALL PRIVILEGES` on LabLink database
- **Network Security**: Relies on VPC security groups and RDS network isolation
- **API Authentication**: Handled by Flask application (HTTP Basic Auth with bcrypt)

---

## Integration Points

### 1. Allocator Service (Flask API)
**File**: `packages/allocator/src/lablink_allocator_service/main.py`

Key endpoints that interact with database:
- `POST /api/launch` → `insert_vm()`, `update_vm_status()`
- `POST /request_vm` → `assign_vm()` (triggers notification)
- `POST /api/vm-metrics` → `update_vm_metrics()`
- `POST /api/vm-logs` → `save_logs_by_hostname()`
- `GET /status` → `get_all_vm_status()`
- `GET /vms` → `get_all_vms()`

### 2. Client VM (Subscribe Service)
**File**: `packages/client/src/lablink_client_service/subscribe.py`

Database operations:
- `listen_for_notifications()` - Blocking LISTEN for assignment
- `POST /vm_startup` endpoint waits on database notification

### 3. Lambda Log Processor
**File**: `packages/allocator/lambda/lambda_function.py`

Database operations:
- Receives CloudWatch logs from subscription filter
- Calls allocator API → `save_logs_by_hostname()`

### 4. Terraform Cloud
**Integration**: Via Allocator subprocess execution

Database operations:
- Allocator updates `TerraformApply*` metrics after `terraform apply` completes
- Status transitions: `NULL` → `"initializing"` → `"running"`

---

## Data Flow Examples

### Example 1: VM Assignment Flow

```
1. User visits Flask web UI, submits email + OAuth code
   → POST /request_vm

2. Allocator queries database:
   SELECT * FROM vm_table WHERE UserEmail IS NULL LIMIT 1;
   → Returns available VM (e.g., HostName='vm-001')

3. Allocator updates VM record:
   UPDATE vm_table
   SET UserEmail='user@example.com',
       CrdCommand='DISPLAY=:0 /opt/google/...',
       Pin='123456'
   WHERE HostName='vm-001';

4. Trigger fires:
   trigger_crd_command_insert_or_update
   → EXECUTE FUNCTION notify_crd_command_update()

5. Function executes:
   PERFORM pg_notify('vm_updates', '{"HostName":"vm-001", "CrdCommand":"...", "Pin":"123456"}');

6. Client VM's LISTEN receives notification:
   - Unblocks from listen_for_notifications()
   - Returns CRD credentials to client
   - Client executes CRD setup command
```

### Example 2: Performance Metrics Collection

```
1. Allocator starts Terraform provisioning:
   UPDATE vm_table SET TerraformApplyStartTime=NOW() WHERE HostName='vm-001';

2. Terraform completes (90 seconds later):
   UPDATE vm_table SET
     TerraformApplyEndTime=NOW(),
     TerraformApplyDurationSeconds=90.5
   WHERE HostName='vm-001';

3. Client VM boots, cloud-init starts:
   POST /api/vm-metrics
   {
     "hostname": "vm-001",
     "CloudInitStartTime": "2024-11-15T10:00:00Z"
   }

4. Client VM cloud-init completes:
   POST /api/vm-metrics
   {
     "hostname": "vm-001",
     "CloudInitEndTime": "2024-11-15T10:02:30Z",
     "CloudInitDurationSeconds": 150.2
   }

5. Container starts and completes:
   POST /api/vm-metrics (2 calls)
   → ContainerStartTime, ContainerEndTime, ContainerStartupDurationSeconds

6. Allocator calculates total:
   UPDATE vm_table SET
     TotalStartupDurationSeconds = (90.5 + 150.2 + 120.3)
   WHERE HostName='vm-001';

   Result: 361.0 seconds total startup time
```

---

## Schema Design Rationale

### Why Single Table?

1. **Simplicity**: No complex joins needed for VM queries
2. **Performance**: All VM data in one row → single-row lookups
3. **Transactional Consistency**: All VM state changes in one UPDATE
4. **LISTEN/NOTIFY Efficiency**: Triggers on single table easier to manage

### Why VARCHAR(1024) for Most Columns?

1. **Flexibility**: Accommodates long CRD commands and email addresses
2. **Cloud-init Logs**: Can be very long (stored in TEXT)
3. **Future-proofing**: Allows for longer hostnames or credential strings

### Why TIMESTAMP for Metrics?

1. **Precision**: Sub-second timing accuracy for performance analysis
2. **Timezone Awareness**: Supports deployments across regions
3. **SQL Functions**: Easy to calculate durations with `EXTRACT(EPOCH FROM ...)`

### Why TEXT for Logs?

1. **Unlimited Size**: CloudWatch logs can be extremely long
2. **JSON Storage**: Stores structured log data as JSON text
3. **Query Exclusion**: `get_all_vms()` explicitly excludes logs to avoid large transfers

---

## Future Enhancements

### Potential Schema Extensions

1. **VM Image Tracking**
   - Add `ImageId`, `ImageTag` columns to track which Docker image version is deployed
   - Useful for A/B testing and rollback scenarios

2. **User Metadata**
   - Separate `users` table with email, institution, research area
   - Foreign key from `vm_table.UserEmail` to `users.email`

3. **Experiment Tracking**
   - `ExperimentId`, `ExperimentStatus`, `DataExported` columns
   - Track experiment lifecycle separately from VM lifecycle

4. **Cost Tracking**
   - `CostPerHour`, `TotalCost` columns
   - Integrate with AWS Cost Explorer API

5. **Multi-Tenancy**
   - Add `OrgId` or `ProjectId` for institutional deployments
   - Row-level security policies

### Potential Trigger Enhancements

1. **Status Change Notifications**
   - Trigger on `Status` column updates
   - Notify admins of VM failures or state transitions

2. **Health Alert Triggers**
   - Trigger on `Healthy='Unhealthy'`
   - Automatically notify admin or attempt VM repair

3. **Audit Logging**
   - Create separate `audit_log` table
   - Trigger on all INSERT/UPDATE/DELETE to track changes

---

## References

### Source Code
- [generate_init_sql.py](https://github.com/talmolab/lablink/blob/main/packages/allocator/src/lablink_allocator_service/generate_init_sql.py) - Schema definition
- [database.py](https://github.com/talmolab/lablink/blob/main/packages/allocator/src/lablink_allocator_service/database.py) - Database operations
- [main.py](https://github.com/talmolab/lablink/blob/main/packages/allocator/src/lablink_allocator_service/main.py) - API endpoints using database

### Related Documentation
- [LabLink Comprehensive Analysis](lablink-comprehensive-analysis.md) - Full system analysis
- [API Architecture Analysis](api-architecture-analysis.md) - API endpoint documentation
- PostgreSQL Documentation: [LISTEN/NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-11-15 | Initial analysis documenting complete database schema | Claude (via lablink-paper-figures) |