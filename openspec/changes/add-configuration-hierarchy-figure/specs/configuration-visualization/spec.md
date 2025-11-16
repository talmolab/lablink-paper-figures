# Configuration Visualization Specification

## ADDED Requirements

### Requirement: Configuration Hierarchy Tree Diagram
The system SHALL generate a hierarchical tree diagram visualizing LabLink's configuration parameters organized into 8 primary categories: Deployment Environment, SSL/Network Strategy, Compute Configuration, Application Settings, Scaling & Reliability, AWS Infrastructure, Authentication & Security, and Monitoring & Logging.

#### Scenario: Generate configuration tree for paper publication
- **WHEN** `plot_configuration_hierarchy.py` is executed with `--fontsize-preset paper --dpi 300`
- **THEN** a PNG diagram is created showing all 8 configuration categories with readable labels at 14pt font size and 300 DPI resolution

#### Scenario: Display SSL provider decision options
- **WHEN** the configuration tree is rendered
- **THEN** the SSL Strategy branch shows 4 mutually exclusive options (none, letsencrypt, cloudflare, acm) with use-case annotations (Development, Production, Enterprise)

#### Scenario: Show GPU auto-detection
- **WHEN** the Compute Configuration branch is displayed
- **THEN** GPU instances show annotation "gpu_support: true (auto-detected)" and CPU instances show "gpu_support: false (auto-detected)"

#### Scenario: Indicate conditional requirements
- **WHEN** ssl_provider=acm is shown
- **THEN** a note indicating "requires: certificate_arn, Route53" is displayed using dashed connection and yellow background

---

### Requirement: Configuration Layer Color-Coding
The system SHALL use distinct colors to differentiate between infrastructure layer (config.yaml), runtime layer (terraform.runtime.tfvars), and optional/conditional parameters.

#### Scenario: Infrastructure layer parameters
- **WHEN** infrastructure-level categories (Deployment Environment, SSL Strategy, Auth & Security) are rendered
- **THEN** they use blue color scheme (#3498db family) to indicate config.yaml source

#### Scenario: Runtime layer parameters
- **WHEN** runtime-level categories (Compute Configuration, Application Settings) are rendered
- **THEN** they use red/orange color scheme (#e74c3c, #f39c12) to indicate terraform.runtime.tfvars source

#### Scenario: Optional parameter annotations
- **WHEN** conditional requirements are shown (e.g., ACM certificate requirement)
- **THEN** they use yellow background (#fff3cd) with note shape to indicate optionality

---

### Requirement: Configuration Legend
The system SHALL include a legend explaining the three configuration layers: Infrastructure Layer (config.yaml), Runtime Layer (terraform.runtime.tfvars), and Optional/Conditional parameters.

#### Scenario: Legend visibility
- **WHEN** the configuration tree diagram is generated
- **THEN** a legend is displayed in a dashed-border cluster with three example nodes showing each layer type

---

### Requirement: Multi-Format Output Support
The system SHALL support generating configuration tree diagrams in PNG, SVG, and PDF formats with configurable DPI and font size presets.

#### Scenario: PNG output for paper
- **WHEN** executed with `--format png --dpi 300 --fontsize-preset paper`
- **THEN** a 300 DPI PNG file is created with 14pt node fonts and 16pt title font

#### Scenario: SVG output for presentations
- **WHEN** executed with `--format svg --fontsize-preset presentation`
- **THEN** a scalable SVG file is created with 16pt node fonts suitable for slides

#### Scenario: Poster format
- **WHEN** executed with `--fontsize-preset poster`
- **THEN** fonts are scaled to 20pt for conference poster display

---

### Requirement: Configuration Decision Flow
The system SHALL organize configuration parameters in a top-to-bottom decision flow representing the typical deployment planning sequence: Environment selection → SSL strategy → Compute resources → Application configuration → Scaling parameters.

#### Scenario: Environment as first decision
- **WHEN** the tree is rendered
- **THEN** Deployment Environment is positioned as the leftmost top-level category, showing dev/test/prod/ci-test options

#### Scenario: SSL strategy follows environment
- **WHEN** the tree is rendered
- **THEN** SSL/Network Strategy is positioned adjacent to Environment, with edges showing typical pairings (dev→none, prod→letsencrypt/acm)

---

### Requirement: Configuration Metadata Documentation
The system SHALL generate a metadata file alongside each diagram containing: generation timestamp, configuration source files, format, DPI, font preset, and total parameter count.

#### Scenario: Metadata file creation
- **WHEN** a configuration diagram is generated
- **THEN** a `configuration_hierarchy_metadata.txt` file is created in the output directory with ISO-format timestamp and all generation parameters

---

### Requirement: Configuration Analysis Document
The system SHALL maintain a comprehensive configuration analysis document (`analysis/lablink-configuration-analysis.md`) documenting all configuration parameters, their types, requirements, defaults, and effects on infrastructure.

#### Scenario: Complete parameter documentation
- **WHEN** the analysis document is consulted
- **THEN** all 25+ configuration parameters are documented with: name, type, required/optional status, default value, description, code references, and usage examples

#### Scenario: Common configuration patterns
- **WHEN** the analysis document is referenced
- **THEN** it provides 4+ complete configuration examples for common deployment scenarios (local dev, workshop, production, enterprise)

#### Scenario: Configuration decision tree
- **WHEN** planning a deployment
- **THEN** the analysis document provides a 5-level decision tree guiding parameter selection: Environment → SSL → Compute → Application → Scale
