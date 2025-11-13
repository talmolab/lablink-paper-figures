# Diagram Improvements Specification

## ADDED Requirements

### Requirement: Diagram Title Placement at Top

The diagram generation system SHALL place all diagram titles at the top of the image (not bottom) for improved professional appearance and scanning usability.

#### Scenario: Title placement for main architecture diagram
- **WHEN** generating lablink-architecture.png diagram
- **THEN** the title "LabLink Core Architecture" SHALL appear at the top of the diagram
- **AND** the title SHALL use 32pt font size
- **AND** the title SHALL be implemented via GraphViz `labelloc="t"` attribute

#### Scenario: Title placement for all essential diagrams
- **WHEN** generating any of the 4 essential diagrams (architecture, crd-connection, logging-pipeline, vm-provisioning)
- **THEN** all titles SHALL appear at top of diagram
- **AND** placement SHALL be consistent across all diagrams

### Requirement: Increased Text Size for Readability

The diagram generation system SHALL use increased font sizes for all text elements (except titles) to ensure readability in printed publications at 300 DPI.

#### Scenario: Node label text size
- **WHEN** generating any essential diagram
- **THEN** node labels SHALL use 14pt font size (increased from 11pt)
- **AND** font SHALL be "Helvetica" for consistency
- **AND** text SHALL be readable when printed at typical paper sizes (6-8 inches wide)

#### Scenario: Edge label text size
- **WHEN** generating any essential diagram
- **THEN** edge labels SHALL use 14pt font size (increased from 12pt)
- **AND** font SHALL be "Helvetica" for consistency
- **AND** edge labels SHALL be large enough to read without magnification in print

#### Scenario: Title text size unchanged
- **WHEN** generating any essential diagram
- **THEN** diagram titles SHALL remain at 32pt font size
- **AND** cluster labels SHALL remain at 32pt font size
- **AND** visual hierarchy (title > labels) SHALL be maintained

### Requirement: Improved Edge Label Positioning

The diagram generation system SHALL configure edge labels to position clearly and avoid excessive overlap with edge lines, within GraphViz layout engine capabilities.

#### Scenario: Edge label float configuration
- **WHEN** generating any essential diagram
- **THEN** edge attributes SHALL include `labelfloat="true"`
- **AND** this SHALL allow GraphViz to intelligently position labels away from edges
- **AND** labeldistance and labelangle SHALL be configured for clarity

#### Scenario: GraphViz limitation documentation
- **WHEN** documenting edge label positioning
- **THEN** known GraphViz limitation SHALL be documented: "No native 'always N pixels above line' positioning exists"
- **AND** `labelfloat=true` SHALL be documented as "good enough" solution
- **AND** developers SHALL understand this is not perfect but significantly better than default

### Requirement: Icon Replacement for Missing Graphics

The diagram generation system SHALL replace generic Blank placeholder nodes with semantically appropriate icons from the diagrams library or custom icons where needed.

#### Scenario: Replace CloudWatch Agent Blank node
- **WHEN** generating logging-pipeline diagram
- **THEN** CloudWatch Agent SHALL use `aws.management.Cloudwatch` icon OR appropriate monitoring icon
- **AND** Blank node SHALL NOT be used
- **AND** icon SHALL visually represent monitoring/agent functionality

#### Scenario: Replace Subscription Filter Blank node
- **WHEN** generating logging-pipeline diagram
- **THEN** Subscription Filter SHALL use `CloudwatchEventEventBased` icon from `diagrams.aws.management`
- **AND** icon SHALL visually represent event-based filtering

#### Scenario: Replace Python script Blank nodes in CRD diagram
- **WHEN** generating crd-connection diagram
- **THEN** subscribe.py SHALL use `programming.language.Python` icon with label "subscribe.py (LISTEN)"
- **AND** connect_crd.py SHALL use `programming.language.Python` icon with label "connect_crd.py"
- **AND** icons SHALL clearly indicate these are Python scripts

#### Scenario: Replace database TRIGGER and pg_notify Blank nodes
- **WHEN** generating crd-connection diagram
- **THEN** TRIGGER SHALL use RDS or PostgreSQL icon with label "Database TRIGGER"
- **AND** pg_notify() SHALL use `onprem.database.Postgresql` icon with label "pg_notify()"
- **AND** icons SHALL represent database-related functionality

#### Scenario: Replace Terraform subprocess Blank node
- **WHEN** generating vm-provisioning diagram
- **THEN** Terraform subprocess SHALL use Custom node with terraform.png icon OR diagrams library Terraform icon if available
- **AND** Terraform logo SHALL be recognizable
- **AND** icon SHALL be ~256x256px for consistency

#### Scenario: Acceptable use of Blank nodes
- **WHEN** no semantically appropriate icon exists in diagrams library
- **AND** custom icon would be overly complex or unclear
- **THEN** Blank node MAY be used as fallback
- **AND** rationale SHALL be documented in code comments

### Requirement: Accurate Edge Label Text

The diagram generation system SHALL use technically accurate and precise edge label text that correctly describes system behavior.

#### Scenario: CRD connection accuracy
- **WHEN** generating crd-connection diagram
- **THEN** edge from connect_crd.py to CRD SHALL be labeled "Authenticates & Connects to" (not "Launches")
- **AND** edge from CRD to user SHALL be labeled "WebRTC P2P Connection" (technically precise)
- **AND** labels SHALL reflect that CRD authenticates and establishes connection, not application launch

#### Scenario: Subscription filter clarity
- **WHEN** generating logging-pipeline diagram
- **THEN** edge from log group to subscription filter SHALL be labeled "Triggers (on pattern match)"
- **AND** label SHALL clarify that triggering is pattern-based
- **AND** mechanism SHALL be clear from label text

#### Scenario: VM provisioning title accuracy
- **WHEN** generating vm-provisioning diagram
- **THEN** diagram title SHALL be "LabLink VM Provisioning" (not "VM Provisioning & Lifecycle")
- **AND** title SHALL accurately reflect diagram scope (provisioning only, not full lifecycle)

### Requirement: Complete Architectural Flows

The diagram generation system SHALL show complete architectural flows including missing feedback paths and viewing endpoints.

#### Scenario: Admin viewing logs in logging pipeline
- **WHEN** generating logging-pipeline diagram
- **THEN** diagram SHALL include Admin user node
- **AND** edge from database to admin SHALL show "View logs (web UI)"
- **AND** complete logging story SHALL be shown: collection → storage → viewing

#### Scenario: VM feedback to allocator in provisioning
- **WHEN** generating vm-provisioning diagram
- **THEN** diagram SHALL include edge from Client VM to Allocator labeled "Status updates (POST /api/vm-metrics)"
- **AND** diagram SHALL include edge from Allocator to Database labeled "Store provisioning metrics"
- **AND** two-way communication SHALL be visible (not just one-way provisioning)

#### Scenario: CRD authentication context
- **WHEN** generating crd-connection diagram
- **THEN** Client VM SHALL be annotated as "Client VM (Admin-provisioned)"
- **AND** context SHALL clarify VMs are pre-provisioned, not created by CRD connection
- **AND** CRD authentication mechanism SHALL be explained in documentation or annotations

### Requirement: Consistent Styling Helper Methods

The diagram generation code SHALL use reusable helper methods to ensure consistent styling across all diagrams.

#### Scenario: Graph attribute consistency
- **WHEN** generating any essential diagram
- **THEN** diagram SHALL use `_create_graph_attr()` helper method
- **AND** method SHALL return consistent dictionary with labelloc, fontsize, dpi, etc.
- **AND** no diagram SHALL have inline graph_attr duplication

#### Scenario: Node attribute consistency
- **WHEN** generating any essential diagram
- **THEN** diagram SHALL use `_create_node_attr()` helper method
- **AND** method SHALL return consistent dictionary with fontsize=14, fontname="Helvetica"
- **AND** all diagrams SHALL have uniform node label styling

#### Scenario: Edge attribute consistency
- **WHEN** generating any essential diagram
- **THEN** diagram SHALL use `_create_edge_attr()` helper method
- **AND** method SHALL return consistent dictionary with fontsize=14, labelfloat="true"
- **AND** all diagrams SHALL have uniform edge label styling

#### Scenario: Helper method parameterization
- **WHEN** helper methods are defined
- **THEN** they SHALL accept parameters for customization (e.g., fontsize, dpi)
- **AND** default values SHALL be publication-quality (dpi=300, fontsize=14)
- **AND** methods SHALL have docstrings documenting parameters

### Requirement: Publication Quality Maintenance

The diagram generation system SHALL maintain 300 DPI resolution and publication-ready quality for all diagrams.

#### Scenario: DPI resolution preservation
- **WHEN** generating any essential diagram
- **THEN** output SHALL be 300 DPI PNG format
- **AND** resolution SHALL be sufficient for print publication
- **AND** DPI setting SHALL be configurable via parameter (default 300)

#### Scenario: File size reasonableness
- **WHEN** generating any essential diagram
- **THEN** output PNG file size SHALL be between 100KB and 300KB typically
- **AND** file size SHALL not balloon excessively from styling changes
- **AND** file SHALL be in PNG format with white background

#### Scenario: Print readability validation
- **WHEN** diagrams are printed at typical paper sizes (6-8 inches wide)
- **THEN** all text SHALL be readable without magnification
- **AND** text size SHALL be appropriate for comfortable reading
- **AND** layout SHALL not overflow or have excessive text overlap

### Requirement: Technical Accuracy Validation

The diagram generation system and documentation SHALL validate technical accuracy of all diagram elements against actual LabLink codebase.

#### Scenario: WebRTC verification for CRD
- **WHEN** documenting CRD connection mechanism
- **THEN** WebRTC claim SHALL be verified via research (confirmed: CRD uses WebRTC + Chromoting)
- **AND** documentation SHALL cite sources (web search results confirming WebRTC usage)
- **AND** technical accuracy SHALL be maintained

#### Scenario: Code reference validation
- **WHEN** diagram shows architectural flow (e.g., subscribe.py, connect_crd.py, TRIGGER)
- **THEN** corresponding code files SHALL exist in LabLink codebase
- **AND** flow SHALL match actual code behavior
- **AND** any discrepancies SHALL be documented

#### Scenario: Missing context documentation
- **WHEN** diagram omits important context (e.g., VMs are admin-provisioned)
- **THEN** context SHALL be added via annotations or documentation
- **AND** readers SHALL not be misled by incomplete information

## MODIFIED Requirements

None - This is a new capability, not modifying existing requirements.

## REMOVED Requirements

None - This is additive improvement, not removing functionality.
