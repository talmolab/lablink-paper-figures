# LabLink Configurability Features - Comprehensive Analysis

## Overview
LabLink is a cloud-based VM allocation and management system with multiple configurable aspects for deployment flexibility and customization.

## Key Configurability Areas Found

### 1. **SSL/TLS Configuration (4 Mutually Exclusive Options)**
Located in: `config.yaml` (lablink-template/lablink-infrastructure/)

The system supports 4 different SSL provider strategies:
- **none**: Direct HTTP on port 80 (development/testing)
- **letsencrypt**: Caddy proxy handles SSL termination (automatic certificate)
- **cloudflare**: CloudFlare proxy handles SSL, Caddy serves HTTP internally
- **acm**: AWS ALB handles SSL termination with ACM certificate

**Related code:** 
- `lablink-infrastructure/main.tf` (conditional resource creation)
- `lablink-infrastructure/alb.tf` (ALB configuration)
- `lablink-infrastructure/user_data.sh` (Caddy installation based on SSL provider)

**Data available:**
- Architecture analysis documents detail all 4 configurations
- Diagram generation supports all SSL strategies with proper annotations

### 2. **Deployment Environment Configuration**
Located in: `config.yaml` with `resource_suffix` parameter

Supports multiple deployment tiers:
- **dev**: Local development (no S3 backend)
- **test**: Test environment (S3 backend, auto-deploy on push)
- **prod**: Production (S3 backend, manual deploy)
- **ci-test**: CI testing environment (S3 backend)

**Configuration parameters:**
- Admin username and password (bcrypt hashed)
- Database password
- AWS credentials (access key, secret key, region)
- Resource naming (suffix appended to all AWS resources)

### 3. **Machine Type & GPU Configuration**
Located in: Terraform runtime variables

Configurable aspects:
- **Machine type**: `g4dn.xlarge`, `p3.8xlarge`, CPU-only instances, etc.
- **GPU support**: Optional, depends on machine type
- **Instance count**: Dynamic scaling of client VMs
- **Docker image**: Selection of base image (GPU-enabled or CPU-only)

**Related files:**
- `packages/allocator/src/lablink_allocator_service/terraform/main.tf`
- `terraform.runtime.tfvars` (generated per deployment)

### 4. **Application & Workspace Configuration**
Located in: Terraform runtime variables

Configurable options:
- **subject_software**: Target application (e.g., "sleap", "custom-app")
- **repository**: Git repository to clone in VM
- **startup_on_error**: How to handle provisioning errors ("continue" or "fail")
- **custom_startup_script**: Optional script execution per VM
- **file_extension**: Extension filter for data collection (e.g., ".slp" for SLEAP)

### 5. **Network & Connectivity Configuration**
Located in: `config.yaml` and Terraform

Configurable aspects:
- **Admin server port**: 5000 (Flask internal), 80/443 (external)
- **Database host/port**: RDS PostgreSQL configuration
- **Security groups**: Allow rules for SSH, HTTP, HTTPS
- **DNS configuration**: Optional Route53 DNS management
- **VPC and subnet selection**: AWS networking

### 6. **Logging & Observability Configuration**
Located in: CloudWatch configuration in Terraform

Configurable options:
- **Log group name**: `lablink-cloud-init-{env}`
- **Log retention**: CloudWatch log retention period
- **CloudWatch agent**: Configuration for log streaming
- **Lambda function**: Log processor configuration
- **Monitoring thresholds**: GPU health, usage tracking intervals

### 7. **API Authentication Configuration**
Located in: `config.yaml` and Flask app initialization

Configurable aspects:
- **Admin credentials**: Username/password pairs (HTTP Basic Auth)
- **Password hashing**: bcrypt for secure password storage
- **Authentication scopes**: Different endpoints with different auth levels:
  - Public endpoints: No auth required
  - Admin endpoints: HTTP Basic Auth required
  - VM endpoints: Hostname validation only

### 8. **Font & Diagram Rendering Configuration**
Located in: `scripts/plotting/` and `src/diagram_gen/`

Preset configurations for different output contexts:
- **paper**: 14pt fonts, 300 DPI, 6.5" width (two-column journal)
- **poster**: 20pt fonts, 300 DPI, 12" width (conference poster)
- **presentation**: 16pt fonts, 150 DPI, 10"x7.5" (slide decks)

**Graphviz settings**:
- `nodesep`: Node separation (0.6-0.9)
- `ranksep`: Rank separation (0.75-1.2)
- `fontsize`: Font size (14-20pt based on preset)
- `dpi`: Output resolution (150-300)
- `splines`: Edge rendering ("ortho", "curved", etc.)

## Available Data & Documentation

### Configuration Data Files
1. **lablink-comprehensive-analysis.md**: 
   - Complete CI/CD pipeline configuration
   - API endpoint specifications
   - Network flow with ports and protocols
   - Database schema and operations

2. **api-architecture-analysis.md**:
   - 22 API endpoints documented
   - Request/response specifications
   - Authentication mechanisms
   - Database operations per endpoint

3. **lablink-architecture-analysis.md**:
   - 8 major architectural mechanisms
   - Complete flow descriptions
   - Configuration parameters
   - Code references for each mechanism

### Processed Data Files
- `data/processed/deployment_impact/workshops.csv`: Workshop deployment timeline data
- `data/processed/gpu_reliance/gpu_timeseries.csv`: GPU adoption over time
- `data/processed/os_distribution/os_stats.csv`: OS distribution stats

## Visualization Opportunities

### 1. **Configuration Options Matrix** (New Opportunity)
- **Data**: SSL strategies (4), deployment environments (4), machine types (10+)
- **Visualization**: Heatmap or comparison table
- **Value**: Shows LabLink's flexibility for different deployment scenarios

### 2. **Deployment Configuration Impact** (New Opportunity)
- **Data**: Cost vs. performance vs. setup complexity for different configurations
- **Visualization**: 2D scatter plot or bubble chart
- **Value**: Helps users choose appropriate configuration

### 3. **API Endpoint Distribution by Authentication Level**
- **Data**: 22 endpoints, breakdown by auth type (public, admin, validated)
- **Visualization**: Donut chart or stacked bar chart
- **Value**: Shows security architecture

### 4. **Deployment Environment Complexity**
- **Data**: Resource count, configuration options per environment
- **Visualization**: Stepped progression diagram
- **Value**: Illustrates scaling from dev to prod

## Configuration Validation & Testing

**Existing validation:**
- `config-validation.yml` GitHub workflow
- `lablink-validate-config` command-line tool
- Schema validation for config.yaml
- Type checking for all configuration parameters

**Test coverage:**
- Configuration parsing tests
- Environment-specific deployment tests
- Terraform configuration validation
- Docker image configuration tests

## Related Diagrams & Specs
- `openspec/changes/add-architecture-diagram/` directory contains extensive design documentation
- `openspec/specs/` contains formal requirement specifications
- Font presets documented in README.md and graphviz-settings-reference.md

## Key Insights for New Visualizations

1. **Configuration complexity** is high but well-documented
2. **SSL strategies** are mutually exclusive - perfect for comparison visualization
3. **Deployment environments** form a logical progression (dev→test→prod)
4. **Machine types** correlate with cost and performance
5. **API structure** shows clear separation of concerns (public/admin/validated)
6. **Monitoring system** has multiple configurable parameters

## Potential Figure Ideas

1. **Configuration Decision Tree**: SSL provider → Machine type → Environment
2. **Configurability Spectrum**: Axis of flexibility vs. complexity
3. **Feature Comparison Table**: Which configurations enable which features
4. **Deployment Cost Analysis**: Configuration impact on AWS spending
5. **Performance Characteristics**: Configuration impact on startup time, throughput
