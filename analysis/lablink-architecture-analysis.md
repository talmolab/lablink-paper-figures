# LabLink Architecture Analysis: Comprehensive Diagram Proposal

**Date:** 2025-11-13  
**Purpose:** Identify all distinct architectural mechanisms and flows for research paper diagrams

---

## Executive Summary

LabLink is a cloud-based system for provisioning and managing remote desktop environments for computational research. The architecture consists of **8 major distinct mechanisms** that should be visualized separately for clarity and pedagogical value.

**Current Status:** Main diagram shows the core flow (Admin → Allocator → Client VMs → CloudWatch → Lambda → Allocator callback). However, this misses several critical flows including CRD connection setup, database notifications, VM startup sequences, and data collection.

---

## Part 1: Architectural Mechanisms Discovered

### 1. **Infrastructure Provisioning Flow**
**What it does:** Admin provisions the LabLink allocator server and AWS infrastructure  
**Components:**
- Admin (external)
- Terraform (tool)
- AWS EC2 (Allocator Server)
- AWS EIP (Elastic IP)
- AWS Security Groups
- AWS IAM Roles & Instance Profiles
- AWS S3 (Terraform state backend)
- AWS DynamoDB (state locking)
- PostgreSQL RDS (database)
- Optional: Route53 (DNS), ACM Certificate, ALB (SSL termination), Caddy (SSL proxy)

**Flow:**
1. Admin runs Terraform from lablink-template/lablink-infrastructure
2. Terraform provisions Elastic IP (persistent or dynamic strategy)
3. Terraform creates EC2 instance for Allocator
4. Terraform sets up IAM roles for EC2 and Lambda
5. Terraform creates RDS PostgreSQL database
6. Terraform creates CloudWatch Log Group for client VMs
7. Terraform creates Lambda function for log processing
8. Terraform optionally sets up DNS, SSL, and ALB
9. EC2 user_data.sh runs, installing Docker and optionally Caddy
10. Docker container pulls and runs allocator image
11. Allocator initializes Terraform workspace for client VMs

**Code References:**
- `/c/repos/lablink-template/lablink-infrastructure/main.tf`
- `/c/repos/lablink-template/lablink-infrastructure/alb.tf`
- `/c/repos/lablink-template/lablink-infrastructure/user_data.sh`
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (main() function)

---

### 2. **Client VM Provisioning Flow**
**What it does:** Allocator dynamically provisions client VMs via Terraform subprocess  
**Components:**
- Allocator Server
- Terraform (embedded in allocator)
- AWS EC2 (Client VMs)
- AWS Security Groups (client-specific)
- AWS IAM Roles (CloudWatch permissions)
- PostgreSQL Database (VM registry)
- S3 Bucket (runtime.tfvars storage)

**Flow:**
1. Admin accesses `/admin/create` web UI
2. Admin enters number of VMs to create
3. Allocator writes `terraform.runtime.tfvars` with configuration
4. Allocator runs `terraform apply` with instance_count parameter
5. Terraform provisions EC2 instances with GPU/CPU configuration
6. Each EC2 gets IAM instance profile for CloudWatch
7. Terraform outputs timing data (start_time, end_time, duration)
8. Allocator stores timing data in PostgreSQL
9. Allocator uploads runtime.tfvars to S3 for backup
10. Database creates VM records with "initializing" status

**Code References:**
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (launch() endpoint)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/terraform/main.tf`
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/database.py` (update_terraform_timing)

---

### 3. **Client VM Startup & Initialization Flow**
**What it does:** Client VM boots up, installs CloudWatch agent, and starts container  
**Components:**
- Client VM EC2 instance
- AWS CloudWatch Agent
- CloudWatch Logs (log group)
- Docker runtime
- NVIDIA drivers (if GPU)
- Allocator API (status updates)

**Flow:**
1. **Cloud-init Phase (EC2 boot):**
   - EC2 user_data.sh begins execution
   - VM sends status "initializing" to Allocator API
   - Wait for apt/dpkg lock release
   - Download and install CloudWatch agent
   - Configure CloudWatch to stream /var/log/cloud-init-output.log
   - Start CloudWatch agent (logs now streaming)
   - Check GPU support (nvidia-smi)
   - Configure Docker daemon (nvidia runtime if GPU)
   - Pull application Docker image
   - Create config directory and mount custom startup script

2. **Container Startup Phase:**
   - Launch Docker container with environment variables
   - VM sends status "running" to Allocator API
   - Record cloud-init end time
   - Send timing metrics to Allocator API (/api/vm-metrics)

3. **Container Initialization Phase (inside Docker):**
   - Record container start time
   - Activate Python virtual environment
   - Clone tutorial repository if specified
   - Run custom startup script if exists
   - Start background services:
     - `subscribe` (waits for CRD command assignment)
     - `update_inuse_status` (monitors process usage)
     - `check_gpu` (GPU health monitoring)
   - Record container end time
   - Send container timing metrics to Allocator API
   - Tail logs to keep container alive

**Code References:**
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/terraform/user_data.sh`
- `/c/repos/lablink/packages/client/start.sh`
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (update_vm_status, receive_vm_metrics)

---

### 4. **CRD Connection Setup via PostgreSQL Notify Flow**
**What it does:** User requests VM access, allocator assigns VM, client VM receives notification and connects CRD  
**Components:**
- User (external, via web form)
- Allocator Web UI (/)
- PostgreSQL Database (VM table + TRIGGER + NOTIFY)
- Client VM Container (subscribe service)

**Flow:**
1. **User Request:**
   - User visits allocator homepage (/)
   - User enters email and CRD command (contains --code)
   - User submits form to /api/request_vm

2. **Allocator Assignment:**
   - Allocator validates CRD command (must contain --code)
   - Allocator checks for available VMs (status='running', useremail IS NULL)
   - Allocator assigns VM by updating database record:
     - Sets useremail, crdcommand, pin
     - Sets inuse=FALSE, healthy=NULL

3. **Database Trigger:**
   - PostgreSQL TRIGGER fires on CrdCommand INSERT/UPDATE
   - TRIGGER calls notify_crd_command_update() function
   - Function executes pg_notify() with payload:
     ```json
     {
       "HostName": "lablink-vm-prod-1",
       "CrdCommand": "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=...",
       "Pin": "123456"
     }
     ```

4. **Client VM Notification:**
   - Client VM's `subscribe` service is LISTEN-ing on channel 'vm_updates'
   - Service receives notification via PostgreSQL connection
   - Service parses JSON payload
   - Service checks if hostname matches this VM
   - Service calls connect_to_crd() with pin and command

5. **CRD Connection:**
   - reconstruct_command() parses and validates CRD command
   - Executes: `DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=... --redirect-url=... --name=...`
   - Inputs PIN twice for verification
   - Chrome Remote Desktop connects to user's Google account
   - User can now access VM via browser

6. **Success Response:**
   - Allocator web UI displays success page with hostname and PIN

**Code References:**
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (submit_vm_details, vm_startup endpoints)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/database.py` (assign_vm, listen_for_notifications)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py` (TRIGGER definition)
- `/c/repos/lablink/packages/client/src/lablink_client_service/subscribe.py`
- `/c/repos/lablink/packages/client/src/lablink_client_service/connect_crd.py`

---

### 5. **Logging & Observability Flow (CloudWatch → Lambda → Allocator)**
**What it does:** Client VM logs are collected, processed, and stored in allocator database  
**Components:**
- Client VM (cloud-init-output.log)
- CloudWatch Agent (running on client VM)
- CloudWatch Logs (log group + log stream per VM)
- CloudWatch Log Subscription Filter
- Lambda Function (log_processor)
- Allocator API (/api/vm-logs)
- PostgreSQL Database (logs column)

**Flow:**
1. **Log Collection:**
   - Client VM writes logs to /var/log/cloud-init-output.log
   - CloudWatch Agent tails log file
   - Agent streams logs to CloudWatch Logs
   - Each VM has its own log stream (lablink-vm-{env}-{index})

2. **Log Processing:**
   - CloudWatch Log Subscription Filter matches all logs (pattern="")
   - Filter triggers Lambda function for each log batch
   - Lambda receives gzipped, base64-encoded log events

3. **Lambda Processing:**
   - Lambda decompresses and decodes log data
   - Extracts log_group, log_stream, and messages array
   - Constructs JSON payload:
     ```json
     {
       "log_group": "lablink-cloud-init-prod",
       "log_stream": "lablink-vm-prod-1",
       "messages": ["line1", "line2", ...]
     }
     ```

4. **Callback to Allocator:**
   - Lambda POSTs payload to Allocator API_ENDPOINT (env var)
   - Endpoint: `{allocator_url}/api/vm-logs`
   - Allocator validates VM exists
   - Allocator appends new logs to existing logs in database
   - Allocator saves combined logs to PostgreSQL logs column

5. **Admin Access:**
   - Admin visits /admin/instances to view VM list
   - Admin clicks VM to view /admin/logs/{hostname}
   - Page fetches logs via /api/vm-logs/{hostname}
   - If logs are None and status='initializing', returns 503 (agent installing)
   - Otherwise, displays logs in web UI

**Code References:**
- `/c/repos/lablink-template/lablink-infrastructure/lambda_function.py`
- `/c/repos/lablink-template/lablink-infrastructure/main.tf` (Lambda, subscription filter)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (receive_vm_logs, get_vm_logs_by_hostname)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/database.py` (save_logs_by_hostname, get_vm_logs)

---

### 6. **VM Status Monitoring & Reporting Flow**
**What it does:** Client VMs report health, status, and usage back to allocator  
**Components:**
- Client VM Container (background services)
- Allocator API (multiple endpoints)
- PostgreSQL Database (status, inuse, healthy columns)

**Sub-flows:**

#### 6a. **VM Status Updates (initializing → running → error)**
1. Client VM sends POST to /api/vm-status during startup
2. Allocator updates status column in database
3. Admin can query /api/vm-status or /api/vm-status/{hostname}

#### 6b. **GPU Health Monitoring**
1. `check_gpu` service runs nvidia-smi every 20 seconds
2. If status changes (Healthy/Unhealthy/N/A), POSTs to /api/gpu_health
3. Allocator updates healthy column
4. If nvidia-smi not found, sets "N/A" and exits loop

#### 6c. **Application Usage Tracking**
1. `update_inuse_status` service monitors process list every 20 seconds
2. Checks if SUBJECT_SOFTWARE process is running
3. If state changes, POSTs to /api/update_inuse_status
4. Allocator updates inuse boolean column

#### 6d. **Performance Metrics Collection**
1. Client VMs send timing data to /api/vm-metrics/{hostname}
2. Two phases:
   - Cloud-init: start, end, duration
   - Container: start, end, duration
3. Allocator stores timing data in database
4. Allocator calculates TotalStartupDurationSeconds:
   - Terraform + CloudInit + Container durations

**Code References:**
- `/c/repos/lablink/packages/client/src/lablink_client_service/check_gpu.py`
- `/c/repos/lablink/packages/client/src/lablink_client_service/update_inuse_status.py`
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (update_vm_status, update_gpu_health, update_inuse_status, receive_vm_metrics)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/database.py` (update_vm_metrics, calculate_total_startup_time)

---

### 7. **Data Collection & Export Flow**
**What it does:** Admin downloads generated data files from all client VMs  
**Components:**
- Admin (web UI)
- Allocator Server
- SSH/rsync (between allocator and client VMs)
- Docker containers (on client VMs)
- Temporary file system
- Zip archive

**Flow:**
1. Admin clicks "Download Data" button
2. Allocator calls /api/scp-client endpoint
3. For each client VM:
   - SSH into VM using private key from Terraform
   - Find files with specified extension inside Docker container:
     - Run: `docker exec {container_id} find /home/client -name "*.{ext}"`
   - Extract files from container to VM:
     - Run: `docker cp {container_id}:{file_path} /tmp/extracted/`
   - Rsync files from VM to allocator's temp directory:
     - Run: `rsync -avz -e "ssh -i {key}" ubuntu@{vm_ip}:/tmp/extracted/ {local_dir}/`
4. Create zip archive with timestamp: `lablink_data{timestamp}.zip`
5. Send zip file as HTTP response (as_attachment=True)
6. Delete zip file after request completes

**Code References:**
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (download_all_data endpoint)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/utils/scp.py` (find_files_in_container, extract_files_from_docker, rsync_files_to_allocator)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/utils/terraform_utils.py` (get_instance_ips, get_ssh_private_key)

---

### 8. **VM Teardown & Cleanup Flow**
**What it does:** Admin destroys all client VMs and cleans up resources  
**Components:**
- Admin (web UI)
- Allocator Server
- Terraform (destroy command)
- PostgreSQL Database (clear all records)
- AWS EC2 (client VMs deleted)

**Flow:**
1. Admin navigates to /admin/instances/delete
2. Admin clicks "Destroy" button
3. Allocator runs: `terraform destroy -auto-approve -var-file=terraform.runtime.tfvars`
4. Terraform deletes all client VM resources:
   - EC2 instances
   - Security groups
   - IAM roles and instance profiles
   - SSH key pairs
5. Allocator calls database.clear_database()
6. Database executes: `DELETE FROM {vm_table};`
7. All VM records removed from PostgreSQL
8. Success message displayed in web UI

**Code References:**
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/main.py` (destroy endpoint)
- `/c/repos/lablink/packages/allocator/src/lablink_allocator_service/database.py` (clear_database)

---

## Part 2: Proposed Diagram Types

### **Essential Diagrams (Priority 1)**

#### **Diagram 1: System Overview**
- **Purpose:** Provide a high-level understanding of LabLink's architecture and major components
- **Components:**
  - Admin (external)
  - LabLink Infrastructure cluster: Allocator, PostgreSQL
  - Dynamic Compute cluster: Client VMs (show 3 to illustrate multi-tenancy)
  - Observability cluster: CloudWatch Logs, Lambda
- **Flow:**
  1. Admin → API Requests → Allocator
  2. Allocator → Provisions → Client VMs (orange dotted)
  3. Client VMs → Logs → CloudWatch
  4. CloudWatch → Triggers → Lambda
  5. Lambda → Callback → Allocator
- **Scope:** Core architecture only, no optional components (DNS, SSL, ALB)
- **Current Status:** ✅ Already implemented in main diagram

---

#### **Diagram 2: VM Provisioning & Lifecycle**
- **Purpose:** Show how client VMs are provisioned dynamically and their lifecycle stages
- **Components:**
  - Admin Web UI
  - Allocator Server
  - Terraform Engine (embedded)
  - PostgreSQL Database
  - AWS EC2 (Client VMs)
  - S3 Bucket
- **Flow:**
  1. Admin → "Create VMs" request → Allocator
  2. Allocator → Writes runtime.tfvars → Filesystem
  3. Allocator → terraform apply → Terraform Engine
  4. Terraform Engine → Provisions → AWS EC2 (Client VMs)
  5. Terraform Engine → Returns timing data → Allocator
  6. Allocator → Stores VM records + timing → PostgreSQL
  7. Allocator → Uploads tfvars → S3
  8. Client VM → user_data.sh execution → Multiple stages:
     - Stage 1: Install CloudWatch Agent
     - Stage 2: Configure Docker (GPU/CPU)
     - Stage 3: Pull & Launch Container
  9. Each stage → Status updates → Allocator API
- **Annotations:**
  - Show status transitions: initializing → running → error
  - Show timing metrics collection: Terraform, CloudInit, Container
- **Code References:** Launch endpoint, terraform/main.tf, user_data.sh

---

#### **Diagram 3: CRD Connection Setup via Database Notification**
- **Purpose:** Explain the PostgreSQL LISTEN/NOTIFY mechanism for real-time VM assignment
- **Components:**
  - User (external, web browser)
  - Allocator Web Form
  - PostgreSQL Database (with TRIGGER highlighted)
  - Client VM Container (subscribe service)
  - Chrome Remote Desktop
- **Flow:**
  1. User → Submits email + CRD command → Allocator web form
  2. Allocator → Validates CRD command → Success/Error
  3. Allocator → Queries available VMs → PostgreSQL (WHERE useremail IS NULL)
  4. Allocator → UPDATE VM record → PostgreSQL (SET useremail, crdcommand, pin)
  5. PostgreSQL TRIGGER → Fires → notify_crd_command_update()
  6. PostgreSQL → pg_notify('vm_updates', JSON payload) → Notification
  7. Client VM (subscribe) → LISTEN 'vm_updates' → Receives notification
  8. Client VM → Parses payload → Validates hostname
  9. Client VM → Executes CRD start-host command → Chrome Remote Desktop
  10. Chrome Remote Desktop → Connects to user's Google account → User can access VM
- **Special Callouts:**
  - Highlight the TRIGGER as a key architectural mechanism
  - Show blocking wait on allocator side (long-polling pattern)
  - Show infinite retry loop on client side
- **Code References:** submit_vm_details, assign_vm, listen_for_notifications, subscribe.py, connect_crd.py, generate_init_sql.py

---

#### **Diagram 4: Logging Pipeline (CloudWatch → Lambda → Allocator)**
- **Purpose:** Show how logs flow from client VMs back to the allocator for centralized storage
- **Components:**
  - Client VM (cloud-init-output.log file)
  - CloudWatch Agent
  - CloudWatch Logs (log group + stream)
  - Log Subscription Filter
  - Lambda Function
  - Allocator API
  - PostgreSQL Database
- **Flow:**
  1. Client VM → Writes logs → /var/log/cloud-init-output.log
  2. CloudWatch Agent → Tails file → Streams to CloudWatch Logs
  3. Each VM → Separate log stream → lablink-vm-{env}-{index}
  4. Log Subscription Filter → Matches all logs → Triggers Lambda
  5. Lambda → Decompresses gzip data → Extracts messages
  6. Lambda → POST payload → Allocator /api/vm-logs
  7. Allocator → Validates VM exists → Appends logs
  8. Allocator → Saves to database → PostgreSQL logs column
  9. Admin → Views logs → Web UI (/admin/logs/{hostname})
- **Annotations:**
  - Show gzip/base64 encoding at Lambda boundary
  - Show log aggregation (multiple log events → single API call)
  - Note: Lambda executes in AWS-managed VPC
- **Code References:** lambda_function.py, receive_vm_logs, save_logs_by_hostname

---

### **Supplementary Diagrams (Priority 2)**

#### **Diagram 5: Infrastructure Provisioning (Allocator Setup)**
- **Purpose:** Show one-time setup of LabLink infrastructure by admin
- **Components:**
  - Admin Workstation
  - Terraform CLI
  - AWS Provider
  - All AWS resources (EC2, EIP, RDS, S3, DynamoDB, CloudWatch, Lambda, IAM, Security Groups)
  - Optional: Route53, ACM, ALB, Caddy
- **Flow:**
  1. Admin → Runs terraform init/apply → Terraform
  2. Terraform → Creates resources in parallel:
     - EIP (persistent or dynamic)
     - RDS PostgreSQL instance
     - EC2 Allocator instance with IAM role
     - CloudWatch Log Group for client VMs
     - Lambda function for log processing
     - S3 bucket + DynamoDB table for state
  3. Terraform (optional branch) → Creates DNS/SSL resources:
     - Route53 A record
     - ACM certificate + ALB (if provider=acm)
     - Caddy proxy (if provider=letsencrypt/cloudflare)
  4. EC2 instance → Runs user_data.sh:
     - Installs Docker
     - Optionally installs Caddy
     - Pulls allocator image
     - Starts allocator container
  5. Allocator container → Initializes Terraform workspace for client VMs
- **Scope:** Focus on infrastructure layer, not application logic
- **Code References:** main.tf, alb.tf, user_data.sh

---

#### **Diagram 6: VM Status & Health Monitoring**
- **Purpose:** Show the multiple monitoring mechanisms running on client VMs
- **Components:**
  - Client VM Container
  - Three background services (subscribe, update_inuse_status, check_gpu)
  - Allocator API (multiple endpoints)
  - PostgreSQL Database
- **Flow (3 parallel sub-flows):**
  
  **Sub-flow A: Status Updates**
  1. VM → POST /api/vm-status → Allocator
  2. Allocator → Updates status column → PostgreSQL
  3. Values: initializing, running, error, unknown
  
  **Sub-flow B: GPU Health**
  1. check_gpu service → Runs nvidia-smi every 20s
  2. If status changes → POST /api/gpu_health → Allocator
  3. Allocator → Updates healthy column → PostgreSQL
  4. Values: Healthy, Unhealthy, N/A
  
  **Sub-flow C: Application Usage**
  1. update_inuse_status → Monitors process list every 20s
  2. Checks if SUBJECT_SOFTWARE process exists
  3. If state changes → POST /api/update_inuse_status → Allocator
  4. Allocator → Updates inuse boolean → PostgreSQL
- **Annotations:** Show all three services running concurrently with different polling intervals
- **Code References:** check_gpu.py, update_inuse_status.py, main.py (multiple endpoints)

---

#### **Diagram 7: Data Collection & Export**
- **Purpose:** Show how admin retrieves generated data files from client VMs
- **Components:**
  - Admin Web UI
  - Allocator Server (with SSH client)
  - Client VMs (with Docker containers)
  - Temporary filesystem
  - Zip archive
- **Flow:**
  1. Admin → Clicks "Download Data" → Allocator web UI
  2. Allocator → Gets VM IPs + SSH key → Terraform outputs
  3. For each VM (parallel):
     - Allocator → SSH to VM → Runs docker exec find command
     - Allocator → Identifies files with extension → Returns file list
     - Allocator → docker cp files → VM /tmp/extracted/
     - Allocator → rsync files → Allocator temp directory
  4. Allocator → Creates zip archive → lablink_data{timestamp}.zip
  5. Allocator → Sends as HTTP download → Admin browser
  6. Allocator → Deletes zip file → Cleanup
- **Scope:** Focus on data movement, not file formats
- **Code References:** download_all_data, scp.py utilities

---

#### **Diagram 8: VM Teardown & Cleanup**
- **Purpose:** Show how infrastructure is cleaned up
- **Components:**
  - Admin Web UI
  - Allocator Server
  - Terraform (destroy command)
  - AWS EC2 (Client VMs)
  - PostgreSQL Database
- **Flow:**
  1. Admin → Clicks "Destroy" → Allocator web UI
  2. Allocator → terraform destroy → Terraform
  3. Terraform → Deletes AWS resources:
     - EC2 instances
     - Security groups
     - IAM roles
     - SSH key pairs
  4. Allocator → Calls clear_database() → PostgreSQL
  5. PostgreSQL → DELETE FROM vm_table → Success
  6. Allocator → Returns success message → Admin UI
- **Scope:** Simple, linear flow
- **Code References:** destroy endpoint, clear_database

---

### **Optional/Reference Diagrams (Priority 3)**

#### **Diagram 9: Network Routing (DNS → ALB → Allocator)**
- **Purpose:** Show how external requests reach the allocator with optional SSL termination
- **Components:**
  - User Browser
  - Route53 DNS
  - Application Load Balancer (optional)
  - Caddy Proxy (optional)
  - Allocator Container (port 5000)
- **Flow (conditional based on SSL provider):**
  - **No SSL:** User → HTTP → EIP → Allocator:5000
  - **ACM SSL:** User → HTTPS → Route53 → ALB → HTTP:5000 → Allocator
  - **Let's Encrypt/Cloudflare SSL:** User → HTTPS → Route53 → EIP → Caddy:443 → HTTP:5000 → Allocator
- **Annotations:** Show which components are created based on config
- **Code References:** alb.tf, main.tf (conditional resources)

---

#### **Diagram 10: Database Schema & Relationships**
- **Purpose:** Show PostgreSQL table structure and TRIGGER mechanism
- **Components:**
  - VM Table (schema with all columns)
  - TRIGGER: trigger_crd_command_insert_or_update
  - FUNCTION: notify_crd_command_update()
  - NOTIFY channel: vm_updates
- **Content:**
  - Table columns: HostName (PK), Pin, CrdCommand, UserEmail, InUse, Healthy, Status, Logs, timing columns, CreatedAt
  - TRIGGER logic: Fires AFTER INSERT OR UPDATE OF CrdCommand
  - FUNCTION logic: Executes pg_notify with JSON payload
- **Scope:** Database-centric view
- **Code References:** generate_init_sql.py

---

## Part 3: How Diagrams Fit Together

### **The Complete Story (for paper readers):**

1. **Start with Diagram 1 (System Overview):** Gives reader the big picture - what are the major components and how do they relate?

2. **Dive into Diagram 2 (VM Provisioning):** How does the dynamic compute layer actually get created? This is the core innovation - VMs are provisioned on-demand.

3. **Explain Diagram 3 (CRD Connection Setup):** Once VMs exist, how do users connect to them? This shows the clever use of database notifications for real-time coordination.

4. **Show Diagram 4 (Logging Pipeline):** How does the system maintain observability? This demonstrates the CloudWatch → Lambda → Allocator feedback loop.

5. **Optionally reference Diagrams 5-10:** For readers who want deeper understanding of specific subsystems.

### **Diagram Categories:**

- **Core Functionality (Essential):** Diagrams 1-4 → These tell the complete story
- **Deployment & Operations (Supplementary):** Diagrams 5, 8, 9 → How system is set up and torn down
- **Monitoring & Data (Supplementary):** Diagrams 6, 7 → How system tracks health and collects results
- **Implementation Details (Reference):** Diagram 10 → For developers/implementers

---

## Part 4: Recommendations

### **For Research Paper:**

**Essential (must include):**
1. ✅ Diagram 1: System Overview (already created)
2. ⭐ Diagram 2: VM Provisioning & Lifecycle (high priority)
3. ⭐ Diagram 3: CRD Connection via Database Notification (high priority - unique mechanism)
4. ⭐ Diagram 4: Logging Pipeline (high priority)

**Supplementary (include if space permits):**
- Diagram 6: VM Status & Health Monitoring (shows system robustness)
- Diagram 7: Data Collection & Export (shows end-to-end workflow)

**Total recommendation:** 4-6 diagrams for comprehensive coverage

### **For Poster:**

**Must have:**
1. Diagram 1: System Overview only

**Optional:**
2. Simplified version of Diagram 2 (VM Provisioning flow as a sequence)

### **For Documentation/Wiki:**

**Include all 10 diagrams** for complete technical reference

---

## Part 5: Key Findings

### **Mechanisms Not in Current Diagram:**

1. ❌ **PostgreSQL LISTEN/NOTIFY pattern** - This is architecturally significant and unique
2. ❌ **VM startup sequence** (3 phases: Terraform → Cloud-init → Container)
3. ❌ **Multiple monitoring services** running in parallel on each VM
4. ❌ **Data collection via SSH/rsync/Docker** - shows how results are retrieved
5. ❌ **Terraform subprocess execution** - shows how allocator provisions VMs
6. ❌ **Database-driven timing metrics** - performance monitoring system
7. ❌ **Optional SSL/DNS components** - configurability of deployment

### **Architectural Highlights:**

- **Multi-tier provisioning:** Infrastructure tier (Allocator) + Dynamic tier (Client VMs)
- **Event-driven coordination:** Database TRIGGER + NOTIFY for real-time VM assignment
- **Comprehensive observability:** Logs, status, health, usage, and performance metrics
- **Container-based isolation:** Each VM runs application in Docker with NVIDIA support
- **Terraform-as-library:** Embedded Terraform for dynamic resource management
- **Long-polling pattern:** Client VMs block waiting for assignments (604800s timeout)

---

## Appendix: Complete Flow Map

```
User Journey:
1. Admin provisions infrastructure (Diagram 5)
2. Admin creates VMs (Diagram 2)
3. VMs start up in 3 phases (Diagram 2)
4. VMs send monitoring data (Diagram 6)
5. User requests VM access (Diagram 3)
6. Allocator assigns VM via database (Diagram 3)
7. VM receives notification and connects CRD (Diagram 3)
8. User works in VM, logs are collected (Diagram 4)
9. Admin downloads generated data (Diagram 7)
10. Admin destroys VMs (Diagram 8)
```

---

## Next Steps

1. Review this analysis with team
2. Prioritize diagrams based on paper page limit
3. Create Diagram 2 (VM Provisioning & Lifecycle)
4. Create Diagram 3 (CRD Connection Setup)
5. Create Diagram 4 (Logging Pipeline)
6. Update generator.py with new diagram types
7. Generate high-resolution versions for paper submission
