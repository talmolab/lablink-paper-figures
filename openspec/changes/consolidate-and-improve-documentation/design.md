# Design: Documentation Consolidation and Organization

## Overview

This design establishes a clear, hierarchical documentation structure that consolidates overlapping content, improves discoverability, and ensures technical accuracy across all documentation.

## Current State Analysis

### Existing Documentation Files

| File | Purpose | Status | Issues |
|------|---------|--------|--------|
| `README.md` | Repository overview | Active | Missing diagram docs, needs update |
| `BUG_ANALYSIS_AND_FIX_PLAN.md` | GPU bug analysis | Dev artifact | Should be archived |
| `analysis/lablink-comprehensive-analysis.md` | Infrastructure overview | Active | Main reference, needs verification |
| `analysis/infrastructure-verification-2025-11-15.md` | Recent verification | Active | Should merge into comprehensive |
| `analysis/api-architecture-analysis.md` | 22 Flask endpoints | Active | Good, keep |
| `analysis/database-schema-analysis.md` | PostgreSQL schema | Active | Good, keep |
| `analysis/crd-workflow-corrected.md` | CRD workflow (current) | Active | Good, keep |
| `analysis/crd-workflow-research.md` | CRD research notes | Outdated? | Check if still relevant |
| `analysis/lablink-architecture-analysis.md` | Architecture overview | Active | Overlaps with comprehensive |
| `analysis/lablink-configuration-analysis.md` | Configuration system | Active | Good, keep |
| `analysis/graphviz-settings-reference.md` | GraphViz reference | Active | Move to development docs |

### Content Overlap Analysis

**Infrastructure Coverage:**
- `lablink-comprehensive-analysis.md` - Broad infrastructure overview
- `infrastructure-verification-2025-11-15.md` - Detailed verification with evidence
- `lablink-architecture-analysis.md` - Architecture patterns

**Resolution:** Merge verification findings into comprehensive analysis, archive verification report, deprecate architecture-analysis if redundant.

**CRD Workflow:**
- `crd-workflow-corrected.md` - Current, accurate workflow
- `crd-workflow-research.md` - Research/discovery notes

**Resolution:** Keep corrected version, check if research notes have value for future reference or archive.

## Proposed Documentation Architecture

### Directory Structure

```
docs/
├── README.md                          # Documentation index with navigation
├── getting-started.md                 # Quick start: setup, first diagram, basic usage
├── architecture/                      # LabLink architecture documentation
│   ├── README.md                      # Architecture overview index
│   ├── infrastructure.md              # AWS infrastructure (EC2, Lambda, IAM, etc.)
│   ├── api-endpoints.md               # 22 Flask API endpoints documentation
│   ├── database-schema.md             # PostgreSQL schema (in-container)
│   ├── workflows.md                   # Key workflows (CRD, VM provisioning, logging)
│   └── configuration.md               # Configuration system and hierarchy
├── diagrams/                          # Diagram documentation
│   ├── README.md                      # Diagram suite overview
│   ├── generating-diagrams.md         # How to generate (CLI, presets, formats)
│   └── diagram-reference.md           # Each of 12 diagrams explained
├── development/                       # Development guides
│   ├── graphviz-reference.md          # GraphViz technical settings
│   ├── contributing.md                # How to contribute
│   └── testing.md                     # Testing strategy
└── archived/                          # Archived development notes
    ├── gpu-reliance-bug-2025-11.md    # BUG_ANALYSIS_AND_FIX_PLAN.md
    └── infrastructure-verification-2025-11-15.md
```

### Content Mapping

#### 1. Main README.md Updates

**Add sections:**
- Overview of 12 generated diagrams with thumbnails
- Quick links to key documentation
- Clearer setup instructions with diagram generation example
- Link to `docs/README.md` for full documentation

**Update sections:**
- Repository structure (mention `docs/` directory)
- Quick start example (generate a diagram)

#### 2. docs/README.md (NEW)

Documentation index with:
- Clear navigation to all doc sections
- Brief description of each major topic
- "Where to start" guide for different user types:
  - New users → getting-started.md
  - Understanding LabLink → architecture/README.md
  - Generating diagrams → diagrams/README.md
  - Contributing → development/contributing.md

#### 3. docs/getting-started.md (NEW)

Quick start guide:
- Prerequisites (Python 3.10+, uv, Terraform)
- Installation steps
- Generate your first diagram
- Understanding the output
- Next steps (links to other docs)

#### 4. docs/architecture/infrastructure.md (CONSOLIDATED)

Merge content from:
- `lablink-comprehensive-analysis.md` (main content)
- `infrastructure-verification-2025-11-15.md` (verification evidence)
- `lablink-architecture-analysis.md` (if unique content exists)

Sections:
1. Overview (high-level architecture)
2. Allocator Tier (persistent infrastructure)
   - EC2 instance, Docker container
   - PostgreSQL (in-container)
   - Flask API
   - Terraform binary
   - Lambda function
   - CloudWatch
   - IAM roles
3. Client VM Tier (runtime-provisioned)
   - EC2 instances
   - Security groups
   - IAM roles
4. Conditional Components (ACM SSL)
   - ALB, target groups, listeners
   - Caddy reverse proxy (non-ACM)
5. What's NOT in infrastructure (RDS, ElastiCache, NAT Gateway, etc.)

#### 5. docs/architecture/workflows.md (CONSOLIDATED)

Merge workflow documentation:
- CRD connection workflow (from `crd-workflow-corrected.md`)
- VM provisioning workflow
- Logging pipeline workflow

#### 6. docs/diagrams/README.md (NEW)

Overview of all 12 diagrams:
- Purpose of diagram suite
- Essential vs supplementary diagrams
- When to use each diagram
- Output formats (PNG, PDF, SVG)
- Font presets (paper, poster, presentation)

#### 7. docs/diagrams/diagram-reference.md (NEW)

Detailed documentation for each diagram:

1. **lablink-architecture.png** - Main architecture overview
2. **lablink-architecture-detailed.png** - Detailed architecture with all components
3. **lablink-api-architecture.pdf** - API architecture with 22 endpoints
4. **lablink-vm-provisioning.pdf** - VM provisioning workflow
5. **lablink-crd-connection.pdf** - CRD connection workflow (15 steps)
6. **lablink-logging-pipeline.pdf** - CloudWatch logging pipeline
7. **lablink-database-schema.png** - PostgreSQL schema
8. **lablink-cicd-workflow.pdf** - CI/CD pipeline
9. **lablink-network-flow.pdf** - Network traffic flow
10. **lablink-network-flow-enhanced.pdf** - Enhanced network flow
11. **lablink-monitoring.pdf** - Monitoring architecture
12. **lablink-data-collection.pdf** - Data collection flow

For each: Purpose, Key components, When to use, Related diagrams

#### 8. docs/diagrams/generating-diagrams.md (NEW)

Practical guide to generating diagrams:
- CLI usage and options
- Font presets (paper 14pt, poster 20pt, presentation 16pt)
- Output formats (PNG, PDF, SVG)
- Generating single diagram vs all diagrams
- Customizing output directory
- Troubleshooting common issues

#### 9. docs/development/graphviz-reference.md (MOVED)

Move `analysis/graphviz-settings-reference.md` to development docs.
This is technical reference for developers, not user-facing documentation.

## Implementation Strategy

### Phase 1: Prepare and Verify (No Changes)

1. Read all 9 analysis files completely
2. Extract unique content from each
3. Identify overlaps and redundancies
4. Verify technical accuracy against:
   - `infrastructure-verification-2025-11-15.md` findings
   - Actual code in lablink repository
   - Generated diagrams in `figures/main/`
5. Create content mapping spreadsheet

### Phase 2: Create New Documentation Structure

1. Create `docs/` directory and subdirectories
2. Write `docs/README.md` (documentation index)
3. Write `docs/getting-started.md` (quick start)
4. Write `docs/diagrams/README.md` (diagram overview)
5. Write `docs/diagrams/generating-diagrams.md` (how-to guide)
6. Write `docs/diagrams/diagram-reference.md` (12 diagrams documented)

### Phase 3: Consolidate Architecture Documentation

1. Create `docs/architecture/infrastructure.md` (merge comprehensive + verification)
2. Create `docs/architecture/api-endpoints.md` (move from analysis)
3. Create `docs/architecture/database-schema.md` (move from analysis)
4. Create `docs/architecture/workflows.md` (merge CRD + VM provisioning + logging)
5. Create `docs/architecture/configuration.md` (move from analysis)

### Phase 4: Update Root Documentation

1. Update `README.md`:
   - Add diagram showcase section
   - Update repository structure
   - Add quick start with diagram example
   - Link to `docs/README.md`
2. Move `BUG_ANALYSIS_AND_FIX_PLAN.md` to `docs/archived/gpu-reliance-bug-2025-11.md`

### Phase 5: Clean Up and Verify

1. Archive `infrastructure-verification-2025-11-15.md` to `docs/archived/`
2. Evaluate whether to keep `crd-workflow-research.md` or archive
3. Verify all cross-references work
4. Check for broken links
5. Ensure no information was lost

## Content Consolidation Details

### Infrastructure Documentation

**Source files:**
- `analysis/lablink-comprehensive-analysis.md` (primary)
- `analysis/infrastructure-verification-2025-11-15.md` (verification evidence)
- `analysis/lablink-architecture-analysis.md` (check for unique content)

**Target:** `docs/architecture/infrastructure.md`

**Key content to include:**
- PostgreSQL runs INSIDE allocator Docker container (NOT AWS RDS)
- Evidence: Dockerfile line 13, no aws_db_instance in Terraform
- All infrastructure components verified with Terraform resource names
- Conditional components (ALB for ACM SSL only)
- Components NOT in infrastructure (RDS, ElastiCache, NAT Gateway)

### Workflow Documentation

**Source files:**
- `analysis/crd-workflow-corrected.md` (CRD workflow)
- Embedded in comprehensive analysis (VM provisioning, logging)

**Target:** `docs/architecture/workflows.md`

**Workflows to document:**
1. **CRD Connection** (15-step workflow)
   - PostgreSQL LISTEN/NOTIFY
   - Long-polling HTTP connection
   - Database triggers and channels
2. **VM Provisioning**
   - Terraform execution from allocator container
   - 3-phase startup sequence
   - Status updates and callbacks
3. **Logging Pipeline**
   - CloudWatch Agent → CloudWatch Logs → Lambda → Allocator API → PostgreSQL

## Technical Accuracy Checklist

Critical facts to verify in all documentation:

- [ ] PostgreSQL runs in Docker container, NOT AWS RDS
- [ ] 22 Flask API endpoints (not 18, not 20)
- [ ] Client VMs run Python scripts (subscribe.py, check_gpu.py, connect_crd.py)
- [ ] Client VMs do NOT run Flask (Flask only on allocator)
- [ ] CRD workflow uses LISTEN/NOTIFY (not polling)
- [ ] 12 diagrams total (not 11, not 13)
- [ ] ALB is conditional (ACM SSL provider only)
- [ ] Terraform runs INSIDE allocator container
- [ ] Database edges use `constraint="false"` for rendering
- [ ] Font presets: paper (14pt), poster (20pt), presentation (16pt)

## Migration Strategy

**Keep original files until new structure is verified:**
- Don't delete files from `analysis/` until new `docs/` structure is complete
- Use git to track changes
- Commit new `docs/` structure first
- Then archive/remove old files in separate commit
- This allows easy rollback if needed

**Validation before cleanup:**
1. All content from old files accounted for in new structure
2. Technical accuracy verified
3. Cross-references working
4. No broken links
5. User review of new documentation structure

## Success Metrics

1. **Discoverability**: New user can find diagram generation guide in < 2 clicks from README
2. **Completeness**: All 12 diagrams documented with purpose and usage
3. **Accuracy**: Zero incorrect statements about infrastructure (PostgreSQL, Flask, etc.)
4. **Organization**: No duplicate content across files
5. **Navigation**: Clear hierarchy with documentation index
