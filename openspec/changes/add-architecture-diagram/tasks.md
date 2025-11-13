# Implementation Tasks (REVISED)

## Phase 1: Fix Critical Parser Issues (HIGH PRIORITY)

### 1.1 Locals Block Parsing and Variable Resolution
- [x] 1.1.1 Add `parse_locals_block()` function to extract `locals {}` definitions
- [ ] 1.1.2 Extract simple key-value assignments (string and boolean literals)
- [ ] 1.1.3 Handle conditional expressions in locals (e.g., `create_alb = ssl_provider == "acm"`)
- [ ] 1.1.4 Store locals in dict for variable resolution
- [ ] 1.1.5 Implement `resolve_variable_references()` to replace `local.X` with values
- [ ] 1.1.6 Update instance_type parsing to handle both quoted strings AND local references
- [ ] 1.1.7 Test: Verify allocator instance_type shows "t3.large" not "unknown"

### 1.2 CloudWatch Subscription Filter Parsing
- [ ] 1.2.1 Add `subscription_filters` field to `ParsedTerraformConfig` dataclass
- [ ] 1.2.2 Implement regex pattern for `aws_cloudwatch_log_subscription_filter` resources
- [ ] 1.2.3 Parse `destination_arn` (Lambda function reference)
- [ ] 1.2.4 Parse `log_group_name` (CloudWatch log group reference)
- [ ] 1.2.5 Parse `filter_pattern` attribute
- [ ] 1.2.6 Store subscription filters in config
- [ ] 1.2.7 Test: Verify subscription filter appears in parsed config

### 1.3 Conditional Resource Detection
- [ ] 1.3.1 Add `is_conditional` boolean field to `TerraformResource` dataclass
- [ ] 1.3.2 Add `condition` string field to store the condition expression
- [ ] 1.3.3 Detect `count` parameter in resource blocks
- [ ] 1.3.4 Parse ternary conditional: `count = condition ? 1 : 0`
- [ ] 1.3.5 Extract condition expression (before the `?`)
- [ ] 1.3.6 Resolve local variables in condition expressions
- [ ] 1.3.7 Mark resource as conditional if `count` contains `? :`
- [ ] 1.3.8 Test: Verify ALB marked as conditional with "ssl_provider == acm"
- [ ] 1.3.9 Test: Verify Route53 marked as conditional with appropriate condition

## Phase 2: Multi-Tier Terraform Architecture (HIGH PRIORITY)

### 2.1 Parse Both Terraform Directories
- [ ] 2.1.1 Add `tier` field to `ParsedTerraformConfig` ("infrastructure" or "client_vm")
- [ ] 2.1.2 Add `is_runtime_provisioned` boolean field to mark client VM resources
- [ ] 2.1.3 Create `parse_lablink_architecture()` function that takes TWO directory paths
- [ ] 2.1.4 Parse infrastructure Terraform from `lablink-template/lablink-infrastructure`
- [ ] 2.1.5 Parse client VM Terraform from `lablink/packages/allocator/.../terraform`
- [ ] 2.1.6 Mark client VM config as `tier="client_vm"` and `is_runtime_provisioned=True`
- [ ] 2.1.7 Return tuple of both configs: `(infra_config, client_config)`
- [ ] 2.1.8 Test: Verify both configs parsed successfully

### 2.2 Merge or Separate Client VM Resources
- [ ] 2.2.1 Decide: Merge into single config OR keep separate for different visual treatment
- [ ] 2.2.2 If merging: Tag each resource with its tier
- [ ] 2.2.3 If separate: Pass both configs to diagram generator
- [ ] 2.2.4 Ensure client VMs distinguishable from infrastructure VMs

### 2.3 Update CLI Script for Two Directories
- [ ] 2.3.1 Add `--client-vm-terraform-dir` CLI argument
- [ ] 2.3.2 Add `LABLINK_CLIENT_VM_TERRAFORM_DIR` environment variable support
- [ ] 2.3.3 Update main execution flow to parse both directories
- [ ] 2.3.4 Pass both configs to diagram generation functions

## Phase 3: Visual Encoding Implementation (HIGH PRIORITY)

### 3.1 Node Styling Based on Resource Type
- [ ] 3.1.1 Create `get_node_style()` function that takes `TerraformResource`
- [ ] 3.1.2 Implement solid border for always-present infrastructure (default)
- [ ] 3.1.3 Implement dashed border for conditional resources (`is_conditional=True`)
- [ ] 3.1.4 Implement dotted border for runtime-provisioned resources
- [ ] 3.1.5 Define color palette: blue (infra), green (conditional), orange (runtime)
- [ ] 3.1.6 Apply fillcolor based on resource type
- [ ] 3.1.7 Test: Verify ALB has dashed green border
- [ ] 3.1.8 Test: Verify client VM has dotted orange border

### 3.2 Condition Annotations
- [ ] 3.2.1 Extract human-readable condition from `resource.condition`
- [ ] 3.2.2 Add annotation to node label: `"\n(When ssl.provider=acm)"`
- [ ] 3.2.3 Format condition nicely (replace `local.` references with values)
- [ ] 3.2.4 Add "Runtime-provisioned" annotation for client VM resources
- [ ] 3.2.5 Test: Verify ALB shows "(When ssl.provider=acm)"

### 3.3 Nested Components in EC2 Nodes
- [ ] 3.3.1 Design sub-node rendering within EC2 instances
- [ ] 3.3.2 Show Flask, PostgreSQL, Terraform inside allocator EC2
- [ ] 3.3.3 Show Docker, subject software, CloudWatch agent inside client EC2
- [ ] 3.3.4 Show Caddy inside allocator EC2 with annotation "(Let's Encrypt/Cloudflare)"
- [ ] 3.3.5 Use smaller font size for nested components
- [ ] 3.3.6 Test: Verify nested components visible in diagram

## Phase 4: Redesigned Diagram Clusters (MEDIUM PRIORITY)

### 4.1 Implement New Cluster Structure
- [ ] 4.1.1 Remove old "LabLink Core" cluster
- [ ] 4.1.2 Create "Access Layer (Configurable)" cluster
- [ ] 4.1.3 Add Route53, ALB, note about 4 patterns to Access Layer
- [ ] 4.1.4 Create "LabLink Infrastructure" cluster
- [ ] 4.1.5 Add allocator EC2, EIP, security groups, IAM to Infrastructure
- [ ] 4.1.6 Create "Dynamic Compute" cluster
- [ ] 4.1.7 Add client VMs (from client VM Terraform) to Dynamic Compute
- [ ] 4.1.8 Create "Observability & Logging" cluster
- [ ] 4.1.9 Add CloudWatch logs, Lambda, subscription filter to Observability
- [ ] 4.1.10 Create "IAM & Permissions" cluster (detailed diagram only)
- [ ] 4.1.11 Add all IAM roles and policies to IAM cluster

### 4.2 Subscription Filter as Edge, Not Node
- [ ] 4.2.1 Remove subscription filter from being created as a diagram node
- [ ] 4.2.2 Create edge from CloudWatch log group to Lambda function
- [ ] 4.2.3 Label edge with "triggers" or "subscription filter"
- [ ] 4.2.4 Use subscription filter attributes to find source and destination
- [ ] 4.2.5 Parse references like `aws_lambda_function.log_processor.arn`
- [ ] 4.2.6 Match to actual Lambda and CloudWatch nodes in diagram
- [ ] 4.2.7 Test: Verify CloudWatch → Lambda connection visible

### 4.3 Runtime Provisioning Flow
- [ ] 4.3.1 Add dashed edge from allocator to client VMs
- [ ] 4.3.2 Label edge: "Terraform subprocess"
- [ ] 4.3.3 Show that allocator provisions client VMs, not infrastructure Terraform
- [ ] 4.3.4 Add annotation explaining two-tier architecture

## Phase 5: New Diagram Types (MEDIUM PRIORITY)

### 5.1 Configuration Matrix Diagram
- [ ] 5.1.1 Decide: Use Diagrams library table OR matplotlib table
- [ ] 5.1.2 Create 5x4 table: rows for components, columns for configs
- [ ] 5.1.3 Add IP-only, Let's Encrypt, Cloudflare, ACM columns
- [ ] 5.1.4 Add rows: Allocator EC2, EIP, Route53, ALB, Caddy, SSL, DNS, Access URL
- [ ] 5.1.5 Populate with ✓ / ✗ for present/absent
- [ ] 5.1.6 Add text descriptions for SSL provider and DNS management
- [ ] 5.1.7 Export to PNG at 300 DPI
- [ ] 5.1.8 Save to `figures/main/lablink-configuration-matrix.png`

### 5.2 Logging Flow Diagram
- [ ] 5.2.1 Create linear left-to-right flow diagram
- [ ] 5.2.2 Show: Client VM → CloudWatch Agent → Log Group
- [ ] 5.2.3 Show: Log Group → Subscription Filter → Lambda
- [ ] 5.2.4 Show: Lambda → POST /api/vm-logs → Allocator API
- [ ] 5.2.5 Show: Allocator → PostgreSQL database
- [ ] 5.2.6 Add numbered steps (1, 2, 3, 4)
- [ ] 5.2.7 Include data format annotations (e.g., "JSON logs")
- [ ] 5.2.8 Export to `figures/supplementary/lablink-logging-flow.png`

### 5.3 Multi-Config Network Flow
- [ ] 5.3.1 Update network flow diagram to show 4 different paths
- [ ] 5.3.2 Use color coding: one color per config pattern
- [ ] 5.3.3 Show decision points (if ACM → ALB path, if Let's Encrypt → Caddy path)
- [ ] 5.3.4 Label each path with configuration name
- [ ] 5.3.5 Show final destination (all end at allocator Flask app)

### 5.4 Update Main Architecture Diagram
- [ ] 5.4.1 Implement new 5-cluster design
- [ ] 5.4.2 Apply visual encoding (borders, colors, annotations)
- [ ] 5.4.3 Show subscription filter as edge
- [ ] 5.4.4 Include resources from BOTH Terraform tiers
- [ ] 5.4.5 Add legend explaining border styles and colors
- [ ] 5.4.6 Keep poster-friendly fonts (18pt titles, 16pt labels, Helvetica-Bold)
- [ ] 5.4.7 Test: Generate and review for accuracy

### 5.5 Update Detailed Diagram
- [ ] 5.5.1 Include ALL resources from both Terraform tiers
- [ ] 5.5.2 Show all security groups
- [ ] 5.5.3 Show all IAM roles and policy attachments
- [ ] 5.5.4 Show EIP associations, target group attachments
- [ ] 5.5.5 Show TLS keys and SSH key pairs
- [ ] 5.5.6 Apply same visual encoding as main diagram
- [ ] 5.5.7 May be more cluttered - that's OK for detailed view

## Phase 6: Testing and Validation (HIGH PRIORITY)

### 6.1 Parser Tests
- [ ] 6.1.1 Test locals parsing with sample Terraform
- [ ] 6.1.2 Test variable resolution (local.allocator_instance_type → "t3.large")
- [ ] 6.1.3 Test conditional resource detection (count parsing)
- [ ] 6.1.4 Test subscription filter parsing
- [ ] 6.1.5 Test parsing both Terraform directories
- [ ] 6.1.6 Test error handling for missing files/directories
- [ ] 6.1.7 Run `uv run pytest tests/test_terraform_parser.py -v`

### 6.2 Diagram Generation Tests
- [ ] 6.2.1 Test visual encoding function (border styles, colors)
- [ ] 6.2.2 Test cluster creation with new structure
- [ ] 6.2.3 Test subscription filter rendered as edge
- [ ] 6.2.4 Test multi-tier resource inclusion
- [ ] 6.2.5 Test all 5 diagram types generate without errors
- [ ] 6.2.6 Run `uv run pytest tests/test_diagram_generation.py -v`

### 6.3 Integration Testing
- [ ] 6.3.1 Run script with actual infrastructure Terraform
- [ ] 6.3.2 Run script with actual client VM Terraform
- [ ] 6.3.3 Verify all 5 diagrams generate successfully
- [ ] 6.3.4 Check output file sizes (should be reasonable, not huge)
- [ ] 6.3.5 Open each PNG and verify visual quality
- [ ] 6.3.6 Verify DPI is 300 for publication quality

### 6.4 Accuracy Validation
- [ ] 6.4.1 Compare diagram to actual Terraform files line-by-line
- [ ] 6.4.2 Verify instance type is "t3.large"
- [ ] 6.4.3 Verify CloudWatch → Lambda connection shown
- [ ] 6.4.4 Verify ALB marked as conditional
- [ ] 6.4.5 Verify Route53 marked as conditional
- [ ] 6.4.6 Verify client VMs marked as runtime-provisioned
- [ ] 6.4.7 Verify subscription filter shown as trigger edge
- [ ] 6.4.8 Count resources: should match Terraform resource count

### 6.5 Configuration Testing
- [ ] 6.5.1 Ideally: Test with all 4 config YAML files if possible
- [ ] 6.5.2 Verify diagram adapts to different configurations
- [ ] 6.5.3 Verify conditional resources appear/disappear appropriately
- [ ] 6.5.4 Verify configuration matrix accurately represents all 4 patterns

## Phase 7: Documentation and Finalization (LOW PRIORITY)

### 7.1 Code Documentation
- [ ] 7.1.1 Add docstrings to all new parsing functions
- [ ] 7.1.2 Document visual encoding scheme in code comments
- [ ] 7.1.3 Add examples to function docstrings
- [ ] 7.1.4 Run `ruff check .` and fix any issues
- [ ] 7.1.5 Run `ruff format .` to ensure consistent formatting

### 7.2 User Documentation
- [ ] 7.2.1 Update README with diagram generation instructions
- [ ] 7.2.2 Document both Terraform directory requirements
- [ ] 7.2.3 Explain each diagram type and its purpose
- [ ] 7.2.4 Add examples of CLI usage
- [ ] 7.2.5 Document environment variables

### 7.3 Architecture Documentation
- [ ] 7.3.1 Keep ARCHITECTURAL_ANALYSIS.md up to date
- [ ] 7.3.2 Document two-tier Terraform architecture
- [ ] 7.3.3 Document 4 DNS/SSL deployment patterns
- [ ] 7.3.4 Create diagram legend explaining visual encoding

### 7.4 OpenSpec Finalization
- [ ] 7.4.1 Mark all tasks as completed in this file
- [ ] 7.4.2 Update spec.md with new requirements (if needed)
- [ ] 7.4.3 Run `openspec validate add-architecture-diagram --strict`
- [ ] 7.4.4 Fix any validation errors
- [ ] 7.4.5 Prepare for archiving once deployed

## Success Criteria Checklist

- [ ] ✅ Instance type shows "t3.large" not "unknown"
- [ ] ✅ CloudWatch → Lambda connection visible with subscription filter label
- [ ] ✅ Client VMs clearly marked as "Runtime-provisioned"
- [ ] ✅ ALB shown with dashed border and "(When ssl.provider=acm)" annotation
- [ ] ✅ Route53 shown with dashed border and appropriate condition
- [ ] ✅ Diagram includes resources from BOTH infrastructure and client VM Terraform
- [ ] ✅ Configuration matrix diagram shows all 4 deployment patterns
- [ ] ✅ All 5 diagram types generate without errors
- [ ] ✅ Diagrams render at 300 DPI publication quality
- [ ] ✅ Poster-friendly fonts (18pt/16pt Helvetica-Bold) maintained
- [ ] ✅ Visual encoding (colors, borders) clearly distinguishes resource types
- [ ] ✅ Clusters properly organized into 5 architectural layers
- [ ] ✅ All tests pass (`pytest`)
- [ ] ✅ Code quality checks pass (`ruff`)
- [ ] ✅ OpenSpec validation passes

## Known Issues and TODOs

- [ ] Consider: Should we parse Terraform variables from `variables.tf` as well?
- [ ] Consider: Should we parse data sources (e.g., `data.aws_eip.allocator`)?
- [ ] Consider: Should we show security group rules in detailed diagram?
- [ ] Consider: Should we add Terraform state parsing for deployed resource IDs?
- [ ] Consider: Should configuration matrix be interactive (HTML) vs static image?

## Notes

- Initial implementation (Phase 1-3) already partially completed
- Many tasks marked as completed in previous implementation
- This revised task list focuses on FIXES and ENHANCEMENTS
- Priority order: Phase 1 > Phase 2 > Phase 3 > Phase 6 > Phase 4 > Phase 5 > Phase 7
- Can parallelize: Phase 1 + Phase 2 + Phase 3 (all parsing/architecture work)
- Phase 4-5 depend on Phase 1-3 completion
- Phase 6 should be ongoing throughout implementation