# Architecture Visualization Specification

## ADDED Requirements

### Requirement: Terraform Configuration Parsing

The system SHALL parse Terraform configuration files to extract infrastructure component definitions including resources, data sources, and their relationships.

#### Scenario: Parse EC2 instance resources

- **WHEN** Terraform files contain EC2 instance definitions
- **THEN** extract instance type, AMI, tags, security groups, and IAM role associations

#### Scenario: Parse networking resources

- **WHEN** Terraform files contain networking components (ALB, EIP, security groups, Route53)
- **THEN** extract resource names, connections, and configuration parameters

#### Scenario: Parse IAM and observability resources

- **WHEN** Terraform files contain IAM roles, policies, and CloudWatch resources
- **THEN** extract role names, attached policies, and log group configurations

#### Scenario: Handle missing or malformed Terraform files

- **WHEN** Terraform files are missing or contain syntax errors
- **THEN** raise clear error messages indicating which files failed to parse

### Requirement: Architecture Diagram Generation

The system SHALL generate publication-quality architecture diagrams showing component relationships and data flow paths.

#### Scenario: Generate main architecture diagram

- **WHEN** generating the main paper diagram
- **THEN** produce a simplified, high-level view showing key components (allocator, client VMs, ALB, CloudWatch, Lambda) with clear visual hierarchy

#### Scenario: Generate detailed technical diagram

- **WHEN** generating the supplementary diagram
- **THEN** produce a comprehensive view including all security groups, IAM roles, Route53 records, and detailed networking configuration

#### Scenario: Show request routing paths

- **WHEN** generating network flow diagram
- **THEN** clearly illustrate traffic flow from external users through DNS → ALB/EIP → EC2 → backend services

#### Scenario: Apply consistent visual styling

- **WHEN** generating any diagram
- **THEN** use consistent colors, shapes, and labels following publication quality standards (readable fonts, appropriate DPI, clear component grouping)

### Requirement: Multi-Format Diagram Export

The system SHALL export diagrams in multiple formats suitable for different use cases.

#### Scenario: Export high-resolution PNG for publication

- **WHEN** exporting PNG format
- **THEN** generate at minimum 300 DPI resolution with proper sizing for journal requirements

#### Scenario: Export vector formats

- **WHEN** exporting SVG or PDF formats
- **THEN** generate scalable vector graphics preserving all visual elements

#### Scenario: Save to appropriate output directories

- **WHEN** saving diagrams
- **THEN** place main diagrams in `figures/main/` and detailed diagrams in `figures/supplementary/` following project conventions

### Requirement: Component Relationship Mapping

The system SHALL accurately represent how infrastructure components interact and depend on each other.

#### Scenario: Map security group rules to resources

- **WHEN** parsing security groups
- **THEN** show which resources are protected by which security groups and what ports/protocols are allowed

#### Scenario: Show IAM role attachments

- **WHEN** parsing IAM resources
- **THEN** clearly indicate which EC2 instances and Lambda functions use which IAM roles and what permissions they grant

#### Scenario: Illustrate logging flow

- **WHEN** showing observability components
- **THEN** demonstrate the path from client VMs → CloudWatch Logs → Lambda processor → Allocator API

### Requirement: Configurable Diagram Options

The system SHALL support configuration options to customize diagram generation for different audiences.

#### Scenario: Toggle component visibility

- **WHEN** configuring diagram generation
- **THEN** allow showing/hiding specific component types (e.g., exclude IAM details for simplified view)

#### Scenario: Adjust layout and grouping

- **WHEN** configuring diagram layout
- **THEN** allow grouping related components (e.g., all networking in one cluster, all compute in another)

#### Scenario: Customize output format preferences

- **WHEN** running diagram generation script
- **THEN** accept command-line arguments or config file to specify output formats, DPI, and sizing

### Requirement: Reproducible Diagram Generation

The system SHALL ensure diagrams can be regenerated consistently from the same Terraform source files.

#### Scenario: Deterministic output from same inputs

- **WHEN** running diagram generation multiple times on unchanged Terraform files
- **THEN** produce identical output files (same layout, same components, same styling)

#### Scenario: Script-based workflow integration

- **WHEN** integrating with figure generation workflow
- **THEN** provide a command-line script that can be run as part of automated figure generation pipeline

#### Scenario: Version tracking

- **WHEN** generating diagrams
- **THEN** include metadata indicating which Terraform files and versions were used as source