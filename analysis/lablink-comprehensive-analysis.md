# LabLink Comprehensive System Analysis

**Analysis Date:** 2025-11-13  
**Repositories Analyzed:**
- `lablink` (main repository)
- `lablink-template` (deployment template)

---

## Table of Contents

1. [GitHub Workflows Analysis](#1-github-workflows-analysis)
2. [API Endpoints Catalog](#2-api-endpoints-catalog)
3. [Network Flow Analysis](#3-network-flow-analysis)
4. [Diagram Specifications](#4-diagram-specifications)

---

## 1. GitHub Workflows Analysis

### 1.1 Workflow Inventory

| Workflow File | Repository | Name | Primary Purpose | Triggers |
|--------------|------------|------|-----------------|----------|
| `ci.yml` | lablink | CI for Lablink Services | Lint and test Python packages | PR (packages/**, .github/workflows/ci.yml) |
| `docs.yml` | lablink | LabLink Docs | Build and deploy documentation | Release, Push (main/test/dev), Workflow Dispatch, PR |
| `publish-pip.yml` | lablink | Publish Python Packages | Build and publish to PyPI | Release, Tag push, Workflow Dispatch |
| `lablink-images.yml` | lablink | Build and Push Docker Images | Build Docker images for allocator and client | Workflow Dispatch, PR, Push (main/test) |
| `terraform-deploy.yml` | lablink-template | Deploy LabLink Infrastructure | Deploy infrastructure to AWS | Push (test branch), Workflow Dispatch, Repository Dispatch |
| `terraform-destroy.yml` | lablink-template | Destroy LabLink Infrastructure | Tear down AWS infrastructure | Workflow Dispatch (manual confirmation) |
| `config-validation.yml` | lablink-template | Validate Configuration | Validate config.yaml files | PR (config files), Workflow Dispatch |

### 1.2 CI/CD Pipeline Details

#### **Continuous Integration (ci.yml)**

**Triggers:**
- Pull requests modifying `packages/**` or `.github/workflows/ci.yml`

**Jobs:**

1. **lint** (Matrix Strategy)
   - Packages: `lablink-client`, `lablink-allocator`
   - Python version: 3.10
   - Steps:
     - Checkout code
     - Set up UV package manager
     - Install dependencies (`uv sync --all-extras`)
     - Run ruff linter (`uv run ruff check src tests`)

2. **test** (Matrix Strategy)
   - Packages: `lablink-client`, `lablink-allocator`
   - Python version: 3.10
   - Steps:
     - Checkout code
     - Set up UV package manager
     - Configure AWS credentials (for allocator Terraform tests only)
     - Setup Terraform 1.6.6 (allocator only)
     - Install dependencies (`uv sync --all-extras`)
     - Remove backend.tf for local testing (allocator only)
     - Run pytest with coverage (`--cov-fail-under=90`)
   - Coverage Requirements:
     - Client: 90% minimum
     - Allocator: 90% minimum

3. **docker-build-test-allocator**
   - Steps:
     - Build allocator dev Docker image (`Dockerfile.dev`)
     - Verify venv activation
     - Verify console scripts exist (`lablink-allocator`, `generate-init-sql`)
     - Verify dev dependencies (pytest, ruff, coverage)
     - Verify package imports
     - Execute console scripts to ensure they run

**Secrets/Environment:**
- `AWS_ROLE_ARN` - for Terraform testing
- `AWS_REGION` - defaults to us-west-2

---

#### **Docker Image Build (lablink-images.yml)**

**Triggers:**
- Workflow Dispatch (manual) - allows environment selection (test/ci-test/prod)
- Pull requests modifying `packages/**` or `.github/workflows/lablink-images.yml`
- Push to `main` or `test` branches (packages/** or workflow file)

**Build Strategy:**
- **Dev Builds** (PR, push to main/test, manual test/ci-test):
  - Uses `Dockerfile.dev` (includes source code)
  - No package version required
  - Tagged with `-test` suffix
  
- **Production Builds** (manual prod):
  - Uses `Dockerfile` (pulls from PyPI)
  - Requires `allocator_version` and `client_version` inputs
  - Tagged without `-test` suffix

**Jobs:**

1. **build** (Matrix Strategy)
   - Images: `lablink-allocator-image`, `lablink-client-base-image`
   - Platform: linux/amd64
   - Steps:
     - Validate production build requirements (prod only)
     - Select Dockerfile (.dev for dev builds, standard for prod)
     - Set environment suffix (-test for dev builds)
     - Generate tags (includes SHA, latest, version-specific)
     - Build and push to GitHub Container Registry
   - Tags Generated (example for allocator):
     ```
     ghcr.io/{owner}/lablink-allocator-image:linux-amd64{-test}
     ghcr.io/{owner}/lablink-allocator-image:linux-amd64-{SHA}{-test}
     ghcr.io/{owner}/lablink-allocator-image:linux-amd64-latest{-test}
     ghcr.io/{owner}/lablink-allocator-image:linux-amd64-terraform-1.4.6{-test}
     ghcr.io/{owner}/lablink-allocator-image:linux-amd64-postgres-15{-test}
     ghcr.io/{owner}/lablink-allocator-image:{VERSION} (prod only)
     ```

2. **verify-allocator**
   - Depends on: build
   - Steps:
     - Pull built allocator image (SHA-tagged for consistency)
     - Verify console scripts (`lablink-allocator`, `generate-init-sql`)
     - Verify package imports (main, database, get_config)
     - Verify dev dependencies (dev images only)
     - Run pytest tests (dev images only)
     - Verify entry points are callable
     - Execute console scripts with timeout

3. **verify-client**
   - Depends on: build
   - Steps:
     - Pull built client image (SHA-tagged)
     - Verify console scripts (`check_gpu`, `subscribe`, `update_inuse_status`)
     - Verify package imports
     - Verify uv is available
     - Verify dev dependencies (dev images only)
     - Run pytest tests (dev images only)
     - Verify entry points are callable
     - Execute console scripts with timeout
     - Verify custom-startup.sh execution mechanism

**Environment Variables:**
- `GITHUB_TOKEN` - for GHCR authentication

---

#### **Python Package Publishing (publish-pip.yml)**

**Triggers:**
- Release published (GitHub release)
- Tag push matching patterns:
  - `lablink-allocator-service_v*`
  - `lablink-client-service_v*`
- Workflow Dispatch (manual testing with dry_run option)

**Matrix Strategy:**
- Packages:
  - `lablink-allocator-service` (dir: packages/allocator)
  - `lablink-client-service` (dir: packages/client)

**Guardrails:**

1. **Branch Verification**
   - Releases must be from `main` branch
   - Validates `github.event.release.target_commitish`

2. **Version Verification**
   - Tag version must match `pyproject.toml` version
   - Format: `{package-name}_v{version}`

3. **Package Metadata Check**
   - Required fields: name, version, description, authors
   - Package name must match expected value

4. **Linting**
   - Runs ruff check on src and tests

5. **Test Suite**
   - Runs pytest with coverage (can be skipped with `skip_tests` input)
   - Coverage report generated but threshold set to 0 (informational)

6. **Build Verification**
   - Builds package with `uv build`
   - Verifies artifacts in dist/

**Publishing:**
- Uses `uv publish` (trusted publishing with OIDC)
- Dry run available for testing
- Outputs package version for Docker image building

**Permissions:**
- `id-token: write` - for PyPI trusted publishing
- `contents: read`

---

#### **Documentation Deployment (docs.yml)**

**Triggers:**
- Release published
- Push to main/test/dev branches (docs/**, mkdocs.yml, workflow file, package .py files)
- Workflow Dispatch
- Pull requests (docs/**, mkdocs.yml)

**Jobs:**

1. **docs**
   - Platform: Ubuntu latest
   - Python: 3.11
   - Steps:
     - Checkout with full history (`fetch-depth: 0`)
     - Setup UV package manager
     - Install dependencies including docs extra
     - Configure Git for deployment (github-actions bot)
     - Determine version (prod/test/dev based on branch)
     - Deploy documentation:
       - **Release**: Deploy with tag version and latest alias
       - **Branch push**: Deploy to environment-specific version (prod/test/dev)
       - **Manual/PR**: Build only (no deployment)
     - Set default version to prod (main branch only)

**Documentation Versioning:**
- Uses `mike` for multi-version docs
- Versions: `prod`, `test`, `dev`, and release tags
- Default version: `latest` (for releases) or `prod` (for main branch)

**Permissions:**
- `contents: write` - for GitHub Pages deployment

---

#### **Terraform Deployment (terraform-deploy.yml)**

**Triggers:**
- Push to `test` branch
- Workflow Dispatch (environment: test/prod/ci-test)
- Repository Dispatch (deploy-prod-image event)

**Environment Determination:**
- Workflow dispatch: Uses input environment
- Repository dispatch: Uses payload environment
- Push to test branch: Uses "test" environment

**Steps:**

1. **Pre-deployment Validation**
   - Validate config.yaml using `lablink-validate-config`
   - Creates temporary UV project for validation

2. **Secret Injection**
   - Injects `ADMIN_PASSWORD` and `DB_PASSWORD` from GitHub secrets
   - Replaces `PLACEHOLDER_ADMIN_PASSWORD` and `PLACEHOLDER_DB_PASSWORD` in config.yaml
   - Warns if using default values

3. **Terraform Initialization**
   - Extracts bucket name from config.yaml
   - Initializes with S3 backend: `backend-{env}.hcl`
   - Configures state locking with DynamoDB

4. **Terraform Validation**
   - Runs `terraform fmt -check`
   - Runs `terraform validate`

5. **CloudWatch Log Group Import**
   - Attempts to import existing log groups to prevent conflicts:
     - `lablink-cloud-init-{env}`
     - `/aws/lambda/lablink_log_processor_{env}`
   - Continues on error (resources may not exist yet)

6. **Terraform Apply**
   - Runs plan with `-var="resource_suffix={env}"`
   - Applies with `-auto-approve`
   - On failure: Destroys infrastructure automatically

7. **Post-deployment Actions**
   - Save SSH private key as artifact (retention: 1 day)
   - Validate DNS configuration (if enabled)
   - Verify DNS resolution and HTTPS connectivity
   - Verify service health:
     - HTTP connectivity (max 2 minutes)
     - HTTPS/SSL certificate (max 3 minutes, Let's Encrypt only)
   - Output deployment summary

**Health Checks:**
- Tests HTTP connectivity (status 200/308/301 accepted)
- Tests HTTPS connectivity for Let's Encrypt (status 200/302)
- Waits up to 5 minutes for HTTPS (DNS + SSL certificate acquisition)

**Secrets/Environment:**
- `AWS_ROLE_ARN` - OIDC role for AWS authentication
- `AWS_REGION` - defaults to us-west-2
- `ADMIN_PASSWORD` - admin console password
- `DB_PASSWORD` - PostgreSQL database password

**Artifacts:**
- `lablink-key-{env}` - SSH private key (1 day retention)

**Permissions:**
- `id-token: write` - for AWS OIDC
- `contents: read`

---

#### **Terraform Destroy (terraform-destroy.yml)**

**Triggers:**
- Workflow Dispatch (manual only, requires confirmation)

**Inputs:**
- `confirm_destroy`: Must type "yes" to proceed
- `environment`: test/prod/ci-test

**Safety:**
- Job only runs if `confirm_destroy == 'yes'`

**Steps:**

1. **Infrastructure State Initialization**
   - Initializes infrastructure Terraform with S3 backend
   - Extracts bucket name from config.yaml

2. **Client VM Destruction (State-only)**
   - Creates temporary directory with minimal backend config
   - Initializes with S3 state: `{env}/client/terraform.tfstate`
   - Checks for resources in state
   - Destroys client VMs using state only (no .tf files needed)
   - Continues on error (non-fatal)

3. **Infrastructure Destruction**
   - Destroys main infrastructure: `terraform destroy -auto-approve`
   - Uses `-var="resource_suffix={env}"`

**Resources Destroyed:**
- Client VMs (from separate state)
- Allocator EC2 instance
- Security groups
- EIP association (EIP retained if using persistent strategy)
- CloudWatch log groups
- Lambda function
- IAM roles and policies
- Route53 DNS records (if terraform_managed)
- ALB resources (if using ACM SSL)

**Permissions:**
- `id-token: write` - for AWS OIDC
- `contents: read`

---

#### **Configuration Validation (config-validation.yml)**

**Triggers:**
- Pull requests modifying config files
- Workflow Dispatch (with custom config path)

**Steps:**
- Creates temporary UV project
- Installs `lablink-allocator-service` from PyPI
- Runs `lablink-validate-config` on config.yaml
- Reports success/failure with actionable messages

**Default Config Path:**
- `lablink-infrastructure/config/config.yaml`

**Validation Checks:**
- Schema validation against structured config
- Required fields presence
- Type checking
- Dependency validation (e.g., ACM requires certificate_arn)

**Permissions:**
- `contents: read`

---

### 1.3 Workflow Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     Development Flow                         │
└─────────────────────────────────────────────────────────────┘

PR Created/Updated (packages/**)
    │
    ├─► ci.yml (lint + test)
    │       │
    │       ├─► Lint packages
    │       ├─► Run tests with coverage
    │       └─► Build Docker test
    │
    └─► lablink-images.yml (build dev images)
            │
            ├─► Build allocator-dev image
            ├─► Build client-dev image
            ├─► Verify allocator image
            └─► Verify client image

Push to main/test
    │
    ├─► docs.yml (build docs for environment)
    │
    └─► lablink-images.yml (build dev images)

┌─────────────────────────────────────────────────────────────┐
│                     Release Flow                             │
└─────────────────────────────────────────────────────────────┘

Create Git Tag (lablink-*-service_v*)
    │
    └─► publish-pip.yml
            │
            ├─► Validate version matches tag
            ├─► Run guardrails (lint, test, metadata)
            ├─► Build package
            └─► Publish to PyPI

Create GitHub Release
    │
    ├─► publish-pip.yml (publish packages)
    │
    └─► docs.yml (deploy versioned docs)

Manual Production Image Build
    │
    └─► lablink-images.yml (workflow_dispatch, env=prod)
            │
            ├─► Requires allocator_version + client_version
            ├─► Builds from PyPI packages
            └─► Tags without -test suffix

┌─────────────────────────────────────────────────────────────┐
│                  Deployment Flow                             │
└─────────────────────────────────────────────────────────────┘

Push to test branch
    │
    └─► terraform-deploy.yml (auto-deploy to test)

Manual Deployment
    │
    └─► terraform-deploy.yml (workflow_dispatch)
            │
            ├─► Validate config.yaml
            ├─► Inject secrets
            ├─► Initialize Terraform with S3 backend
            ├─► Import existing CloudWatch log groups
            ├─► Apply infrastructure
            ├─► Verify DNS and service health
            └─► Save SSH key artifact

Manual Teardown
    │
    └─► terraform-destroy.yml
            │
            ├─► Destroy client VMs (from S3 state)
            └─► Destroy infrastructure
```

---

### 1.4 CI/CD Integration Points

**AWS Services:**
- **OIDC Authentication**: Workflows use `aws-actions/configure-aws-credentials@v3` with role assumption
- **S3**: Terraform state backend
- **DynamoDB**: Terraform state locking (lock-table)
- **CloudWatch**: Log group imports during deployment
- **ECR/GHCR**: Docker image storage

**External Services:**
- **GitHub Container Registry**: Docker image hosting
- **PyPI**: Python package hosting (trusted publishing with OIDC)
- **GitHub Pages**: Documentation hosting

**Testing Infrastructure:**
- **Terraform**: Version 1.6.6 used consistently
- **Python**: 3.10 for packages, 3.11 for docs
- **UV**: Package manager for all workflows

---

## 2. API Endpoints Catalog

### 2.1 Complete Endpoint List

All endpoints serve from Flask app running on port 5000 (internal).

#### **Public Endpoints (No Authentication)**

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/` | GET | Home page | N/A | HTML (index.html) |
| `/api/request_vm` | POST | Request VM allocation | Form: `email`, `crd_command` | HTML (success.html or error) |
| `/api/unassigned_vms_count` | GET | Get count of available VMs | N/A | JSON: `{"count": int}` |
| `/vm_startup` | POST | Wait for VM notification | JSON: `{"hostname": str}` | JSON: notification data |
| `/api/update_inuse_status` | POST | Update VM in-use status | JSON: `{"hostname": str, "status": bool}` | JSON: `{"message": str}` |
| `/api/gpu_health` | POST | Update GPU health status | JSON: `{"gpu_status": bool, "hostname": str}` | JSON: `{"message": str}` |
| `/api/vm-status` | POST | Update VM status | JSON: `{"hostname": str, "status": str}` | JSON: `{"message": str}` |
| `/api/vm-status/<hostname>` | GET | Get VM status by hostname | Path param: hostname | JSON: `{"hostname": str, "status": str}` |
| `/api/vm-status` | GET | Get all VM statuses | N/A | JSON: array of VM status objects |
| `/api/vm-logs` | POST | Receive VM logs from Lambda | JSON: `{"log_group": str, "log_stream": str, "messages": [str]}` | JSON: `{"message": str}` |
| `/api/vm-logs/<hostname>` | GET | Get VM logs by hostname | Path param: hostname | JSON: `{"hostname": str, "logs": str}` |
| `/api/vm-metrics/<hostname>` | POST | Receive VM cloud-init metrics | JSON: metrics data | JSON: `{"message": str}` |

#### **Admin UI Endpoints (Authentication Required)**

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/admin` | GET | Admin dashboard | N/A | HTML (admin.html) |
| `/admin/create` | GET | Create instances page | N/A | HTML (create-instances.html) |
| `/admin/instances` | GET | View all instances | N/A | HTML (instances.html) |
| `/admin/instances/delete` | GET | Delete instances page | N/A | HTML (delete-instances.html) |
| `/admin/logs/<hostname>` | GET | View VM logs | Path param: hostname | HTML (instance-logs.html) |

#### **Admin API Endpoints (Authentication Required)**

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/api/admin/set-aws-credentials` | POST | Set AWS credentials | Form: `aws_access_key_id`, `aws_secret_access_key`, `aws_token` | HTML (admin.html with message) |
| `/api/admin/unset-aws-credentials` | POST | Unset AWS credentials | N/A | HTML (admin.html with message) |
| `/api/launch` | POST | Launch new VMs | Form: `num_vms` | HTML (dashboard.html with output/error) |
| `/destroy` | POST | Destroy all VMs | N/A | HTML (delete-dashboard.html with output/error) |
| `/api/scp-client` | GET | Download all VM data | N/A | File (ZIP archive) |

---

### 2.2 Endpoint Details by Category

#### **VM Request Flow (Public)**

**1. GET /**
- **Purpose**: Display VM request form
- **Authentication**: None
- **Template**: `index.html`
- **Fields**: Email input, CRD command input

**2. POST /api/request_vm**
- **Purpose**: Submit VM request and assign VM
- **Authentication**: None
- **Request Body**:
  ```
  email: string (required)
  crd_command: string (required, must contain "--code")
  ```
- **Validation**:
  - Email and CRD command required
  - CRD command must contain "--code"
  - Available VMs must exist
- **Database Operations**:
  - `database.get_unassigned_vms()` - check availability
  - `database.assign_vm(email, crd_command, PIN)` - assign VM
  - `database.get_vm_details(email)` - retrieve assigned VM details
- **Response**:
  - Success: `success.html` with hostname and PIN
  - Error: `index.html` with error message
- **PIN**: Hardcoded to "123456"

**3. GET /api/unassigned_vms_count**
- **Purpose**: Real-time count of available VMs
- **Authentication**: None
- **Database Operations**: `database.get_unassigned_vms()`
- **Response**: `{"count": 5}`

---

#### **VM Lifecycle Management (Public API - Called by Client VMs)**

**4. POST /vm_startup**
- **Purpose**: Wait for PostgreSQL notification when VM is ready
- **Authentication**: None
- **Request Body**: `{"hostname": "lablink-vm-test-1"}`
- **Database Operations**:
  - `database.get_vm_by_hostname(hostname)` - verify VM exists
  - `database.listen_for_notifications(channel, target_hostname)` - wait for notification
- **PostgreSQL**: Uses `LISTEN vm_updates` mechanism
- **Response**: Notification data when VM status changes

**5. POST /api/update_inuse_status**
- **Purpose**: Client VM reports when user starts/stops using it
- **Authentication**: None
- **Request Body**: `{"hostname": str, "status": bool}`
- **Database Operations**: `database.update_vm_in_use(hostname, in_use)`

**6. POST /api/gpu_health**
- **Purpose**: Client VM reports GPU health status
- **Authentication**: None
- **Request Body**: `{"gpu_status": bool, "hostname": str}`
- **Database Operations**: `database.update_health(hostname, healthy)`

**7. POST /api/vm-status**
- **Purpose**: Update VM status (initializing, running, error, etc.)
- **Authentication**: None
- **Request Body**: `{"hostname": str, "status": str}`
- **Database Operations**: `database.update_vm_status(hostname, status)`
- **Status Values**: "initializing", "running", "error", "available", "assigned"

**8. GET /api/vm-status/<hostname>**
- **Purpose**: Get specific VM status
- **Authentication**: None
- **Database Operations**: `database.get_status_by_hostname(hostname)`
- **Response**: `{"hostname": "lablink-vm-test-1", "status": "running"}`

**9. GET /api/vm-status**
- **Purpose**: Get all VM statuses
- **Authentication**: None
- **Database Operations**: `database.get_all_vm_status()`
- **Response**: Array of VM status objects

---

#### **Logging and Metrics (Public API - Called by Lambda and Client VMs)**

**10. POST /api/vm-logs**
- **Purpose**: Receive VM logs from Lambda log processor
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "log_group": "lablink-cloud-init-test",
    "log_stream": "lablink-vm-test-1",
    "messages": ["log line 1", "log line 2"]
  }
  ```
- **Database Operations**:
  - `database.vm_exists(log_stream)` - verify VM exists
  - `database.get_vm_logs(hostname)` - get existing logs
  - `database.save_logs_by_hostname(hostname, logs)` - append new logs
- **Caller**: Lambda function `lablink_log_processor_{env}`

**11. GET /api/vm-logs/<hostname>**
- **Purpose**: Retrieve VM logs for monitoring
- **Authentication**: None (can be called by client or admin)
- **Database Operations**:
  - `database.get_vm_by_hostname(hostname)` - verify VM exists
  - `database.get_vm_logs(hostname)` - retrieve logs
- **Response**:
  - Normal: `{"hostname": "lablink-vm-test-1", "logs": "...log content..."}`
  - Initializing with no logs: `503 Service Unavailable` - "VM is installing CloudWatch agent"
  - Not found: `404 Not Found`

**12. POST /api/vm-metrics/<hostname>**
- **Purpose**: Receive cloud-init performance metrics from client VM
- **Authentication**: None
- **Request Body**: JSON with timing metrics
- **Database Operations**:
  - `database.update_vm_metrics(hostname, metrics)` - store metrics
  - `database.calculate_total_startup_time(hostname)` - calculate total time

---

#### **Admin Dashboard (Authentication Required)**

**Authentication Mechanism:**
- HTTP Basic Auth using Flask-HTTPAuth
- Username: `cfg.app.admin_user` (from config.yaml)
- Password: `cfg.app.admin_password` (from config.yaml, injected from GitHub secret)
- Password stored as bcrypt hash

**13. GET /admin**
- **Purpose**: Admin dashboard landing page
- **Authentication**: Required
- **AWS Validation**:
  - Checks for `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` env vars
  - Validates credentials using `validate_aws_credentials()`
- **Response**:
  - Valid credentials: admin.html with success message
  - Invalid credentials: admin.html with error message
  - No credentials: admin.html without message

**14. GET /admin/create**
- **Purpose**: Display VM creation form
- **Authentication**: Required
- **Template**: `create-instances.html`

**15. GET /admin/instances**
- **Purpose**: View all VMs in database
- **Authentication**: Required
- **Database Operations**: `database.get_all_vms()`
- **Template**: `instances.html` with VM list

**16. GET /admin/instances/delete**
- **Purpose**: Display VM deletion interface
- **Authentication**: Required
- **Template**: `delete-instances.html`
- **Config Data**: Passes `cfg.machine.extension` to template

**17. GET /admin/logs/<hostname>**
- **Purpose**: View logs for specific VM
- **Authentication**: Required
- **Database Operations**: `database.vm_exists(hostname)` - verify VM exists
- **Template**: `instance-logs.html` (loads logs via AJAX from `/api/vm-logs/<hostname>`)

---

#### **Admin Operations (Authentication Required)**

**18. POST /api/admin/set-aws-credentials**
- **Purpose**: Set AWS credentials for Terraform operations
- **Authentication**: Required
- **Request Body** (form data):
  ```
  aws_access_key_id: string (required)
  aws_secret_access_key: string (required)
  aws_token: string (optional)
  ```
- **Validation**:
  - Access key and secret key required
  - Validates credentials using `validate_aws_credentials()`
  - Removes env vars if validation fails
- **Environment Variables Set**:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN`
- **Response**: admin.html with success/error message

**19. POST /api/admin/unset-aws-credentials**
- **Purpose**: Remove AWS credentials from environment
- **Authentication**: Required
- **Environment Variables Removed**:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_SESSION_TOKEN`
- **Response**: admin.html with unset message

**20. POST /api/launch**
- **Purpose**: Launch new client VMs using Terraform
- **Authentication**: Required
- **Request Body** (form data):
  ```
  num_vms: integer (required, > 0)
  ```
- **Terraform Operations**:
  1. Calculate total VMs: `num_vms + database.get_row_count()`
  2. Check GPU support: `check_support_nvidia(machine_type)`
  3. Generate allocator URL: `get_allocator_url(cfg, allocator_ip)`
  4. Write `terraform.runtime.tfvars`:
     ```hcl
     allocator_ip = "..."
     allocator_url = "..."
     machine_type = "..."
     image_name = "..."
     repository = "..."
     client_ami_id = "..."
     subject_software = "..."
     resource_suffix = "..."
     gpu_support = "true/false"
     cloud_init_output_log_group = "..."
     region = "..."
     startup_on_error = "continue/fail"
     ```
  5. Run: `terraform apply -auto-approve -var-file=terraform.runtime.tfvars -var=instance_count={total_vms}`
  6. Upload runtime file to S3: `upload_to_s3(runtime_file, env, bucket_name, region)`
  7. Store timing data: `get_instance_timings()` and `database.update_terraform_timing()`
- **Terraform Directory**: `packages/allocator/src/lablink_allocator_service/terraform/`
- **Response**: dashboard.html with Terraform output (ANSI codes stripped)

**21. POST /destroy**
- **Purpose**: Destroy all client VMs using Terraform
- **Authentication**: Required
- **Terraform Operations**:
  1. Run: `terraform destroy -auto-approve -var-file=terraform.runtime.tfvars`
  2. Clear database: `database.clear_database()`
- **Response**: delete-dashboard.html with Terraform output

**22. GET /api/scp-client**
- **Purpose**: Download all data files from client VMs
- **Authentication**: Required
- **File Extension**: From `cfg.machine.extension` (e.g., ".slp" for SLEAP)
- **Process**:
  1. Get instance IPs: `get_instance_ips(terraform_dir)`
  2. Get SSH key: `get_ssh_private_key(terraform_dir)`
  3. For each VM:
     - Find files in Docker container: `find_files_in_container(ip, key_path, extension)`
     - Extract files from Docker: `extract_files_from_docker(ip, key_path, files)`
     - Rsync files to allocator: `rsync_files_to_allocator(ip, key_path, local_dir, extension)`
  4. Create ZIP archive with timestamp: `lablink_data{timestamp}.zip`
  5. Send file and delete after request
- **SSH Operations**: Uses `subprocess` to run ssh/rsync commands
- **Response**: ZIP file download

---

### 2.3 API Architecture Diagram Specification

```
┌─────────────────────────────────────────────────────────────────┐
│                     API Architecture                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│   External Users    │
│   (Port 80/443)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Public Endpoints (No Auth)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ User Interface                                              │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ GET  /                       → index.html                  │ │
│  │ POST /api/request_vm         → Form: email, crd_command   │ │
│  │ GET  /api/unassigned_vms_count → JSON: count              │ │
│  │                                                             │ │
│  │ Database: get_unassigned_vms(), assign_vm(),              │ │
│  │          get_vm_details()                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ VM Lifecycle (Called by Client VMs)                        │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ POST /vm_startup              → PostgreSQL LISTEN          │ │
│  │ POST /api/update_inuse_status → JSON: hostname, status    │ │
│  │ POST /api/gpu_health          → JSON: gpu_status, hostname│ │
│  │ POST /api/vm-status           → JSON: hostname, status    │ │
│  │ GET  /api/vm-status/<hostname> → JSON: status             │ │
│  │ GET  /api/vm-status           → JSON: all statuses        │ │
│  │                                                             │ │
│  │ Database: update_vm_in_use(), update_health(),            │ │
│  │          update_vm_status(), get_status_by_hostname()     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Logging & Metrics (Called by Lambda & Client VMs)          │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ POST /api/vm-logs             → JSON: log_group, messages │ │
│  │ GET  /api/vm-logs/<hostname>  → JSON: logs                │ │
│  │ POST /api/vm-metrics/<hostname> → JSON: metrics           │ │
│  │                                                             │ │
│  │ Database: save_logs_by_hostname(), get_vm_logs(),         │ │
│  │          update_vm_metrics(), calculate_total_startup_time()│
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│              Admin Endpoints (HTTP Basic Auth)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Admin UI Pages                                              │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ GET  /admin                   → admin.html (dashboard)     │ │
│  │ GET  /admin/create            → create-instances.html      │ │
│  │ GET  /admin/instances         → instances.html             │ │
│  │ GET  /admin/instances/delete  → delete-instances.html      │ │
│  │ GET  /admin/logs/<hostname>   → instance-logs.html         │ │
│  │                                                             │ │
│  │ Database: get_all_vms(), vm_exists()                       │ │
│  │ AWS: validate_aws_credentials()                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Admin Operations                                            │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ POST /api/admin/set-aws-credentials   → Set env vars      │ │
│  │ POST /api/admin/unset-aws-credentials → Clear env vars    │ │
│  │ POST /api/launch                      → Terraform apply   │ │
│  │ POST /destroy                         → Terraform destroy │ │
│  │ GET  /api/scp-client                  → Download ZIP      │ │
│  │                                                             │ │
│  │ Terraform: apply, destroy                                  │ │
│  │ Database: get_row_count(), clear_database(),              │ │
│  │          update_terraform_timing()                         │ │
│  │ AWS: check_support_nvidia(), upload_to_s3()               │ │
│  │ SSH: get_instance_ips(), find_files_in_container(),       │ │
│  │     extract_files_from_docker(), rsync_files_to_allocator()│
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                  External Service Integration                    │
└─────────────────────────────────────────────────────────────────┘

Flask App (Port 5000)
    │
    ├──► PostgreSQL (Port 5432)
    │     │
    │     ├─ VM assignment table
    │     ├─ VM status tracking
    │     ├─ Log storage
    │     ├─ Metrics storage
    │     └─ PostgreSQL NOTIFY/LISTEN (vm_updates channel)
    │
    ├──► AWS Services
    │     │
    │     ├─ S3 (Terraform state, runtime tfvars)
    │     ├─ EC2 (Instance metadata, GPU support checks)
    │     └─ STS (Credential validation)
    │
    ├──► Terraform (subprocess)
    │     │
    │     ├─ Client VM provisioning
    │     ├─ Timing data extraction
    │     └─ SSH key management
    │
    └──► SSH/Rsync (subprocess)
          │
          ├─ File discovery in Docker containers
          ├─ File extraction from containers
          └─ File transfer to allocator
```

---

### 2.4 Database Operations per Endpoint

| Endpoint | Database Queries | PostgreSQL Features |
|----------|------------------|---------------------|
| `/api/request_vm` | SELECT (get_unassigned_vms), UPDATE (assign_vm), SELECT (get_vm_details) | Table scan, row update |
| `/vm_startup` | SELECT (get_vm_by_hostname), LISTEN (vm_updates) | LISTEN/NOTIFY mechanism |
| `/api/update_inuse_status` | UPDATE (update_vm_in_use) | Row update |
| `/api/gpu_health` | UPDATE (update_health) | Row update |
| `/api/vm-status` (POST) | UPDATE (update_vm_status) | Row update |
| `/api/vm-status/<hostname>` (GET) | SELECT (get_status_by_hostname) | Single row lookup |
| `/api/vm-status` (GET) | SELECT (get_all_vm_status) | Table scan |
| `/api/vm-logs` (POST) | SELECT (vm_exists), SELECT (get_vm_logs), UPDATE (save_logs_by_hostname) | Row update with text append |
| `/api/vm-logs/<hostname>` (GET) | SELECT (get_vm_by_hostname), SELECT (get_vm_logs) | Single row lookup |
| `/api/vm-metrics/<hostname>` | UPDATE (update_vm_metrics), UPDATE (calculate_total_startup_time) | JSON field update |
| `/admin/instances` | SELECT (get_all_vms) | Table scan |
| `/api/launch` | SELECT (get_row_count), UPDATE (update_terraform_timing) | Count query, batch update |
| `/destroy` | DELETE (clear_database) | Table truncate |
| `/api/scp-client` | SELECT (get_row_count) | Count query |

---

## 3. Network Flow Analysis

### 3.1 Port Mapping Table

| Source | Destination | Port | Protocol | Purpose | Data Payload |
|--------|-------------|------|----------|---------|--------------|
| **External User** | DNS Server | 53 | UDP | DNS resolution for allocator FQDN | Query: A record for allocator domain |
| **External User** | ALB/EIP | 80 | TCP/HTTP | Access allocator (HTTP) | HTTP requests (GET /, POST /api/request_vm) |
| **External User** | ALB/EIP | 443 | TCP/HTTPS | Access allocator (HTTPS) | HTTPS requests (encrypted) |
| **External User** | Allocator EIP | 22 | TCP/SSH | Admin SSH access to allocator | SSH commands, file transfers |
| **ALB** | Allocator EC2 | 5000 | TCP/HTTP | Forward requests to allocator (ACM SSL only) | Proxied HTTP requests |
| **Caddy (on Allocator)** | Allocator Container | 5000 | TCP/HTTP | Reverse proxy (Let's Encrypt/CloudFlare SSL) | Proxied HTTP requests |
| **Allocator Container** | RDS PostgreSQL | 5432 | TCP/PostgreSQL | Database queries and LISTEN/NOTIFY | SQL queries, NOTIFY messages |
| **Allocator Container** | Client VMs | 22 | TCP/SSH | SSH for file operations (rsync) | SSH commands, rsync data |
| **Client VMs** | Allocator | 80/443 | TCP/HTTP(S) | API calls (status updates, metrics) | JSON: POST /api/update_inuse_status, etc. |
| **Client VMs** | CloudWatch | 443 | TCP/HTTPS | Send logs to CloudWatch | CloudWatch Logs API (PutLogEvents) |
| **CloudWatch** | Lambda | N/A | AWS Internal | Trigger Lambda on new logs | Compressed log events (gzip + base64) |
| **Lambda** | Allocator | 80/443 | TCP/HTTP(S) | POST logs to allocator | JSON: POST /api/vm-logs |
| **Client VM** | Chrome Remote Desktop | Various | TCP | CRD connectivity (handled by CRD service) | CRD protocol (P2P via Google relay) |

---

### 3.2 Protocol Details

#### **HTTP/HTTPS**
- **HTTP (Port 80)**:
  - Direct access when SSL provider = "none"
  - Redirect to HTTPS when SSL provider = "letsencrypt", "cloudflare", or "acm"
- **HTTPS (Port 443)**:
  - Let's Encrypt: Caddy handles SSL termination on allocator EC2
  - CloudFlare: CloudFlare proxy handles SSL, Caddy serves HTTP
  - ACM: ALB handles SSL termination, forwards HTTP to allocator on port 5000
  - Certificate acquisition: Let's Encrypt automatic via ACME protocol

#### **SSH (Port 22)**
- **Allocator SSH**:
  - Admin access for troubleshooting
  - Key: Generated by Terraform, stored in allocator EC2
- **Client VM SSH**:
  - Allocator connects for file operations
  - Key: Generated by Terraform, stored in allocator container
  - Used for: `find`, `docker cp`, `rsync`

#### **PostgreSQL (Port 5432)**
- **Connection String**: `postgresql://{user}:{password}@{host}:{port}/{dbname}`
- **Features Used**:
  - Standard SQL queries (SELECT, UPDATE, INSERT, DELETE)
  - LISTEN/NOTIFY for real-time VM notifications
  - JSON field storage for metrics
  - Text field storage for logs

#### **CloudWatch API (Port 443)**
- **Client VMs → CloudWatch**:
  - Uses `watchtower` Python library
  - API: `logs.PutLogEvents`
  - Authentication: IAM instance profile
  - Log Group: `lablink-cloud-init-{env}`
  - Log Stream: VM hostname (e.g., `lablink-vm-test-1`)

#### **Chrome Remote Desktop**
- **Ports**: Managed by CRD service (not exposed in security groups)
- **Protocol**: Proprietary Google protocol over WebRTC
- **Connection**: P2P via Google relay servers
- **Data**: Desktop streaming, input events

---

### 3.3 Data Payload Specifications

#### **User → Allocator (VM Request)**
```
POST /api/request_vm
Content-Type: application/x-www-form-urlencoded

email=user@example.com&crd_command=DISPLAY=:20%20/opt/google/chrome-remote-desktop/start-host%20--code=...
```

**Response (Success)**:
```html
<!DOCTYPE html>
<html>
  <body>
    <h1>VM Assigned</h1>
    <p>Hostname: lablink-vm-test-1</p>
    <p>PIN: 123456</p>
  </body>
</html>
```

#### **Allocator → PostgreSQL (VM Assignment)**
```sql
-- Check availability
SELECT * FROM vms WHERE email IS NULL LIMIT 1;

-- Assign VM
UPDATE vms
SET email = 'user@example.com',
    crd_command = 'DISPLAY=:20 /opt/google/chrome-remote-desktop/start-host --code=...',
    pin = '123456',
    status = 'assigned',
    updated_at = NOW()
WHERE hostname = 'lablink-vm-test-1';

-- Notify listeners
NOTIFY vm_updates, 'lablink-vm-test-1';

-- Retrieve details
SELECT hostname, pin FROM vms WHERE email = 'user@example.com';
```

#### **Client VM → CloudWatch (Logs)**
```python
# Via watchtower library
logger = CloudWatchLogHandler(
    log_group_name="lablink-cloud-init-test",
    log_stream_name="lablink-vm-test-1",
    boto3_client=session
)
logger.info("VM started successfully")
```

**CloudWatch API Call**:
```json
{
  "logGroupName": "lablink-cloud-init-test",
  "logStreamName": "lablink-vm-test-1",
  "logEvents": [
    {
      "timestamp": 1731542400000,
      "message": "VM started successfully"
    }
  ]
}
```

#### **CloudWatch → Lambda (Log Subscription)**
```json
{
  "awslogs": {
    "data": "H4sIAA...base64-encoded-gzipped-log-data..."
  }
}
```

**Decoded Data**:
```json
{
  "logGroup": "lablink-cloud-init-test",
  "logStream": "lablink-vm-test-1",
  "logEvents": [
    {"message": "VM started successfully", "timestamp": 1731542400000}
  ]
}
```

#### **Lambda → Allocator (Log Forwarding)**
```
POST /api/vm-logs HTTP/1.1
Host: allocator.example.com
Content-Type: application/json

{
  "log_group": "lablink-cloud-init-test",
  "log_stream": "lablink-vm-test-1",
  "messages": [
    "VM started successfully",
    "Installing dependencies...",
    "Docker container started"
  ]
}
```

**Response**:
```json
{
  "message": "VM logs posted successfully"
}
```

#### **Client VM → Allocator (Status Update)**
```
POST /api/update_inuse_status HTTP/1.1
Host: allocator.example.com
Content-Type: application/json

{
  "hostname": "lablink-vm-test-1",
  "status": true
}
```

#### **Client VM → Allocator (GPU Health)**
```
POST /api/gpu_health HTTP/1.1
Host: allocator.example.com
Content-Type: application/json

{
  "hostname": "lablink-vm-test-1",
  "gpu_status": true
}
```

#### **Client VM → Allocator (Metrics)**
```
POST /api/vm-metrics/lablink-vm-test-1 HTTP/1.1
Host: allocator.example.com
Content-Type: application/json

{
  "cloud_init_start": "2025-11-13T10:00:00Z",
  "cloud_init_end": "2025-11-13T10:05:30Z",
  "docker_pull_start": "2025-11-13T10:01:00Z",
  "docker_pull_end": "2025-11-13T10:03:00Z",
  "container_start": "2025-11-13T10:03:00Z",
  "container_ready": "2025-11-13T10:05:30Z"
}
```

#### **Allocator → Terraform (Launch VMs)**
```bash
terraform apply -auto-approve \
  -var-file=terraform.runtime.tfvars \
  -var=instance_count=5
```

**terraform.runtime.tfvars**:
```hcl
allocator_ip = "203.0.113.42"
allocator_url = "https://allocator.example.com"
machine_type = "g4dn.xlarge"
image_name = "ghcr.io/talmolab/lablink-client-base-image:linux-amd64-latest-test"
repository = "https://github.com/talmolab/sleap-tutorial-data.git"
client_ami_id = "ami-0601752c11b394251"
subject_software = "sleap"
resource_suffix = "test"
gpu_support = "true"
cloud_init_output_log_group = "lablink-cloud-init-test"
region = "us-west-2"
startup_on_error = "continue"
```

#### **Allocator → Client VM (SSH File Discovery)**
```bash
# Find files in Docker container
ssh -i /path/to/key ubuntu@203.0.113.43 \
  "docker exec client-container find /workspace -name '*.slp'"

# Extract files from container
ssh -i /path/to/key ubuntu@203.0.113.43 \
  "docker cp client-container:/workspace/file.slp /tmp/"

# Rsync files to allocator
rsync -avz -e "ssh -i /path/to/key" \
  ubuntu@203.0.113.43:/tmp/*.slp \
  /local/temp/dir/
```

---

### 3.4 Network Flow Sequence Diagrams

#### **VM Request and Assignment Flow**

```
┌──────────┐   ┌─────────┐   ┌──────────────┐   ┌────────────┐
│   User   │   │ ALB/EIP │   │  Allocator   │   │ PostgreSQL │
│ (Browser)│   │(80/443) │   │ (Port 5000)  │   │(Port 5432) │
└─────┬────┘   └────┬────┘   └──────┬───────┘   └─────┬──────┘
      │             │               │                  │
      │ HTTP GET /  │               │                  │
      ├────────────►│               │                  │
      │             │  Proxy        │                  │
      │             ├──────────────►│                  │
      │             │               │ SELECT unassigned│
      │             │               ├─────────────────►│
      │             │               │◄─────────────────┤
      │             │               │ (count: 5)       │
      │             │  index.html   │                  │
      │◄────────────┼───────────────┤                  │
      │             │               │                  │
      │ POST /api/  │               │                  │
      │  request_vm │               │                  │
      │ (email, crd)│               │                  │
      ├────────────►│               │                  │
      │             │  Proxy        │                  │
      │             ├──────────────►│                  │
      │             │               │ UPDATE assign_vm │
      │             │               ├─────────────────►│
      │             │               │                  │
      │             │               │ NOTIFY vm_updates│
      │             │               ├─────────────────►│
      │             │               │                  │
      │             │               │ SELECT details   │
      │             │               ├─────────────────►│
      │             │               │◄─────────────────┤
      │             │  success.html │                  │
      │◄────────────┼───────────────┤                  │
      │             │               │                  │
```

#### **Client VM Startup and Logging Flow**

```
┌───────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐
│ Client VM │  │  Allocator   │  │ PostgreSQL │  │CloudWatch│  │ Lambda │
│(cloud-init│  │ (Port 5000)  │  │(Port 5432) │  │  Logs    │  │Function│
└─────┬─────┘  └──────┬───────┘  └─────┬──────┘  └────┬─────┘  └───┬────┘
      │               │                 │               │            │
      │ POST /vm_startup                │               │            │
      │ {"hostname":"vm-1"}             │               │            │
      ├──────────────►│                 │               │            │
      │               │ LISTEN vm_updates               │            │
      │               ├────────────────►│               │            │
      │               │ (waits for      │               │            │
      │               │  notification)  │               │            │
      │               │                 │               │            │
      │ Log: "Starting Docker"          │               │            │
      ├─────────────────────────────────┼──────────────►│            │
      │               │                 │  (PutLogEvents)            │
      │               │                 │               │            │
      │               │                 │               │ Trigger    │
      │               │                 │               ├───────────►│
      │               │                 │               │            │
      │               │ POST /api/vm-logs               │  Decompress│
      │               │ {"log_group":..., "messages":...}   & Parse │
      │               │◄────────────────┼───────────────┼────────────┤
      │               │                 │               │            │
      │               │ UPDATE logs     │               │            │
      │               ├────────────────►│               │            │
      │               │                 │               │            │
      │               │ NOTIFY vm_updates              │            │
      │               ├────────────────►│               │            │
      │               │                 │               │            │
      │               │ (notification   │               │            │
      │               │  received)      │               │            │
      │◄──────────────┤                 │               │            │
      │ Response      │                 │               │            │
```

#### **Admin VM Launch Flow**

```
┌─────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐  ┌─────┐
│  Admin  │  │  Allocator   │  │ PostgreSQL │  │ Terraform │  │ AWS │
│(Browser)│  │ (Port 5000)  │  │(Port 5432) │  │(subprocess│  │ API │
└────┬────┘  └──────┬───────┘  └─────┬──────┘  └─────┬─────┘  └──┬──┘
     │              │                 │                │           │
     │ POST /api/launch              │                │           │
     │ {"num_vms": 3}                │                │           │
     ├─────────────►│                 │                │           │
     │              │ SELECT count    │                │           │
     │              ├────────────────►│                │           │
     │              │◄────────────────┤                │           │
     │              │ (current: 2)    │                │           │
     │              │                 │                │           │
     │              │ Write terraform.runtime.tfvars   │           │
     │              ├─────────────────┼───────────────►│           │
     │              │                 │                │           │
     │              │ terraform apply -var=instance_count=5        │
     │              ├─────────────────┼───────────────►│           │
     │              │                 │                │           │
     │              │                 │                │ Create EC2│
     │              │                 │                ├──────────►│
     │              │                 │                │           │
     │              │                 │                │◄──────────┤
     │              │                 │                │ (IPs, SSH)│
     │              │                 │                │           │
     │              │                 │ UPDATE timings │           │
     │              │◄────────────────┼────────────────┤           │
     │              ├────────────────►│                │           │
     │              │                 │                │           │
     │              │ Upload to S3    │                │           │
     │              ├─────────────────┼────────────────┼──────────►│
     │              │                 │                │           │
     │◄─────────────┤                 │                │           │
     │ dashboard.html                 │                │           │
     │ (terraform output)             │                │           │
```

#### **Data Download Flow (SCP)**

```
┌─────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐
│  Admin  │  │  Allocator   │  │ Client VM │  │  Docker   │
│(Browser)│  │ (Port 5000)  │  │(SSH:22)   │  │ Container │
└────┬────┘  └──────┬───────┘  └─────┬─────┘  └─────┬─────┘
     │              │                 │               │
     │ GET /api/scp-client            │               │
     ├─────────────►│                 │               │
     │              │                 │               │
     │              │ ssh: find *.slp │               │
     │              ├────────────────►│               │
     │              │                 │ docker exec   │
     │              │                 ├──────────────►│
     │              │                 │◄──────────────┤
     │              │◄────────────────┤ (file list)   │
     │              │                 │               │
     │              │ ssh: docker cp  │               │
     │              ├────────────────►│               │
     │              │                 │ docker cp     │
     │              │                 ├──────────────►│
     │              │                 │◄──────────────┤
     │              │◄────────────────┤ (files to /tmp│
     │              │                 │               │
     │              │ rsync files     │               │
     │              ├────────────────►│               │
     │              │◄────────────────┤               │
     │              │ (files transferred)             │
     │              │                 │               │
     │              │ Create ZIP      │               │
     │              │ (in /tmp)       │               │
     │              │                 │               │
     │◄─────────────┤                 │               │
     │ lablink_data.zip                               │
```

---

## 4. Diagram Specifications

### 4.1 Enhanced Network Flow Diagram

**Title**: LabLink Network Architecture with Ports and Protocols

**Components to Include**:

1. **External Layer**
   - User Browser
   - DNS Server (Port 53 UDP)
   - Chrome Remote Desktop Relay Servers

2. **AWS Network Boundary**
   - Route53 DNS (if enabled)
   - Elastic IP (EIP)
   - Application Load Balancer (ACM only)
   - Security Groups (allow_http, alb_sg, lablink_sg)

3. **Allocator Layer**
   - EC2 Instance (Ubuntu 24.04)
     - Caddy (Ports 80/443 → 5000, Let's Encrypt/CloudFlare only)
     - Docker Container
       - Flask App (Port 5000)
       - Terraform (subprocess)
     - SSH Daemon (Port 22)
   - PostgreSQL Database (Port 5432)
     - Connection from allocator container
     - LISTEN/NOTIFY mechanism

4. **Client VM Layer**
   - EC2 Instances (Client VMs)
     - Ubuntu 24.04 + Docker + Nvidia Drivers
     - Docker Container (lablink-client)
       - Client services (subscribe, update_inuse_status, check_gpu)
       - Chrome Remote Desktop
       - User workspace
     - SSH Daemon (Port 22)

5. **AWS Services Layer**
   - CloudWatch Logs
     - Log Group: lablink-cloud-init-{env}
     - Log Streams: VM hostnames
   - Lambda Function
     - lablink_log_processor_{env}
     - Triggered by CloudWatch subscription
   - S3
     - Terraform state storage
     - Runtime tfvars backup

**Connection Labels**:

| From | To | Label |
|------|-----|-------|
| User | DNS | Port 53 UDP: A record query |
| User | ALB/EIP | Port 80 HTTP: GET /, POST /api/request_vm |
| User | ALB/EIP | Port 443 HTTPS: Encrypted requests |
| ALB | Allocator EC2 | Port 5000 HTTP: Proxied requests (ACM only) |
| Caddy | Allocator Container | Port 5000 HTTP: Proxied requests (Let's Encrypt/CloudFlare) |
| Allocator Container | PostgreSQL | Port 5432: SQL queries, NOTIFY/LISTEN |
| Allocator Container | Client VM | Port 22 SSH: Find files, rsync |
| Client VM | Allocator | Port 80/443 HTTP(S): POST status, metrics, logs |
| Client VM | CloudWatch | Port 443 HTTPS: PutLogEvents API |
| CloudWatch | Lambda | AWS Internal: Subscription filter trigger |
| Lambda | Allocator | Port 80/443 HTTP(S): POST /api/vm-logs |
| Chrome Remote Desktop | Google Relay | Various: P2P desktop streaming |

**Annotations**:
- Security Group Rules:
  - allow_http: Ingress 22, 80, 443; Egress all
  - alb_sg: Ingress 80, 443; Egress all
  - lablink_sg: Ingress 22; Egress all
- SSL Providers:
  - none: Direct HTTP on port 80
  - letsencrypt: Caddy (80→5000, 443→5000 with auto SSL)
  - cloudflare: Caddy (80→5000), CloudFlare handles SSL
  - acm: ALB (80→443 redirect, 443→5000 with ACM cert)
- Database: PostgreSQL 15, default port 5432
- Log Flow: Client VM → CloudWatch → Lambda → Allocator → PostgreSQL

---

### 4.2 CI/CD Pipeline Diagram

**Title**: LabLink CI/CD Pipeline

**Stages**:

1. **Development**
   - PR Created/Updated
     - Trigger: ci.yml
       - Lint (ruff)
       - Test (pytest, coverage ≥90%)
       - Docker build test
     - Trigger: lablink-images.yml
       - Build dev images (-test suffix)
       - Verify allocator image
       - Verify client image
     - Trigger: docs.yml (if docs modified)
       - Build docs (no deploy)

2. **Release Preparation**
   - Tag pushed (lablink-*-service_v*)
     - Trigger: publish-pip.yml
       - Guardrail 1: Branch verification (must be main)
       - Guardrail 2: Version verification (tag = pyproject.toml)
       - Guardrail 3: Metadata check
       - Guardrail 4: Linting
       - Guardrail 5: Test suite
       - Guardrail 6: Build verification
       - Publish to PyPI (trusted publishing)

3. **Production Image Build**
   - Manual Workflow Dispatch (env=prod)
     - Requires: allocator_version, client_version
     - Trigger: lablink-images.yml
       - Build from PyPI packages (not source)
       - Tag without -test suffix
       - Verify images
       - Push to GHCR

4. **Documentation Deployment**
   - Release Published
     - Trigger: docs.yml
       - Deploy with version tag
       - Set as latest
   - Push to main/test/dev
     - Trigger: docs.yml
       - Deploy to environment-specific version

5. **Infrastructure Deployment**
   - Push to test branch
     - Trigger: terraform-deploy.yml (auto-deploy test)
   - Manual Workflow Dispatch
     - Trigger: terraform-deploy.yml
       - Validate config.yaml
       - Inject secrets
       - Terraform init (S3 backend)
       - Terraform apply
       - Verify DNS and health
       - Save SSH key artifact

6. **Infrastructure Teardown**
   - Manual Workflow Dispatch (confirmation required)
     - Trigger: terraform-destroy.yml
       - Destroy client VMs (S3 state)
       - Destroy infrastructure

**Artifacts**:
- Python packages (PyPI)
- Docker images (GHCR)
- Documentation (GitHub Pages)
- SSH keys (GitHub Actions artifacts, 1 day retention)

**Secrets**:
- AWS_ROLE_ARN (OIDC)
- AWS_REGION (default: us-west-2)
- ADMIN_PASSWORD
- DB_PASSWORD
- GITHUB_TOKEN (automatic)

---

### 4.3 API Architecture Diagram

**Title**: LabLink Allocator API Architecture

**Layers**:

1. **Ingress Layer**
   - ALB (ACM SSL only)
     - Listener 80 → Redirect 443
     - Listener 443 → Target Group (Port 5000)
   - Caddy (Let's Encrypt/CloudFlare)
     - Port 80/443 → Port 5000
   - Direct (No SSL)
     - Port 80 → Port 5000

2. **Application Layer (Flask - Port 5000)**
   - **Public Endpoints** (No Auth)
     - User Interface
       - GET /
       - POST /api/request_vm
       - GET /api/unassigned_vms_count
     - VM Lifecycle
       - POST /vm_startup
       - POST /api/update_inuse_status
       - POST /api/gpu_health
       - POST /api/vm-status
       - GET /api/vm-status/<hostname>
       - GET /api/vm-status
     - Logging & Metrics
       - POST /api/vm-logs
       - GET /api/vm-logs/<hostname>
       - POST /api/vm-metrics/<hostname>
   
   - **Admin Endpoints** (HTTP Basic Auth)
     - Admin UI
       - GET /admin
       - GET /admin/create
       - GET /admin/instances
       - GET /admin/instances/delete
       - GET /admin/logs/<hostname>
     - Admin Operations
       - POST /api/admin/set-aws-credentials
       - POST /api/admin/unset-aws-credentials
       - POST /api/launch
       - POST /destroy
       - GET /api/scp-client

3. **Integration Layer**
   - **PostgreSQL Database** (Port 5432)
     - Tables: vms
     - Features: LISTEN/NOTIFY, JSON fields
   - **Terraform** (subprocess)
     - Client VM provisioning
     - State management (S3 backend)
   - **AWS SDK** (boto3)
     - S3 operations
     - EC2 metadata
     - STS credential validation
   - **SSH/Rsync** (subprocess)
     - File discovery
     - File extraction
     - File transfer

4. **External Callers**
   - Web Browsers (Users)
   - Client VMs (API calls)
   - Lambda Function (log forwarding)
   - Admins (SSH, API)

**Data Flows**:
- User → Allocator: HTTP form data (email, crd_command)
- Allocator → PostgreSQL: SQL queries, NOTIFY
- PostgreSQL → Allocator: Query results, LISTEN notifications
- Client VM → Allocator: JSON (status, metrics, logs)
- Allocator → Terraform: subprocess (apply, destroy)
- Allocator → Client VM: SSH commands, rsync
- Lambda → Allocator: JSON (log events)

---

### 4.4 Database Schema Diagram

**Title**: LabLink Database Schema (PostgreSQL)

**Table: vms**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing unique ID |
| hostname | VARCHAR(255) | UNIQUE, NOT NULL | VM hostname (e.g., lablink-vm-test-1) |
| email | TEXT | NULLABLE | Assigned user email |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'available' | VM status (available, assigned, initializing, running, error) |
| crd_command | TEXT | NULLABLE | Chrome Remote Desktop command |
| pin | VARCHAR(10) | NULLABLE | CRD PIN code |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |
| in_use | BOOLEAN | DEFAULT FALSE | User actively using VM |
| healthy | BOOLEAN | DEFAULT TRUE | GPU health status |
| logs | TEXT | NULLABLE | Accumulated VM logs |
| metrics | JSON | NULLABLE | Cloud-init performance metrics |
| terraform_timing_seconds | NUMERIC | NULLABLE | Terraform provisioning time |
| terraform_timing_start | TIMESTAMP | NULLABLE | Terraform start time |
| terraform_timing_end | TIMESTAMP | NULLABLE | Terraform end time |
| total_startup_time_seconds | NUMERIC | NULLABLE | Total startup time |

**Indexes**:
- PRIMARY KEY on id
- UNIQUE INDEX on hostname
- INDEX on email (for lookups)
- INDEX on status (for filtering)

**Triggers/Functions**:
- NOTIFY trigger on vms table updates:
  ```sql
  CREATE OR REPLACE FUNCTION notify_vm_update()
  RETURNS TRIGGER AS $$
  BEGIN
    PERFORM pg_notify('vm_updates', NEW.hostname);
    RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER vm_update_trigger
  AFTER UPDATE ON vms
  FOR EACH ROW
  EXECUTE FUNCTION notify_vm_update();
  ```

**Channels**:
- vm_updates: NOTIFY/LISTEN for real-time VM status updates

---

### 4.5 Client VM Startup Sequence Diagram

**Title**: Client VM Startup and Registration

```
┌──────────┐  ┌───────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐
│Terraform │  │ Client VM │  │  Allocator   │  │ PostgreSQL │  │CloudWatch│
│          │  │(cloud-init│  │ (Port 5000)  │  │(Port 5432) │  │  Logs    │
└────┬─────┘  └─────┬─────┘  └──────┬───────┘  └─────┬──────┘  └────┬─────┘
     │              │                │                │               │
     │ Create EC2   │                │                │               │
     ├─────────────►│                │                │               │
     │              │                │                │               │
     │              │ Cloud-init     │                │               │
     │              │ starts         │                │               │
     │              │                │                │               │
     │              │ Install CloudWatch             │               │
     │              │ agent          │                │               │
     │              ├────────────────┼────────────────┼──────────────►│
     │              │                │                │ (create stream│
     │              │                │                │               │
     │              │ POST /api/vm-status            │               │
     │              │ (status: initializing)         │               │
     │              ├───────────────►│                │               │
     │              │                │ UPDATE status  │               │
     │              │                ├───────────────►│               │
     │              │                │                │               │
     │              │ Log: "Starting Docker"         │               │
     │              ├────────────────┼────────────────┼──────────────►│
     │              │                │                │               │
     │              │ Pull Docker    │                │               │
     │              │ image          │                │               │
     │              │                │                │               │
     │              │ Start container│                │               │
     │              │                │                │               │
     │              │ POST /api/vm-status            │               │
     │              │ (status: running)              │               │
     │              ├───────────────►│                │               │
     │              │                │ UPDATE status  │               │
     │              │                ├───────────────►│               │
     │              │                │ NOTIFY         │               │
     │              │                ├───────────────►│               │
     │              │                │                │               │
     │              │ POST /vm_startup               │               │
     │              │ (wait for assignment)          │               │
     │              ├───────────────►│                │               │
     │              │                │ LISTEN         │               │
     │              │                ├───────────────►│               │
     │              │                │ (blocks)       │               │
     │              │                │                │               │
[User assigns VM via web UI]        │                │               │
     │              │                │                │               │
     │              │                │ NOTIFY received│               │
     │              │◄───────────────┼────────────────┤               │
     │              │ Response:      │                │               │
     │              │ {email, crd}   │                │               │
     │              │                │                │               │
     │              │ Execute CRD    │                │               │
     │              │ command        │                │               │
     │              │                │                │               │
     │              │ POST /api/update_inuse_status  │               │
     │              │ (status: true) │                │               │
     │              ├───────────────►│                │               │
     │              │                │ UPDATE in_use  │               │
     │              │                ├───────────────►│               │
     │              │                │                │               │
     │              │ POST /api/vm-metrics           │               │
     │              │ (cloud-init times)             │               │
     │              ├───────────────►│                │               │
     │              │                │ UPDATE metrics │               │
     │              │                ├───────────────►│               │
     │              │                │                │               │
```

---

## 5. Summary

This comprehensive analysis provides complete documentation of:

1. **7 GitHub Workflows** across 2 repositories
   - CI/CD automation for testing, building, publishing, and deployment
   - Comprehensive guardrails for package publishing
   - Multi-environment deployment support (dev, test, prod, ci-test)

2. **22 API Endpoints** in the Flask allocator service
   - 12 public endpoints (no authentication)
   - 10 admin endpoints (HTTP Basic Auth)
   - Complete request/response specifications
   - Database operations per endpoint

3. **Network Architecture** with complete port mapping
   - 10+ network flows with ports and protocols
   - Data payload specifications
   - Sequence diagrams for key operations

4. **Diagram Specifications** for visualization
   - Enhanced network flow diagram
   - CI/CD pipeline diagram
   - API architecture diagram
   - Database schema diagram
   - Client VM startup sequence

**Key Insights**:

- **Port Usage**:
  - External: 22 (SSH), 53 (DNS), 80 (HTTP), 443 (HTTPS)
  - Internal: 5000 (Flask), 5432 (PostgreSQL)
  
- **SSL Strategies**:
  - Let's Encrypt: Caddy handles SSL on EC2 (ports 80/443 → 5000)
  - CloudFlare: CloudFlare proxy handles SSL, Caddy serves HTTP
  - ACM: ALB handles SSL termination, forwards to port 5000
  - None: Direct HTTP access on port 80

- **Logging Pipeline**:
  - Client VMs → CloudWatch Logs (HTTPS 443)
  - CloudWatch → Lambda (subscription filter)
  - Lambda → Allocator (HTTP/HTTPS, POST /api/vm-logs)
  - Allocator → PostgreSQL (port 5432, save logs)

- **Real-time Communication**:
  - PostgreSQL LISTEN/NOTIFY for VM assignment notifications
  - Client VMs wait on `/vm_startup` endpoint
  - Allocator triggers NOTIFY on assignment

- **File Operations**:
  - SSH (port 22) from allocator to client VMs
  - Docker exec to find files in containers
  - Docker cp to extract files to VM filesystem
  - Rsync to transfer files to allocator
  - ZIP compression for download

**Deployment Environments**:
- **dev**: Local development, no S3 backend
- **test**: Test environment, S3 backend, auto-deploy on push
- **prod**: Production environment, S3 backend, manual deploy
- **ci-test**: CI testing environment, S3 backend, separate resources

---

**End of Analysis**
