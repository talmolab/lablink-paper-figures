# Tasks: Expand LabLink Architecture Diagram Suite

## Phase 1: Foundation & Setup ✅

- [x] 1.1 Create OpenSpec change proposal structure
- [x] 1.2 Write comprehensive proposal.md with rationale and impact analysis
- [x] 1.3 Write design.md with architectural decisions and trade-offs
- [x] 1.4 Write tasks.md (this file)
- [x] 1.5 Create specs/architecture-diagrams/spec.md with ADDED requirements and scenarios
- [x] 1.6 Validate proposal with `openspec validate expand-diagram-suite --strict` - PASSED ✅

## Phase 2: Generator Infrastructure

- [ ] 2.1 Add stub methods to `src/diagram_gen/generator.py`:
  - [ ] 2.1.1 Add `build_vm_provisioning_diagram()` method signature with docstring
  - [ ] 2.1.2 Add `build_crd_connection_diagram()` method signature with docstring
  - [ ] 2.1.3 Add `build_logging_pipeline_diagram()` method signature with docstring
  - [ ] 2.1.4 Add `build_monitoring_diagram()` method signature with docstring
  - [ ] 2.1.5 Add `build_data_collection_diagram()` method signature with docstring

- [ ] 2.2 Add utility methods for complex components:
  - [ ] 2.2.1 Implement `_create_database_with_trigger()` - Returns (vm_table, trigger, notify_func) components
  - [ ] 2.2.2 Implement `_create_terraform_subprocess()` - Shows Terraform inside Allocator with nested notation
  - [ ] 2.2.3 Implement `_create_three_phase_startup()` - Returns (phase1, phase2, phase3) with timing annotations
  - [ ] 2.2.4 Implement `_create_parallel_monitoring_flows()` - Returns list of 3 concurrent service flows

- [ ] 2.3 Update CLI script `scripts/plotting/generate_architecture_diagram.py`:
  - [ ] 2.3.1 Add new diagram type options to argparse: vm-provisioning, crd-connection, logging-pipeline, monitoring, data-collection
  - [ ] 2.3.2 Add `--all-essential` flag that generates [main, vm-provisioning, crd-connection, logging-pipeline]
  - [ ] 2.3.3 Add `--all-supplementary` flag that generates [monitoring, data-collection]
  - [ ] 2.3.4 Update help text with description of each diagram type
  - [ ] 2.3.5 Add conditional logic to call appropriate builder method based on diagram type

## Phase 3: Priority 1 Diagrams (Essential)

### 3.1 VM Provisioning & Lifecycle Diagram

- [ ] 3.1.1 Implement `build_vm_provisioning_diagram()` core structure:
  - [ ] Create Admin Web UI component
  - [ ] Create Allocator Server component
  - [ ] Create Terraform subprocess notation inside Allocator
  - [ ] Create PostgreSQL Database cluster
  - [ ] Create AWS EC2 Client VMs cluster
  - [ ] Create S3 Bucket component

- [ ] 3.1.2 Add provisioning flow edges:
  - [ ] Admin → "Create VMs" request → Allocator
  - [ ] Allocator → Writes runtime.tfvars → Filesystem
  - [ ] Allocator → terraform apply subprocess → Terraform
  - [ ] Terraform → Provisions → AWS EC2
  - [ ] Terraform → Returns timing data → Allocator
  - [ ] Allocator → Stores VM records → PostgreSQL
  - [ ] Allocator → Uploads tfvars → S3

- [ ] 3.1.3 Add 3-phase startup sequence:
  - [ ] Create Phase 1 annotation: "Install CloudWatch Agent"
  - [ ] Create Phase 2 annotation: "Configure Docker (GPU/CPU)"
  - [ ] Create Phase 3 annotation: "Pull & Launch Container"
  - [ ] Add status transition labels: initializing → running
  - [ ] Add timing metrics edges to `/api/vm-metrics`

- [ ] 3.1.4 Add code reference comments in docstring
- [ ] 3.1.5 Test diagram generation: `pytest tests/test_diagram_generation.py::test_vm_provisioning_diagram`
- [ ] 3.1.6 Generate high-DPI version: `--dpi 300 --format png`
- [ ] 3.1.7 Visual inspection for clarity and accuracy

### 3.2 CRD Connection via Database Notification Diagram ⭐

- [ ] 3.2.1 Implement `build_crd_connection_diagram()` core structure:
  - [ ] Create User (external) component with single user icon
  - [ ] Create Allocator Web Form component
  - [ ] Create PostgreSQL Database cluster with special trigger notation
  - [ ] Create Client VM Container with subscribe service
  - [ ] Create Chrome Remote Desktop component

- [ ] 3.2.2 Add database TRIGGER components:
  - [ ] Create VM Table icon inside PostgreSQL cluster
  - [ ] Create TRIGGER component with special notation/icon
  - [ ] Create pg_notify() function component
  - [ ] VM Table → UPDATE → TRIGGER edge
  - [ ] TRIGGER → Fires → pg_notify() edge
  - [ ] pg_notify() → Notification (dashed edge) → subscribe service

- [ ] 3.2.3 Add user request flow edges:
  - [ ] User → Submits email + CRD command → Allocator web form
  - [ ] Allocator → Validates CRD command → Decision node
  - [ ] Allocator → Queries available VMs (WHERE useremail IS NULL) → PostgreSQL
  - [ ] Allocator → UPDATE VM record (SET useremail, crdcommand, pin) → PostgreSQL

- [ ] 3.2.4 Add CRD connection flow edges:
  - [ ] Client VM subscribe → LISTEN 'vm_updates' → PostgreSQL
  - [ ] Subscribe → Receives notification → Validates hostname
  - [ ] Subscribe → Executes CRD start-host command → Chrome Remote Desktop
  - [ ] Chrome Remote Desktop → Connects to Google account → User access

- [ ] 3.2.5 Add special annotations:
  - [ ] Highlight TRIGGER as "Key architectural mechanism"
  - [ ] Add long-polling annotation: "Blocks up to 7 days waiting for assignment"
  - [ ] Add payload format example in edge label: {HostName, CrdCommand, Pin}

- [ ] 3.2.6 Add code reference comments with specific line numbers
- [ ] 3.2.7 Validate code references exist:
  - [ ] Check `../lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py` exists
  - [ ] Verify TRIGGER definition present in SQL template
  - [ ] Check `../lablink/packages/client/src/lablink_client_service/subscribe.py` exists
  - [ ] Verify LISTEN command present
- [ ] 3.2.8 Test diagram generation
- [ ] 3.2.9 Generate high-DPI version
- [ ] 3.2.10 Visual inspection - ensure TRIGGER notation is clear

### 3.3 Logging Pipeline Diagram (Enhanced)

- [ ] 3.3.1 Implement `build_logging_pipeline_diagram()` core structure:
  - [ ] Create Client VM with cloud-init-output.log file notation
  - [ ] Create CloudWatch Agent component
  - [ ] Create CloudWatch Logs cluster (log group + stream)
  - [ ] Create Log Subscription Filter component
  - [ ] Create Lambda Function component
  - [ ] Create Allocator API component
  - [ ] Create PostgreSQL Database component

- [ ] 3.3.2 Add log collection flow edges:
  - [ ] Client VM → Writes logs → /var/log/cloud-init-output.log
  - [ ] CloudWatch Agent → Tails file → Streams to CloudWatch Logs
  - [ ] Add annotation: "One log stream per VM: lablink-vm-{env}-{index}"

- [ ] 3.3.3 Add log processing flow edges:
  - [ ] Log Subscription Filter → Matches all logs (pattern="") → Triggers Lambda
  - [ ] Lambda → Decompresses gzip/base64 data → Extracts messages
  - [ ] Add annotation showing payload format: {log_group, log_stream, messages[]}

- [ ] 3.3.4 Add callback flow edges:
  - [ ] Lambda → POST payload → Allocator /api/vm-logs endpoint
  - [ ] Allocator → Validates VM exists → Decision node
  - [ ] Allocator → Appends logs → PostgreSQL logs column
  - [ ] Add error annotation: "Returns 503 if status='initializing' (agent installing)"

- [ ] 3.3.5 Add admin access flow:
  - [ ] Admin → Views logs → Web UI /admin/logs/{hostname}
  - [ ] Web UI → Fetches logs → Allocator API
  - [ ] Allocator API → Retrieves logs → PostgreSQL

- [ ] 3.3.6 Add technical annotations:
  - [ ] Show gzip encoding at Lambda boundary
  - [ ] Show log aggregation (multiple events → single API call)
  - [ ] Note Lambda executes in AWS-managed VPC

- [ ] 3.3.7 Add code reference comments
- [ ] 3.3.8 Test diagram generation
- [ ] 3.3.9 Generate high-DPI version
- [ ] 3.3.10 Visual inspection

## Phase 4: Priority 2 Diagrams (Supplementary)

### 4.1 VM Status & Health Monitoring Diagram

- [ ] 4.1.1 Implement `build_monitoring_diagram()` core structure:
  - [ ] Create Client VM Container cluster
  - [ ] Create three background service components (subscribe, update_inuse_status, check_gpu)
  - [ ] Create Allocator API cluster with multiple endpoints
  - [ ] Create PostgreSQL Database component

- [ ] 4.1.2 Add Sub-flow A: Status Updates (parallel flow 1):
  - [ ] VM → POST /api/vm-status → Allocator
  - [ ] Allocator → Updates status column → PostgreSQL
  - [ ] Add annotation: "Values: initializing, running, error, unknown"

- [ ] 4.1.3 Add Sub-flow B: GPU Health (parallel flow 2):
  - [ ] check_gpu service → Runs nvidia-smi every 20s → Decision node
  - [ ] If status changes → POST /api/gpu_health → Allocator
  - [ ] Allocator → Updates healthy column → PostgreSQL
  - [ ] Add annotation: "Values: Healthy, Unhealthy, N/A"

- [ ] 4.1.4 Add Sub-flow C: Application Usage (parallel flow 3):
  - [ ] update_inuse_status → Monitors process list every 20s → Decision node
  - [ ] Checks if SUBJECT_SOFTWARE process exists → Boolean
  - [ ] If state changes → POST /api/update_inuse_status → Allocator
  - [ ] Allocator → Updates inuse boolean → PostgreSQL

- [ ] 4.1.5 Add visual indication of concurrency:
  - [ ] Use horizontal alignment for three parallel flows
  - [ ] Add "Concurrent Monitoring Services" annotation
  - [ ] Use different colors for each sub-flow to distinguish

- [ ] 4.1.6 Add code reference comments
- [ ] 4.1.7 Test diagram generation
- [ ] 4.1.8 Generate high-DPI version
- [ ] 4.1.9 Visual inspection

### 4.2 Data Collection & Export Diagram

- [ ] 4.2.1 Implement `build_data_collection_diagram()` core structure:
  - [ ] Create Admin Web UI component
  - [ ] Create Allocator Server (with SSH client notation)
  - [ ] Create Client VMs cluster (with Docker containers)
  - [ ] Create Temporary Filesystem component
  - [ ] Create Zip Archive component

- [ ] 4.2.2 Add data collection flow edges:
  - [ ] Admin → Clicks "Download Data" → Allocator /api/scp-client
  - [ ] Allocator → Gets VM IPs + SSH key → Terraform outputs

- [ ] 4.2.3 Add per-VM processing (show as loop or parallel):
  - [ ] Allocator → SSH to VM → Runs docker exec find command
  - [ ] Allocator → Identifies files with extension → Returns file list
  - [ ] Allocator → docker cp files → VM /tmp/extracted/
  - [ ] Allocator → rsync files → Allocator temp directory
  - [ ] Add annotation: "Parallel processing for all VMs"

- [ ] 4.2.4 Add archive creation flow:
  - [ ] Allocator → Creates zip archive → lablink_data{timestamp}.zip
  - [ ] Allocator → Sends as HTTP download → Admin browser
  - [ ] Allocator → Deletes zip file → Cleanup (dashed edge showing cleanup)

- [ ] 4.2.5 Add technical annotations:
  - [ ] Show SSH connection notation
  - [ ] Show Docker boundary between container and VM
  - [ ] Show rsync transfer

- [ ] 4.2.6 Add code reference comments
- [ ] 4.2.7 Test diagram generation
- [ ] 4.2.8 Generate high-DPI version
- [ ] 4.2.9 Visual inspection

## Phase 5: Testing & Validation

### 5.1 Unit Tests

- [ ] 5.1.1 Create `tests/test_diagram_generation.py` test cases:
  - [ ] `test_vm_provisioning_diagram_generation()` - Verify file created
  - [ ] `test_crd_connection_diagram_generation()` - Verify file created
  - [ ] `test_logging_pipeline_diagram_generation()` - Verify file created
  - [ ] `test_monitoring_diagram_generation()` - Verify file created
  - [ ] `test_data_collection_diagram_generation()` - Verify file created

- [ ] 5.1.2 Create code reference validation tests:
  - [ ] `test_crd_diagram_code_references()` - Validate TRIGGER in SQL, LISTEN in subscribe.py
  - [ ] `test_provisioning_diagram_code_references()` - Validate launch() endpoint, terraform files
  - [ ] `test_logging_diagram_code_references()` - Validate lambda_function.py, receive_vm_logs()
  - [ ] `test_monitoring_diagram_code_references()` - Validate check_gpu.py, update_inuse_status.py
  - [ ] `test_data_collection_diagram_code_references()` - Validate scp.py utilities

### 5.2 Integration Tests

- [ ] 5.2.1 Test CLI with new diagram types:
  - [ ] Test `--diagram-type vm-provisioning`
  - [ ] Test `--diagram-type crd-connection`
  - [ ] Test `--diagram-type logging-pipeline`
  - [ ] Test `--diagram-type monitoring`
  - [ ] Test `--diagram-type data-collection`
  - [ ] Test `--all-essential` flag generates 4 diagrams
  - [ ] Test `--all-supplementary` flag generates 2 diagrams
  - [ ] Test `--diagram-type all` generates all 8 diagrams (including existing 3)

- [ ] 5.2.2 Test output formats:
  - [ ] Test PNG generation for all new diagrams
  - [ ] Test SVG generation for all new diagrams
  - [ ] Test PDF generation for all new diagrams

- [ ] 5.2.3 Test DPI settings:
  - [ ] Test 300 DPI (paper quality)
  - [ ] Test 150 DPI (screen quality)
  - [ ] Verify file sizes are reasonable

### 5.3 Visual Validation

- [ ] 5.3.1 Generate all diagrams locally and inspect:
  - [ ] Check font sizes are consistent (cluster: 32pt, nodes: 11pt, edges: 12pt)
  - [ ] Check spacing is adequate (no overlapping components)
  - [ ] Check alignment is clean (components in straight lines where appropriate)
  - [ ] Check colors are consistent across diagrams
  - [ ] Check edge routing is clean (no crossed edges where avoidable)

- [ ] 5.3.2 Validate against analysis document:
  - [ ] Compare VM provisioning diagram to analysis section 2
  - [ ] Compare CRD connection diagram to analysis section 4
  - [ ] Compare logging pipeline diagram to analysis section 5
  - [ ] Compare monitoring diagram to analysis section 6
  - [ ] Compare data collection diagram to analysis section 7

- [ ] 5.3.3 Check accessibility:
  - [ ] Verify colors work for colorblind readers (use colorblind simulator)
  - [ ] Verify font sizes are readable when printed
  - [ ] Verify edge labels are legible

## Phase 6: Documentation & Finalization

### 6.1 Update README.md

- [ ] 6.1.1 Add "Architecture Diagrams" section with:
  - [ ] Overview paragraph explaining diagram suite
  - [ ] Table of diagrams with Name, Purpose, Priority, Output path columns
  - [ ] Usage examples for generating each diagram type

- [ ] 6.1.2 Add "Diagram Selection Guide" subsection:
  - [ ] For paper: Include Priority 1 diagrams (essential)
  - [ ] For poster: Include only main diagram
  - [ ] For documentation: Include all diagrams
  - [ ] For presentations: Mix and match based on topic

- [ ] 6.1.3 Add "Diagram Relationships" subsection:
  - [ ] Explain how diagrams fit together
  - [ ] Show flow: Overview → Provisioning → Connection → Monitoring
  - [ ] Note which diagrams show related mechanisms

### 6.2 Add Figure Captions

- [ ] 6.2.1 Create `figures/main/CAPTIONS.md` with paper-ready captions:
  - [ ] Caption for lablink-architecture.png (System Overview)
  - [ ] Caption for lablink-vm-provisioning.png
  - [ ] Caption for lablink-crd-connection.png
  - [ ] Caption for lablink-logging-pipeline.png

- [ ] 6.2.2 Create `figures/supplementary/CAPTIONS.md`:
  - [ ] Caption for lablink-monitoring.png
  - [ ] Caption for lablink-data-collection.png

### 6.3 Update Analysis Document

- [ ] 6.3.1 Add "Implementation Status" section to `analysis/lablink-architecture-analysis.md`:
  - [ ] Mark implemented diagrams with ✅
  - [ ] Add links to generated PNG files
  - [ ] Add notes on any deviations from original design

### 6.4 OpenSpec Validation

- [ ] 6.4.1 Run `openspec validate expand-diagram-suite --strict`
- [ ] 6.4.2 Resolve any validation errors or warnings
- [ ] 6.4.3 Mark change as ready for review

## Phase 7: Review & Iteration

- [ ] 7.1 Internal review:
  - [ ] Review with LabLink maintainers for code accuracy
  - [ ] Review with paper authors for pedagogical clarity
  - [ ] Review with designers for visual consistency

- [ ] 7.2 Incorporate feedback:
  - [ ] Address code accuracy issues
  - [ ] Simplify overly complex diagrams
  - [ ] Fix visual inconsistencies
  - [ ] Update documentation

- [ ] 7.3 Final generation:
  - [ ] Generate all Priority 1 diagrams at 300 DPI
  - [ ] Generate all Priority 2 diagrams at 300 DPI
  - [ ] Commit to repository
  - [ ] Update metadata files

## Success Criteria

- [x] ✅ Comprehensive analysis document created (analysis/lablink-architecture-analysis.md)
- [ ] ✅ OpenSpec proposal validated with no errors
- [ ] ✅ All 5 new diagram builder methods implemented and tested
- [ ] ✅ All Priority 1 diagrams generated and visually validated
- [ ] ✅ All Priority 2 diagrams generated and visually validated
- [ ] ✅ Code references validated against actual lablink codebase
- [ ] ✅ README updated with diagram documentation
- [ ] ✅ Figure captions written for paper
- [ ] ✅ All tests passing (pytest returns 0 exit code)

## Estimated Effort

- Phase 1: ✅ Complete (0.5 days)
- Phase 2: 0.5 days (infrastructure setup)
- Phase 3: 1.5 days (3 essential diagrams @ 0.5 days each)
- Phase 4: 0.5 days (2 supplementary diagrams @ 0.25 days each)
- Phase 5: 0.5 days (testing and validation)
- Phase 6: 0.5 days (documentation)
- Phase 7: 0.5 days (review and iteration)

**Total**: ~4 days of focused work

## Dependencies

- Requires `add-architecture-diagram` change to be complete (provides base infrastructure)
- Requires access to `../lablink` repository for code reference validation
- Requires Python diagrams library and graphviz installed
