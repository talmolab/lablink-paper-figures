# Expand LabLink Architecture Diagram Suite

## Why

The current architecture diagram (System Overview) shows only the high-level infrastructure flow: Admin → Allocator → Client VMs → CloudWatch → Lambda → Allocator. However, comprehensive codebase analysis reveals **7 additional distinct architectural mechanisms** that are critical to understanding how LabLink works:

1. **VM Provisioning & Lifecycle** - How allocator dynamically provisions VMs via Terraform subprocess with 3-phase startup (Terraform → Cloud-init → Container)
2. **CRD Connection Setup via PostgreSQL LISTEN/NOTIFY** - Unique real-time VM assignment mechanism using database triggers (not shown at all currently)
3. **Logging Pipeline Details** - CloudWatch agent installation, log streaming, Lambda processing, and database storage
4. **VM Status & Health Monitoring** - Three parallel monitoring services (status, GPU health, process usage)
5. **Data Collection & Export** - SSH/Docker-based file retrieval via rsync
6. **Infrastructure Provisioning** - Initial allocator setup via Terraform
7. **VM Teardown & Cleanup** - Infrastructure destruction workflow

**Problem**: Research paper readers cannot understand the complete LabLink architecture from a single diagram. Key innovations like the PostgreSQL LISTEN/NOTIFY pattern for real-time coordination are completely absent.

**Evidence from codebase**:
- `../lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py` - Defines PostgreSQL TRIGGER that fires `pg_notify()` on CRD command updates
- `../lablink/packages/client/src/lablink_client_service/subscribe.py` - Client VMs LISTEN on database channel for assignments
- `../lablink/packages/allocator/src/lablink_allocator_service/main.py` - `/api/launch` endpoint runs Terraform as subprocess, `/vm_startup` uses `listen_for_notifications()`
- `../lablink/packages/client/start.sh` - Shows 3-phase startup with timing metrics sent back to allocator
- `../lablink/packages/client/src/lablink_client_service/check_gpu.py`, `update_inuse_status.py` - Parallel monitoring services

## What Changes

### New Diagram Types (Priority 1 - Essential for Paper)

**Diagram 2: VM Provisioning & Lifecycle**
- **Purpose**: Show how allocator dynamically creates VMs via embedded Terraform and the 3-phase startup sequence
- **Components**: Admin Web UI, Allocator, Terraform subprocess, PostgreSQL, AWS EC2, S3
- **Key flows**:
  1. Admin → "Create VMs" → Allocator writes `terraform.runtime.tfvars` → `terraform apply` subprocess
  2. Terraform provisions EC2 instances → returns timing data → stored in PostgreSQL
  3. Client VM executes user_data.sh with 3 phases:
     - Phase 1: Install CloudWatch Agent (status: initializing)
     - Phase 2: Configure Docker (GPU/CPU detection)
     - Phase 3: Pull & launch container (status: running)
  4. Each phase sends timing metrics to `/api/vm-metrics` endpoint
- **Code references**: `main.py::launch()`, `terraform/main.tf`, `user_data.sh`, `start.sh`

**Diagram 3: CRD Connection Setup via Database Notification** ⭐ **Unique mechanism**
- **Purpose**: Explain the PostgreSQL LISTEN/NOTIFY pattern for real-time VM-to-user assignment
- **Components**: User (browser), Allocator web form, PostgreSQL (with TRIGGER), Client VM (subscribe service), Chrome Remote Desktop
- **Key flows**:
  1. User submits email + CRD command → Allocator validates
  2. Allocator queries available VMs (WHERE useremail IS NULL)
  3. Allocator UPDATEs VM record (SET useremail, crdcommand, pin)
  4. PostgreSQL TRIGGER fires → `notify_crd_command_update()` → `pg_notify('vm_updates', JSON)`
  5. Client VM subscribe service (LISTEN 'vm_updates') receives notification
  6. Client VM parses payload, validates hostname, executes CRD start-host command
  7. Chrome Remote Desktop connects to user's Google account
- **Highlight**: TRIGGER as architectural innovation, long-polling pattern (7-day timeout), blocking wait on allocator side
- **Code references**: `submit_vm_details()`, `assign_vm()`, `listen_for_notifications()`, `subscribe.py`, `connect_crd.py`, `generate_init_sql.py`

**Diagram 4: Logging Pipeline (CloudWatch → Lambda → Allocator)** - Enhanced version
- **Purpose**: Show complete logging flow from agent installation to database storage
- **Components**: Client VM (cloud-init-output.log), CloudWatch Agent, CloudWatch Logs, Subscription Filter, Lambda, Allocator API, PostgreSQL
- **Key flows**:
  1. Client VM cloud-init writes to `/var/log/cloud-init-output.log`
  2. CloudWatch Agent tails file → streams to CloudWatch Logs (one log stream per VM)
  3. Subscription Filter (pattern="") triggers Lambda for each batch
  4. Lambda decompresses gzip/base64 data → extracts messages
  5. Lambda POSTs to `/api/vm-logs` with payload {log_group, log_stream, messages}
  6. Allocator validates VM exists → appends logs to PostgreSQL logs column
  7. Admin views via `/admin/logs/{hostname}` web UI
- **Annotations**: Show gzip encoding, log aggregation, 503 error during agent installation
- **Code references**: `lambda_function.py`, `receive_vm_logs()`, `save_logs_by_hostname()`

### New Diagram Types (Priority 2 - Supplementary)

**Diagram 5: CI/CD Pipeline & GitHub Workflows**
- **Purpose**: Show comprehensive GitHub Actions workflows for testing, building, deploying, and destroying infrastructure
- **Components**: GitHub Actions, PyPI, GHCR, AWS (OIDC, S3, DynamoDB), Terraform
- **Key flows**:
  1. **Development Flow**: PR → ci.yml (lint + test) + lablink-images.yml (build dev images) + verification
  2. **Release Flow**: Git tag → publish-pip.yml (6 guardrails) → PyPI publication → docs deployment
  3. **Deployment Flow**: Push to test branch or manual dispatch → terraform-deploy.yml (validate, inject secrets, apply, verify) → Save SSH key artifact
  4. **Destruction Flow**: Manual confirmation → terraform-destroy.yml (destroy client VMs from S3 state + destroy infrastructure)
- **Workflow dependencies**: Show job sequences and dependencies within each workflow
- **Annotations**: Highlight OIDC authentication, trusted publishing, coverage requirements (90%), verification steps
- **Code references**: `.github/workflows/*.yml` in lablink and lablink-template repos

**Diagram 6: API Endpoint Architecture**
- **Purpose**: Comprehensive map of all 22 Flask API endpoints showing authentication boundaries, database operations, and external service integrations
- **Components**:
  - External Users (browsers)
  - Public API cluster (12 endpoints, no auth)
  - Admin API cluster (10 endpoints, basic auth)
  - PostgreSQL Database
  - External Services (AWS via subprocess, SSH/Docker, Terraform)
- **Key endpoint groups**:
  - **User Interface**: `/` (home), `/api/request_vm` (VM allocation), `/api/unassigned_vms_count`
  - **VM Communication**: `/vm_startup` (LISTEN/NOTIFY), `/api/update_inuse_status`, `/api/gpu_health`, `/api/vm-status`
  - **Logging**: `/api/vm-logs` (Lambda callback), `/api/vm-logs/<hostname>` (retrieve), `/api/vm-metrics/<hostname>`
  - **Admin Dashboard**: `/admin`, `/admin/create`, `/admin/instances`, `/admin/instances/delete`, `/admin/logs/<hostname>`
  - **Admin Operations**: `/api/admin/set-aws-credentials`, `/api/launch` (Terraform apply), `/destroy` (Terraform destroy), `/api/scp-client` (data download)
- **Visual encoding**:
  - Authentication boundary line separating public from admin endpoints
  - Color coding: User-facing (green), VM-facing (blue), Admin (red), Lambda-facing (orange)
  - Database operation icons per endpoint
  - External service call annotations (Terraform subprocess, SSH, AWS SDK)
- **Code references**: `main.py` (all @app.route decorators)

**Diagram 7: Enhanced Network Flow with Ports & Protocols**
- **Purpose**: Enhanced version of existing network-flow diagram with complete port numbers, protocols, and data payloads at each step
- **Components**: External User, DNS (port 53), ALB/EIP (80/443), Caddy Proxy (optional), Allocator Flask (5000), RDS PostgreSQL (5432), Client VMs (22), CloudWatch (443), Lambda, Chrome Remote Desktop
- **Enhanced details per flow**:
  1. **User → DNS**: Port 53 UDP, Query: A record for allocator FQDN
  2. **User → ALB/EIP**: Ports 80/443 TCP, HTTP GET / or POST /api/request_vm with form data (email, crd_command)
  3. **ALB → Allocator** (ACM SSL only): Port 5000 HTTP, proxied requests
  4. **Caddy → Allocator** (Let's Encrypt/CloudFlare SSL): Port 5000 HTTP, proxied requests
  5. **Allocator → PostgreSQL**: Port 5432, SQL queries (SELECT, UPDATE, INSERT) + LISTEN/NOTIFY messages
  6. **Allocator → Client VMs**: Port 22 SSH, commands: `docker exec find`, `docker cp`, `rsync -avz`
  7. **Client VMs → Allocator**: Port 80/443 HTTP(S), JSON payloads: POST /api/update_inuse_status, POST /api/gpu_health, POST /api/vm-metrics
  8. **Client VMs → CloudWatch**: Port 443 HTTPS, CloudWatch Logs API PutLogEvents, log stream per VM
  9. **CloudWatch → Lambda**: AWS internal, compressed log events (gzip + base64 encoded)
  10. **Lambda → Allocator**: Port 80/443 HTTP(S), JSON: POST /api/vm-logs with {log_group, log_stream, messages[]}
  11. **Client VM → Chrome Remote Desktop**: CRD ports (managed by service), proprietary Google protocol over WebRTC, P2P via relay
- **SSL Strategy Annotations**: Show 4 different SSL configurations:
  - None: Direct HTTP port 80 → 5000
  - Let's Encrypt: HTTPS 443 → Caddy SSL termination → HTTP 5000
  - CloudFlare: HTTPS 443 → CloudFlare proxy → Caddy HTTP 80 → 5000
  - ACM: HTTPS 443 → ALB SSL termination → HTTP 5000
- **Protocol details**: HTTP/HTTPS, SSH (key-based auth), PostgreSQL (connection string), CloudWatch API (IAM auth), CRD (WebRTC)
- **Code references**: `main.tf` (security groups, ALB listeners), `alb.tf`, `user_data.sh` (Caddy setup)

**Diagram 8: VM Status & Health Monitoring**
- **Purpose**: Show three parallel monitoring services on each client VM
- **Components**: Client VM container, three background services, Allocator API, PostgreSQL
- **Key flows** (3 concurrent):
  - Sub-flow A: VM status updates (initializing/running/error) → `/api/vm-status`
  - Sub-flow B: GPU health (check_gpu runs nvidia-smi every 20s) → `/api/gpu_health`
  - Sub-flow C: Application usage (monitors process list every 20s) → `/api/update_inuse_status`
- **Code references**: `check_gpu.py`, `update_inuse_status.py`, `main.py` (multiple endpoints)

**Diagram 9: Data Collection & Export**
- **Purpose**: Show how admin retrieves generated files from client VMs
- **Components**: Admin UI, Allocator (SSH client), Client VMs (Docker containers), temp filesystem, zip archive
- **Key flows**:
  1. Admin clicks "Download Data" → `/api/scp-client`
  2. For each VM (parallel): SSH → docker exec find → docker cp → rsync to allocator
  3. Create zip archive → HTTP download → cleanup
- **Code references**: `download_all_data()`, `scp.py`, `terraform_utils.py`

### Generator Code Changes

**Modified**: `src/diagram_gen/generator.py`
- Add new methods:
  - `build_vm_provisioning_diagram()` - Shows Terraform subprocess and 3-phase startup
  - `build_crd_connection_diagram()` - Shows PostgreSQL LISTEN/NOTIFY flow with TRIGGER
  - `build_logging_pipeline_diagram()` - Enhanced version with agent installation and database storage
  - `build_monitoring_diagram()` - Shows parallel monitoring services
  - `build_data_collection_diagram()` - Shows SSH/Docker/rsync flow
- Enhance `build_main_diagram()` - Keep current simplified version as is
- Add utility methods:
  - `_create_database_with_trigger()` - Visual representation of PostgreSQL TRIGGER
  - `_create_parallel_flows()` - Show concurrent monitoring services
  - `_create_subprocess_notation()` - Show Terraform as embedded subprocess

**Modified**: `scripts/plotting/generate_architecture_diagram.py`
- Add diagram type options: `vm-provisioning`, `crd-connection`, `logging-pipeline`, `monitoring`, `data-collection`
- Add `--all-essential` flag to generate priority 1 diagrams
- Add `--all-supplementary` flag for priority 2 diagrams
- Update help text with descriptions of each diagram type

### New Files

- `figures/main/lablink-vm-provisioning.png` - VM provisioning & lifecycle diagram
- `figures/main/lablink-crd-connection.png` - Database notification diagram
- `figures/main/lablink-logging-pipeline.png` - Enhanced logging flow
- `figures/supplementary/lablink-monitoring.png` - Monitoring services diagram
- `figures/supplementary/lablink-data-collection.png` - Data export diagram
- `analysis/lablink-architecture-analysis.md` - Comprehensive mechanism documentation (already created by Plan agent)

### Updated Files

- `README.md` - Add section explaining each diagram type and when to use which
- `tests/test_diagram_generation.py` - Add tests for new diagram types
- `openspec/changes/expand-diagram-suite/DESIGN.md` - Architectural reasoning for diagram choices

## Impact

### Affected Components
- **Modified**: `src/diagram_gen/generator.py` - Add 5 new diagram builder methods (~400 lines)
- **Modified**: `scripts/plotting/generate_architecture_diagram.py` - Add new diagram types and flags (~50 lines)
- **Modified**: `tests/test_diagram_generation.py` - Test new diagrams (~100 lines)
- **New**: 5 diagram PNG files (main: 3, supplementary: 2)
- **New**: Analysis documentation (already exists)
- **Modified**: `README.md` - Documentation updates

### External Dependencies
- **Requires**: Access to `../lablink` codebase for code references and validation
- **Diagrams library**: May need additional icons (User icon for single admin, database with trigger notation)
- **No new Python dependencies**: Uses existing diagrams, graphviz packages

### Breaking Changes
- **None**: All changes are additive. Existing `main` diagram type still works exactly as before.

### User-Visible Changes
- Users can now generate 6 diagram types instead of 3
- New CLI flags: `--all-essential`, `--all-supplementary`
- Each diagram clearly shows one architectural mechanism (easier to understand)
- PostgreSQL LISTEN/NOTIFY pattern now documented and visualized

### Paper Impact
- **Essential diagrams** (must include in paper): 4 diagrams total
  1. System Overview (existing, improved)
  2. VM Provisioning & Lifecycle (new)
  3. CRD Connection via Database Notification (new) ⭐ Unique innovation
  4. Logging Pipeline (enhanced)
- **Supplementary diagrams** (include if space permits): 5 diagrams
  5. CI/CD Pipeline & GitHub Workflows (new) - Shows testing, deployment, destruction workflows
  6. API Endpoint Architecture (new) - Complete catalog of 22 endpoints with auth boundaries
  7. Enhanced Network Flow with Ports & Protocols (enhanced) - Replaces existing network-flow diagram
  8. VM Status & Health Monitoring (new)
  9. Data Collection & Export (new)

### Documentation
- Analysis document explains all 8 mechanisms discovered in codebase
- Each diagram has clear purpose, components, flows, and code references
- README provides guidance on which diagrams to use for different audiences

## Risk Assessment

### Low Risk
- All changes are additive (no modifications to existing working diagrams)
- Well-defined scope based on actual codebase analysis
- Each diagram shows distinct mechanism (minimal overlap)

### Medium Risk
- Diagram complexity: CRD connection diagram shows database TRIGGER which may require custom notation
- Code references: Need to ensure all referenced files actually exist in lablink repo
- Testing: Need to validate that flows match actual code behavior

### Mitigation
- Start with highest priority diagrams (2, 3, 4)
- Review each diagram with codebase maintainers
- Add explicit validation tests that check code references
- Create draft versions before finalizing high-DPI versions

## Success Criteria

1. ✅ Generate Diagram 2 (VM Provisioning) showing Terraform subprocess and 3-phase startup
2. ✅ Generate Diagram 3 (CRD Connection) showing PostgreSQL LISTEN/NOTIFY with TRIGGER
3. ✅ Generate Diagram 4 (Logging Pipeline) with CloudWatch agent and database storage
4. ✅ All diagrams validate against actual codebase (code references exist and match behavior)
5. ✅ Tests pass for all new diagram types
6. ✅ README documents when to use each diagram type
7. ✅ Paper includes 4-6 diagrams that tell complete LabLink story

## Alternatives Considered

### Alternative 1: Single comprehensive diagram with everything
- **Rejected**: Too cluttered, impossible to understand
- **Why**: Current simplified overview already at limit of complexity

### Alternative 2: Sequence diagrams instead of architecture diagrams
- **Rejected**: Sequence diagrams better for timing, not for showing components
- **Why**: Architecture diagrams better show system structure and relationships

### Alternative 3: Just add more detail to existing diagrams
- **Rejected**: Mechanisms are orthogonal, each deserves focused diagram
- **Why**: VM provisioning ≠ CRD connection ≠ logging ≠ monitoring

## Dependencies

### Upstream
- Requires `add-architecture-diagram` change to be completed first (provides base generator infrastructure)

### Downstream
- None: This is a leaf change (adds diagrams, doesn't affect other components)

## Timeline Estimate

- **Phase 1** (Essential diagrams): 1-2 days
  - Day 1: Implement Diagram 2 (VM Provisioning) and tests
  - Day 2: Implement Diagrams 3 (CRD) and 4 (Logging) and tests
- **Phase 2** (Supplementary diagrams): 1.5-2 days
  - Day 1: Implement Diagram 5 (CI/CD Workflows) and Diagram 6 (API Architecture) and tests
  - Day 2: Implement Diagram 7 (Enhanced Network Flow) and Diagrams 8-9 (Monitoring, Data Collection) and tests
- **Phase 3** (Documentation & validation): 0.5-1 day
  - Update README with all 9 diagrams, validate code references, final testing

**Total**: 3-5 days (increased from original estimate due to 3 additional complex diagrams)

## Notes

- Analysis document at `analysis/lablink-architecture-analysis.md` provides detailed specifications for each diagram
- All diagrams grounded in actual code behavior (not theoretical)
- Focus on pedagogical value: each diagram teaches one clear concept
- PostgreSQL LISTEN/NOTIFY pattern is architecturally unique and should be highlighted in paper
