# Design: Expand LabLink Architecture Diagram Suite

## Problem Space

### Current State
- **One diagram**: System Overview showing Admin → Allocator → VMs → CloudWatch → Lambda → Allocator
- **Missing mechanisms**: VM provisioning, CRD setup, monitoring, data collection, detailed logging
- **Paper readability**: Single diagram insufficient to explain complete system

### Requirements
1. **Pedagogical clarity**: Each diagram should teach one architectural concept
2. **Code accuracy**: All flows must match actual implementation in lablink codebase
3. **Publication quality**: Suitable for research paper (clean, professional, high DPI)
4. **Completeness**: Together, diagrams should cover all major architectural mechanisms
5. **Modularity**: Each diagram can be understood independently

## Architectural Decisions

### Decision 1: Multiple Focused Diagrams vs. One Comprehensive Diagram

**Options Considered**:
1. Expand existing diagram to show everything
2. Create multiple focused diagrams (one per mechanism)
3. Create layered diagrams (overview → detailed views)

**Chosen**: Option 2 (Multiple focused diagrams)

**Rationale**:
- Cognitive load: Research shows humans can understand ~7±2 components at once
- Orthogonal mechanisms: VM provisioning, CRD connection, logging, monitoring are independent concerns
- Paper flexibility: Authors can choose which diagrams to include based on page limits
- Reusability: Individual diagrams useful for presentations, documentation, teaching

**Trade-offs**:
- More files to maintain
- Readers need to look at multiple diagrams to understand full system
- Risk of inconsistency across diagrams

**Mitigation**:
- Use consistent visual style (same icons, colors, fonts)
- Add cross-references in captions
- Create shared component library in generator code

### Decision 2: PostgreSQL LISTEN/NOTIFY Representation

**Challenge**: How to visually represent database triggers and notifications?

**Options Considered**:
1. Show as simple database icon with edge labels
2. Explicitly show TRIGGER as separate component inside database cluster
3. Use sequence diagram notation for temporal flow
4. Custom notation with special trigger symbol

**Chosen**: Option 2 (TRIGGER as component inside PostgreSQL cluster)

**Rationale**:
- Architectural significance: TRIGGER is not just a database feature, it's a key coordination mechanism
- Pedagogical value: Makes the "magic" of real-time notification explicit
- Code accuracy: Matches implementation in `generate_init_sql.py` where TRIGGER is explicitly defined
- Unique innovation: This pattern is unusual, deserves visual emphasis

**Implementation**:
```python
with Cluster("PostgreSQL Database"):
    vm_table = Custom("VM Table", icon_path)
    trigger = Custom("TRIGGER\n(on CrdCommand)", icon_path)
    notify_function = Custom("pg_notify()", icon_path)

    vm_table >> Edge(label="UPDATE") >> trigger
    trigger >> Edge(label="Fires") >> notify_function
    notify_function >> Edge(label="Notification", style="dashed") >> subscribe_service
```

**Validation**:
- Check `generate_init_sql.py` for TRIGGER definition
- Verify `subscribe.py` actually uses PostgreSQL LISTEN
- Confirm payload format matches

### Decision 3: Diagram Prioritization (Essential vs. Supplementary)

**Challenge**: Which diagrams are must-have vs. nice-to-have?

**Prioritization Framework**:
- **Priority 1 (Essential)**: Shows unique mechanism or core functionality, not redundant with existing diagrams
- **Priority 2 (Supplementary)**: Shows supporting functionality or operational details, useful but not critical
- **Priority 3 (Reference)**: Implementation details for developers, not for paper

**Classification**:

**Priority 1 (Essential - must include in paper)**:
1. System Overview (existing) - High-level architecture
2. VM Provisioning & Lifecycle (new) - Core dynamic allocation mechanism
3. CRD Connection via Database Notification (new) - **Unique architectural innovation**
4. Logging Pipeline (enhanced) - Observability infrastructure

**Rationale**:
- CRD diagram shows unique LISTEN/NOTIFY pattern (not found in similar systems)
- VM provisioning shows Terraform-as-subprocess (core innovation)
- Logging shows cloud-native observability (important for scalability claims)
- Together: provisioning (how VMs created) → connection (how users access) → monitoring (how system observed)

**Priority 2 (Supplementary - include if space permits)**:
5. VM Status & Health Monitoring - Shows robustness mechanisms
6. Data Collection & Export - Shows end-to-end research workflow

**Rationale**:
- Monitoring diagram shows system is production-ready, but mechanism is standard (polling)
- Data collection shows practical research use case, but SSH/rsync is conventional
- Both valuable but not architecturally novel

**Priority 3 (Reference - for documentation/wiki)**:
- Infrastructure Provisioning (initial setup)
- VM Teardown & Cleanup
- Network Routing (DNS/SSL variants)
- Database Schema

**Rationale**:
- Important for operators, not for research contribution
- Better suited for documentation than paper

### Decision 4: Visual Encoding Strategy

**Challenge**: How to indicate different types of components and relationships?

**Encoding Dimensions**:

**1. Component Type** (via icon + cluster)
- AWS services: Use diagrams library AWS icons (EC2, Lambda, CloudWatch, RDS)
- External entities: User, Admin icons
- Custom components: Allocator, TRIGGER, subscribe service

**2. Execution Context** (via cluster boundaries)
- Infrastructure cluster: Long-lived AWS resources
- Dynamic Compute cluster: Runtime-provisioned VMs
- Observability cluster: Monitoring and logging
- PostgreSQL Database cluster: Data layer with TRIGGER

**3. Control Flow** (via edge attributes)
- Solid edges: Direct API calls, data flow
- Dashed edges: Asynchronous notifications, triggers
- Orange edges: Resource provisioning actions
- Edge labels: Action or data being transferred

**4. Timing/Sequence** (via annotations)
- Number annotations: (1), (2), (3) for sequence steps
- Phase labels: "Phase 1: Cloud-init", "Phase 2: Docker", "Phase 3: Container"
- Status transitions: initializing → running → error

**5. Special Notation**:
- Subprocess: Show Terraform inside Allocator with dotted boundary
- Long-polling: Show wait symbol on edge (⏳ or "blocks up to 7 days")
- Parallel flows: Use horizontal alignment with "concurrent" annotation

**Consistency Rules**:
- Always use same icon for same component across diagrams
- Always use same cluster name across diagrams
- Always use same color scheme across diagrams
- Edge label font size: 12pt (consistent with current main diagram)

### Decision 5: Code Reference Validation

**Challenge**: How to ensure diagrams accurately represent code?

**Validation Strategy**:

**1. File-level validation**:
- Each diagram must document code references in docstring
- Example: `# Code: main.py::launch(), terraform/main.tf, user_data.sh`
- CI could validate files exist (future enhancement)

**2. Flow-level validation**:
- Each edge must correspond to actual function call or data flow
- Example: "Lambda → POST /api/vm-logs → Allocator" verified in `lambda_function.py` lines 32-36

**3. Component-level validation**:
- Each component must correspond to actual code construct
- Example: TRIGGER verified in `generate_init_sql.py` lines 51-59

**4. Test-driven diagram generation**:
- Write test first that specifies expected components and edges
- Generate diagram
- Assert diagram contains expected elements

**Implementation**:
```python
def test_crd_connection_diagram_accuracy():
    """Validate CRD connection diagram matches codebase."""
    # Read actual code files
    sql_code = Path("../lablink/.../generate_init_sql.py").read_text()
    subscribe_code = Path("../lablink/.../subscribe.py").read_text()

    # Verify key components exist in code
    assert "pg_notify" in sql_code
    assert "TRIGGER" in sql_code
    assert "LISTEN" in subscribe_code
    assert "vm_updates" in subscribe_code  # channel name

    # Generate diagram
    builder.build_crd_connection_diagram(...)

    # Verify diagram has expected components
    # (This would require diagram introspection, may not be feasible)
```

## Component Design

### Generator Class Structure

**Current** (`generator.py`):
```python
class LabLinkDiagramBuilder:
    def __init__(self, config: ParsedTerraformConfig)
    def build_main_diagram(...)
    def build_detailed_diagram(...)
    def build_network_flow_diagram(...)
    def _create_compute_components(...)
    def _create_observability_components(...)
```

**Enhanced**:
```python
class LabLinkDiagramBuilder:
    # Existing methods (unchanged)
    def build_main_diagram(...)
    def build_detailed_diagram(...)
    def build_network_flow_diagram(...)

    # New diagram builders (Priority 1)
    def build_vm_provisioning_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300
    ):
        """Generate VM provisioning & lifecycle diagram.

        Shows: Admin → Allocator → Terraform subprocess → AWS EC2
        with 3-phase startup sequence and timing metrics.

        Code references:
        - main.py::launch() - Terraform subprocess execution
        - terraform/main.tf - Client VM provisioning
        - user_data.sh - Cloud-init phase
        - start.sh - Container startup phase
        """

    def build_crd_connection_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300
    ):
        """Generate CRD connection setup diagram.

        Shows: User → Allocator → PostgreSQL (TRIGGER) → Client VM (subscribe)
        → Chrome Remote Desktop

        Code references:
        - main.py::submit_vm_details() - User request handling
        - database.py::assign_vm() - UPDATE VM record
        - generate_init_sql.py - TRIGGER definition
        - subscribe.py - LISTEN for notifications
        - connect_crd.py - Execute CRD command
        """

    def build_logging_pipeline_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300
    ):
        """Generate enhanced logging pipeline diagram.

        Shows: Client VM → CloudWatch Agent → CloudWatch Logs →
        Subscription Filter → Lambda → Allocator API → PostgreSQL

        Code references:
        - user_data.sh - CloudWatch agent installation
        - lambda_function.py - Log processing
        - main.py::receive_vm_logs() - Log storage
        - database.py::save_logs_by_hostname() - Database persistence
        """

    # New diagram builders (Priority 2)
    def build_monitoring_diagram(...)
    def build_data_collection_diagram(...)

    # Utility methods for complex components
    def _create_database_with_trigger(self) -> tuple:
        """Create PostgreSQL cluster with TRIGGER visualization."""

    def _create_terraform_subprocess(self, parent_cluster) -> Any:
        """Show Terraform as subprocess inside Allocator."""

    def _create_parallel_monitoring_flows(self) -> list:
        """Create three concurrent monitoring service flows."""

    def _create_three_phase_startup(self) -> tuple:
        """Create 3-phase client VM startup sequence."""
```

### CLI Updates

**Current**:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type main|detailed|network-flow|all \
  --format png|svg|pdf \
  --dpi 300
```

**Enhanced**:
```bash
python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type main|detailed|network-flow|vm-provisioning|crd-connection|logging-pipeline|monitoring|data-collection|all \
  --format png|svg|pdf \
  --dpi 300 \
  [--all-essential]  # Generate priority 1 diagrams (main, vm-provisioning, crd-connection, logging-pipeline)
  [--all-supplementary]  # Generate priority 2 diagrams (monitoring, data-collection)
```

## Implementation Plan

### Phase 1: Infrastructure Setup
1. Create `expand-diagram-suite` OpenSpec change directory ✅
2. Write proposal.md ✅
3. Write design.md (this file) ✅
4. Write tasks.md (next)
5. Create stub methods in `generator.py`

### Phase 2: Essential Diagrams (Priority 1)
1. Implement `build_vm_provisioning_diagram()`
   - Show Terraform subprocess notation
   - Show 3-phase startup sequence
   - Add timing metric annotations
2. Implement `build_crd_connection_diagram()`
   - Create database cluster with TRIGGER component
   - Show LISTEN/NOTIFY flow
   - Add long-polling annotation
3. Implement `build_logging_pipeline_diagram()`
   - Enhance existing logging flow
   - Show CloudWatch agent installation
   - Show database log storage

### Phase 3: Supplementary Diagrams (Priority 2)
1. Implement `build_monitoring_diagram()`
   - Show three parallel services
   - Use horizontal alignment
2. Implement `build_data_collection_diagram()`
   - Show SSH/Docker/rsync flow
   - Show zip creation

### Phase 4: Testing & Validation
1. Add tests for each new diagram type
2. Validate code references exist
3. Generate all diagrams at high DPI
4. Update README with diagram descriptions

### Phase 5: Documentation
1. Add diagram usage guide to README
2. Document code references in each diagram method
3. Create paper figure captions

## Testing Strategy

### Unit Tests
- Test each diagram builder method independently
- Mock ParsedTerraformConfig if needed
- Assert diagram files are created

### Integration Tests
- Generate all diagrams with actual Terraform configs
- Validate file sizes are reasonable (not empty, not gigantic)
- Check metadata files are created

### Code Reference Tests
- For each diagram, validate referenced files exist in lablink repo
- Check referenced functions/classes exist
- Warn if code structure has changed

### Visual Inspection
- Generate all diagrams locally
- Manual review for clarity, consistency, accuracy
- Check font sizes, spacing, alignment

## Open Questions

1. **Custom icons for TRIGGER?** - May need to create custom SVG for database trigger
2. **Subprocess notation?** - How to best show Terraform inside Allocator? Dotted boundary? Nested cluster?
3. **Long-polling visualization?** - How to indicate blocking wait? Clock icon? Special edge style?
4. **Paper page limits?** - How many diagrams will paper actually include? Affects prioritization.
5. **Color accessibility?** - Should validate colors work for colorblind readers

## Dependencies

### Internal
- Requires `add-architecture-diagram` change completed (provides base infrastructure)
- Requires Python diagrams library
- Requires graphviz

### External
- Access to `../lablink` repo for code reference validation
- Access to `../lablink-template` repo for Terraform configs

## Success Metrics

1. **Coverage**: All 8 architectural mechanisms from analysis have corresponding diagrams
2. **Accuracy**: All code references valid (files and functions exist)
3. **Clarity**: Each diagram understandable by someone unfamiliar with LabLink
4. **Consistency**: Same visual style across all diagrams
5. **Completeness**: Paper readers can understand full system from 4-6 diagrams

## Future Enhancements

- Sequence diagrams for temporal flows (alternative to architecture diagrams)
- Interactive web-based diagrams (Plotly/D3.js)
- Animated diagrams showing flow over time
- Diagram diff tool to show architecture evolution
- Auto-generated diagrams from runtime telemetry (show actual flows, not designed flows)
