# LabLink Architecture Documentation

This directory contains comprehensive analysis documentation of the **LabLink system** infrastructure and architecture, based on analysis of the [lablink](https://github.com/talmolab/lablink) and [lablink-template](https://github.com/talmolab/lablink-template) repositories.

> **Note**: This documentation analyzes the LabLink system to support figure generation for the academic paper. The actual LabLink source code lives in the lablink/lablink-template repositories.

## Documentation Files

### [Infrastructure Overview](infrastructure.md)
Complete analysis of LabLink's AWS infrastructure, based on Terraform code analysis.

**Key topics**:
- **Allocator Tier**: EC2 instance, Docker container, PostgreSQL (in-container), Flask API, Terraform
- **Client VM Tier**: Dynamically provisioned EC2 instances with GPU/CPU options
- **Conditional Components**: Multiple features based on `config.yaml` settings
  - ALB (when `ssl.provider == "acm"`)
  - Route53 DNS records (when `dns.enabled == true`)
  - EIP strategy (persistent vs dynamic)
  - Custom startup scripts (when `startup_script.enabled == true`)
- **What's NOT used**: RDS, ElastiCache, NAT Gateway, VPC Peering

**Critical findings**:
- ✅ PostgreSQL 15 runs INSIDE allocator Docker container (NOT AWS RDS)
- ✅ Flask API has 22 endpoints across 5 functional groups
- ✅ Client VMs run Python scripts only (NO Flask)
- ✅ Infrastructure is highly configurable via `config.yaml`

### [API Endpoints](api-endpoints.md)
Authoritative documentation of LabLink's 22 Flask API endpoints.

**Functional groups**:
1. User Interface (2 endpoints) - Web UI, status display
2. Query API (4 endpoints) - Status queries, public access
3. Admin Management (10 endpoints) - Authentication, VM lifecycle, admin tasks
4. VM Callbacks (5 endpoints) - Instance registration, metrics, hostname validation
5. Lambda Callback (1 endpoint) - Log processing from CloudWatch

### [Database Schema](database-schema.md)
PostgreSQL database schema running inside allocator container.

**Key tables**:
- `instances` - VM instance records with status, metrics
- `logs` - Application and system logs from CloudWatch
- Configuration and state tables

### [Workflows](workflows.md)
Detailed analysis of LabLink's four key operational workflows.

**Workflows documented**:
1. **CRD Connection** - 15-step PostgreSQL LISTEN/NOTIFY mechanism for real-time desktop connection
2. **VM Provisioning** - Terraform-based provisioning with 3-phase startup sequence
3. **Logging Pipeline** - CloudWatch Agent → Lambda → Allocator API → PostgreSQL
4. **CI/CD Workflow** - GitHub Actions with OIDC authentication (PyPI + AWS)

### [Configuration System](configuration.md)
Analysis of LabLink's hierarchical configuration system (`config.yaml`).

**Key configuration sections**:
- **DNS**: Domain name, Route53 zone management, pattern-based subdomain creation
- **SSL**: Provider selection (none/letsencrypt/cloudflare/acm), email for certs, staging vs production
- **EIP**: Persistent vs dynamic IP allocation strategies
- **Startup Scripts**: Custom VM initialization scripts with error handling
- **Database**: PostgreSQL connection parameters (in-container)
- **Machine**: Client VM type, AMI, Docker image, repository

## Quick Reference

### PostgreSQL Architecture
```
Allocator EC2 Instance
└── Docker Container
    ├── Flask API (port 5000)
    ├── PostgreSQL 15 (localhost:5432) ← IN-CONTAINER
    └── Terraform binary (provisions VMs)
```

**Evidence**: `lablink/packages/allocator/Dockerfile:13`
```dockerfile
RUN apt-get install postgresql postgresql-contrib
```

### Flask API Endpoints
- **Total**: 22 endpoints
- **Groups**: User Interface (2), Query API (4), Admin Management (10), VM Callbacks (5), Lambda Callback (1)
- **Location**: Allocator Docker container only (NOT on client VMs)

### Client VM Software
- **Python scripts**: `subscribe.py`, `check_gpu.py`, `connect_crd.py`
- **NO Flask**: Client VMs do not run Flask API
- **Evidence**: `lablink/packages/client/pyproject.toml` has no Flask dependency

### Conditional Components

LabLink infrastructure is highly configurable. These components are conditionally deployed based on `config.yaml` settings:

| Component | Condition | Config Parameter |
|-----------|-----------|------------------|
| Application Load Balancer (ALB) | `ssl.provider == "acm"` | `ssl.provider` |
| Route53 DNS A Record | `dns.enabled && dns.terraform_managed` | `dns.enabled`, `dns.terraform_managed` |
| Route53 Hosted Zone | `dns.enabled && dns.create_zone` | `dns.create_zone` |
| Persistent EIP | `eip.strategy == "persistent"` | `eip.strategy` |
| Dynamic EIP | `eip.strategy == "dynamic"` | `eip.strategy` |
| Custom Startup Script | `startup_script.enabled` | `startup_script.enabled` |

**SSL Provider Options**:
- `none` - HTTP only (no SSL)
- `letsencrypt` - Caddy with Let's Encrypt auto-SSL
- `cloudflare` - CloudFlare proxy mode
- `acm` - AWS Certificate Manager with ALB

## Analysis Methodology

All architecture documentation follows these principles:

1. **Evidence-based**: Every technical claim cites source code with file:line references
2. **Verified against code**: Analysis cross-checked against actual lablink/lablink-template repositories
3. **Infrastructure-as-code**: Terraform files are source of truth for AWS resources
4. **Configuration-aware**: Documents conditional components based on `config.yaml` settings
5. **Corrects misconceptions**: Explicitly documents what's NOT used (e.g., RDS, ElastiCache)

## Related Documentation

- [Architecture Diagrams](../figures/architecture-diagrams/README.md) - Visual representations of this infrastructure
- [Generating Diagrams](../figures/architecture-diagrams/generating.md) - How to generate diagrams from Terraform
- [Configuration Examples](https://github.com/talmolab/lablink-template/tree/main/lablink-infrastructure/config) - Example config.yaml files for different deployment scenarios

## Recent Updates

- Verified PostgreSQL runs in-container (NOT AWS RDS)
- Documented all 22 Flask API endpoints with functional grouping
- Clarified client VMs run Python scripts only (NO Flask)
- Added comprehensive conditional component documentation based on config.yaml
- Added CI/CD workflow documentation with OIDC authentication
- Consolidated infrastructure verification findings with evidence citations
