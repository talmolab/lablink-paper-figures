# Tasks: Consolidate and Improve Documentation

## Overview

Systematic review and consolidation of all documentation to ensure accuracy, completeness, and clear organization for the lablink-paper-figures repository. Includes documentation for ALL figure types: architecture diagrams (12), software complexity, SLEAP dependencies, GPU costs, deployment impact, OS distribution, GPU reliance, configuration hierarchy, and QR codes.

---

## Phase 1: Audit and Verification (No Changes)

### Task 1.1: Audit all existing documentation

**Estimated effort**: 2-3 hours

**Actions:**
- [ ] Read all 9 files in `analysis/` directory completely
- [ ] Read `README.md`, `BUG_ANALYSIS_AND_FIX_PLAN.md`
- [ ] Identify all figure types currently generated:
  - 12 architecture diagrams (from Terraform)
  - Software complexity over time
  - SLEAP dependency graph
  - GPU cost trends
  - Deployment impact timeline
  - OS distribution
  - GPU reliance
  - Configuration hierarchy
  - QR codes
- [ ] Check README.md coverage for each figure type
- [ ] Create content inventory spreadsheet with columns:
  - File name
  - Primary topic
  - Figures documented
  - Unique content
  - Overlapping content
  - Technical claims (need verification)
  - Last updated
  - Status (current/outdated/unclear)

**Validation:**
- Inventory covers all 11 documentation files
- All 9+ figure types identified
- Each file has primary topic identified
- Overlaps clearly marked

---

### Task 1.2: Verify technical accuracy against source repositories

**Estimated effort**: 2-3 hours

**Actions:**
- [ ] Clone/update lablink and lablink-template repositories
- [ ] Verify PostgreSQL deployment:
  ```bash
  grep -n "postgresql" c:/repos/lablink/packages/allocator/Dockerfile
  grep -r "aws_db_instance" c:/repos/lablink-template/lablink-infrastructure/
  ```
- [ ] Verify Flask API endpoints (count and categorization):
  ```bash
  grep -E "@app\.(route|get|post)" c:/repos/lablink/packages/allocator/src/lablink_allocator_service/app.py | wc -l
  ```
- [ ] Verify client VM software (no Flask):
  ```bash
  grep -i "flask" c:/repos/lablink/packages/client/pyproject.toml
  ```
- [ ] Verify Terraform resources in lablink-infrastructure
- [ ] Verify GitHub Actions workflows for OIDC usage (if workflows exist in lablink repos)
- [ ] Document verification results with file paths and line numbers

**Validation:**
- PostgreSQL confirmed as in-container (Dockerfile line 13)
- No aws_db_instance found in Terraform
- Flask endpoint count = 22
- Client pyproject.toml has no Flask dependency
- CI/CD workflow details verified from actual workflows

---

### Task 1.3: Identify documentation gaps

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Check if all 12 architecture diagrams are documented with purpose
- [ ] Check if ALL other figures are documented:
  - Software complexity (plot_software_complexity.py)
  - SLEAP dependency graph (generate_sleap_dependency_graph.py)
  - GPU cost trends (plot_gpu_cost_trends.py)
  - Deployment impact (plot_deployment_impact.py)
  - OS distribution (plot_os_distribution.py)
  - GPU reliance (plot_gpu_reliance.py)
  - Configuration hierarchy (plot_configuration_hierarchy.py)
  - QR codes (generate_qr_codes.py)
- [ ] Check if diagram generation workflow is documented
- [ ] Check if font presets are explained
- [ ] Check if output directory best practices are documented
- [ ] Check if each data/ subdirectory has README
- [ ] Create list of missing documentation topics with priorities

**Validation:**
- Gap list created for all figure types
- Each gap has clear scope and priority

---

### Task 1.4: Audit folder structure for README coverage

**Estimated effort**: 30 minutes

**Actions:**
- [ ] List all directories that should have READMEs:
  ```bash
  find . -type d -not -path "*/\.*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*"
  ```
- [ ] Check which folders have READMEs:
  ```bash
  find . -name "README.md" -o -name "readme.md"
  ```
- [ ] Identify folders missing READMEs:
  - data/ subdirectories
  - src/ subdirectories
  - scripts/ subdirectories
  - notebooks/
  - tests/
- [ ] Create checklist of READMEs to add

**Validation:**
- Complete inventory of directories
- Clear list of missing READMEs

---

## Phase 2: Create New Documentation Structure

### Task 2.1: Create docs/ directory structure

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Create directory structure:
  ```bash
  mkdir -p docs/{architecture,figures,development,archived}
  mkdir -p docs/figures/{architecture-diagrams,analysis-figures}
  ```
- [ ] Create placeholder README.md files:
  - docs/README.md
  - docs/architecture/README.md
  - docs/figures/README.md
  - docs/figures/architecture-diagrams/README.md
  - docs/figures/analysis-figures/README.md
  - docs/development/README.md
  - docs/archived/README.md

**Validation:**
```bash
test -f docs/README.md && echo "✓ docs/README.md"
test -f docs/architecture/README.md && echo "✓ architecture/README.md"
test -f docs/figures/README.md && echo "✓ figures/README.md"
test -f docs/figures/architecture-diagrams/README.md && echo "✓ architecture-diagrams/README.md"
test -f docs/figures/analysis-figures/README.md && echo "✓ analysis-figures/README.md"
test -f docs/development/README.md && echo "✓ development/README.md"
```

---

### Task 2.2: Create documentation index (docs/README.md)

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Write clear introduction explaining this repo's purpose: "Generate publication-quality figures for LabLink paper by analyzing LabLink system"
- [ ] Add "Where to start" section for different user types:
  - New users → getting-started.md
  - Generate architecture diagrams → figures/architecture-diagrams/README.md
  - Generate analysis figures → figures/analysis-figures/README.md
  - Understand LabLink system → architecture/README.md
  - Contributing → development/contributing.md
- [ ] Add navigation tree showing ALL documentation:
  ```
  docs/
  ├── getting-started.md
  ├── architecture/ (LabLink system analysis)
  │   ├── infrastructure.md
  │   ├── api-endpoints.md
  │   ├── database-schema.md
  │   ├── workflows.md
  │   └── configuration.md
  ├── figures/ (All figure generation)
  │   ├── architecture-diagrams/ (12 diagrams from Terraform)
  │   └── analysis-figures/ (9+ analysis figures)
  └── development/
      ├── graphviz-reference.md
      └── contributing.md
  ```
- [ ] Link to main README.md
- [ ] Add "Quick Links" section for common tasks

**Validation:**
- All sections linked with descriptions
- Clear guidance for different user types
- Navigation tree shows complete structure

---

### Task 2.3: Create getting started guide (docs/getting-started.md)

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Write prerequisites:
  - Python 3.10+
  - uv package manager
  - graphviz system package
  - Access to lablink/lablink-template repos (for architecture diagrams)
- [ ] Write installation steps:
  ```bash
  git clone <repo>
  cd lablink-paper-figures
  uv sync --all-extras
  ```
- [ ] Write "Generate your first figure" tutorials:
  - Architecture diagram:
    ```bash
    uv run python scripts/plotting/generate_architecture_diagram.py \
      --terraform-dir ../lablink-template/lablink-infrastructure \
      --diagram-type main --fontsize-preset paper
    ```
  - Analysis figure:
    ```bash
    uv run python scripts/plotting/plot_gpu_cost_trends.py --preset paper
    ```
- [ ] Explain output locations and formats
- [ ] Add troubleshooting section
- [ ] Add "Next steps" linking to detailed figure documentation

**Validation:**
- Prerequisites complete and accurate
- Installation steps tested
- Example commands work
- Clear progression to next steps

---

## Phase 3: Architecture Diagram Documentation

### Task 3.1: Create architecture diagrams overview (docs/figures/architecture-diagrams/README.md)

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Write overview explaining these diagrams visualize LabLink infrastructure from Terraform
- [ ] List all 12 diagram types:
  1. lablink-architecture (main)
  2. lablink-architecture-detailed
  3. lablink-api-architecture
  4. lablink-vm-provisioning
  5. lablink-crd-connection
  6. lablink-logging-pipeline
  7. lablink-database-schema
  8. lablink-cicd-workflow
  9. lablink-network-flow
  10. lablink-network-flow-enhanced
  11. lablink-monitoring
  12. lablink-data-collection
- [ ] Explain essential vs supplementary categorization
- [ ] Document font preset system (paper 14pt, poster 20pt, presentation 16pt)
- [ ] Document output formats (PNG, SVG, PDF)
- [ ] Link to detailed reference and generation guide

**Validation:**
- All 12 diagrams listed
- Purpose of suite clear
- Links to detailed docs

---

### Task 3.2: Create architecture diagram reference (docs/figures/architecture-diagrams/diagram-reference.md)

**Estimated effort**: 2-3 hours

**Actions:**
- [ ] Document each of 12 diagrams with template:
  ```markdown
  ## [Diagram Name]
  **File**: lablink-[name].{png,pdf,svg}
  **Source**: Analyzes Terraform in lablink-template/lablink-infrastructure
  **Purpose**: [What it shows]
  **Key Components**: [Main elements]
  **When to use**: [Use cases - main paper vs supplementary]
  **Related diagrams**: [Cross-references]
  **Technical notes**: [Special features, e.g., PostgreSQL in-container, 22 endpoints, OIDC]
  ```
- [ ] Include visual examples or links to figures/main/
- [ ] Add section on recent fixes (database edges, Flask icon, CI/CD icons)
- [ ] Cross-reference analysis documents for technical details

**Validation:**
- All 12 diagrams documented consistently
- Technical accuracy verified
- Helpful guidance for choosing diagrams

---

### Task 3.3: Create architecture diagram generation guide (docs/figures/architecture-diagrams/generating.md)

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Document prerequisites (Terraform directories)
- [ ] Document CLI usage with all options:
  - `--terraform-dir` (required)
  - `--client-vm-terraform-dir` (optional)
  - `--diagram-type` (all, all-essential, all-supplementary, specific)
  - `--fontsize-preset` (paper, poster, presentation)
  - `--format` (png, svg, pdf, all)
  - `--output-dir` (figures/main or figures/supplementary)
  - `--dpi` (default 300)
- [ ] Document environment variables:
  - LABLINK_TERRAFORM_DIR
  - LABLINK_CLIENT_VM_TERRAFORM_DIR
- [ ] Provide examples:
  - Generate all for paper
  - Generate poster versions
  - Generate single diagram
  - Use environment variables
- [ ] Document output directory workflow:
  - ALWAYS use figures/main/ or figures/supplementary/
  - Timestamped folders auto-generated and gitignored
  - DO NOT use custom directories
- [ ] Add troubleshooting section

**Validation:**
- All options documented
- Examples tested
- Output workflow clear

---

## Phase 4: Analysis Figures Documentation

### Task 4.1: Create analysis figures overview (docs/figures/analysis-figures/README.md)

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Write overview explaining these figures support LabLink paper motivation and analysis
- [ ] List all analysis figure types with scripts:
  1. **Software Complexity** (`plot_software_complexity.py`) - Dependency growth 2000-2025
  2. **SLEAP Dependencies** (`generate_sleap_dependency_graph.py`) - Network graph
  3. **GPU Cost Trends** (`plot_gpu_cost_trends.py`) - Professional/consumer GPU pricing
  4. **Deployment Impact** (`plot_deployment_impact.py`) - Workshop timeline
  5. **OS Distribution** (`plot_os_distribution.py`) - Operating system analysis
  6. **GPU Reliance** (`plot_gpu_reliance.py`) - GPU dependency scoring
  7. **Configuration Hierarchy** (`plot_configuration_hierarchy.py`) - Config structure
  8. **QR Codes** (`generate_qr_codes.py`) - Access codes for demos
- [ ] Explain purpose of each figure type for paper
- [ ] Document common patterns:
  - Preset system (paper/poster/presentation)
  - Data sources (PyPI, conda-forge, Epoch AI, GitHub)
  - Output formats and locations
- [ ] Link to individual figure documentation

**Validation:**
- All 8+ figure types listed
- Clear purpose for each
- Common patterns documented

---

### Task 4.2: Create software complexity documentation (docs/figures/analysis-figures/software-complexity.md)

**Estimated effort**: 30-45 minutes

**Actions:**
- [ ] Extract from README.md "Generating Scientific Software Complexity Figure" section
- [ ] Document purpose: "Motivate LabLink by showing growing complexity of scientific software"
- [ ] Document data sources: conda-forge, PyPI, GitHub
- [ ] Document generation workflow:
  1. Collect data: `scripts/analysis/collect_dependency_data.py`
  2. Process: `scripts/analysis/process_dependency_data.py`
  3. Plot: `scripts/plotting/plot_software_complexity.py`
- [ ] Document presets and output
- [ ] Link to data/software_complexity_README.md

**Validation:**
- Complete workflow documented
- Data sources clear
- Examples work

---

### Task 4.3: Create SLEAP dependency documentation (docs/figures/analysis-figures/sleap-dependencies.md)

**Estimated effort**: 30-45 minutes

**Actions:**
- [ ] Extract from README.md "Generating SLEAP Dependency Network Graph" section
- [ ] Document purpose: "Show complexity of computational research software"
- [ ] Document generation:
  ```bash
  uv run python scripts/plotting/generate_sleap_dependency_graph.py \
    --sleap-source C:/repos/sleap \
    --preset paper
  ```
- [ ] Document options (max-depth, exclude-optional, etc.)
- [ ] Document output files

**Validation:**
- Generation process clear
- All options documented

---

### Task 4.4: Create GPU cost trends documentation (docs/figures/analysis-figures/gpu-costs.md)

**Estimated effort**: 30-45 minutes

**Actions:**
- [ ] Extract from README.md "Generating GPU Cost Trends Visualization" section
- [ ] Document purpose: "Demonstrate sustained high cost motivating cloud-based GPU access"
- [ ] Document data source: Epoch AI ML Hardware Database
- [ ] Document data setup (download from epoch.ai)
- [ ] Document generation and presets
- [ ] Link to data/raw/gpu_prices/README.md

**Validation:**
- Data source clear
- Setup instructions complete
- Examples work

---

### Task 4.5: Create deployment impact documentation (docs/figures/analysis-figures/deployment-impact.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Document purpose: "Timeline of LabLink deployments and workshops"
- [ ] Document data source: data/processed/deployment_impact/workshops.csv
- [ ] Document generation:
  ```bash
  uv run python scripts/plotting/plot_deployment_impact.py --preset paper
  ```
- [ ] Document output

**Validation:**
- Purpose clear
- Generation documented

---

### Task 4.6: Create OS distribution documentation (docs/figures/analysis-figures/os-distribution.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Document purpose
- [ ] Document data source
- [ ] Document generation and presets
- [ ] Document output

**Validation:**
- Complete documentation

---

### Task 4.7: Create GPU reliance documentation (docs/figures/analysis-figures/gpu-reliance.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Document purpose: "Score packages by GPU dependency level"
- [ ] Document scoring methodology (0-5 scale)
- [ ] Document generation
- [ ] Note BUG_ANALYSIS_AND_FIX_PLAN.md for historical context (will be archived)

**Validation:**
- Scoring methodology clear
- Generation documented

---

### Task 4.8: Create configuration hierarchy documentation (docs/figures/analysis-figures/configuration-hierarchy.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Document purpose: "Visualize LabLink configuration system"
- [ ] Document generation
- [ ] Document simple vs detailed versions
- [ ] Link to docs/architecture/configuration.md

**Validation:**
- Both versions documented
- Clear purpose

---

### Task 4.9: Create QR code documentation (docs/figures/analysis-figures/qr-codes.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Document purpose: "Generate QR codes for demo access"
- [ ] Document generation process
- [ ] Document output and usage

**Validation:**
- Purpose and usage clear

---

## Phase 5: LabLink Architecture Analysis Documentation

### Task 5.1: Create consolidated infrastructure documentation (docs/architecture/infrastructure.md)

**Estimated effort**: 2-3 hours

**Actions:**
- [ ] Merge content from:
  - analysis/lablink-comprehensive-analysis.md (primary)
  - analysis/infrastructure-verification-2025-11-15.md (evidence)
  - analysis/lablink-architecture-analysis.md (unique content if any)
- [ ] Organize into clear sections:
  1. Overview - LabLink system purpose
  2. Allocator Tier (persistent infrastructure)
     - EC2 instance (Ubuntu 24.04)
     - Docker container (Flask + PostgreSQL + Terraform)
     - PostgreSQL 15 (IN-CONTAINER, NOT RDS) with evidence
     - Flask API (22 endpoints, 5 groups)
     - Terraform binary (v1.4.6, provisions client VMs)
     - Lambda function (log aggregation)
     - CloudWatch Log Group
     - IAM roles (allocator, Lambda)
  3. Client VM Tier (runtime-provisioned)
     - EC2 instances (variable count, GPU/CPU)
     - Security groups
     - IAM roles and instance profiles
     - Software: Python scripts (subscribe.py, check_gpu.py, connect_crd.py) - NO FLASK
  4. Conditional Components (ACM SSL only)
     - ALB, security groups, target groups, listeners
     - Alternative: Caddy reverse proxy (non-ACM SSL)
  5. What's NOT in Infrastructure
     - ❌ AWS RDS (PostgreSQL is in-container)
     - ❌ ElastiCache, NAT Gateway, VPC Peering, S3 for app data
- [ ] Cite evidence with file:line format:
  - PostgreSQL: lablink/packages/allocator/Dockerfile:13
  - Flask endpoints: lablink/packages/allocator/src/lablink_allocator_service/app.py
  - Terraform resources: lablink-infrastructure/main.tf
- [ ] Add note: "Analysis of LabLink system from lablink/lablink-template repositories"
- [ ] Credit source files

**Validation:**
- PostgreSQL in-container with evidence
- 22 Flask endpoints documented
- Client VMs documented as Python-only
- All Terraform resources cited
- No duplicate content

---

### Task 5.2: Move API endpoint documentation (docs/architecture/api-endpoints.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Copy analysis/api-architecture-analysis.md → docs/architecture/api-endpoints.md
- [ ] Verify 22 endpoints across 5 functional groups:
  - User Interface: 2
  - Query API: 4
  - Admin Management: 10
  - VM Callbacks: 5
  - Lambda Callback: 1
- [ ] Add header: "Authoritative documentation of LabLink Flask API endpoints"
- [ ] Update cross-references

**Validation:**
- 22 endpoints preserved
- Grouping correct (2+4+10+5+1=22)

---

### Task 5.3: Move database schema documentation (docs/architecture/database-schema.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Copy analysis/database-schema-analysis.md → docs/architecture/database-schema.md
- [ ] Add note: "PostgreSQL 15 runs inside allocator Docker container"
- [ ] Update cross-references

**Validation:**
- Schema documentation complete
- In-container architecture noted

---

### Task 5.4: Create workflows documentation (docs/architecture/workflows.md)

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Extract and consolidate 4 key workflows:
  1. **CRD Connection Workflow** (from crd-workflow-corrected.md)
     - 15-step sequence
     - PostgreSQL LISTEN/NOTIFY mechanism
     - Long-polling HTTP connection
  2. **VM Provisioning Workflow** (from comprehensive analysis)
     - Terraform execution from allocator
     - 3-phase startup sequence
     - Status updates and callbacks
  3. **Logging Pipeline** (from comprehensive analysis)
     - CloudWatch Agent → Logs → Lambda → Allocator API → PostgreSQL
  4. **CI/CD Workflow** (from analysis, verify against actual workflows)
     - GitHub Actions pipelines
     - PyPI OIDC trusted publishing (if applicable to LabLink)
     - AWS OIDC for Terraform deploy/destroy
     - Required secrets and permissions
- [ ] Use consistent structure for each workflow
- [ ] Link to related diagrams

**Validation:**
- All 4 workflows documented
- OIDC mechanisms explained with evidence
- Clear step-by-step flows

---

### Task 5.5: Move configuration documentation (docs/architecture/configuration.md)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Copy analysis/lablink-configuration-analysis.md → docs/architecture/configuration.md
- [ ] Update cross-references
- [ ] Link to configuration hierarchy figures

**Validation:**
- Configuration docs preserved
- Links work

---

## Phase 6: Development Documentation and Folder READMEs

### Task 6.1: Move GraphViz reference (docs/development/graphviz-reference.md)

**Estimated effort**: 15 minutes

**Actions:**
- [ ] Move analysis/graphviz-settings-reference.md → docs/development/graphviz-reference.md
- [ ] Add header: "Technical reference for diagram developers"
- [ ] Update cross-references

**Validation:**
- GraphViz docs in development/
- All content preserved

---

### Task 6.2: Create contributing guide (docs/development/contributing.md)

**Estimated effort**: 1 hour

**Actions:**
- [ ] Write contribution guidelines:
  - Code style (Ruff, 88 char lines)
  - Testing with pytest
  - Documentation updates required
  - OpenSpec for change proposals
  - Pull request process
- [ ] Document figure generation workflow for contributors
- [ ] Link to development tools

**Validation:**
- Clear process
- Tools documented

---

### Task 6.3: Add READMEs to data/ subdirectories

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Create/update data/README.md (overview of data organization)
- [ ] Verify/create data/raw/README.md (original immutable data, gitignored except READMEs)
- [ ] Verify/create data/processed/README.md (cleaned data ready for plotting)
- [ ] Ensure data/raw/gpu_prices/README.md exists (documented in main README)
- [ ] Check for data/software_complexity_README.md (referenced in main README)
- [ ] Create READMEs for any other data/ subdirectories:
  - data/processed/deployment_impact/
  - data/processed/sleap_dependencies/
  - etc.
- [ ] Each README should explain:
  - What data is in this folder
  - Source of data
  - How to regenerate/update (if applicable)
  - Which scripts use this data

**Validation:**
- All data/ subdirectories have READMEs
- Clear data provenance
- Usage documented

---

### Task 6.4: Add READMEs to src/ subdirectories

**Estimated effort**: 1 hour

**Actions:**
- [ ] Create src/README.md (overview of reusable modules)
- [ ] Create src/diagram_gen/README.md:
  - Purpose: Infrastructure diagram generation logic
  - Main class: LabLinkDiagramBuilder
  - Font preset system
  - Helper methods
- [ ] Create src/terraform_parser/README.md:
  - Purpose: Parse Terraform HCL
  - Usage in diagram generation
- [ ] Create src/dependency_graph/README.md:
  - Purpose: Network analysis for SLEAP dependencies
  - Key functions
- [ ] Create src/gpu_costs/README.md (if exists):
  - Purpose: GPU pricing data processing
- [ ] Each README explains module purpose and key exports

**Validation:**
- All src/ subdirectories documented
- Clear module purposes

---

### Task 6.5: Add READMEs to scripts/ subdirectories

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Create scripts/README.md (overview of scripts organization)
- [ ] Create scripts/analysis/README.md:
  - Purpose: Data collection and processing
  - List scripts with brief description
- [ ] Create scripts/plotting/README.md:
  - Purpose: Figure generation
  - List all 10 plotting scripts with brief description
  - Link to docs/figures/ for detailed usage

**Validation:**
- Scripts organization clear
- All scripts listed

---

### Task 6.6: Add READMEs to other directories

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Create/update notebooks/README.md (if notebooks/ exists):
  - Purpose: Exploratory analysis
  - Note: Prototype here, refactor to scripts/
- [ ] Create/update tests/README.md:
  - Purpose: Unit tests for src/ modules
  - How to run tests: `uv run pytest`
  - Coverage: `uv run pytest --cov=src`
- [ ] Create figures/README.md:
  - Explain main/ (committed) vs supplementary/ (committed) vs run_*/ (gitignored)
  - Link to docs/figures/

**Validation:**
- All major directories have READMEs
- Purpose of each directory clear

---

## Phase 7: Archive and Update

### Task 7.1: Archive development artifacts

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Create docs/archived/README.md explaining archive purpose
- [ ] Move BUG_ANALYSIS_AND_FIX_PLAN.md → docs/archived/gpu-reliance-bug-2025-11.md
- [ ] Move analysis/infrastructure-verification-2025-11-15.md → docs/archived/
- [ ] Evaluate analysis/crd-workflow-research.md:
  - If valuable for history: move to docs/archived/
  - If superseded: can be removed
- [ ] Add note in archive README: "Historical development notes, superseded by consolidated docs/"

**Validation:**
- Root clean of dev artifacts
- Archive organized and explained

---

### Task 7.2: Update main README.md

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Add "Generated Figures" section after "Repository Structure"
- [ ] Organize by category:
  - **Architecture Diagrams (12)**: List with brief descriptions, link to docs/figures/architecture-diagrams/
  - **Analysis Figures (8+)**: List with brief descriptions, link to docs/figures/analysis-figures/
- [ ] Add generation examples for both types
- [ ] Update repository structure to include docs/ directory:
  ```
  ├── docs/              # Consolidated documentation
  │   ├── architecture/  # LabLink system analysis
  │   ├── figures/       # All figure generation guides
  │   └── development/   # Developer guides
  ```
- [ ] Add "Documentation" section linking to docs/README.md
- [ ] Verify technical accuracy (PostgreSQL in-container, 22 endpoints, etc.)
- [ ] Ensure all figure types mentioned

**Validation:**
- All figure types showcased
- Links work
- Professional presentation
- Technical accuracy verified

---

## Phase 8: Verification and Validation

### Task 8.1: Verify no information loss

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Compare content inventory (Task 1.1) with new docs/ structure
- [ ] Ensure all unique content preserved
- [ ] Check all cross-references work
- [ ] Verify no broken links:
  ```bash
  # If using markdown-link-check
  npx markdown-link-check docs/**/*.md README.md
  ```
- [ ] Check all figure types documented

**Validation:**
- 100% unique content preserved
- 0 broken links
- All 12 architecture diagrams documented
- All 8+ analysis figures documented

---

### Task 8.2: Verify all folders have findable READMEs

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Generate folder tree with READMEs:
  ```bash
  find . -name "README.md" -o -name "readme.md" | sort
  ```
- [ ] Verify coverage:
  - Root: README.md ✓
  - docs/ and all subdirectories
  - data/ and all subdirectories
  - src/ and all subdirectories
  - scripts/ and all subdirectories
  - figures/
  - tests/
  - notebooks/ (if exists)
- [ ] Check README.md mentions docs/README.md prominently

**Validation:**
- Every directory has README
- READMEs form navigable hierarchy
- Users can explore repo structure via READMEs

---

### Task 8.3: Validate with fresh eyes

**Estimated effort**: 1-2 hours

**Actions:**
- [ ] Follow docs/getting-started.md as if new user
- [ ] Generate an architecture diagram following guide
- [ ] Generate an analysis figure following guide
- [ ] Navigate documentation hierarchy:
  - Start at README.md
  - Follow to docs/README.md
  - Explore architecture/, figures/, development/
  - Check that all paths work
- [ ] Verify technical accuracy of key claims:
  - PostgreSQL in-container (not RDS) with evidence
  - 22 Flask endpoints across 5 groups
  - Client VMs run Python (not Flask)
  - CI/CD OIDC (if documented for LabLink)
  - All 12 architecture diagrams listed
  - All 8+ analysis figures listed
- [ ] Read through all new docs for clarity and completeness

**Validation:**
- Getting started works for new user
- All figure types can be generated
- Navigation hierarchy clear
- Technical accuracy 100%
- Professional documentation quality

---

### Task 8.4: Clean up analysis/ directory (optional)

**Estimated effort**: 30 minutes

**Actions:**
- [ ] Evaluate each remaining file in analysis/:
  - Keep if active research/work-in-progress
  - Consider removing if fully duplicated in docs/
- [ ] Add analysis/README.md if keeping files:
  - Explain: "Work-in-progress analysis and research notes"
  - Note: "Consolidated documentation in docs/ directory"
- [ ] Ensure no confusion between analysis/ (WIP) and docs/ (authoritative)

**Validation:**
- Clear distinction between analysis/ and docs/
- No duplicate authoritative content

---

## Summary

**Total Estimated Effort**: 25-35 hours

**Breakdown by Phase:**
- Phase 1 (Audit): 6-8 hours
- Phase 2 (Structure): 2.5-4 hours
- Phase 3 (Architecture Diagrams): 4-6 hours
- Phase 4 (Analysis Figures): 4-6 hours
- Phase 5 (LabLink Architecture): 5-7 hours
- Phase 6 (Development & Folder READMEs): 4-6 hours
- Phase 7 (Archive & Update): 1.5-2.5 hours
- Phase 8 (Verification): 3-5 hours

**Critical Path:**
Phase 1 (Audit) → Phase 2 (Structure) → Phases 3-6 (parallel) → Phase 7 (Archive) → Phase 8 (Verify)

**Success Criteria:**
- ✅ All documentation consolidated in docs/ hierarchy
- ✅ Every directory has findable README
- ✅ All 12 architecture diagrams documented with purpose
- ✅ All 8+ analysis figures documented with generation guides
- ✅ PostgreSQL in-container correctly documented with evidence
- ✅ 22 Flask endpoints documented (not on client VMs)
- ✅ CI/CD OIDC mechanisms documented
- ✅ Clear navigation from README → docs → specific topics
- ✅ Getting started guide works for new users
- ✅ 100% unique content preserved
- ✅ 0 broken links
- ✅ Professional quality suitable for academic publication
