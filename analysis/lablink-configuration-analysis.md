# LabLink Configuration Analysis

**Analysis Date:** 2025-11-15
**Updated:** 2026-03-31 (deployment_name+environment, CLI wizard, new monitoring config, logging changes)
**Purpose:** Comprehensive documentation of all configuration parameters in LabLink infrastructure
**Sources:** lablink CLI config (~/.lablink/config.yaml), lablink-template/lablink-infrastructure config.yaml, terraform.runtime.tfvars, LabLink allocator code

---

## Executive Summary

LabLink's configurability is organized into multiple layers that allow deployment flexibility across different environments, security postures, compute requirements, and application needs. Configuration parameters span:

- **Infrastructure layer** (config.yaml): Core parameters for deployment identity, SSL, authentication, AWS setup, and monitoring
- **Runtime layer** (terraform.runtime.tfvars): Parameters for VM provisioning and application configuration
- **Conditional resources**: Components that are created based on configuration choices
- **Auto-detected parameters**: Values derived from other settings (e.g., GPU support from machine type)

This multi-layered approach enables LabLink to serve use cases ranging from local development to enterprise production deployments.

> **Major Changes Since Nov 2025 (PR #284, #296):**
> - `resource_suffix` replaced by `deployment_name` + `environment` for multi-tenant isolation
> - New CLI tool provides TUI wizard (`lablink configure`) as alternative to manual config editing
> - Config file location: `~/.lablink/config.yaml` (CLI) or `lablink-infrastructure/config/config.yaml` (template)
> - New monitoring config section: budget alerts, CloudTrail, CloudWatch alarms
> - CloudWatch logging config removed (replaced by self-hosted log shipper)

---

## Table of Contents

1. [Configuration Layers Overview](#1-configuration-layers-overview)
2. [Infrastructure Layer (config.yaml)](#2-infrastructure-layer-configyaml)
3. [Runtime Layer (terraform.runtime.tfvars)](#3-runtime-layer-terraformruntimetfvars)
4. [Derived and Auto-Detected Parameters](#4-derived-and-auto-detected-parameters)
5. [Conditional Infrastructure Components](#5-conditional-infrastructure-components)
6. [Configuration Decision Tree](#6-configuration-decision-tree)
7. [Configuration Validation](#7-configuration-validation)
8. [Common Configuration Patterns](#8-common-configuration-patterns)

---

## 1. Configuration Layers Overview

LabLink configuration is organized into three primary layers:

### 1.1 Infrastructure Layer
**File:** `~/.lablink/config.yaml` (CLI tool) or `lablink-infrastructure/config/config.yaml` (template repo)
**Purpose:** Persistent infrastructure configuration that defines how the allocator server is deployed
**Scope:** Set once per environment, rarely changes
**Managed by:** System administrators (via TUI wizard or manual editing)

### 1.2 Runtime Layer
**File:** Generated as `terraform.runtime.tfvars` by allocator at VM provisioning time
**Purpose:** Dynamic configuration for client VM provisioning
**Scope:** Can change with each VM provisioning request
**Managed by:** Allocator service (based on user requests and admin settings)

### 1.3 Derived Layer
**Source:** Computed from other configuration values
**Purpose:** Automatic parameter derivation to reduce configuration complexity
**Examples:** GPU support detection, allocator URL generation, log group naming

---

## 2. Infrastructure Layer (config.yaml)

### 2.1 SSL Provider Configuration

**Parameter:** `ssl_provider`
**Type:** Enum: `none` | `letsencrypt` | `cloudflare` | `acm`
**Required:** Yes
**Default:** None (must be explicitly set)

**Purpose:** Determines SSL/TLS termination strategy and network routing architecture.

**Options:**

#### `none` - Direct HTTP Access
- **Use case:** Local development, testing
- **Network path:** User → HTTP:80 → Allocator:5000
- **Components:** No additional components required
- **Ports:** 80 (HTTP only)
- **Considerations:** No encryption, not suitable for production

#### `letsencrypt` - Caddy with Automatic SSL
- **Use case:** Production deployments with automatic certificate management
- **Network path:** User → HTTPS:443 → Caddy → HTTP:5000 → Allocator
- **Components:** Caddy reverse proxy installed on allocator EC2 instance
- **Ports:** 80 (HTTP redirect), 443 (HTTPS)
- **SSL termination:** Caddy (automatic Let's Encrypt certificates)
- **Requirements:** Public domain name, Route53 DNS entry
- **Considerations:** Certificate auto-renewal, 90-day expiry

#### `cloudflare` - CloudFlare Proxy
- **Use case:** Production with CloudFlare CDN/DDoS protection
- **Network path:** User → CloudFlare → HTTP:80 → Caddy → HTTP:5000 → Allocator
- **Components:** Caddy for local routing, CloudFlare handles SSL externally
- **Ports:** 80 (HTTP from CloudFlare), CloudFlare manages 443
- **SSL termination:** CloudFlare (external to AWS)
- **Requirements:** CloudFlare account, domain configuration
- **Considerations:** Additional latency from CloudFlare proxy, DDoS protection

#### `acm` - AWS Certificate Manager with ALB
- **Use case:** Enterprise production with AWS-native SSL
- **Network path:** User → HTTPS:443 → ALB → HTTP:5000 → Allocator
- **Components:** Application Load Balancer (ALB), ACM certificate
- **Ports:** 80 (redirect to 443), 443 (HTTPS)
- **SSL termination:** ALB
- **Requirements:** ACM certificate ARN, Route53 DNS
- **Additional resources:** ALB, target groups, listener rules
- **Considerations:** Higher AWS costs, AWS-native integration

**Code references:**
- SSL strategy evaluation: `lablink-infrastructure/main.tf` (conditional resource creation)
- Caddy installation: `lablink-infrastructure/user_data.sh`
- ALB configuration: `lablink-infrastructure/alb.tf`

---

### 2.2 Deployment Identity (Updated 2026-03, PR #296)

#### Deployment Name

**Parameter:** `deployment_name`
**Type:** String (3-32 chars, kebab-case)
**Required:** Yes
**Example:** `sleap-lablink`

**Purpose:** Unique identifier for a LabLink deployment. Enables multiple independent deployments in the same AWS account. Used as the primary component in resource naming and Terraform state scoping.

**Validation:** Must be 3-32 characters, kebab-case (lowercase letters, numbers, hyphens).

#### Environment

**Parameter:** `environment`
**Type:** Enum: `dev` | `test` | `ci-test` | `prod`
**Required:** Yes

**Purpose:** Defines the deployment environment and associated policies.

**Environments:**

#### `dev` - Local Development
- **S3 backend:** No (local Terraform state)
- **Deployment trigger:** Manual only
- **SSL provider:** Typically `none`
- **Use case:** Local testing, rapid iteration

#### `test` - Test Environment
- **S3 backend:** Yes (shared state)
- **Deployment trigger:** Automatic on push to `test` branch
- **SSL provider:** Typically `letsencrypt` or `none`
- **Use case:** Integration testing, staging

#### `prod` - Production
- **S3 backend:** Yes (shared state with locking)
- **Deployment trigger:** Manual workflow dispatch only
- **SSL provider:** Typically `letsencrypt`, `cloudflare`, or `acm`
- **Use case:** Live production workloads

#### `ci-test` - CI Testing
- **S3 backend:** Yes (isolated resources)
- **Deployment trigger:** CI/CD pipeline
- **SSL provider:** Typically `none`
- **Use case:** Automated testing in CI

**Resource naming convention:**
- Allocator resources: `{deployment_name}-{resource_type}-{environment}` (e.g., `sleap-lablink-sg-prod`)
- Client VM resources: `{software}-lablink-client-{environment}` (e.g., `sleap-lablink-client-prod-1`)
- Terraform state key: `{deployment_name}/{environment}/terraform.tfstate`
- S3 bucket: Account-scoped with path-based isolation (`lablink-tf-state-{account_id}`)

---

### 2.3 Authentication Configuration

#### Admin Credentials

**Parameters:**
- `admin_username`: String (e.g., "admin")
- `admin_password`: String (bcrypt hashed)

**Purpose:** HTTP Basic Authentication for admin endpoints.

**Security:**
- Passwords stored as bcrypt hashes in config.yaml
- Verified via `verify_password()` function in Flask app
- Required for all `/admin/*` and `/api/admin/*` endpoints

**Protected operations:**
- VM provisioning (`POST /api/launch`)
- VM destruction (`POST /destroy`)
- AWS credential management
- Data download (`GET /api/scp-client`)
- Log access (`GET /admin/logs/<hostname>`)

#### Database Password

**Parameter:** `database_password`
**Type:** String
**Purpose:** PostgreSQL RDS authentication

**Usage:**
- Allocator → PostgreSQL connection
- Generated during initial deployment
- Stored in config.yaml (injected from GitHub secrets in CI/CD)

---

### 2.4 AWS Configuration

#### AWS Credentials

**Parameters:**
- `aws_access_key_id`: String (e.g., "AKIA...")
- `aws_secret_access_key`: String (secret)
- `aws_region`: String (e.g., "us-west-2")

**Purpose:** Terraform AWS provider authentication for infrastructure provisioning.

**Scope:**
- Infrastructure deployment (lablink-infrastructure/)
- Client VM provisioning (runtime Terraform operations)
- S3 state backend access
- AWS service interactions (EC2, RDS, CloudWatch, Lambda)

**Security:**
- Credentials injected from GitHub secrets in CI/CD workflows
- Not committed to version control
- Can be updated via `/api/admin/set-aws-credentials` endpoint

#### Terraform State Backend

**Parameter:** `bucket_name`
**Type:** String
**Purpose:** S3 bucket name for Terraform state storage

**Usage:**
- Enabled for `test`, `prod`, `ci-test` environments
- Disabled for `dev` (local state)
- Supports state locking via DynamoDB
- Enables multi-user collaboration

---

## 3. Runtime Layer (terraform.runtime.tfvars)

Runtime configuration is generated dynamically by the allocator when provisioning client VMs. Parameters are written to `terraform.runtime.tfvars` and passed to Terraform.

> **Note (2026-03):** `resource_suffix` has been replaced by `resource_prefix` (derived from `deployment_name` + `environment`). The `cloud_init_output_log_group` parameter has been removed since logging no longer uses CloudWatch.

### 3.1 Compute Configuration

#### Machine Type

**Parameter:** `machine_type`
**Type:** String
**Examples:** `g4dn.xlarge`, `p3.8xlarge`, `t3.medium`, `t3.large`

**Purpose:** AWS EC2 instance type for client VMs.

**Common options:**

**GPU Instances:**
- `g4dn.xlarge` - 1 NVIDIA T4 GPU, 4 vCPUs, 16 GB RAM (cost-effective)
- `g4dn.2xlarge` - 1 NVIDIA T4 GPU, 8 vCPUs, 32 GB RAM
- `p3.2xlarge` - 1 NVIDIA V100 GPU, 8 vCPUs, 61 GB RAM (high-performance)
- `p3.8xlarge` - 4 NVIDIA V100 GPUs, 32 vCPUs, 244 GB RAM (multi-GPU)

**CPU Instances:**
- `t3.medium` - 2 vCPUs, 4 GB RAM (lightweight)
- `t3.large` - 2 vCPUs, 8 GB RAM
- `t3.xlarge` - 4 vCPUs, 16 GB RAM

**Selection criteria:**
- GPU requirement of target application (e.g., SLEAP requires GPU)
- Cost constraints
- Performance requirements
- Availability in selected AWS region

**Code reference:** Machine type evaluation: `packages/allocator/src/lablink_allocator_service/main.py` (`check_support_nvidia()`)

---

#### GPU Support

**Parameter:** `gpu_support`
**Type:** Boolean (`"true"` | `"false"` as strings)
**Auto-detected:** Yes (based on machine_type)

**Purpose:** Determines whether to provision GPU-enabled Docker images and drivers.

**Detection logic:**
```python
def check_support_nvidia(machine_type: str) -> bool:
    """Check if machine type supports NVIDIA GPUs."""
    gpu_instance_families = ['g4dn', 'g5', 'p3', 'p4']
    return any(family in machine_type.lower() for family in gpu_instance_families)
```

**Effects when `true`:**
- Uses GPU-enabled Docker base image
- Installs NVIDIA drivers via cloud-init
- Enables `check_gpu` monitoring service
- Runs `nvidia-smi` health checks every 20s

**Effects when `false`:**
- Uses CPU-only Docker base image
- Skips GPU driver installation
- GPU health monitoring reports "N/A"

---

#### Instance Count

**Parameter:** `instance_count`
**Type:** Integer
**Passed as:** Terraform command-line variable (`-var=instance_count=N`)

**Purpose:** Number of client VMs to provision in a single Terraform apply operation.

**Calculation:**
```
instance_count = requested_vms + current_vm_count
```

**Constraints:**
- Must be > 0
- Limited by AWS account quotas for EC2 instances
- Limited by available Elastic IPs (if using persistent EIP strategy)

**Code reference:** `POST /api/launch` endpoint calculates total: `num_vms + database.get_row_count()`

---

### 3.2 Application Configuration

#### Subject Software

**Parameter:** `subject_software`
**Type:** String
**Examples:** `"sleap"`, `"deeplabcut"`, `"custom-app"`

**Purpose:** Identifies the target application for usage monitoring.

**Usage:**
- `update_inuse_status` service monitors for process matching this name
- Process list checked every 20s: `ps aux | grep <subject_software>`
- Updates `inuse` boolean in PostgreSQL when process state changes
- Enables usage tracking for billing/analytics

**Example:**
- `subject_software = "sleap"` → Monitors for `sleap` process
- When SLEAP launches → `inuse = true`
- When SLEAP exits → `inuse = false`

---

#### Repository

**Parameter:** `repository`
**Type:** String (Git repository URL)
**Example:** `"https://github.com/talmolab/sleap-tutorial-data.git"`

**Purpose:** Git repository cloned into `/workspace` directory of client VMs.

**Behavior:**
- Cloned during cloud-init startup
- Available to user immediately upon connection
- Can contain tutorial data, example scripts, or application code
- Enables pre-populated workspace for users

**Typical use cases:**
- SLEAP tutorial data for workshops
- Custom analysis scripts
- Application-specific configuration files

---

#### File Extension

**Parameter:** `file_extension`
**Type:** String (with leading dot)
**Example:** `".slp"` (SLEAP project files), `".h5"` (HDF5 data files)

**Purpose:** Filter for data collection when admin downloads files from VMs.

**Usage in data collection flow:**
1. Admin clicks "Download Data" in web UI
2. Allocator SSHs to each VM
3. Runs: `docker exec client-container find /workspace -name '*<extension>'`
4. Copies matching files from VMs to allocator
5. Creates ZIP archive with collected files

**Common extensions:**
- `.slp` - SLEAP project files
- `.h5` - HDF5 data files
- `.mp4` - Video files
- `.csv` - Analysis results

---

#### Startup Error Handling

**Parameter:** `startup_on_error`
**Type:** Enum: `"continue"` | `"fail"`

**Purpose:** Defines VM behavior when cloud-init provisioning encounters errors.

**Options:**

**`continue`** - Robust mode (default for workshops)
- VM continues startup even if some provisioning steps fail
- Allows partial functionality
- Useful when network issues or repository clone failures shouldn't block VM access
- Enables troubleshooting via remote desktop

**`fail`** - Strict mode (default for production)
- VM startup fails immediately on any error
- Terraform apply reports failure
- Prevents partially-configured VMs
- Ensures consistency

**Code reference:** Passed to cloud-init script in `packages/allocator/src/lablink_allocator_service/terraform/main.tf`

---

### 3.3 Docker and AMI Configuration

#### Docker Image Name

**Parameter:** `image_name`
**Type:** String (Docker image reference)
**Examples:**
- `"ghcr.io/talmolab/lablink-client-base-image:linux-amd64-latest-test"`
- `"ghcr.io/talmolab/lablink-client-base-image:linux-amd64-v1.2.3"`

**Purpose:** Specifies which Docker image to pull and run on client VMs.

**Image variants:**
- **Test images** (suffix `-test`): Built from source during CI, includes dev dependencies
- **Production images**: Built from published PyPI packages, minimal dependencies
- **GPU images**: Include CUDA libraries and NVIDIA container runtime
- **CPU images**: Lightweight, no GPU dependencies

**Selection logic:**
- Test/CI environments → `-test` suffix images
- Production → Versioned release images
- GPU machine types → GPU-enabled base image
- CPU machine types → CPU-only base image

---

#### Client AMI ID

**Parameter:** `client_ami_id`
**Type:** String (AWS AMI identifier)
**Example:** `"ami-0601752c11b394251"` (Ubuntu 22.04 in us-west-2)

**Purpose:** Base Amazon Machine Image for client VM EC2 instances.

**Requirements:**
- Must support Docker installation
- Must support cloud-init
- Should match selected AWS region
- Typically Ubuntu 22.04 LTS or newer

**Region-specific:**
- Different AMI IDs for each AWS region
- Must be updated when changing `region` parameter

---

### 3.4 Network Configuration

#### Allocator IP

**Parameter:** `allocator_ip`
**Type:** String (IPv4 address)
**Source:** Terraform output from infrastructure deployment

**Purpose:** IP address of allocator server for client VMs to communicate with.

**Usage:**
- Client VMs use this IP to:
  - POST status updates (`/api/vm-status`)
  - POST GPU health (`/api/gpu_health`)
  - POST usage status (`/api/update_inuse_status`)
  - POST timing metrics (`/api/vm-metrics/<hostname>`)
  - GET CRD command via database LISTEN/NOTIFY

**Generation:** Retrieved from Terraform output of infrastructure deployment (Elastic IP or dynamic IP)

---

#### Allocator URL

**Parameter:** `allocator_url`
**Type:** String (HTTP/HTTPS URL)
**Examples:**
- `"http://203.0.113.42"` (when ssl_provider=none)
- `"https://allocator.example.com"` (when SSL enabled)

**Purpose:** Full URL for client VMs to reach allocator API endpoints.

**Generation logic:**
```python
def get_allocator_url(cfg, allocator_ip):
    if cfg.ssl.provider in ['letsencrypt', 'cloudflare', 'acm']:
        return f"https://{cfg.domain.name}"
    else:
        return f"http://{allocator_ip}"
```

**Usage:** Client services construct API endpoints by appending paths (e.g., `{allocator_url}/api/vm-status`)

---

### 3.5 Logging Configuration

#### ~~CloudWatch Log Group~~ (Removed)

> **Removed in PR #279 (2026-03).** The `cloud_init_output_log_group` parameter no longer exists. Logging now uses a self-hosted `log_shipper.sh` that ships logs directly to the allocator.

**Current log flow:**
1. Client VM cloud-init → `/var/log/cloud-init-output.log` → `log_shipper.sh` → Allocator (`POST /api/vm-logs`)
2. Client VM Docker container → json-logs → `log_shipper.sh` → Allocator (`POST /api/vm-logs`)
3. Allocator → PostgreSQL (`cloudinitlogs` + `dockerlogs` columns)

**New parameter:** `api_token` — Auto-generated Bearer token passed to client VMs for authenticated log shipping.

---

#### AWS Region

**Parameter:** `region`
**Type:** String
**Example:** `"us-west-2"`, `"us-east-1"`, `"eu-west-1"`

**Purpose:** AWS region for client VM resources.

**Scope:**
- EC2 instance placement
- AMI selection (must use region-specific AMI)
- CloudWatch Logs region
- Availability zone selection

**Considerations:**
- Must match infrastructure deployment region
- Affects latency to allocator
- Pricing varies by region
- GPU instance availability varies by region

---

## 4. Derived and Auto-Detected Parameters

### 4.1 GPU Support Detection

**Derived from:** `machine_type`
**Algorithm:** Pattern matching against GPU instance families

```python
gpu_instance_families = ['g4dn', 'g5', 'p3', 'p4', 'p5']
gpu_support = any(family in machine_type.lower() for family in gpu_instance_families)
```

**Impact:**
- Docker image selection (GPU vs CPU base image)
- NVIDIA driver installation
- GPU health monitoring enablement

---

### 4.2 Allocator URL Generation

**Derived from:** `ssl_provider`, `allocator_ip`, `domain.name`

**Logic:**
- SSL enabled (`letsencrypt`, `cloudflare`, `acm`) → `https://{domain}`
- SSL disabled (`none`) → `http://{allocator_ip}`

**Purpose:** Ensures client VMs use correct protocol and hostname

---

### 4.3 ~~Log Group Naming~~ (Removed)

> **Removed in PR #279.** CloudWatch log groups are no longer used. Logging is handled by self-hosted log shipper.

---

### 4.4 Resource Naming (Updated PR #296)

**Derived from:** `deployment_name` + `environment` (+ `software` for client VMs)

**Allocator resources pattern:** `{deployment_name}-{resource_type}-{environment}`
**Client VM resources pattern:** `{software}-lablink-client-{environment}-{index}`

**Examples (deployment_name=sleap-lablink, environment=prod):**
- Allocator security group: `sleap-lablink-sg-prod`
- Allocator EC2: `sleap-lablink-allocator-prod`
- Client EC2 instances: `sleap-lablink-client-prod-1`
- Client security group: `sleap-lablink-client-sg-prod`
- Terraform state key: `sleap-lablink/prod/terraform.tfstate`
- S3 bucket: `lablink-tf-state-{account_id}` (account-scoped, shared)

---

## 5. Conditional Infrastructure Components

### 5.1 SSL-Dependent Resources

#### When `ssl_provider = "acm"`
**Created:**
- Application Load Balancer (ALB)
- ALB target group
- HTTPS listener (port 443)
- HTTP listener (port 80, redirect to 443)
- ALB security group

**Not created:**
- Caddy proxy installation
- Route53 DNS (optional, can be manual)

**Code reference:** `lablink-infrastructure/alb.tf` with `count = local.ssl_provider == "acm" ? 1 : 0`

---

#### When `ssl_provider = "letsencrypt" | "cloudflare"`
**Created:**
- Caddy installation via user_data.sh
- Route53 A record (if terraform_managed = true)

**Not created:**
- ALB infrastructure

**Code reference:** `lablink-infrastructure/user_data.sh` (conditional Caddy install)

---

#### When `ssl_provider = "none"`
**Created:**
- Direct port 80 access to allocator

**Not created:**
- ALB
- Caddy
- Route53 DNS entries

---

### 5.2 Environment-Dependent Resources

#### When `resource_suffix != "dev"`
**Created:**
- S3 backend configuration
- DynamoDB table for state locking
- Remote state management

**Code reference:** `backend.tf` generation in deployment workflows

---

#### When `resource_suffix = "dev"`
**Created:**
- Local Terraform state file

**Not created:**
- S3 bucket
- DynamoDB table

---

## 6. Configuration Decision Tree

### Level 0: Deployment Identity (New)

```
Choose deployment_name:
└─ Unique kebab-case name (3-32 chars), e.g., "sleap-lablink", "dlc-workshop"
   └─ Enables multi-tenant isolation in same AWS account
```

### Level 1: Environment Selection

```
Choose environment:
├─ dev    → Local state, no S3, manual deploy, ssl=none
├─ test   → S3 state, auto-deploy on push, ssl=letsencrypt or none
├─ prod   → S3 state, manual deploy, ssl=letsencrypt/cloudflare/acm
└─ ci-test → S3 state, CI deploy, ssl=none
```

### Level 2: SSL Strategy

```
Choose ssl_provider based on environment:
├─ none         → Development only, HTTP:80
├─ letsencrypt  → Production, automatic certs, Caddy proxy
├─ cloudflare   → Production, CloudFlare CDN, DDoS protection
└─ acm          → Enterprise, AWS-native, ALB + ACM certificate
    └─ requires: certificate_arn, Route53, ALB configuration
```

### Level 3: Compute Resources

```
Choose machine_type based on application:
├─ GPU Required (SLEAP, DeepLabCut, ML workflows)
│  ├─ Cost-effective  → g4dn.xlarge (1 GPU)
│  ├─ High-performance → p3.2xlarge (1 V100)
│  └─ Multi-GPU       → p3.8xlarge (4 V100s)
│     └─ auto-sets: gpu_support = true
└─ CPU Only (data processing, visualization)
   ├─ Lightweight → t3.medium
   ├─ Standard    → t3.large
   └─ Heavy       → t3.xlarge
      └─ auto-sets: gpu_support = false
```

### Level 4: Application Settings

```
Choose application configuration:
├─ SLEAP
│  ├─ subject_software = "sleap"
│  ├─ file_extension = ".slp"
│  └─ repository = sleap-tutorial-data
├─ DeepLabCut
│  ├─ subject_software = "deeplabcut"
│  ├─ file_extension = ".h5"
│  └─ repository = deeplabcut-examples
└─ Custom
   ├─ subject_software = custom process name
   ├─ file_extension = custom extension
   └─ repository = custom Git repo
```

### Level 5: Scaling and Reliability

```
Configure scaling:
├─ instance_count: 1-N VMs
└─ startup_on_error:
   ├─ continue → Workshop/demo mode (robust)
   └─ fail     → Production mode (strict)
```

---

## 7. Configuration Validation

### 7.1 Validation Workflow

**Workflow:** `.github/workflows/config-validation.yml`

**Triggers:**
- Pull requests modifying `config.yaml`
- Manual workflow dispatch

**Validation steps:**
1. Run `lablink-validate-config` CLI tool
2. Check required fields present
3. Validate ssl_provider enum
4. Validate resource_suffix format
5. Check AWS credentials format (if provided)

**Code reference:** `lablink-validate-config` command (implemented in lablink packages)

---

### 7.2 Required Parameters

**config.yaml (infrastructure layer):**
- `ssl_provider` ✓
- `resource_suffix` ✓
- `admin_username` ✓
- `admin_password` ✓
- `database_password` ✓

**terraform.runtime.tfvars (runtime layer):**
- `allocator_ip` ✓
- `allocator_url` ✓
- `machine_type` ✓
- `image_name` ✓
- `repository` ✓
- `client_ami_id` ✓
- `subject_software` ✓
- `resource_suffix` ✓
- `gpu_support` ✓
- `cloud_init_output_log_group` ✓
- `region` ✓
- `startup_on_error` ✓

---

### 7.3 Conditional Requirements

**If `ssl_provider = "acm"`:**
- `certificate_arn` required
- Route53 configuration required

**If `resource_suffix != "dev"`:**
- `bucket_name` required for S3 backend

---

## 8. Common Configuration Patterns

### 8.1 Local Development

```yaml
# config.yaml
ssl_provider: none
resource_suffix: dev
admin_username: admin
admin_password: <bcrypt_hash>
# No S3 backend needed
```

```hcl
# terraform.runtime.tfvars
machine_type = "t3.medium"
gpu_support = "false"
subject_software = "sleap"
repository = "https://github.com/talmolab/sleap-tutorial-data.git"
startup_on_error = "continue"
```

**Characteristics:**
- Fast iteration
- No SSL overhead
- Minimal AWS costs
- Local Terraform state

---

### 8.2 Workshop/Tutorial Deployment

```yaml
# config.yaml
ssl_provider: letsencrypt
resource_suffix: test
admin_username: workshop-admin
# Auto-deploy on push to test branch
```

```hcl
# terraform.runtime.tfvars
machine_type = "g4dn.xlarge"
gpu_support = "true"
subject_software = "sleap"
repository = "https://github.com/talmolab/sleap-tutorial-data.git"
file_extension = ".slp"
startup_on_error = "continue"  # Robust for workshops
instance_count = 20  # Support 20 participants
```

**Characteristics:**
- GPU-enabled for SLEAP
- Automatic SSL certificates
- Resilient startup (continue on error)
- Pre-loaded tutorial data

---

### 8.3 Production Research Deployment

```yaml
# config.yaml
ssl_provider: acm
resource_suffix: prod
admin_username: admin
# Requires ACM certificate ARN
# Manual deployment only
```

```hcl
# terraform.runtime.tfvars
machine_type = "p3.8xlarge"
gpu_support = "true"
subject_software = "sleap"
repository = "https://github.com/research-lab/analysis-scripts.git"
file_extension = ".h5"
startup_on_error = "fail"  # Strict validation
instance_count = 5
```

**Characteristics:**
- Multi-GPU instances
- AWS-native SSL (ALB + ACM)
- Strict startup validation
- Research-specific repository

---

### 8.4 Enterprise with CloudFlare

```yaml
# config.yaml
ssl_provider: cloudflare
resource_suffix: prod
admin_username: it-admin
# CloudFlare handles SSL, DDoS protection
```

```hcl
# terraform.runtime.tfvars
machine_type = "g5.4xlarge"  # Latest GPU generation
gpu_support = "true"
subject_software = "custom-app"
repository = "https://github.com/enterprise/proprietary-tools.git"
file_extension = ".dat"
startup_on_error = "fail"
instance_count = 10
```

**Characteristics:**
- CloudFlare DDoS protection
- Latest GPU hardware
- Custom application
- Enterprise-grade security

---

## Appendix A: Configuration Parameter Reference

### Infrastructure Layer (config.yaml)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `deployment_name` | String | Yes | - | Unique deployment identifier (3-32 chars, kebab-case) |
| `environment` | Enum | Yes | - | Environment: dev, test, prod, ci-test |
| `ssl_provider` | Enum | Yes | - | SSL strategy: none, letsencrypt, cloudflare, acm |
| `admin_username` | String | Yes | - | Admin HTTP Basic Auth username |
| `admin_password` | String | Yes | - | Admin password (bcrypt hash) |
| `database_password` | String | Yes | - | PostgreSQL password |
| `aws_access_key_id` | String | Yes | - | AWS access key |
| `aws_secret_access_key` | String | Yes | - | AWS secret key |
| `aws_region` | String | Yes | - | AWS region (e.g., us-west-2) |
| `bucket_name` | String | Conditional | - | S3 bucket for Terraform state (if not dev) |
| `domain.name` | String | Conditional | - | Domain name (if SSL enabled) |
| `certificate_arn` | String | Conditional | - | ACM certificate ARN (if ssl_provider=acm) |

### Runtime Layer (terraform.runtime.tfvars)

| Parameter | Type | Required | Auto-Detected | Description |
|-----------|------|----------|---------------|-------------|
| `allocator_ip` | String | Yes | Yes | Allocator EC2 IP address |
| `allocator_url` | String | Yes | Yes | Full allocator URL (HTTP/HTTPS) |
| `machine_type` | String | Yes | No | EC2 instance type |
| `gpu_support` | Boolean | Yes | Yes | GPU availability (from machine_type) |
| `image_name` | String | Yes | No | Docker image reference |
| `client_ami_id` | String | Yes | No | AWS AMI ID |
| `repository` | String | Yes | No | Git repository URL |
| `subject_software` | String | Yes | No | Application process name |
| `resource_prefix` | String | Yes | Yes | Resource naming prefix (from deployment_name + environment) |
| `api_token` | String | Yes | Yes | Bearer token for VM-to-allocator auth |
| `region` | String | Yes | No | AWS region |
| `startup_on_error` | Enum | Yes | No | Error handling: continue, fail |
| `file_extension` | String | No | No | File extension for data collection |
| `instance_count` | Integer | Yes | No | Number of VMs (CLI arg) |

---

## Appendix B: Code References

### Configuration Loading
- `packages/allocator/src/lablink_allocator_service/conf/structured_config.py` - Shared config schema
- `packages/cli/src/lablink_cli/config/schema.py` - CLI config validation
- `lablink-infrastructure/config/config.yaml` - Infrastructure config template (template repo)
- `~/.lablink/config.yaml` - Default config location (CLI tool)

### Configuration Usage
- `packages/allocator/src/lablink_allocator_service/main.py` - Runtime tfvars generation
- `packages/allocator/src/lablink_allocator_service/terraform/main.tf` - Terraform variables
- `packages/cli/src/lablink_cli/commands/deploy.py` - CLI deployment

### Validation
- `.github/workflows/config-validation.yml` - CI validation workflow (template repo)
- `packages/cli/src/lablink_cli/config/schema.py` - CLI config validation

### SSL Configuration
- `packages/cli/src/lablink_cli/terraform/main.tf` - Conditional resource creation (CLI)
- `packages/cli/src/lablink_cli/terraform/alb.tf` - ALB configuration (ssl_provider=acm)
- `lablink-infrastructure/main.tf` - Conditional resource creation (template repo)
- `lablink-infrastructure/alb.tf` - ALB configuration (template repo)

### TUI Wizard (New)
- `packages/cli/src/lablink_cli/tui/wizard.py` - Textual-based configuration wizard
- Guides admin through: deployment name, environment, AWS region, machine type, DNS, SSL, monitoring

---

**Document Version:** 2.0
**Last Updated:** 2026-03-31
**Maintained by:** LabLink Documentation Team
