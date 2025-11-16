# Capability: API Diagram Visualization

## Overview

Generate publication-quality API architecture diagrams for the LabLink Flask API (22 endpoints) using an actor-centric visualization pattern that clearly shows:
- External actors (User, Admin, Client VM, Lambda)
- Allocator infrastructure with grouped API categories
- Security requirements (Public, Authenticated, Validated)
- Data flows between actors and API groups

## MODIFIED Requirements

### Requirement: Generate actor-centric API architecture diagram

The system SHALL generate an API architecture diagram using an actor-centric pattern instead of endpoint-by-endpoint node representation.

**Previous behavior**: Generated diagram with 18+ individual endpoint nodes (Storage/Firewall icons) nested in 6 clusters, resulting in vertical column layout with broken edges.

**New behavior**: Generate diagram with 4 external actors, central Allocator cluster containing Flask API and 5 functional API groups, using horizontal LR layout.

#### Scenario: Generate diagram with horizontal layout

**Given** the diagram type is `api-architecture`
**And** the direction is set to `"LR"` (left-to-right)
**When** the diagram is generated
**Then** the output image should have width > height
**And** actors should be positioned on the left
**And** Allocator infrastructure should be in the center
**And** database should be on the right or within Allocator cluster
**And** all edges should be rendered properly (no broken/missing arrows)

#### Scenario: Show 4 external actors

**Given** the API architecture diagram is being generated
**When** external actors are created
**Then** the diagram must include exactly 4 actor nodes:
- User (labeled "User" or "Researcher")
- Admin (labeled "Admin")
- Client VM (EC2 instance icon)
- Lambda (Lambda function icon, labeled "Log Processor" or "Lambda")
**And** all actors should use appropriate icons from diagrams library

#### Scenario: Show Allocator as central infrastructure

**Given** the API architecture diagram is being generated
**When** the Allocator infrastructure is created
**Then** a Cluster named "LabLink Allocator" or "LabLink Allocator (EC2)" must be created
**And** the cluster must contain:
- Flask API server node (labeled "Flask API" with route count)
- HTTP Basic Auth security component (IAM icon)
- 5 functional API group elements (see next scenario)
**And** the cluster should be visually centered between actors and database

#### Scenario: Group endpoints into 5 functional categories

**Given** the Allocator cluster is being created
**When** API endpoint groups are defined
**Then** exactly 5 functional groups must be shown:

1. **User Interface** (2 endpoints) - Public access
   - Label must include endpoint count
   - Must indicate public access (no auth required)

2. **Admin Management** (10 endpoints) - Authenticated access
   - Label must include endpoint count
   - Must clearly indicate "@auth.login_required" or "HTTP Basic Auth required"

3. **VM-to-Allocator API** (5 endpoints) - Public with validation
   - Label must include endpoint count
   - Must indicate "hostname validated" or similar validation requirement

4. **Query API** (4 endpoints) - Public access
   - Label must include endpoint count
   - Must indicate public access

5. **Lambda Callback** (1 endpoint) - Internal validation
   - Label must include endpoint count
   - Must indicate internal or validated access

**And** groups should be represented as simple labeled boxes or text annotations (not individual endpoint nodes)
**And** total endpoint count across all groups must equal 22

#### Scenario: Use color-coded edges for security levels

**Given** edges are being created between actors and API groups
**When** security requirements differ
**Then** edge colors must indicate access level:
- **Green (#28a745)**: Public endpoints (User → User Interface, User/Admin → Query API)
- **Gold/Yellow (#ffc107)**: Authenticated endpoints (Admin → Admin Management)
- **Blue (#007bff)**: Validated endpoints (Client VM → VM Callbacks)
- **Purple (#6f42c1)**: Internal endpoints (Lambda → Lambda Callback)
- **Gray (#6c757d)**: Database operations

**And** authenticated flows must include IAM/lock icon or visual security indicator
**And** validated flows should include validation indicator (checkmark, shield, or label)

#### Scenario: Show data flows to database

**Given** the API groups interact with the database
**When** database edges are created
**Then** connections must be shown from API groups to PostgreSQL database:
- User Interface → Database (VM assignment writes)
- Admin Management → Database (provisioning, teardown writes)
- VM Callbacks → Database (status, metrics, health writes)
- Query API → Database (status, logs reads)
- Lambda Callback → Database (log writes)

**And** edges may be simplified to show Flask API → Database if individual group edges create clutter

#### Scenario: Support configurable font presets

**Given** the `fontsize_preset` parameter is provided
**When** the diagram is generated
**Then** font sizes must be applied from the preset:
- `"paper"`: 14pt fonts for publication
- `"poster"`: 20pt fonts for poster presentation
- `"presentation"`: 16pt fonts for slides

**And** all text (node labels, edge labels, titles) must be scaled consistently
**And** the diagram must render legibly at all three preset sizes

#### Scenario: Render with minimal cluster nesting

**Given** the diagram uses nested clusters
**When** the cluster hierarchy is defined
**Then** maximum nesting depth must not exceed 2 levels:
- Level 1: Allocator cluster (optional: separate clusters for actors if needed)
- Level 2: API group boxes within Allocator (if groups are clusters)

**And** this ensures LR direction works correctly and edges route properly

#### Scenario: Generate output in specified format

**Given** the format parameter is `"png"`, `"jpg"`, or `"svg"`
**When** the diagram is generated
**Then** the output file must be created with the specified extension
**And** the file must be a valid image in the requested format
**And** PNG format must use the specified DPI (default 300)
**And** the filename must be `lablink-api-architecture.{format}`

### Requirement: Ensure text readability on all node types

The system SHALL ensure all text is readable by avoiding white text on white backgrounds.

#### Scenario: Use black font color for all nodes

**Given** node attributes are being configured
**When** the `node_attr` dictionary is created
**Then** `fontcolor` must be set to `"black"`
**And** this must apply to all node types (Flask, EC2, Lambda, RDS, Blank, etc.)
**And** API group boxes must also use black font color if using Blank nodes

#### Scenario: Use visible background colors for group boxes

**Given** API groups are represented as Blank nodes or simple boxes
**When** the visual styling is applied
**Then** background color should be light gray (#f8f9fa) or similar light color
**And** border color should be visible (#dee2e6 or similar)
**And** text should remain black for contrast
**And** this prevents white-on-white readability issues

### Requirement: Maintain reference to comprehensive endpoint documentation

The system SHALL link the simplified diagram to the comprehensive endpoint documentation.

#### Scenario: Include reference to analysis document in docstring

**Given** the `build_api_architecture_diagram()` method is being documented
**When** the docstring is written
**Then** it must include a reference to `analysis/api-architecture-analysis.md`
**And** it must state that all 22 endpoints are documented there
**And** it should explain that the diagram shows architectural patterns, not exhaustive inventory

#### Scenario: Generate success message with documentation reference

**Given** the diagram has been generated successfully
**When** the success message is printed
**Then** the message should reference the analysis document for endpoint details:
```
API architecture diagram saved to {output_path}
See analysis/api-architecture-analysis.md for complete endpoint documentation (22 endpoints)
```

## ADDED Requirements

None. This change modifies an existing capability.

## REMOVED Requirements

### Requirement: Generate individual nodes for each endpoint

**Removed**: The previous approach of creating individual Storage (GET) and Firewall (POST) nodes for representative endpoints is replaced by functional grouping.

**Rationale**: Individual endpoint nodes caused severe layout issues (vertical stacking, broken edges) and do not follow industry best practices for API visualization.

#### Scenario: Create Storage node for each GET endpoint

**REMOVED**: No longer creating individual Storage nodes for GET endpoints like `GET /`, `GET /api/vm-status`, etc.

#### Scenario: Create Firewall node for each POST endpoint

**REMOVED**: No longer creating individual Firewall nodes for POST endpoints like `POST /api/request_vm`, `POST /vm_startup`, etc.

#### Scenario: Nest endpoints in 6 categorical clusters

**REMOVED**: No longer using deep cluster nesting (User Interface → Admin Management → VM API → Query API → Lambda Callback → Security).

**Rationale**: Deep nesting overrides LR direction and causes vertical stacking.

## Dependencies

- Python `diagrams` library (mingrammer/diagrams)
- GraphViz backend
- Font preset system (defined in `DiagramGenerator._create_graph_attr()`)
- Analysis document: `analysis/api-architecture-analysis.md`

## Testing Notes

Test with all three font presets:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type api-architecture \
  --fontsize-preset poster

uv run python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type api-architecture \
  --fontsize-preset paper

uv run python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type api-architecture \
  --fontsize-preset presentation
```

Verify:
1. Horizontal layout (width > height)
2. All 4 actors visible
3. All 5 API groups visible with endpoint counts
4. Security levels indicated by colors
5. All edges rendered properly
6. Text readable at 100% zoom
7. File size reasonable (< 2MB for PNG)
