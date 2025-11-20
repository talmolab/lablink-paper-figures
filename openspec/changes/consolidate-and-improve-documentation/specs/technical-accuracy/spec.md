# Capability: Technical Accuracy of LabLink System Analysis

## Overview

Ensure all analysis documentation accurately reflects the actual LabLink infrastructure and code from the lablink and lablink-template repositories, correcting previous misconceptions and maintaining accuracy as source systems evolve.

## ADDED Requirements

### Requirement: Document PostgreSQL in-container architecture correctly

The system SHALL document that PostgreSQL runs inside the allocator Docker container in all analysis files.

**Rationale**: Critical finding from infrastructure verification - PostgreSQL is NOT AWS RDS.

**Evidence**: `lablink/packages/allocator/Dockerfile` line 13: `RUN apt-get install postgresql postgresql-contrib`

#### Scenario: PostgreSQL architecture in infrastructure analysis

**Given** analysis documents describe LabLink infrastructure
**When** PostgreSQL is mentioned
**Then** it must state "PostgreSQL 15 (in-container)" or "runs inside allocator Docker container"
**And** it must explicitly state "NOT AWS RDS"
**And** it must cite evidence: Dockerfile installation, no aws_db_instance in Terraform
**And** it must state connection is localhost:5432 within container

---

### Requirement: Document Flask API deployment correctly

The system SHALL document that Flask runs only on allocator, not on client VMs.

**Rationale**: Client VMs run Python scripts; Flask confusion led to incorrect diagram icons.

**Evidence**: `lablink/packages/client/pyproject.toml` has no Flask dependency

#### Scenario: Flask deployment in analysis

**Given** analysis describes LabLink services
**When** documenting Flask API
**Then** it must state "Flask API runs in allocator Docker container (port 5000)"
**And** it must state "Client VMs do NOT run Flask"
**And** it must list client VM software: "Python scripts (subscribe.py, check_gpu.py, connect_crd.py)"

---

### Requirement: Document 22 Flask API endpoints accurately

The system SHALL document exactly 22 Flask endpoints across 5 functional groups.

**Rationale**: Verified count from code analysis is 22, not 18 or 20.

**Source**: `lablink/packages/allocator/src/lablink_allocator_service/app.py`

#### Scenario: API endpoint documentation

**Given** analysis documents Flask API
**When** listing endpoints
**Then** it must state "22 endpoints" total
**And** it must organize by 5 functional groups:
  - User Interface: 2 endpoints
  - Query API: 4 endpoints
  - Admin Management: 10 endpoints
  - VM Callbacks: 5 endpoints
  - Lambda Callback: 1 endpoint
**And** it must reference `analysis/api-architecture-analysis.md` as authoritative source

---

### Requirement: Document LabLink CI/CD workflow with OIDC authentication

The system SHALL document the LabLink CI/CD pipeline including OIDC authentication mechanisms.

**Rationale**: CI/CD workflow is one of the 12 diagrams; must accurately represent the actual GitHub Actions workflows in lablink/lablink-template repositories.

**Source**: GitHub Actions workflows in lablink and lablink-template repositories

#### Scenario: Document PyPI OIDC trusted publishing

**Given** analysis documents LabLink package publishing workflow
**When** describing PyPI publishing
**Then** it must state "Uses PyPI trusted publishing with OIDC"
**And** it must explain "No API tokens stored; GitHub Actions authenticates via OIDC"
**And** it must reference `uv publish` command
**And** it must note this eliminates long-lived credentials

#### Scenario: Document AWS OIDC for Terraform operations

**Given** analysis documents LabLink infrastructure deployment
**When** describing Terraform deployment/destruction
**Then** it must state "Uses AWS OIDC with GitHub Actions for keyless authentication"
**And** it must document required secrets:
  - `AWS_ROLE_ARN` - OIDC role for AWS authentication
  - `AWS_REGION` - AWS region (default: us-west-2)
**And** it must document required permissions:
  - `id-token: write` - for OIDC token acquisition
**And** it must explain "Terraform deploy and destroy use OIDC instead of long-lived AWS keys"

---

### Requirement: Document conditional infrastructure components

The system SHALL document that ALB and Route53 are conditional based on SSL provider configuration.

**Rationale**: Not all LabLink deployments include ALB; it depends on `ssl.provider` variable.

**Source**: `lablink-infrastructure/alb.tf` with count conditions

#### Scenario: Document conditional ALB

**Given** analysis describes load balancing
**When** documenting Application Load Balancer
**Then** it must state "Conditional: deployed only when ssl.provider == 'acm'"
**And** it must list conditional components:
  - aws_lb.allocator_alb
  - aws_security_group.alb_sg
  - aws_lb_target_group.allocator_tg
  - aws_lb_listener.http (redirects to HTTPS)
  - aws_lb_listener.https (terminates SSL)
**And** it must document alternative: "When ssl.provider != 'acm', Caddy reverse proxy handles SSL"

---

### Requirement: Document components NOT in LabLink infrastructure

The system SHALL explicitly list AWS services NOT used by LabLink.

**Rationale**: Prevent assumptions about typical cloud architectures.

#### Scenario: Document missing AWS services

**Given** analysis has "What's NOT in Infrastructure" section
**When** listing services not used
**Then** it must state:
  - ❌ AWS RDS (PostgreSQL is in-container)
  - ❌ ElastiCache (no caching layer)
  - ❌ NAT Gateway (direct internet routing)
  - ❌ VPC Peering (single VPC)
  - ❌ S3 for application data (only for Terraform state)

---

### Requirement: Verify analysis against source repositories

The system SHALL reference specific files and line numbers from lablink/lablink-template repos as evidence.

**Rationale**: Ensure analysis is grounded in actual code, not assumptions.

#### Scenario: Cite evidence for infrastructure claims

**Given** analysis makes claims about LabLink infrastructure
**When** documenting infrastructure components
**Then** each claim must cite source:
  - PostgreSQL: `lablink/packages/allocator/Dockerfile:13`
  - Flask endpoints: `lablink/packages/allocator/src/lablink_allocator_service/app.py`
  - Terraform resources: `lablink-infrastructure/main.tf` with resource names
  - Client software: `lablink/packages/client/pyproject.toml`
**And** verification date must be included for time-sensitive analysis

---

## MODIFIED Requirements

None. This adds accuracy requirements without modifying functionality.

---

## REMOVED Requirements

None. This preserves existing analysis capabilities.

---

## Dependencies

### External Repositories (Read-only Reference)
- `lablink` repository - Core LabLink system code
- `lablink-template` repository - Terraform infrastructure code

### Analysis Files (This Repository)
- `analysis/lablink-comprehensive-analysis.md`
- `analysis/infrastructure-verification-2025-11-15.md`
- `analysis/api-architecture-analysis.md`
- `analysis/database-schema-analysis.md`
- `analysis/crd-workflow-corrected.md`

---

## Testing Notes

### Accuracy Verification Process

**For each technical claim:**
1. Identify source file in lablink or lablink-template repo
2. Verify claim against actual code/configuration
3. Cite file path and line number as evidence
4. Note verification date

**PostgreSQL verification:**
```bash
# Verify PostgreSQL installation in Dockerfile
grep -n "postgresql" c:/repos/lablink/packages/allocator/Dockerfile

# Verify no RDS in Terraform
grep -r "aws_db_instance" c:/repos/lablink-template/lablink-infrastructure/
# Should return: no matches
```

**Flask deployment verification:**
```bash
# Verify client has no Flask dependency
grep "flask" c:/repos/lablink/packages/client/pyproject.toml
# Should return: no matches

# Count Flask endpoints in allocator
grep -E "@app\.(route|get|post)" c:/repos/lablink/packages/allocator/src/lablink_allocator_service/app.py | wc -l
# Should return: 22
```

**OIDC verification:**
```bash
# Find GitHub Actions workflows with OIDC
grep -r "id-token: write" c:/repos/lablink/.github/workflows/
grep -r "AWS_ROLE_ARN" c:/repos/lablink-template/.github/workflows/
```

### Checklist

- [ ] PostgreSQL documented as in-container with evidence
- [ ] Flask documented as allocator-only
- [ ] 22 endpoints documented with grouping
- [ ] PyPI OIDC documented for package publishing
- [ ] AWS OIDC documented for Terraform operations
- [ ] Conditional ALB documented
- [ ] Missing services explicitly listed
- [ ] All claims cite source files

---

## Success Metrics

**Quantitative:**
- 100% of infrastructure claims have source citations
- 0 references to "AWS RDS" in positive context
- 22/22 Flask endpoints documented correctly
- 2/2 OIDC mechanisms documented

**Qualitative:**
- Analysis remains accurate as lablink/lablink-template repos evolve
- Evidence-based approach builds confidence in diagram accuracy
- Clear distinction between LabLink system (what we're analyzing) and this repo (figure generation)
