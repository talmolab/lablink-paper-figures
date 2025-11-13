# Capability: Architecture Diagrams

## Overview

This capability enables generation of comprehensive architecture diagrams for the LabLink system. The diagrams visualize distinct architectural mechanisms including VM provisioning, database-driven coordination, logging pipelines, monitoring services, and data collection workflows.

## ADDED Requirements

### Requirement: Generate VM provisioning and lifecycle diagram

The system SHALL generate a diagram showing how the allocator dynamically provisions client VMs via embedded Terraform subprocess with 3-phase startup sequence (Terraform → Cloud-init → Container).

#### Scenario: Admin provisions new client VMs
**Given** an allocator server is running with embedded Terraform workspace
**When** admin submits "Create 5 VMs" request via web UI
**Then** the VM provisioning diagram shows:
- Admin → "Create VMs" request → Allocator
- Allocator writes `terraform.runtime.tfvars` configuration file
- Allocator executes `terraform apply` as subprocess
- Terraform provisions EC2 instances in AWS
- Terraform returns timing data (start_time, end_time, duration)
- Allocator stores VM records with timing data in PostgreSQL
- Allocator uploads tfvars backup to S3

**And** diagram shows 3-phase client VM startup:
- Phase 1: Install CloudWatch Agent (status: initializing)
- Phase 2: Configure Docker with GPU/CPU detection
- Phase 3: Pull and launch application container (status: running)

**And** each phase sends timing metrics to `/api/vm-metrics` endpoint

**Code references**:
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::launch()`
- `../lablink/packages/allocator/src/lablink_allocator_service/terraform/main.tf`
- `../lablink/packages/allocator/src/lablink_allocator_service/terraform/user_data.sh`
- `../lablink/packages/client/start.sh`

---

### Requirement: Generate CRD connection setup via PostgreSQL LISTEN/NOTIFY diagram

The system SHALL generate a diagram showing the real-time VM assignment mechanism using PostgreSQL database triggers and LISTEN/NOTIFY pattern for coordinating between allocator and client VMs.

#### Scenario: User requests VM access and receives CRD connection
**Given** multiple client VMs are running and available (useremail IS NULL)
**When** user submits email and Chrome Remote Desktop command via web form
**Then** the CRD connection diagram shows:
- User → Submits (email, CRD command) → Allocator web form
- Allocator validates CRD command contains `--code` parameter
- Allocator queries available VMs from PostgreSQL
- Allocator UPDATEs VM record setting (useremail, crdcommand, pin) values

**And** diagram shows PostgreSQL TRIGGER mechanism:
- TRIGGER `trigger_crd_command_insert_or_update` fires on CrdCommand UPDATE
- TRIGGER calls function `notify_crd_command_update()`
- Function executes `pg_notify('vm_updates', JSON_payload)`
- JSON payload contains {HostName, CrdCommand, Pin}

**And** diagram shows client VM notification handling:
- Client VM `subscribe` service LISTEN-ing on 'vm_updates' channel
- Service receives notification via PostgreSQL connection
- Service parses JSON payload and validates hostname matches
- Service executes CRD start-host command with pin
- Chrome Remote Desktop connects to user's Google account

**And** diagram includes annotations:
- "Blocks up to 7 days waiting for assignment" on client LISTEN operation
- "TRIGGER fires on INSERT OR UPDATE OF CrdCommand" on trigger component
- Payload format example in edge label

**Code references**:
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::submit_vm_details()`
- `../lablink/packages/allocator/src/lablink_allocator_service/database.py::assign_vm()`
- `../lablink/packages/allocator/src/lablink_allocator_service/database.py::listen_for_notifications()`
- `../lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py` (TRIGGER definition)
- `../lablink/packages/client/src/lablink_client_service/subscribe.py`
- `../lablink/packages/client/src/lablink_client_service/connect_crd.py`

---

### Requirement: Generate enhanced logging pipeline diagram

The system SHALL generate a diagram showing the complete logging flow from CloudWatch agent installation on client VMs through Lambda processing to database storage in the allocator.

#### Scenario: Client VM logs are collected and stored centrally
**Given** a client VM is provisioned and cloud-init is executing
**When** VM writes logs to `/var/log/cloud-init-output.log`
**Then** the logging pipeline diagram shows:
- Client VM writes log lines to cloud-init-output.log file
- CloudWatch Agent (installed during Phase 1) tails the log file
- Agent streams logs to CloudWatch Logs service (one stream per VM)
- Stream name format: `lablink-vm-{env}-{index}`

**And** diagram shows log processing:
- CloudWatch Log Subscription Filter matches all logs (pattern="")
- Filter triggers Lambda function `log_processor` for each log batch
- Lambda decompresses gzip and base64-encoded log events
- Lambda extracts {log_group, log_stream, messages[]} from payload
- Lambda constructs JSON payload for allocator

**And** diagram shows callback to allocator:
- Lambda POSTs payload to allocator `/api/vm-logs` endpoint
- Allocator validates VM exists by log_stream (hostname)
- Allocator appends new log messages to existing logs in PostgreSQL
- If VM status is 'initializing' and logs are None, returns 503 error

**And** diagram shows admin access:
- Admin views logs via `/admin/logs/{hostname}` web UI
- Web UI fetches logs from allocator API
- Allocator retrieves logs from PostgreSQL logs column

**And** diagram includes technical annotations:
- "gzip + base64 encoding" at Lambda input boundary
- "Log aggregation: multiple events → single API call"
- "Lambda executes in AWS-managed VPC"

**Code references**:
- `../lablink-template/lablink-infrastructure/lambda_function.py`
- `../lablink-template/lablink-infrastructure/main.tf` (Lambda, subscription filter resources)
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::receive_vm_logs()`
- `../lablink/packages/allocator/src/lablink_allocator_service/database.py::save_logs_by_hostname()`

---

### Requirement: Generate VM status and health monitoring diagram

The system SHALL generate a diagram showing three parallel monitoring services running on each client VM that report status, GPU health, and application usage back to the allocator.

#### Scenario: Client VM monitors and reports health status
**Given** a client VM container is running with monitoring services enabled
**When** monitoring services execute their periodic checks
**Then** the monitoring diagram shows three concurrent sub-flows:

**Sub-flow A: VM Status Updates**
- Client VM POSTs status to `/api/vm-status` endpoint during lifecycle events
- Allocator updates status column in PostgreSQL
- Possible values: initializing, running, error, unknown

**Sub-flow B: GPU Health Monitoring**
- `check_gpu` service runs `nvidia-smi` command every 20 seconds
- If GPU status changes, POSTs to `/api/gpu_health` endpoint
- Allocator updates healthy column in PostgreSQL
- Possible values: Healthy, Unhealthy, N/A
- If nvidia-smi not found, sets "N/A" and exits monitoring loop

**Sub-flow C: Application Usage Tracking**
- `update_inuse_status` service checks process list every 20 seconds
- Determines if SUBJECT_SOFTWARE process is running
- If usage state changes, POSTs to `/api/update_inuse_status` endpoint
- Allocator updates inuse boolean column in PostgreSQL

**And** diagram uses visual encoding to show concurrency:
- Three services displayed in horizontal parallel alignment
- Annotation: "Concurrent Monitoring Services"
- Different colors for each sub-flow

**Code references**:
- `../lablink/packages/client/src/lablink_client_service/check_gpu.py`
- `../lablink/packages/client/src/lablink_client_service/update_inuse_status.py`
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::update_vm_status()`
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::update_gpu_health()`
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::update_inuse_status()`

---

### Requirement: Generate data collection and export diagram

The system SHALL generate a diagram showing how admin retrieves generated data files from all client VMs using SSH, Docker, and rsync operations.

#### Scenario: Admin downloads research data from all VMs
**Given** multiple client VMs have generated data files with specific extension
**When** admin clicks "Download Data" button in web UI
**Then** the data collection diagram shows:
- Admin → "Download Data" request → Allocator `/api/scp-client` endpoint
- Allocator retrieves VM IPs and SSH private key from Terraform outputs

**And** for each VM in parallel:
- Allocator SSH-es into VM using private key
- Allocator runs `docker exec find` command to locate files in container
- Allocator identifies files matching specified extension
- Allocator runs `docker cp` to extract files from container to VM `/tmp/extracted/`
- Allocator runs `rsync -avz` to transfer files from VM to allocator temp directory

**And** diagram shows archive creation:
- Allocator creates zip archive named `lablink_data{timestamp}.zip`
- Allocator sends zip file as HTTP download (as_attachment=True)
- Allocator deletes zip file after request completes (cleanup edge)

**And** diagram includes technical annotations:
- "Parallel processing for all VMs"
- SSH connection notation showing authentication
- Docker boundary showing container vs. VM filesystem
- rsync transfer notation

**Code references**:
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py::download_all_data()`
- `../lablink/packages/allocator/src/lablink_allocator_service/utils/scp.py::find_files_in_container()`
- `../lablink/packages/allocator/src/lablink_allocator_service/utils/scp.py::extract_files_from_docker()`
- `../lablink/packages/allocator/src/lablink_allocator_service/utils/scp.py::rsync_files_to_allocator()`
- `../lablink/packages/allocator/src/lablink_allocator_service/utils/terraform_utils.py::get_instance_ips()`

---

### Requirement: Support multiple diagram generation modes

The system SHALL provide CLI flags to generate essential diagrams (priority 1), supplementary diagrams (priority 2), or individual diagram types.

#### Scenario: Generate all essential diagrams for research paper
**Given** the diagram generation script is available
**When** user runs:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --all-essential \
  --output-dir figures/main \
  --format png \
  --dpi 300
```
**Then** system generates 4 essential diagrams:
1. `lablink-architecture.png` (System Overview - existing)
2. `lablink-vm-provisioning.png` (VM Provisioning & Lifecycle)
3. `lablink-crd-connection.png` (CRD Connection via Database Notification)
4. `lablink-logging-pipeline.png` (Logging Pipeline)

**And** each diagram is 300 DPI PNG suitable for publication

#### Scenario: Generate supplementary diagrams
**Given** the diagram generation script is available
**When** user runs:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --all-supplementary \
  --output-dir figures/supplementary \
  --format png \
  --dpi 300
```
**Then** system generates 2 supplementary diagrams:
1. `lablink-monitoring.png` (VM Status & Health Monitoring)
2. `lablink-data-collection.png` (Data Collection & Export)

#### Scenario: Generate individual diagram type
**Given** the diagram generation script is available
**When** user runs:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type crd-connection \
  --output-dir figures/main \
  --format svg \
  --dpi 300
```
**Then** system generates only `lablink-crd-connection.svg`

**And** script supports diagram types:
- main (existing)
- detailed (existing)
- network-flow (existing)
- vm-provisioning (new)
- crd-connection (new)
- logging-pipeline (new)
- monitoring (new)
- data-collection (new)
- all (generates all 8 diagrams)

---

### Requirement: Maintain consistent visual style across all diagrams

The system SHALL use consistent visual encoding for components, edges, clusters, and annotations across all generated diagrams.

#### Scenario: All diagrams use same visual conventions
**Given** multiple diagrams are generated
**Then** all diagrams use consistent styling:

**Component Icons**:
- AWS EC2: AWS library EC2 icon
- AWS Lambda: AWS library Lambda icon
- AWS CloudWatch: AWS library CloudwatchLogs icon
- PostgreSQL: AWS library RDS icon
- Admin/User: diagrams.onprem.client.User icon
- Same icon used for same logical component across all diagrams

**Cluster Styling**:
- Font size: 32pt for cluster names
- Font family: Helvetica (not bold)
- Background: white
- Border: light gray

**Node Styling**:
- Font size: 11pt for node labels
- Font family: Helvetica
- Consistent spacing: nodesep=0.6, ranksep=0.8

**Edge Styling**:
- Font size: 12pt for edge labels
- Solid edges: Direct API calls, data flow
- Dashed edges: Asynchronous notifications, triggers
- Orange edges: Resource provisioning actions
- Edge labels describe action or data transferred

**Layout**:
- Direction: LR (left-to-right) for all diagrams
- Padding: 0.5 inches
- DPI: 300 for publication quality

**Code reference**:
- `src/diagram_gen/generator.py` - Defines `graph_attr`, `node_attr`, `edge_attr` dictionaries
- These dictionaries shall be reused across all diagram builder methods

---

### Requirement: Generate CI/CD pipeline and GitHub workflows diagram

The system SHALL generate a diagram showing the comprehensive GitHub Actions workflows for continuous integration, testing, building, deployment, and infrastructure destruction.

#### Scenario: Developer creates PR with package changes
**Given** a pull request is created modifying `packages/**` files
**When** GitHub Actions workflows are triggered
**Then** the CI/CD diagram shows:
- PR triggers `ci.yml` workflow:
  - lint job runs ruff check on allocator and client packages
  - test job runs pytest with 90% coverage requirement
  - docker-build-test-allocator job builds and verifies dev image
- PR triggers `lablink-images.yml` workflow:
  - Builds allocator-dev and client-dev Docker images
  - Runs verification tests on built images
  - Tags images with `-test` suffix

#### Scenario: Release is published
**Given** a GitHub release is created with tag `lablink-allocator-service_v1.2.3`
**When** release workflows are triggered
**Then** the CI/CD diagram shows:
- `publish-pip.yml` workflow runs 6 guardrails:
  1. Branch verification (must be main)
  2. Version verification (tag matches pyproject.toml)
  3. Package metadata check
  4. Linting with ruff
  5. Test suite with coverage
  6. Build verification
- After guardrails pass: uv publish to PyPI with OIDC trusted publishing
- `docs.yml` workflow builds versioned documentation

#### Scenario: Deployment to test environment
**Given** code is pushed to test branch or manual deployment is triggered
**When** `terraform-deploy.yml` workflow runs
**Then** the CI/CD diagram shows:
- Configure AWS credentials via OIDC
- Validate config.yaml schema
- Inject secrets from GitHub secrets
- Initialize Terraform with S3 backend
- Import existing CloudWatch log groups
- Apply infrastructure with `terraform apply`
- Verify DNS resolution and service health
- Save SSH key as workflow artifact

#### Scenario: Infrastructure destruction
**Given** admin manually triggers `terraform-destroy.yml` with confirmation="yes"
**When** destruction workflow runs
**Then** the CI/CD diagram shows two-stage teardown:
- Stage 1: Destroy client VMs using S3 state (state-only destroy, no .tf files needed)
- Stage 2: Destroy main infrastructure with `terraform destroy`

**And** diagram includes annotations:
- "OIDC authentication" for AWS access
- "Trusted publishing" for PyPI uploads
- "90% coverage requirement" on test jobs
- "Manual confirmation required" on destroy workflow

**Code references**:
- `../lablink/.github/workflows/ci.yml`
- `../lablink/.github/workflows/lablink-images.yml`
- `../lablink/.github/workflows/publish-pip.yml`
- `../lablink/.github/workflows/docs.yml`
- `../lablink-template/.github/workflows/terraform-deploy.yml`
- `../lablink-template/.github/workflows/terraform-destroy.yml`
- `../lablink-template/.github/workflows/config-validation.yml`

---

### Requirement: Generate API endpoint architecture diagram

The system SHALL generate a comprehensive diagram showing all 22 Flask API endpoints with authentication boundaries, database operations, and external service integrations.

#### Scenario: Map all public endpoints without authentication
**Given** the Flask application defines public API endpoints
**When** generating the API architecture diagram
**Then** diagram shows Public API cluster with 12 endpoints:
- **User Interface**: `/` (GET, home page), `/api/request_vm` (POST, VM allocation), `/api/unassigned_vms_count` (GET)
- **VM Communication**: `/vm_startup` (POST, LISTEN/NOTIFY), `/api/update_inuse_status` (POST), `/api/gpu_health` (POST), `/api/vm-status` (POST/GET), `/api/vm-status/<hostname>` (GET)
- **Logging & Metrics**: `/api/vm-logs` (POST, Lambda callback), `/api/vm-logs/<hostname>` (GET), `/api/vm-metrics/<hostname>` (POST)

**And** each endpoint shows:
- HTTP method (GET/POST)
- Request format (form data, JSON)
- Response format (HTML, JSON)
- Database operations icon (SELECT, UPDATE, INSERT)

#### Scenario: Map all admin endpoints with authentication
**Given** the Flask application defines admin API endpoints with `@auth.login_required` decorator
**When** generating the API architecture diagram
**Then** diagram shows Admin API cluster separated by authentication boundary with 10 endpoints:
- **Admin Dashboard**: `/admin` (GET), `/admin/create` (GET), `/admin/instances` (GET), `/admin/instances/delete` (GET), `/admin/logs/<hostname>` (GET)
- **Admin Operations**: `/api/admin/set-aws-credentials` (POST), `/api/admin/unset-aws-credentials` (POST), `/api/launch` (POST, Terraform apply), `/destroy` (POST, Terraform destroy), `/api/scp-client` (GET, data download)

**And** admin endpoints show additional annotations:
- "HTTP Basic Auth" authentication mechanism
- External service calls: "Terraform subprocess", "SSH/Docker", "AWS SDK"
- Database operations: "Table scan", "Row update", "Table truncate"

#### Scenario: Show endpoint to database operation mapping
**Given** endpoints perform various database operations
**When** generating the API architecture diagram
**Then** diagram shows edges from endpoints to PostgreSQL with operation labels:
- `/api/request_vm` → PostgreSQL: SELECT (get_unassigned_vms), UPDATE (assign_vm)
- `/vm_startup` → PostgreSQL: LISTEN (vm_updates channel)
- `/api/vm-logs` → PostgreSQL: UPDATE (save_logs_by_hostname with text append)
- `/api/launch` → PostgreSQL: UPDATE (update_terraform_timing with batch update)
- `/destroy` → PostgreSQL: DELETE (clear_database, table truncate)

#### Scenario: Show endpoint to external service mapping
**Given** admin endpoints interact with external services
**When** generating the API architecture diagram
**Then** diagram shows edges to external services:
- `/api/launch` → Terraform subprocess: Writes runtime.tfvars, runs `terraform apply`, uploads to S3
- `/destroy` → Terraform subprocess: Runs `terraform destroy`, clears database
- `/api/scp-client` → SSH/Docker: Runs `docker exec find`, `docker cp`, `rsync -avz`
- `/api/admin/set-aws-credentials` → AWS SDK: Validates credentials with boto3

**And** diagram uses color coding:
- Green: User-facing endpoints (home, request_vm)
- Blue: VM-facing endpoints (vm_startup, status, metrics, logs)
- Red: Admin endpoints (dashboard, operations)
- Orange: Lambda-facing endpoints (vm-logs POST)

**Code references**:
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py` (all @app.route decorators)

---

### Requirement: Generate enhanced network flow diagram with ports and protocols

The system SHALL generate an enhanced network flow diagram that includes port numbers, protocols, and data payload specifications for every network communication in the system.

#### Scenario: Show complete user request flow with ports
**Given** external user accesses allocator via web browser
**When** generating enhanced network flow diagram
**Then** diagram shows complete flow with port details:
1. User → DNS Server: Port 53 UDP, DNS query for allocator A record
2. User → ALB/EIP: Port 80/443 TCP (HTTP/HTTPS), GET / or POST /api/request_vm
3. ALB → Allocator EC2 (if ACM SSL): Port 5000 HTTP, proxied requests
4. Caddy → Flask (if Let's Encrypt/CloudFlare SSL): Port 5000 HTTP, proxied requests
5. Flask → PostgreSQL: Port 5432, SQL queries and LISTEN/NOTIFY

**And** diagram shows data payloads:
- User request: `email=user@example.com&crd_command=DISPLAY=...`
- PostgreSQL query: `UPDATE vms SET email=..., crd_command=..., pin=... WHERE hostname=...`
- PostgreSQL notification: `NOTIFY vm_updates, 'lablink-vm-test-1'`

#### Scenario: Show SSL termination strategies with port mappings
**Given** LabLink supports 4 different SSL configurations
**When** generating enhanced network flow diagram
**Then** diagram shows 4 separate SSL strategy annotations:

**Strategy 1 - None (IP-only)**:
- User → Allocator EIP: Port 80 HTTP → Flask port 5000

**Strategy 2 - Let's Encrypt**:
- User → Allocator EIP: Port 443 HTTPS → Caddy SSL termination → Flask port 5000 HTTP
- Caddy obtains certificate via ACME protocol

**Strategy 3 - CloudFlare**:
- User → CloudFlare proxy: Port 443 HTTPS (CloudFlare SSL)
- CloudFlare → Caddy: Port 80 HTTP (no local SSL)
- Caddy → Flask: Port 5000 HTTP

**Strategy 4 - ACM (AWS Certificate Manager)**:
- User → ALB: Port 443 HTTPS (ALB SSL termination with ACM certificate)
- ALB → Flask: Port 5000 HTTP

#### Scenario: Show VM communication flows with protocols
**Given** client VMs communicate with allocator and AWS services
**When** generating enhanced network flow diagram
**Then** diagram shows VM communication details:
- Client VM → Allocator: Port 80/443 HTTP(S), JSON payloads for status updates, metrics, GPU health
- Client VM → CloudWatch: Port 443 HTTPS, CloudWatch Logs API (PutLogEvents), IAM instance profile auth
- Allocator → Client VM: Port 22 SSH, key-based authentication, commands: `docker exec`, `docker cp`, `rsync`

**And** diagram shows CloudWatch → Lambda → Allocator logging flow:
- CloudWatch → Lambda: AWS internal, compressed log events (gzip + base64 encoded)
- Lambda → Allocator: Port 80/443 HTTP(S), POST /api/vm-logs with JSON {log_group, log_stream, messages[]}

#### Scenario: Show Chrome Remote Desktop connectivity
**Given** users connect to VMs via Chrome Remote Desktop
**When** generating enhanced network flow diagram
**Then** diagram shows CRD flow:
- Client VM runs CRD start-host command with Google authorization code
- CRD Protocol: Proprietary Google protocol over WebRTC
- Connection: Peer-to-peer via Google relay servers (not direct VM connection)
- Ports: Managed internally by CRD service, not exposed in security groups

**Code references**:
- `../lablink-template/lablink-infrastructure/main.tf` (security groups with port rules)
- `../lablink-template/lablink-infrastructure/alb.tf` (ALB listeners on ports 80/443)
- `../lablink-template/lablink-infrastructure/user_data.sh` (Caddy setup)

---

## MODIFIED Requirements

None. This change adds new diagram capabilities without modifying existing behavior.

## REMOVED Requirements

None. All existing diagram generation functionality is preserved.

## Non-Functional Requirements

### Performance
- Each diagram shall generate in under 5 seconds on standard hardware
- Parallel diagram generation (e.g., `--all-essential`) shall complete in under 20 seconds

### Quality
- All diagrams shall be 300 DPI minimum for print publication
- PNG file sizes shall be under 2MB per diagram
- SVG diagrams shall be valid and render correctly in web browsers

### Maintainability
- Each diagram builder method shall include docstring with:
  - Purpose statement
  - Component list
  - Flow description
  - Code references with file paths and function names
- Code references shall be validated against actual lablink repository structure

### Usability
- CLI help text shall describe purpose of each diagram type
- Error messages shall guide users if referenced code files are not accessible
- Generated diagram metadata files shall include timestamp and configuration used
