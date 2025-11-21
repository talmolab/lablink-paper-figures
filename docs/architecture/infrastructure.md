# LabLink Infrastructure

This document provides a complete inventory of AWS resources and infrastructure components in the LabLink system.

## Architecture Overview

LabLink uses a **two-tier architecture**:

1. **Allocator Tier** - Persistent infrastructure (always running)
   - Single EC2 instance running Flask API + PostgreSQL database
   - Lambda function for log processing
   - CloudWatch log groups

2. **Client VM Tier** - Runtime-provisioned infrastructure (on-demand)
   - Variable number of GPU/CPU EC2 instances
   - Provisioned by Terraform running inside allocator container
   - Destroyed when no longer needed

## Critical Architecture Note: PostgreSQL Database

**PostgreSQL runs INSIDE the allocator Docker container, NOT as a separate AWS RDS instance.**

### Evidence

1. **Dockerfile** (`lablink/packages/allocator/Dockerfile:13`):
   ```dockerfile
   RUN apt-get update && apt-get install -y \
       postgresql postgresql-contrib \
   ```

2. **PostgreSQL Configuration** (`lablink/packages/allocator/Dockerfile:28`):
   ```dockerfile
   COPY pg_hba.conf /etc/postgresql/15/main/pg_hba.conf
   ```

3. **No RDS Resource**: No `aws_db_instance` resource exists in any Terraform file

### Implications

- PostgreSQL 15 is installed and runs locally within the allocator Docker container
- Database connection is `localhost:5432`, not a remote RDS endpoint
- This is a **cost-effective architecture** suitable for research/academic use
- Database lifecycle is tied to the allocator container lifecycle
- No separate database server costs
- No network latency between Flask app and database

## Allocator Tier Components

The allocator tier is the persistent infrastructure that remains running throughout the system's lifetime.

### Core Components

| Component | Terraform Resource | Location | Purpose |
|-----------|-------------------|----------|---------|
| EC2 Instance | `aws_instance.lablink_allocator_server` | main.tf:143-170 | Hosts allocator Docker container |
| Docker Container | user_data.sh | On EC2 instance | Contains Flask + PostgreSQL + Terraform |
| PostgreSQL 15 | Dockerfile apt-get | Inside container | Local database (localhost:5432) |
| Flask API | Python package | Inside container | 22 endpoints, port 5000 |
| Terraform Binary | Dockerfile download | Inside container | v1.4.6, provisions client VMs |
| Lambda Function | `aws_lambda_function.log_processor` | main.tf:336-350 | Log aggregation from client VMs |
| CloudWatch Log Group | `aws_cloudwatch_log_group.client_vm_logs` | main.tf:270-273 | Receives client VM logs |

### Allocator EC2 Instance

**Resource**: `aws_instance.lablink_allocator_server`
**Location**: `lablink-infrastructure/main.tf:143-170`

**Configuration**:
- **AMI**: Ubuntu 24.04 LTS
- **Instance Type**: `t3.large` (2 vCPU, 8 GB RAM)
- **Storage**: 100 GB gp3 volume
- **Public IP**: Allocated (required for user access)
- **Security Group**: `lablink_allocator_sg` (ports 22, 80, 443, 5000)

**User Data Script**:
1. Install Docker
2. Pull allocator Docker image from ECR
3. Start container with environment variables
4. Container startup:
   - Initialize PostgreSQL
   - Create database tables
   - Start Flask application
   - Terraform CLI ready for VM provisioning

### IAM Roles

#### Allocator Instance Role

**Resource**: `aws_iam_role.instance_role`
**Location**: `main.tf:302-313`

**Permissions**:
- S3 access (for Terraform state, if using S3 backend)
- DynamoDB access (for Terraform state locking, if enabled)
- ECR pull (for Docker images)
- CloudWatch Logs write (for allocator logs)

#### Lambda Execution Role

**Resource**: `aws_iam_role.lambda_exec`
**Location**: `main.tf:282-294`

**Permissions**:
- CloudWatch Logs read (for log subscription filter)
- CloudWatch Logs write (for Lambda function logs)

### Lambda Log Processor

**Resource**: `aws_lambda_function.log_processor`
**Location**: `main.tf:336-350`

**Function**:
- Runtime: Python 3.10
- Memory: 128 MB
- Timeout: 60 seconds

**Workflow**:
1. Triggered by CloudWatch Logs subscription filter
2. Receives gzipped/base64-encoded log data
3. Decompresses and parses log entries
4. Extracts hostname from log stream name
5. POSTs structured logs to allocator `/api/vm-logs` endpoint
6. Allocator stores logs in PostgreSQL database

See [workflows.md](workflows.md) for complete logging pipeline details.

## Conditional Components

These components are **conditionally created** based on configuration parameters in `config.yaml`.

### Application Load Balancer (ACM SSL Only)

**Condition**: `ssl.provider == "acm"`

When using AWS Certificate Manager for SSL, an Application Load Balancer is created:

| Component | Terraform Resource | Location | Purpose |
|-----------|-------------------|----------|---------|
| Application Load Balancer | `aws_lb.allocator_alb` | alb.tf:67-81 | SSL termination |
| ALB Security Group | `aws_security_group.alb_sg` | alb.tf:5-37 | Firewall rules |
| Target Group | `aws_lb_target_group.allocator_tg` | alb.tf:84-107 | Routes to allocator EC2 |
| HTTP Listener | `aws_lb_listener.http` | alb.tf:118-133 | Redirects HTTP → HTTPS |
| HTTPS Listener | `aws_lb_listener.https` | alb.tf:136-148 | SSL termination with ACM cert |

**When NOT using ACM** (`ssl.provider == "letsencrypt"` or `"cloudflare"`):
- No ALB is created
- Caddy reverse proxy runs inside allocator container
- Caddy handles SSL termination with Let's Encrypt or Cloudflare

### DNS Configuration

**Condition**: `dns.enabled && dns.terraform_managed`

When DNS is enabled and managed by Terraform:

| Component | Terraform Resource | Purpose |
|-----------|-------------------|---------|
| Route53 Hosted Zone | `aws_route53_zone.main` | DNS zone management |
| Route53 A Record | `aws_route53_record.allocator` | Points domain to allocator IP |

**When NOT Terraform-managed** (`dns.terraform_managed == false`):
- DNS configuration done manually or via external provider
- Terraform does not touch DNS records

### Elastic IP Strategy

**Configuration**: `eip.strategy` (persistent or dynamic)

**Persistent EIP** (`eip.strategy == "persistent"`):
- Resource: `aws_eip.allocator_eip`
- Static IP address allocated
- Survives allocator stop/start
- Recommended for production

**Dynamic IP** (`eip.strategy == "dynamic"`):
- No EIP resource created
- Uses EC2 auto-assigned public IP
- IP changes on instance restart
- Suitable for testing

### Custom Startup Scripts

**Condition**: `startup_script.enabled`

When enabled:
- Custom bash script runs during EC2 instance boot
- Location: Specified in `startup_script.path`
- Use cases: Custom software installation, configuration

## Client VM Tier Components

The client VM tier is **provisioned on-demand** by the allocator using Terraform.

### Client VM Resources

**Provisioned per VM**:

| Component | Terraform Resource | Location | Purpose |
|-----------|-------------------|----------|---------|
| EC2 Instance | `aws_instance.lablink_vm` | terraform/main.tf:61-91 | User workstation |
| Security Group | `aws_security_group.lablink_sg` | terraform/main.tf:10-27 | Firewall (SSH only) |
| IAM Role | `aws_iam_role.cloud_watch_agent_role` | terraform/main.tf:30-45 | CloudWatch permissions |
| IAM Instance Profile | `aws_iam_instance_profile.lablink_instance_profile` | terraform/main.tf:55-58 | Attached to EC2 |

### Client VM EC2 Instance

**Resource**: `aws_instance.lablink_vm`
**Location**: `lablink/packages/allocator/terraform/main.tf:61-91`

**Configuration** (variable):
- **AMI**: Deep Learning AMI (Ubuntu 22.04) - has GPU drivers pre-installed
- **Instance Type**: Variable (e.g., `g4dn.xlarge`, `t3.large`)
  - g4dn.xlarge: 1x NVIDIA T4 GPU, 4 vCPU, 16 GB RAM
  - g4dn.2xlarge: 1x NVIDIA T4 GPU, 8 vCPU, 32 GB RAM
- **Count**: Variable (typically 1-10 VMs)
- **Storage**: 50 GB gp3 volume per VM
- **Public IP**: Allocated (required for Chrome Remote Desktop)

**User Data Script**:
1. Install Docker
2. Pull lablink-client Docker image
3. Start client container
4. Run `subscribe.py` (blocks waiting for user assignment)

### Client VM IAM Role

**Resource**: `aws_iam_role.cloud_watch_agent_role`
**Location**: `terraform/main.tf:30-45`

**Permissions**:
- CloudWatch Logs write (send application logs)
- CloudWatch Metrics write (send GPU metrics)

### Client VM Security Group

**Resource**: `aws_security_group.lablink_sg`
**Location**: `terraform/main.tf:10-27`

**Inbound Rules**:
- Port 22 (SSH): From anywhere (0.0.0.0/0)

**Outbound Rules**:
- All traffic (for package installation, CRD connection)

**Note**: Chrome Remote Desktop uses outbound connections only (no inbound ports needed).

## Network Architecture

### Security Groups

#### Allocator Security Group

**Resource**: `aws_security_group.lablink_allocator_sg`
**Location**: `main.tf` (varies by SSL configuration)

**Inbound Rules**:
- Port 22 (SSH): Administrative access
- Port 80 (HTTP): Web interface or redirect to HTTPS
- Port 443 (HTTPS): Secure web interface
- Port 5000 (Flask): Direct API access (optional, for testing)

**Outbound Rules**:
- All traffic (for Terraform AWS API calls, Docker pulls, etc.)

#### Client VM Security Group

**Resource**: `aws_security_group.lablink_sg`
**Inbound**: SSH only (port 22)
**Outbound**: All traffic

### VPC Configuration

LabLink uses the **default VPC** in the configured AWS region.

**No custom VPC resources**:
- No VPC created by Terraform
- Uses default VPC subnets
- Uses default internet gateway

**Implications**:
- Simpler setup
- Lower cost (no NAT gateway needed)
- All instances have public IPs
- Suitable for small-scale deployments

## Resource Naming Convention

All resources follow a consistent naming pattern:

```
lablink-{component}-{environment}
```

**Examples**:
- `lablink-allocator-prod` - Allocator EC2 instance (production)
- `lablink-client-1` - Client VM #1
- `lablink-log-processor-test` - Lambda function (test environment)

**Environment suffixes**:
- `prod` - Production deployment
- `test` - Testing/staging environment
- `dev` - Development environment

## Infrastructure Provisioning

### Allocator Provisioning

**Method**: Terraform (run locally or in CI/CD)

**Steps**:
1. Clone `lablink-template` repository
2. Configure `config.yaml`
3. Run `terraform init`
4. Run `terraform plan`
5. Run `terraform apply`

**Duration**: ~5 minutes

**Cost**: ~$50-100/month (t3.large + data transfer)

### Client VM Provisioning

**Method**: Terraform (run INSIDE allocator container)

**Trigger**: Admin clicks "Launch VMs" in web interface

**Steps**:
1. Admin specifies count and instance type
2. Flask API calls Terraform subprocess
3. Terraform provisions EC2 instances
4. VMs boot, run subscribe.py
5. VMs wait for user assignment

**Duration**: ~3-5 minutes per batch

**Cost**: Variable by instance type and count
- g4dn.xlarge: ~$0.50/hour (~$360/month if running 24/7)
- Typically run on-demand for workshops (hours to days)

## Monitoring and Logging

### CloudWatch Log Groups

1. **Allocator Logs**:
   - Name: `/aws/ec2/lablink-allocator-{env}`
   - Source: Docker container stdout/stderr
   - Retention: 7 days (configurable)

2. **Client VM Logs**:
   - Name: `lablink-cloud-init-{env}`
   - Source: `/var/log/cloud-init-output.log` on client VMs
   - Retention: 7 days
   - Subscription: Triggers Lambda function

3. **Lambda Logs**:
   - Name: `/aws/lambda/lablink_log_processor_{env}`
   - Source: Lambda function execution
   - Retention: 7 days

### Metrics

**CloudWatch Metrics**:
- EC2 instance metrics (CPU, network, disk)
- Lambda invocation metrics
- ALB request metrics (if using ACM SSL)

**Custom Metrics** (sent by client VMs):
- GPU utilization
- GPU temperature
- GPU memory usage
- Application-level metrics

## Cost Breakdown

### Fixed Costs (Allocator Tier)

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| t3.large EC2 | ~$60 | 2 vCPU, 8 GB RAM |
| 100 GB EBS | ~$10 | gp3 volume |
| Data transfer | ~$10-30 | Variable by usage |
| Lambda invocations | ~$0-1 | Free tier covers most usage |
| **Total** | **~$80-100/month** | Always running |

### Variable Costs (Client VM Tier)

| Instance Type | Hourly Cost | Use Case |
|---------------|-------------|----------|
| g4dn.xlarge | $0.526 | Single GPU, light workloads |
| g4dn.2xlarge | $0.752 | Single GPU, more RAM |
| t3.large | $0.0832 | CPU-only workloads |

**Workshop Example** (5 VMs for 3 days):
- 5x g4dn.xlarge × 72 hours × $0.526 = ~$189
- Plus storage: 5 × 50 GB × $0.10/GB-month × 3/30 days = ~$2.50
- **Total**: ~$191.50 for 3-day workshop

## Terraform State Management

### State Backend

**Configuration**: `backend.tf`

**Options**:
1. **S3 Backend** (recommended for production):
   - State file stored in S3 bucket
   - DynamoDB table for state locking
   - Prevents concurrent modifications
   - Team collaboration support

2. **Local Backend** (development/testing):
   - State file stored locally
   - No locking
   - Single-user only

### State Structure

Two separate Terraform states:

1. **Allocator Infrastructure**:
   - Location: `lablink-infrastructure/`
   - Manages: Allocator EC2, Lambda, CloudWatch, IAM
   - Modified: Rarely (only for infrastructure updates)

2. **Client VMs**:
   - Location: `lablink/packages/allocator/terraform/`
   - Manages: Client EC2 instances and related resources
   - Modified: Frequently (VM provisioning/destruction)

## Disaster Recovery

### Allocator Failure

**Scenario**: Allocator EC2 instance fails

**Recovery**:
1. Terraform recreates EC2 instance from configuration
2. Docker container starts with new PostgreSQL database
3. **Data loss**: All VM assignments and logs lost (database was in-container)
4. Client VMs may still be running but disconnected

**Mitigation**:
- Regular database backups (export PostgreSQL data)
- EBS snapshots of allocator volume (if using persistent EIP)
- External logging (forward logs to external service)

### Client VM Failure

**Scenario**: Client VM crashes or becomes unresponsive

**Recovery**:
1. Admin destroys failed VM via web interface
2. Terraform provisions replacement VM
3. User requests new assignment
4. **Data loss**: User work on failed VM is lost (VMs are ephemeral)

**Mitigation**:
- Users save work to external storage (S3, GitHub, etc.)
- Regular snapshots of user data volumes (if implemented)

## Security Considerations

### Network Security

- All traffic encrypted with HTTPS (ACM or Let's Encrypt)
- Security groups restrict inbound access
- No database exposed to internet (PostgreSQL is localhost-only)

### Authentication

- Admin endpoints: HTTP Basic Auth with bcrypt password hashing
- User endpoints: No authentication (open access for workshop simplicity)
- VM endpoints: Hostname validation (ensures VM exists in database)

### IAM Permissions

- Least privilege principle
- Separate roles for allocator and client VMs
- No overly broad permissions (no `*` actions)

### Secret Management

- AWS credentials stored as environment variables (encrypted at rest)
- Admin password stored as bcrypt hash
- No plaintext secrets in code or logs

## Scalability Limitations

### Current Architecture Limitations

1. **Single allocator instance**: No high availability
   - If allocator fails, entire system unavailable
   - No load balancing across multiple allocators

2. **In-container database**: No data persistence across allocator restarts
   - Database is ephemeral (tied to container lifecycle)
   - No automatic backups

3. **Manual VM provisioning**: Admin must click button to launch VMs
   - No auto-scaling based on demand
   - No queuing system for user requests

4. **Small-scale design**: Suitable for 5-50 users, not thousands
   - Long-polling pattern has one thread per waiting VM
   - Database not optimized for high concurrency

### Scaling Strategies (Future)

**For larger deployments**, consider:

1. **External database**: Migrate PostgreSQL to AWS RDS
   - Data persistence
   - Automatic backups
   - Multi-AZ for high availability

2. **Auto-scaling**: Replace manual provisioning with Auto Scaling Groups
   - Automatically launch VMs based on demand
   - Scale down when idle

3. **Message queue**: Replace long-polling with SQS/SNS
   - Decouple VM waiting from HTTP threads
   - Better scalability for 100+ concurrent users

4. **Multi-region**: Deploy allocators in multiple regions
   - Lower latency for global users
   - Geographic redundancy

## Related Documentation

- [API Endpoints](api-endpoints.md) - All 22 Flask endpoints
- [Database Schema](database-schema.md) - PostgreSQL tables and schema
- [Workflows](workflows.md) - CRD connection, VM provisioning, logging workflows
- [Configuration](configuration.md) - config.yaml parameters

## Diagram Generation

To regenerate infrastructure diagrams:

```bash
# Complete infrastructure overview
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type architecture-detailed \
  --preset poster

# Network flow diagram
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type network-flow \
  --preset poster

# Logging pipeline
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir ../lablink-template/lablink-infrastructure \
  --diagram-type logging-pipeline \
  --preset poster
```
