# Add LabLink Architecture Diagram Generation (REVISED)

## Why

The LabLink paper requires publication-quality architecture diagrams that accurately represent the **two-tier Terraform architecture** and **four distinct DNS/SSL deployment patterns**. Initial implementation revealed critical gaps:

1. **Instance types showing "unknown"** - Parser doesn't resolve `local.variable` references
2. **Missing CloudWatch subscription filters** - The "trigger" between CloudWatch and Lambda isn't shown
3. **Client VMs incorrectly represented** - They're runtime-provisioned via allocator's Terraform subprocess, not infrastructure
4. **Conditional resources not identified** - ALB and Route53 depend on configuration, not always present
5. **Incomplete architecture** - Need to show BOTH infrastructure Terraform AND client VM Terraform

We need comprehensive diagram generation that shows the complete LabLink system across both Terraform tiers.

## What Changes

### Terraform Parsing Improvements
- Parse `locals {}` blocks and resolve variable references (fixes "unknown" instance type)
- Parse CloudWatch subscription filters (shows CloudWatch → Lambda triggers)
- Parse conditional resources with `count` expressions (identifies ALB, Route53 as conditional)
- Support TWO Terraform directories:
  1. **Infrastructure**: `C:\repos\lablink-template\lablink-infrastructure\` (allocator, networking, observability)
  2. **Client VMs**: `C:\repos\lablink\packages\allocator\src\lablink_allocator_service\terraform\` (runtime-provisioned VMs)

### Diagram Generation Enhancements
- Generate **5 diagram types**:
  1. **Main Architecture** - Comprehensive view showing both infrastructure and runtime-provisioned resources
  2. **Configuration Matrix** - Table showing 4 DNS/SSL patterns (IP-only, Let's Encrypt, Cloudflare, ACM)
  3. **Detailed Infrastructure** - All Terraform resources from both tiers with IAM details
  4. **Network Flow** - Request routing for all 4 configurations
  5. **Logging Flow** - Client VM → CloudWatch → Lambda → Allocator data flow

- Visual encoding for resource types:
  - **Solid borders**: Always-present infrastructure
  - **Dashed borders**: Conditional resources (ALB, Route53)
  - **Orange color**: Runtime-provisioned resources (client VMs)
  - **Annotations**: Configuration requirements (e.g., "ACM only", "Runtime-provisioned")

- Proper architectural clustering:
  - Access Layer (DNS/SSL - configurable)
  - LabLink Infrastructure (allocator EC2, IAM, security groups)
  - Dynamic Compute (client VMs - clearly marked as runtime-provisioned)
  - Observability (CloudWatch, Lambda, subscription filters)

### New Resource Types Parsed
- CloudWatch log subscription filters (`aws_cloudwatch_log_subscription_filter`)
- Locals blocks for variable resolution
- Conditional resources (detect `count` expressions)
- EIP associations, target group attachments
- TLS private keys, AWS key pairs (from client VM Terraform)

## Impact

- **Affected specs**: `architecture-visualization` (revised capability)
- **Affected code**:
  - **Modified**: `src/terraform_parser/parser.py` - Add locals parsing, variable resolution, conditional detection, subscription filters
  - **Modified**: `src/diagram_gen/generator.py` - Redesign clusters, add visual encoding, support both Terraform tiers
  - **Modified**: `scripts/plotting/generate_architecture_diagram.py` - Support multiple Terraform directories, new diagram types
  - **New**: `figures/main/lablink-configuration-matrix.png` - Configuration comparison table
  - **New**: `figures/supplementary/lablink-logging-flow.png` - Logging data flow diagram
  - **Modified**: `figures/main/lablink-architecture.png` - Comprehensive architecture with both tiers
  - **Modified**: `figures/supplementary/lablink-architecture-detailed.png` - All resources with IAM
  - **Modified**: `figures/supplementary/lablink-network-flow.png` - Show all 4 routing patterns
  - **Modified**: `tests/test_terraform_parser.py` - Add tests for locals, conditionals, subscription filters
  - **Modified**: `tests/test_diagram_generation.py` - Test multi-tier parsing, visual encoding
  - **New**: `openspec/changes/add-architecture-diagram/ARCHITECTURAL_ANALYSIS.md` - Comprehensive architecture documentation
- **External dependencies**:
  - Requires read access to `lablink-template/lablink-infrastructure` (infrastructure Terraform)
  - Requires read access to `lablink/packages/allocator/src/lablink_allocator_service/terraform` (client VM Terraform)