# Proposal: Add Database Schema Figure

## Problem Statement

The LabLink paper currently lacks a dedicated visualization of the PostgreSQL database schema that powers the VM allocation and management system. While the CRD connection diagram shows the database as a component, it doesn't illustrate:

1. **Table structure**: The VM table's 19 columns organized by functional purpose
2. **Data relationships**: How different column groups (assignment, monitoring, performance) work together
3. **Trigger mechanism**: The database trigger that enables the LISTEN/NOTIFY pattern
4. **Design rationale**: Why a single-table design with comprehensive metrics tracking

### Current State

- **Existing diagrams** (11 total): Architecture, provisioning, CRD connection, logging, API, etc.
- **Database visibility**: Database appears as generic RDS/PostgreSQL icon without schema details
- **Documentation**: New comprehensive database schema analysis created ([database-schema-analysis.md](../../../analysis/database-schema-analysis.md))
- **Missing**: Standalone figure showing table schema, triggers, and data flow

### User Need

Readers of the LabLink paper need to understand:
1. How the database enables the long-polling pattern (blocking HTTP requests up to 7 days)
2. What performance metrics are tracked (3-phase startup sequence)
3. How triggers coordinate real-time notifications between allocator and client VMs
4. Why the single-table design is sufficient for this architecture

## Proposed Solution

Create a new **database schema diagram** with two configuration presets (paper and poster) that visualizes:

### Core Components

1. **VM Table Schema** - Annotated table showing all 19 columns grouped by function:
   - **Assignment columns** (HostName, UserEmail, CrdCommand, Pin)
   - **Monitoring columns** (Status, Healthy, InUse, Logs)
   - **Performance metrics** (9 timing columns for 3-phase startup)
   - **Metadata** (CreatedAt)

2. **Database Trigger Flow**:
   - Trigger: `trigger_crd_command_insert_or_update`
   - Function: `notify_crd_command_update()`
   - Channel: `pg_notify('vm_updates', ...)`

3. **Data Flow Arrows** showing:
   - Allocator → INSERT/UPDATE operations
   - Trigger → pg_notify event
   - Client VMs → LISTEN for notifications
   - Lambda → Log storage

4. **Status Values** annotation showing VM lifecycle states:
   - `initializing` → `running` → `assigned`
   - `available` (unassigned)
   - `error` (failed)

### Visual Style

- **Consistent** with existing architecture diagrams (using `diagrams` library)
- **Two presets**:
  - **Paper format**: 14pt fonts, 300 DPI, optimized for two-column journal layout
  - **Poster format**: 20pt fonts, 300 DPI, optimized for conference poster readability
- **Color coding**:
  - Blue for assignment-related columns
  - Yellow for monitoring columns
  - Green for performance metrics
  - Purple for trigger/notification flow

### Diagram Layout

```
┌───────────────────────────────────────────────────────────┐
│                  PostgreSQL VM Table                      │
├───────────────────────────────────────────────────────────┤
│ Assignment Group          Monitoring Group                │
│  • HostName (PK)           • Status                       │
│  • UserEmail               • Healthy                      │
│  • CrdCommand              • InUse                        │
│  • Pin                     • Logs                         │
│                                                            │
│ Performance Metrics Group                                 │
│  Phase 1: Terraform (3 columns)                          │
│  Phase 2: Cloud-init (3 columns)                         │
│  Phase 3: Container (3 columns)                          │
│  Total: TotalStartupDurationSeconds                      │
│                                                            │
│ Metadata: CreatedAt                                       │
└───────────────────────────────────────────────────────────┘
                    ↓ (UPDATE CrdCommand)
        ┌────────────────────────────┐
        │  TRIGGER                   │
        │  trigger_crd_command_      │
        │  insert_or_update          │
        └────────────────────────────┘
                    ↓
        ┌────────────────────────────┐
        │  FUNCTION                  │
        │  notify_crd_command_       │
        │  update()                  │
        └────────────────────────────┘
                    ↓
        ┌────────────────────────────┐
        │  pg_notify()               │
        │  Channel: 'vm_updates'     │
        │  Payload: {HostName,       │
        │           CrdCommand, Pin} │
        └────────────────────────────┘
                    ↓
              [Client VMs]
           (LISTEN waiting)
```

### Additional Enhancement: CRD Connection Diagram Review

As part of this change, review and potentially enhance the CRD connection diagram to ensure it properly shows the database's role without duplicating the new schema figure.

## Key Technical Approach

1. **New diagram generator method**: `LabLinkDiagramBuilder.build_database_schema_diagram()`
2. **Integration**: Add to `generate_architecture_diagram.py` CLI with `--diagram-type database-schema`
3. **Style consistency**: Use existing `_create_graph_attr()`, `_create_node_attr()`, `_create_edge_attr()` helpers
4. **Preset support**: Implement `fontsize_preset` parameter for paper/poster formats
5. **Output files**:
   - `figures/main/lablink-database-schema.png`
   - `figures/main/lablink-database-schema.pdf`
   - `figures/main/lablink-database-schema.svg`

## Implementation Scope

### In Scope
- ✅ Database schema analysis documentation (completed)
- ✅ Database schema diagram generator method
- ✅ CLI integration for generating schema diagram
- ✅ Support for paper and poster presets
- ✅ Review of CRD connection diagram for potential updates
- ✅ Integration testing with existing diagram generation workflow

### Out of Scope
- ❌ Changes to actual LabLink database implementation
- ❌ Database migration or schema changes
- ❌ Multi-table database designs (LabLink uses single table)
- ❌ Interactive database diagram (static output only)

## Success Criteria

1. **Documentation**: Comprehensive database schema analysis saved in `analysis/database-schema-analysis.md` ✅
2. **Diagram generation**: Command `uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type database-schema --format paper` produces publication-quality figure
3. **Preset support**: Both `--fontsize-preset paper` and `--fontsize-preset poster` produce appropriately sized outputs
4. **Output formats**: PNG, PDF, and SVG versions generated
5. **Visual clarity**: All 19 columns clearly labeled and grouped by function
6. **Trigger flow**: Database trigger mechanism clearly illustrated
7. **Consistency**: Matches visual style of existing architecture diagrams
8. **CRD diagram review**: Existing CRD connection diagram reviewed and updated if needed

## Dependencies

### External Dependencies
- LabLink source code (C:\repos\lablink) - for schema verification ✅
- LabLink template (C:\repos\lablink-template) - for deployment context ✅

### Internal Dependencies
- Existing diagram generation infrastructure (`src/diagram_gen/generator.py`)
- Diagrams library (Python package for architecture diagrams)
- Existing preset system (paper/poster/presentation)

### Blocked By
- None (all required information gathered from source code)

## Alternatives Considered

### Alternative 1: Add schema details to CRD connection diagram
**Rejected**: Would make an already complex diagram (15-step workflow) even more cluttered

### Alternative 2: Add schema details to main architecture diagram
**Rejected**: Main architecture shows system components, not data models. Would confuse architectural and data concerns.

### Alternative 3: Text-only documentation
**Rejected**: Visual diagrams are more effective for understanding database structure and trigger flow, especially for academic papers.

### Alternative 4: Entity-Relationship Diagram (ERD) style
**Considered but modified**: Traditional ERD would be overkill for a single table. Proposed hybrid approach shows table structure + trigger flow + data operations.

## Implementation Strategy

### Phase 1: Diagram Generator (Priority 1)
1. Add `build_database_schema_diagram()` method to `LabLinkDiagramBuilder`
2. Implement table schema visualization with column grouping
3. Add trigger/function/pg_notify flow
4. Support paper and poster presets

### Phase 2: CLI Integration (Priority 1)
1. Add `database-schema` option to `--diagram-type` choices
2. Wire up new method in `generate_architecture_diagram.py`
3. Test with both presets

### Phase 3: CRD Diagram Review (Priority 2)
1. Review existing CRD connection diagram code
2. Check for any database schema details that should be simplified
3. Verify trigger representation is consistent with new schema figure
4. Update if needed

### Phase 4: Validation (Priority 1)
1. Generate diagram in both formats
2. Verify all 19 columns are visible and correctly grouped
3. Validate trigger flow clarity
4. Check visual consistency with other diagrams
5. Run OpenSpec validation

## Open Questions

None - all schema details verified from source code.

## Related Work

- **Existing Analysis**: [database-schema-analysis.md](../../../analysis/database-schema-analysis.md) - Complete schema documentation
- **Related Diagrams**:
  - `lablink-crd-connection` - Shows database trigger in workflow context
  - `lablink-architecture` - Shows PostgreSQL as system component
  - `lablink-logging-pipeline` - Shows database for log storage
- **Source Code**:
  - `C:\repos\lablink\packages\allocator\src\lablink_allocator_service\generate_init_sql.py` - Schema definition
  - `C:\repos\lablink\packages\allocator\src\lablink_allocator_service\database.py` - Database operations
