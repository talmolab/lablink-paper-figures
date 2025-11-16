# Tasks: Add Database Schema Figure

## Phase 1: Foundation (Completed)

- [x] Explore LabLink database schema in C:\repos\lablink
- [x] Document complete table schema with all 19 columns
- [x] Document database triggers and LISTEN/NOTIFY pattern
- [x] Document database operations and integration points
- [x] Create comprehensive analysis in `analysis/database-schema-analysis.md`
- [x] Create OpenSpec proposal structure

## Phase 2: Diagram Generator Implementation

- [ ] Add `build_database_schema_diagram()` method to `LabLinkDiagramBuilder` class in `src/diagram_gen/generator.py`
  - [ ] Create table schema visualization using cluster for table structure
  - [ ] Group columns by function (Assignment, Monitoring, Performance, Metadata)
  - [ ] Use color coding: Blue (assignment), Yellow (monitoring), Green (performance), Purple (triggers)
  - [ ] Add trigger flow: Table → Trigger → Function → pg_notify → Client VMs
  - [ ] Implement `fontsize_preset` parameter support ("paper" and "poster")
  - [ ] Use existing helper methods: `_create_graph_attr()`, `_create_node_attr()`, `_create_edge_attr()`
  - [ ] Set appropriate graph direction (TB for top-to-bottom flow)
  - [ ] Add docstring with code references and description

- [ ] Verify column count accuracy (19 columns total)
  - [ ] Cross-reference with `generate_init_sql.py` lines 29-49
  - [ ] Validate column names match schema exactly
  - [ ] Ensure all column groups are represented

## Phase 3: CLI Integration

- [ ] Update `scripts/plotting/generate_architecture_diagram.py`
  - [ ] Add "database-schema" to `--diagram-type` choices
  - [ ] Add elif branch for database-schema diagram type
  - [ ] Call `builder.build_database_schema_diagram()` with appropriate parameters
  - [ ] Set output path to `lablink-database-schema`
  - [ ] Support all format options (png, svg, pdf)
  - [ ] Add to "all-essential" diagram group (optional, discuss placement)

- [ ] Update help text and examples in CLI docstring

## Phase 4: CRD Connection Diagram Review

- [ ] Review existing `build_crd_connection_diagram()` method in `src/diagram_gen/generator.py`
  - [ ] Check lines 652-769 for database representation
  - [ ] Verify trigger visualization matches new schema diagram
  - [ ] Identify any schema details that should be simplified
  - [ ] Assess if database node should link to schema diagram in paper text

- [ ] Make updates if needed
  - [ ] Simplify database representation if it conflicts with new schema figure
  - [ ] Ensure consistency in trigger/function naming
  - [ ] Update edge labels if needed for clarity
  - [ ] Maintain focus on workflow (not schema details)

## Phase 5: Testing & Validation

- [ ] Generate database schema diagram in paper format
  - [ ] Run: `uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type database-schema --format paper --fontsize-preset paper`
  - [ ] Verify output in `figures/main/lablink-database-schema.png`
  - [ ] Check all 19 columns are visible
  - [ ] Verify column grouping is clear
  - [ ] Validate trigger flow is understandable

- [ ] Generate database schema diagram in poster format
  - [ ] Run: `uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type database-schema --format poster --fontsize-preset poster`
  - [ ] Verify larger fonts (20pt)
  - [ ] Check spacing is adequate
  - [ ] Ensure no text overlap

- [ ] Generate all output formats
  - [ ] Run with `--format all` to get PNG, SVG, PDF
  - [ ] Verify all three formats are created
  - [ ] Check PDF is vector format
  - [ ] Validate SVG opens correctly

- [ ] Visual quality checks
  - [ ] Compare style consistency with other architecture diagrams
  - [ ] Verify color coding is colorblind-friendly
  - [ ] Check font sizes match preset specifications
  - [ ] Ensure DPI is 300 for publication quality

## Phase 6: Integration Testing

- [ ] Test diagram generation in full workflow
  - [ ] Run: `uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type all-essential`
  - [ ] Verify database-schema is included (if added to group)
  - [ ] Check no conflicts with other diagrams

- [ ] Run OpenSpec validation
  - [ ] Execute: `openspec validate add-database-schema-figure --strict`
  - [ ] Resolve any validation errors
  - [ ] Ensure all requirements have scenarios
  - [ ] Verify spec structure is correct

## Phase 7: Documentation & Finalization

- [ ] Update `figures/main/FIGURE_SUMMARY.md` to include new database schema figure
  - [ ] Add description of diagram purpose
  - [ ] Document column count and grouping
  - [ ] Note trigger mechanism visualization
  - [ ] Reference database-schema-analysis.md

- [ ] Create metadata file
  - [ ] Generate `lablink-database-schema_metadata.txt`
  - [ ] Include generation timestamp
  - [ ] Document fontsize preset used
  - [ ] Reference source schema file (generate_init_sql.py)

- [ ] Update README or project docs
  - [ ] Add database schema figure to available figures list
  - [ ] Document generation command
  - [ ] Link to schema analysis documentation

## Dependencies

- **Blocked by**: None
- **Blocks**: None (independent feature)
- **Related**: fix-diagram-quality-issues (shares diagram generation infrastructure)

## Validation Criteria

Each task must meet these criteria before marking complete:
- [ ] Code follows project conventions (Ruff formatted, type hints where appropriate)
- [ ] Generated diagrams are publication quality (300 DPI, clear labels)
- [ ] Both paper and poster presets work correctly
- [ ] No regressions in existing diagram generation
- [ ] OpenSpec validation passes with --strict flag
- [ ] Visual consistency with existing architecture diagrams
- [ ] All 19 database columns accurately represented
- [ ] Trigger flow is clear and matches database-schema-analysis.md

## Estimated Effort

- **Total**: ~4-6 hours
  - Phase 2 (Diagram Generator): 2-3 hours
  - Phase 3 (CLI Integration): 30 minutes
  - Phase 4 (CRD Review): 1 hour
  - Phase 5 (Testing): 1 hour
  - Phase 6 (Integration): 30 minutes
  - Phase 7 (Documentation): 30 minutes