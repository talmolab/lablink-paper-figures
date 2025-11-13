# LabLink Comprehensive Architecture Analysis

## Executive Summary

This document provides a complete architectural understanding of LabLink based on analysis of multiple repositories. This analysis revealed critical misunderstandings in the initial diagram implementation that need to be addressed.

## Repository Structure

### Infrastructure Repositories
1. **lablink-template/lablink-infrastructure** - Infrastructure Terraform (allocator server, networking, observability)
2. **lablink/packages/allocator/src/lablink_allocator_service/terraform** - Client VM Terraform (runtime-provisioned resources)
3. **lablink/packages** - Core application packages (allocator service, client SDK, etc.)
4. **lablink/docs** - Documentation and architecture guides

## Two-Tier Terraform Architecture

### Tier 1: Infrastructure Terraform (lablink-template)
**Purpose**: Deploy the persistent LabLink infrastructure

**Resources**:
- Allocator EC2 instance (`lablink_allocator_server`)
- Elastic IP (always created or looked up)
- Security groups for allocator
- IAM roles and instance profiles
- CloudWatch Log Groups (for client VMs and Lambda)
- Lambda function (log processor)
- CloudWatch Log Subscription Filter (CloudWatch → Lambda trigger)
- **Conditional resources** (based on config):
  - Application Load Balancer (when `ssl.provider = "acm"`)
  - Route53 A record (when `dns.terraform_managed = true`)
  - Route53 Alias record for ALB (when ALB is created)
  - Target groups and listeners (when ALB is created)

**Locals block** (line 242):
```hcl
locals {
  allocator_instance_type = "t3.large"
  install_caddy = contains(["letsencrypt", "cloudflare"], local.ssl_provider)
  create_alb = local.ssl_provider == "acm"
}
```

### Tier 2: Client VM Terraform (lablink/packages/allocator)
**Purpose**: Dynamically provision client VMs at runtime (called by allocator service via Terraform subprocess)

**Resources** (per client VM):
- EC2 instance (`lablink_vm` with `count` parameter)
- Security group for client VM
- IAM role for CloudWatch agent
- IAM instance profile
- TLS private key (for SSH)
- AWS key pair
- Time tracking resources

**Key difference**: These resources are NOT in the infrastructure diagram initially - they're created on-demand when users request VMs via the allocator API.

## Four DNS/SSL Deployment Patterns

The architecture supports **4 mutually exclusive deployment configurations**:

### Pattern 1: IP-Only
```yaml
dns.enabled: false
ssl.provider: "none"
```
**Terraform creates**:
- Allocator EC2 + EIP
- Security groups
- CloudWatch + Lambda
- **NO Route53**
- **NO ALB**
- **NO SSL/TLS**

**Access**: `http://52.40.142.146:5000` (direct IP)

### Pattern 2: Let's Encrypt (Caddy)
```yaml
dns.enabled: true
dns.terraform_managed: true
ssl.provider: "letsencrypt"
```
**Terraform creates**:
- Allocator EC2 + EIP
- Route53 A record → EIP
- Caddy installed via user_data.sh (NOT a Terraform resource)
- **NO ALB**

**Access**: `https://test.lablink.example.com` (Caddy handles SSL termination on EC2)

### Pattern 3: Cloudflare
```yaml
dns.enabled: false  # NOT managed in Terraform!
ssl.provider: "cloudflare"
```
**Terraform creates**:
- Allocator EC2 + EIP
- Caddy installed via user_data.sh
- **NO Route53** (DNS managed externally in Cloudflare)
- **NO ALB**

**Manual step**: User creates A record in Cloudflare pointing to EIP

**Access**: `https://lablink.example.com` (Cloudflare proxy handles SSL)

### Pattern 4: ACM (AWS Certificate Manager)
```yaml
dns.enabled: true
ssl.provider: "acm"
ssl.certificate_arn: "arn:aws:acm:..."
```
**Terraform creates**:
- Allocator EC2 + EIP
- **Application Load Balancer** (conditional!)
- Route53 Alias record → ALB (NOT to EIP)
- Target group
- ALB listener (HTTPS:443 → HTTP:5000)
- **NO Caddy**

**Access**: `https://lablink.example.com` → ALB → EC2:5000 (ALB handles SSL termination)

## Critical Parsing Issues Identified

### Issue 1: Instance Type Shows "unknown"
**Root cause**: Parser regex at `parser.py:82` only matches:
```python
r'instance_type\s*=\s*"([^"]+)"'  # Quoted strings only
```

But Terraform uses:
```hcl
instance_type = local.allocator_instance_type  # Variable reference
```

**Fix required**:
1. Parse `locals {}` blocks
2. Resolve `local.variable_name` references
3. Or: match both quoted strings AND variable references

### Issue 2: Missing CloudWatch Subscription Filter
**Root cause**: Parser doesn't recognize `aws_cloudwatch_log_subscription_filter` resource type

This is the "trigger" connection: CloudWatch Logs → Lambda

**Fix required**: Add subscription filter parsing to show the actual trigger mechanism

### Issue 3: Conditional Resources Not Identified
**Root cause**: Parser doesn't parse `count` or conditional expressions

Example:
```hcl
resource "aws_route53_record" "lablink_a_record" {
  count = local.dns_enabled && local.dns_terraform_managed && !local.create_alb ? 1 : 0
  # ...
}
```

Parser treats this as always present, but it's conditional!

**Fix required**: Parse `count` and mark resources as conditional

### Issue 4: Two Different Route53 Resources
There are actually TWO Route53 resources:
1. `lablink_a_record` - A record pointing to EIP (for Let's Encrypt/IP-only)
2. `lablink_alb_record` - Alias record pointing to ALB (for ACM)

Only ONE is created depending on `create_alb` condition.

**Current diagram**: Shows one generic Route53 node, doesn't differentiate

## Architectural Layers (Correct Abstraction)

### Layer 1: Access Layer (Configurable)
**Components**:
- DNS (Route53 OR Cloudflare OR none)
- SSL Termination (Let's Encrypt/Caddy OR ALB/ACM OR Cloudflare OR none)
- Load Balancer (ALB - conditional, only for ACM)

**Visual treatment**: Dashed borders, annotations showing conditions

### Layer 2: Control Plane (Infrastructure)
**Components**:
- Allocator EC2 instance
- Elastic IP
- Security groups
- IAM roles

**Visual treatment**: Solid borders, always present

### Layer 3: Application Runtime (Inside allocator EC2)
**Components** (NOT Terraform resources):
- Docker container: lablink-allocator
- Flask web application
- PostgreSQL database
- Terraform binary (for spawning client VMs)
- Caddy (conditionally installed)

**Visual treatment**: Show inside EC2 node as nested components

### Layer 4: Dynamic Compute (Runtime-Provisioned)
**Components**:
- Client EC2 instances (created by allocator's Terraform subprocess)
- Client security groups
- Client IAM roles
- TLS keys

**Visual treatment**: Different color/style, annotation "Runtime-provisioned via allocator"

### Layer 5: Observability (Infrastructure)
**Components**:
- CloudWatch Log Groups
- CloudWatch Log Subscription Filter
- Lambda function (log processor)
- Lambda IAM role

**Visual treatment**: Solid borders, show subscription filter as connection

## Data Flow

### User Request Flow
1. User → DNS (Route53 or Cloudflare or direct IP)
2. DNS → SSL termination (Caddy on EC2 OR ALB OR Cloudflare OR none)
3. SSL termination → Allocator Flask app (port 5000)
4. Allocator → Terraform subprocess → Client VM created

### Logging Flow
1. Client VM → CloudWatch agent → CloudWatch Log Group
2. CloudWatch Log Group → (subscription filter) → Lambda function
3. Lambda function → POST /api/vm-logs → Allocator API
4. Allocator → Stores in PostgreSQL database

## Client VM Provisioning Flow
1. User calls `POST /admin/create` on allocator API
2. Allocator service runs Terraform subprocess:
   ```bash
   terraform apply \
     -var="instance_count=1" \
     -var="machine_type=t2.medium" \
     -var="allocator_url=https://allocator.example.com"
   ```
3. Terraform creates:
   - EC2 instance with user_data script
   - Security group (SSH + egress)
   - IAM role for CloudWatch agent
   - SSH key pair
4. User_data script:
   - Installs CloudWatch agent
   - Pulls Docker image from ECR
   - Runs Docker container
   - Registers with allocator
5. CloudWatch agent starts sending logs to infrastructure-defined log group
6. Lambda processes logs and POSTs to allocator

## What Should Be in the Comprehensive Diagram

### Must Include (Infrastructure Terraform):
- ✅ Allocator EC2 instance (with actual instance type: t3.large)
- ✅ Elastic IP
- ✅ Security groups
- ✅ IAM roles and instance profiles
- ✅ CloudWatch Log Groups (both client and lambda)
- ✅ Lambda function
- ✅ CloudWatch subscription filter (as connection/trigger)
- ⚠️ ALB (conditional, show with dashed border + "ACM only")
- ⚠️ Route53 (conditional, show with annotation about options)
- ⚠️ Target groups (conditional, only with ALB)

### Must Include (Client VM Terraform - as separate visual layer):
- ✅ Client EC2 instance (representative, clearly marked as "runtime-provisioned")
- ✅ Client security group
- ✅ Client IAM role
- ✅ Connection showing allocator provisions client VMs

### Must Include (Non-Terraform components - as annotations/labels):
- ✅ Caddy (inside allocator EC2, with note "Let's Encrypt/Cloudflare only")
- ✅ Flask app (inside allocator EC2)
- ✅ PostgreSQL (inside allocator EC2)
- ✅ Docker + subject software (inside client EC2)
- ✅ CloudWatch agent (inside client EC2)

### Should NOT Include:
- ❌ Generic placeholders when real resources exist
- ❌ Hardcoded names that don't match actual resource names
- ❌ Terraform resources that don't exist (e.g., separate EIP resource - it's looked up via data source)

## Recommendations for Diagram Design

### Visual Encoding Strategy

**Color coding**:
- Blue: Always-present infrastructure (allocator EC2, CloudWatch, Lambda, IAM)
- Green: Conditional infrastructure (ALB, Route53, target groups)
- Orange: Runtime-provisioned resources (client VMs)
- Gray: External/manual resources (Cloudflare DNS)

**Border styles**:
- Solid: Always present
- Dashed: Conditional
- Dotted: External to this Terraform

**Annotations**:
- ALB: "Created when ssl.provider=acm"
- Route53: "Created when dns.terraform_managed=true"
- Client VMs: "Dynamically provisioned via allocator Terraform subprocess"
- Caddy: "Installed when ssl.provider=letsencrypt or cloudflare"

### Clustering Strategy

**Cluster 1: "Access Layer (Configurable)"**
- Route53 (dashed border)
- ALB (dashed border)
- Note: "4 deployment patterns: IP-only, Let's Encrypt, Cloudflare, ACM"

**Cluster 2: "LabLink Infrastructure"**
- Allocator EC2 (with nested components: Flask, PostgreSQL, Terraform, Caddy?)
- Elastic IP
- Security groups (maybe hidden for simplicity)

**Cluster 3: "Dynamic Compute"**
- Client VMs (orange, dashed border)
- Client security groups
- Note: "Runtime-provisioned, not in infrastructure"

**Cluster 4: "Observability & Logging"**
- CloudWatch Log Groups
- Subscription filter (as edge/connection)
- Lambda function
- Lambda IAM role

**Cluster 5: "IAM & Permissions"** (detailed diagram only)
- Allocator IAM role
- Lambda IAM role
- Client VM IAM role
- Policies and attachments

### Recommended Diagram Types

**1. Main Architecture (Simplified)**
- Show all 5 layers
- Use color coding for always vs. conditional
- Include key annotations
- Hide IAM details
- Show representative client VM

**2. Configuration Matrix (New!)**
- Table/grid showing 4 columns: IP-only, Let's Encrypt, Cloudflare, ACM
- Rows: DNS, SSL, Route53, ALB, Caddy, Access URL
- Check marks showing what's present in each config

**3. Detailed Infrastructure (All Resources)**
- Show ALL Terraform resources from both tiers
- Include IAM roles and policies
- Show all security groups
- Show conditional resources with annotations
- Include EIP association, target group attachments, etc.

**4. Network Flow (Request Routing)**
- User → DNS → SSL → Allocator
- Show all 4 possible paths
- Numbered steps

**5. Logging Flow**
- Client VM → CloudWatch agent → Log Group → Subscription filter → Lambda → Allocator API
- Show complete data flow

## Next Steps for Implementation

1. **Parse locals blocks** - Extract variable definitions
2. **Resolve variable references** - Replace `local.X` with actual values
3. **Parse conditional resources** - Detect `count` and mark as conditional
4. **Parse subscription filters** - Add new resource type
5. **Parse both Terraform directories** - Infrastructure + client VMs
6. **Redesign clusters** - Use proper architectural layers
7. **Add visual encoding** - Colors, borders, annotations for conditional resources
8. **Create configuration matrix** - Show 4 deployment patterns
9. **Test with all 4 configs** - Verify diagrams work for each pattern