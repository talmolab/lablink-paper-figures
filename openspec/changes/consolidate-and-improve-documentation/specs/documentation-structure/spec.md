# Capability: Documentation Structure and Organization

## Overview

Establish a clear, hierarchical documentation structure that consolidates overlapping content, eliminates duplication, and provides easy navigation for users and contributors.

## ADDED Requirements

### Requirement: Create centralized documentation directory

The system SHALL provide a centralized `docs/` directory with clear hierarchical organization for all user-facing documentation.

**Rationale**: Currently documentation is scattered across root and analysis/ with no clear structure or index.

#### Scenario: Create docs directory structure

**Given** the repository has documentation scattered across multiple locations
**When** the documentation consolidation is implemented
**Then** a `docs/` directory must exist at repository root
**And** it must contain subdirectories: `architecture/`, `diagrams/`, `development/`, `archived/`
**And** each subdirectory must have a `README.md` index file
**And** the directory structure must match the design document layout

---

### Requirement: Provide documentation index with clear navigation

The system SHALL provide a documentation index (`docs/README.md`) that serves as the main entry point for all documentation.

**Rationale**: Users need a clear starting point to navigate documentation.

#### Scenario: Create documentation index

**Given** the `docs/` directory exists
**When** a user opens `docs/README.md`
**Then** it must contain a clear navigation structure with links to all major documentation sections
**And** it must include a "Where to start" guide for different user types:
  - New users → `getting-started.md`
  - Understanding LabLink → `architecture/README.md`
  - Generating diagrams → `diagrams/README.md`
  - Contributing → `development/contributing.md`
**And** each section must have a brief description of its purpose

---

### Requirement: Update main README with diagram showcase

The system SHALL update the main `README.md` to include a diagram showcase section and link to consolidated documentation.

**Rationale**: README is the first thing users see; it should showcase the 12 diagrams and guide to detailed docs.

#### Scenario: Add diagram showcase to README

**Given** the main `README.md` exists
**When** the documentation update is complete
**Then** README must include a "Diagrams" section after "Repository Structure"
**And** the section must list all 12 diagram types with brief descriptions
**And** the section must link to `docs/diagrams/README.md` for details
**And** the section must include generation example: `uv run python scripts/plotting/generate_architecture_diagram.py --diagram-type all --fontsize-preset poster`

#### Scenario: Update repository structure in README

**Given** the main `README.md` contains a "Repository Structure" section
**When** the documentation update is complete
**Then** the structure must include the new `docs/` directory
**And** the structure must describe `docs/` as "Consolidated documentation (architecture, diagrams, development)"
**And** the structure must link to `docs/README.md`

---

### Requirement: Consolidate overlapping infrastructure documentation

The system SHALL consolidate overlapping infrastructure documentation into single authoritative files with no duplicate content.

**Rationale**: Multiple files cover similar topics (lablink-comprehensive-analysis.md, infrastructure-verification-2025-11-15.md, lablink-architecture-analysis.md) creating confusion.

#### Scenario: Merge infrastructure documentation

**Given** multiple files document LabLink infrastructure
**When** consolidation is performed
**Then** a single `docs/architecture/infrastructure.md` file must exist
**And** it must incorporate unique content from:
  - `analysis/lablink-comprehensive-analysis.md` (primary content)
  - `analysis/infrastructure-verification-2025-11-15.md` (verification evidence)
  - `analysis/lablink-architecture-analysis.md` (any unique content)
**And** it must have sections: Overview, Allocator Tier, Client VM Tier, Conditional Components, What's NOT in Infrastructure
**And** no duplicate content may exist across these source files and the new consolidated file

---

### Requirement: Archive development artifacts appropriately

The system SHALL move development artifacts and time-specific analysis documents to an archived/ directory.

**Rationale**: Files like BUG_ANALYSIS_AND_FIX_PLAN.md and dated verification reports are valuable for history but clutter current documentation.

#### Scenario: Archive bug analysis document

**Given** `BUG_ANALYSIS_AND_FIX_PLAN.md` exists at repository root
**When** the archiving is performed
**Then** the file must be moved to `docs/archived/gpu-reliance-bug-2025-11.md`
**And** the root directory must not contain `BUG_ANALYSIS_AND_FIX_PLAN.md`
**And** the archived file must be referenced in `docs/development/` if relevant to ongoing work

#### Scenario: Archive timestamped verification report

**Given** `analysis/infrastructure-verification-2025-11-15.md` exists
**When** its content has been merged into `docs/architecture/infrastructure.md`
**Then** the original file must be moved to `docs/archived/infrastructure-verification-2025-11-15.md`
**And** the `docs/architecture/infrastructure.md` must credit the verification report as a source

---

### Requirement: Eliminate duplicate workflow documentation

The system SHALL consolidate workflow documentation into a single workflows.md file.

**Rationale**: CRD workflow, VM provisioning, and logging pipeline are documented separately but belong together as key LabLink workflows.

#### Scenario: Consolidate workflow documentation

**Given** workflow documentation exists in multiple files
**When** consolidation is performed
**Then** a single `docs/architecture/workflows.md` file must exist
**And** it must include three major workflows:
  - CRD Connection (from `crd-workflow-corrected.md`)
  - VM Provisioning (from comprehensive analysis)
  - Logging Pipeline (from comprehensive analysis)
**And** each workflow must have clear sections: Overview, Components, Step-by-step flow, Technical details
**And** the CRD workflow must document LISTEN/NOTIFY mechanism and 15-step sequence

---

## MODIFIED Requirements

None. This change adds new documentation organization without modifying existing capabilities.

---

## REMOVED Requirements

None. This change preserves all existing information in better-organized form.

---

## Dependencies

- Existing documentation files in `analysis/` directory
- `BUG_ANALYSIS_AND_FIX_PLAN.md` at repository root
- Main `README.md`
- Generated diagrams in `figures/main/`

---

## Testing Notes

### Validation Steps

**Documentation completeness:**
1. Check that all content from source files appears in consolidated files
2. Verify no information was lost during consolidation
3. Confirm all technical details preserved

**Structure validation:**
```bash
# Verify directory structure
ls -la docs/
ls -la docs/architecture/
ls -la docs/diagrams/
ls -la docs/development/
ls -la docs/archived/

# Check all README files exist
test -f docs/README.md && echo "✓ docs/README.md"
test -f docs/architecture/README.md && echo "✓ architecture/README.md"
test -f docs/diagrams/README.md && echo "✓ diagrams/README.md"
```

**Link validation:**
```bash
# Check for broken markdown links (if using markdown-link-check)
npx markdown-link-check docs/**/*.md
```

**Content verification:**
- [ ] All 12 diagrams documented in `docs/diagrams/diagram-reference.md`
- [ ] PostgreSQL in-container architecture in `docs/architecture/infrastructure.md`
- [ ] 22 Flask endpoints in `docs/architecture/api-endpoints.md`
- [ ] All 3 workflows in `docs/architecture/workflows.md`
- [ ] GraphViz reference in `docs/development/graphviz-reference.md`

---

## Success Metrics

**Quantitative:**
- 0 duplicate content blocks across documentation files
- 1 authoritative file per topic (infrastructure, workflows, etc.)
- 100% of existing content preserved in new structure
- 12/12 diagrams documented

**Qualitative:**
- User can find any documentation topic in ≤ 2 clicks from README
- Clear hierarchy with no ambiguity about where information belongs
- Professional documentation structure suitable for academic publication
