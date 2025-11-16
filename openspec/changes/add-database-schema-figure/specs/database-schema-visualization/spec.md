# database-schema-visualization Specification

## Purpose

This capability provides a publication-quality visualization of the LabLink PostgreSQL database schema, illustrating the single-table design with 19 columns, database triggers, and the LISTEN/NOTIFY pattern that enables real-time VM assignment coordination between the allocator service and client VMs.

## ADDED Requirements

### Requirement: VM Table Schema Visualization
The system SHALL visualize the complete PostgreSQL VM table schema with all columns grouped by functional purpose.

#### Scenario: Complete column representation
- **WHEN** generating the database schema diagram
- **THEN** all 19 columns from the VM table are displayed
- **AND** columns are accurately named matching `generate_init_sql.py` lines 29-49
- **AND** the HostName column is marked as PRIMARY KEY
- **AND** the InUse column shows NOT NULL DEFAULT FALSE constraint
- **AND** the CreatedAt column shows DEFAULT NOW() constraint

#### Scenario: Column grouping by function
- **WHEN** visualizing the table structure
- **THEN** columns are organized into 4 functional groups
- **AND** Assignment group contains: HostName, UserEmail, CrdCommand, Pin
- **AND** Monitoring group contains: Status, Healthy, InUse, Logs
- **AND** Performance Metrics group contains: TerraformApplyStartTime, TerraformApplyEndTime, TerraformApplyDurationSeconds, CloudInitStartTime, CloudInitEndTime, CloudInitDurationSeconds, ContainerStartTime, ContainerEndTime, ContainerStartupDurationSeconds, TotalStartupDurationSeconds
- **AND** Metadata group contains: CreatedAt

#### Scenario: Column data types
- **WHEN** displaying column details
- **THEN** VARCHAR(1024) type is shown for HostName, Pin, CrdCommand, UserEmail, Healthy, Status
- **AND** BOOLEAN type is shown for InUse
- **AND** TEXT type is shown for Logs
- **AND** TIMESTAMP type is shown for all timing columns and CreatedAt
- **AND** FLOAT type is shown for all duration columns

### Requirement: Database Trigger Flow Visualization
The system SHALL illustrate the database trigger mechanism that enables real-time VM assignment notifications.

#### Scenario: Trigger components
- **WHEN** generating the database schema diagram
- **THEN** the TRIGGER `trigger_crd_command_insert_or_update` is displayed
- **AND** the FUNCTION `notify_crd_command_update()` is displayed
- **AND** the `pg_notify()` call with channel 'vm_updates' is displayed
- **AND** the notification payload structure is shown: {HostName, CrdCommand, Pin}

#### Scenario: Trigger activation conditions
- **WHEN** illustrating trigger behavior
- **THEN** the diagram shows trigger fires on INSERT
- **AND** the diagram shows trigger fires on UPDATE OF CrdCommand
- **AND** the visual flow indicates this is an AFTER trigger (executes after row modification)

#### Scenario: Notification flow
- **WHEN** visualizing the LISTEN/NOTIFY pattern
- **THEN** arrows show: VM Table → Trigger → Function → pg_notify → Client VMs
- **AND** Client VMs are shown in LISTEN waiting state
- **AND** the communication is labeled as PostgreSQL NOTIFY mechanism

### Requirement: Color Coding and Visual Hierarchy
The system SHALL use consistent color coding to distinguish functional areas of the database schema.

#### Scenario: Functional color groups
- **WHEN** rendering the database schema diagram
- **THEN** Assignment columns use blue color (#007bff)
- **AND** Monitoring columns use yellow/gold color (#ffc107)
- **AND** Performance Metrics columns use green color (#28a745)
- **AND** Trigger/notification flow uses purple color (#6f42c1)
- **AND** all colors are colorblind-friendly

#### Scenario: Visual hierarchy
- **WHEN** organizing diagram elements
- **THEN** VM Table is the primary focus at the top
- **AND** Trigger flow components are arranged vertically below the table
- **AND** Client VMs are shown at the bottom receiving notifications
- **AND** Arrows clearly indicate data flow direction

### Requirement: Format Presets
The system SHALL support paper and poster format presets with appropriate font sizes and spacing.

#### Scenario: Paper format preset
- **WHEN** the `fontsize_preset="paper"` parameter is used
- **THEN** the diagram uses 14pt font for node labels
- **AND** the diagram uses 14pt font for edge labels
- **AND** the diagram uses 32pt font for the title
- **AND** the output DPI is 300
- **AND** spacing is optimized for journal two-column layout

#### Scenario: Poster format preset
- **WHEN** the `fontsize_preset="poster"` parameter is used
- **THEN** the diagram uses 20pt font for node labels
- **AND** the diagram uses 20pt font for edge labels
- **AND** the diagram uses 48pt font for the title
- **AND** the output DPI is 300
- **AND** spacing is increased for conference poster readability

### Requirement: Integration with Diagram Generation CLI
The system SHALL integrate with the existing architecture diagram generation command-line interface.

#### Scenario: CLI database-schema option
- **WHEN** the user runs `generate_architecture_diagram.py --diagram-type database-schema`
- **THEN** the database schema diagram is generated
- **AND** the output is saved to `figures/main/lablink-database-schema.{format}`
- **AND** the command supports `--fontsize-preset` option
- **AND** the command supports `--format` option (png, svg, pdf, all)

#### Scenario: Integration with existing diagram types
- **WHEN** the user specifies `--diagram-type all-essential`
- **THEN** the database schema diagram is optionally included in the output
- **AND** generation of other diagrams is not affected
- **AND** the diagram appears in timestamped run folders if enabled

### Requirement: Output File Formats
The system SHALL generate database schema diagrams in multiple file formats.

#### Scenario: Multiple format support
- **WHEN** generating the database schema diagram
- **THEN** PNG format is supported for raster output
- **AND** PDF format is supported for vector output
- **AND** SVG format is supported for web/vector output
- **AND** all formats contain identical visual content

#### Scenario: File naming convention
- **WHEN** saving output files
- **THEN** files are named `lablink-database-schema.{format}`
- **AND** files follow the existing naming pattern of other architecture diagrams
- **AND** files are saved to the configured output directory (default: `figures/main/`)

### Requirement: Visual Consistency
The system SHALL maintain visual consistency with existing LabLink architecture diagrams.

#### Scenario: Consistent graph attributes
- **WHEN** generating the database schema diagram
- **THEN** the diagram uses the same graph attribute helper methods as other diagrams
- **AND** the diagram uses `_create_graph_attr()` for graph-level settings
- **AND** the diagram uses `_create_node_attr()` for node styling
- **AND** the diagram uses `_create_edge_attr()` for edge styling

#### Scenario: Consistent visual style
- **WHEN** rendering the diagram
- **THEN** the diagram uses Helvetica font family
- **AND** the diagram uses white background
- **AND** the diagram uses orthogonal edge routing (splines="ortho")
- **AND** the diagram uses the same padding and spacing patterns as other architecture diagrams

### Requirement: Documentation and Metadata
The system SHALL provide comprehensive documentation for the database schema visualization.

#### Scenario: Metadata file generation
- **WHEN** the database schema diagram is generated
- **THEN** a metadata file is created at `figures/main/lablink-database-schema_metadata.txt`
- **AND** the metadata includes generation timestamp
- **AND** the metadata includes fontsize preset used
- **AND** the metadata references source schema file (generate_init_sql.py)
- **AND** the metadata includes column count (19)

#### Scenario: Documentation references
- **WHEN** documenting the database schema figure
- **THEN** the figure summary references `analysis/database-schema-analysis.md`
- **AND** code comments reference specific lines in `generate_init_sql.py`
- **AND** the docstring explains the purpose of each visualization component

### Requirement: Performance Metrics Visualization
The system SHALL clearly illustrate the 3-phase VM startup performance tracking structure.

#### Scenario: Phase grouping
- **WHEN** visualizing performance metrics columns
- **THEN** Phase 1 (Terraform) columns are grouped: TerraformApplyStartTime, TerraformApplyEndTime, TerraformApplyDurationSeconds
- **AND** Phase 2 (Cloud-init) columns are grouped: CloudInitStartTime, CloudInitEndTime, CloudInitDurationSeconds
- **AND** Phase 3 (Container) columns are grouped: ContainerStartTime, ContainerEndTime, ContainerStartupDurationSeconds
- **AND** Total startup metric is highlighted: TotalStartupDurationSeconds

#### Scenario: Metrics annotation
- **WHEN** displaying performance metrics
- **THEN** each phase is labeled with its purpose
- **AND** typical duration ranges are optionally annotated
- **AND** the relationship between individual phases and total startup time is clear

### Requirement: Data Flow Integration Points
The system SHALL show how the database integrates with other LabLink components.

#### Scenario: Component interactions
- **WHEN** illustrating database integration
- **THEN** the Allocator service is shown performing INSERT/UPDATE operations
- **AND** Client VMs are shown performing LISTEN operations
- **AND** Lambda functions are shown storing logs via the allocator API
- **AND** arrows indicate the direction of data flow

#### Scenario: Operation labels
- **WHEN** labeling data flow arrows
- **THEN** INSERT operations are labeled clearly
- **AND** UPDATE operations are labeled clearly
- **AND** LISTEN operations are labeled clearly
- **AND** pg_notify events are labeled clearly

### Requirement: CRD Connection Diagram Consistency
The system SHALL ensure the database schema diagram is consistent with the existing CRD connection workflow diagram.

#### Scenario: Trigger representation consistency
- **WHEN** both diagrams are viewed together
- **THEN** the trigger name `trigger_crd_command_insert_or_update` is identical in both
- **AND** the function name `notify_crd_command_update()` is identical in both
- **AND** the channel name 'vm_updates' is identical in both
- **AND** the payload structure is consistent in both diagrams

#### Scenario: Complementary focus
- **WHEN** comparing schema and workflow diagrams
- **THEN** the schema diagram focuses on table structure and trigger mechanics
- **AND** the CRD connection diagram focuses on the 15-step user workflow
- **AND** the schema diagram does not duplicate workflow steps
- **AND** the two diagrams reference each other in documentation
