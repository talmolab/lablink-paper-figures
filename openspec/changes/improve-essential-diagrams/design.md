# Design Document: Essential Diagram Improvements

## Context

The 4 essential architecture diagrams (lablink-architecture, lablink-crd-connection, lablink-logging-pipeline, lablink-vm-provisioning) were created in the `expand-diagram-suite` change. Initial user feedback revealed systematic visual quality issues and accuracy problems that must be addressed before publication.

### Background
- Target: Research paper publication (peer-reviewed journal)
- Format: 300 DPI PNG images for print quality
- Audience: Researchers evaluating LabLink architecture for adoption
- Current state: Functional but has title placement, text size, edge label positioning, missing icons, and conceptual accuracy issues

### Constraints
- Must maintain 300 DPI publication quality
- Must use "diagrams as code" approach (no manual image editing)
- Must work within GraphViz layout engine capabilities and limitations
- Should minimize custom icons (prefer diagrams library built-ins)

### Stakeholders
- Paper authors: Need publication-ready diagrams
- Reviewers: Need accurate, clear architectural representations
- Future users: Need understandable system documentation

## Goals / Non-Goals

### Goals
1. **Visual Quality**: Move titles to top, increase text sizes, improve edge label positioning
2. **Accuracy**: Replace Blank placeholder nodes with proper icons where available
3. **Completeness**: Add missing flows and context (VM feedback, admin log viewing, CRD authentication details)
4. **Consistency**: Apply uniform styling across all 4 essential diagrams
5. **Correctness**: Fix conceptual errors ("Launches CRD" → "Authenticates & Connects", "Lifecycle" → "Provisioning")

### Non-Goals
1. **NOT changing diagram content structure**: No adding/removing major components or clusters
2. **NOT creating elaborate custom icons**: Simple replacements only
3. **NOT addressing supplementary diagrams**: Scope is limited to 4 essential diagrams only
4. **NOT solving GraphViz fundamental limitations**: Accept "good enough" edge label positioning, don't over-engineer
5. **NOT changing diagram generation architecture**: Keep existing LabLinkDiagramBuilder class structure

## Decisions

### Decision 1: Create Helper Methods for Styling

**What**: Extract graph_attr, node_attr, edge_attr creation into reusable helper methods

**Why**: 
- DRY principle: All 4 diagrams need identical styling updates
- Consistency: Ensures uniform appearance across all diagrams
- Maintainability: Single place to adjust global styling in future

**Alternatives Considered**:
- Global constants: Less flexible, harder to override per-diagram if needed
- Keep inline: Leads to code duplication and inconsistency risk

**Implementation**:
```python
def _create_graph_attr(self, dpi=300, title_on_top=True, cluster_fontsize=32):
    """Create consistent graph attributes for all diagrams.
    
    Args:
        dpi: Output resolution (default 300 for publication quality)
        title_on_top: If True, place graph title at top (default True)
        cluster_fontsize: Font size for cluster labels (default 32)
    
    Returns:
        dict: GraphViz graph_attr dictionary
    """
    return {
        "fontsize": str(cluster_fontsize),
        "fontname": "Helvetica",
        "bgcolor": "white",
        "dpi": str(dpi),
        "pad": "0.5",
        "nodesep": "0.6",
        "ranksep": "0.8",
        "splines": "ortho",
        "labelloc": "t" if title_on_top else "b",  # KEY CHANGE
    }
```

### Decision 2: Use `labelfloat=true` for Edge Labels

**What**: Add `labelfloat=true` to edge_attr to allow GraphViz to position edge labels away from edge lines for clarity

**Why**:
- GraphViz limitation: No native "always N pixels above line" positioning
- `labeldistance` and `labelangle` only work for headlabel/taillabel, not regular label
- `labelfloat` allows GraphViz to intelligently position labels to avoid overlaps
- Combined with increased fontsize, provides "good enough" solution

**Alternatives Considered**:
- `xlabel` attribute: Positions labels after layout, but requires knowing which labels need special treatment
- Post-processing with gvpr: Too complex for marginal improvement
- Manual positioning via invisible nodes: Overly complex, fragile
- Accept default positioning: User feedback says it's unacceptable

**Trade-offs**:
- ✅ Pro: Simple, works with GraphViz's layout algorithm
- ✅ Pro: Improves clarity without major code changes
- ⚠️ Con: Still not perfect "above line" positioning
- ⚠️ Con: Label positions may shift unexpectedly with layout changes

**Decision**: Use labelfloat as "good enough" solution, document limitation

### Decision 3: Icon Replacement Strategy

**What**: Replace Blank nodes with diagrams library icons where semantically appropriate, use custom icons sparingly, keep Blank nodes only where no good alternative exists

**Why**:
- Visual professionalism: Proper icons look more polished than generic boxes
- Semantic clarity: Icons convey component type at a glance
- Maintainability: Using library icons avoids custom asset management

**Icon Mapping Table**:

| Current Blank Node | Replacement | Source | Rationale |
|-------------------|-------------|---------|-----------|
| CloudWatch Agent | `onprem.monitoring.Prometheus` or custom | Library or custom | CloudWatch agent is a monitoring service |
| Subscription Filter | `CloudwatchEventEventBased` | Library: `diagrams.aws.management` | Represents event-based filtering |
| Terraform subprocess | Custom: terraform.png | Custom icon | Terraform has distinctive logo |
| TRIGGER (database) | `RDS` with label | Library: `diagrams.aws.database` | Database component |
| pg_notify() | `onprem.database.Postgresql` | Library: `diagrams.onprem.database` | PostgreSQL-specific function |
| subscribe.py | `diagrams.programming.language.Python` | Library | Python script |
| connect_crd.py | `diagrams.programming.language.Python` | Library | Python script |
| Phase nodes (1-3) | Keep as Blank or use numbered clusters | N/A | No clear icon for abstract phases |

**Custom Icon Requirements**:
- Terraform logo: Download from https://www.terraform.io/ (open source)
- Resize to ~256x256px for consistency with diagrams library icons
- Place in `assets/icons/terraform.png`

**Alternative Considered**:
- Use Blank for everything: Rejected, reduces visual quality
- Create custom icons for all: Rejected, too much work for marginal benefit
- Use only library icons: Accepted where possible, custom only when needed

### Decision 4: Edge Label Text Changes for Accuracy

**What**: Update specific edge labels to correct conceptual errors and add clarity

**Changes**:

| Diagram | Current Label | New Label | Reason |
|---------|--------------|-----------|---------|
| CRD Connection | "5. Launches" | "5. Authenticates & Connects to" | CRD doesn't "launch" - it authenticates and establishes connection |
| CRD Connection | "6. WebRTC Connection" | "6. WebRTC P2P Connection" | More technically precise |
| Logging Pipeline | "3. Triggers" | "3. Triggers (on pattern match)" | Clarifies subscription filter behavior |
| VM Provisioning | (title) "VM Provisioning & Lifecycle" | "VM Provisioning" | Diagram doesn't show full lifecycle |

**Why**:
- Accuracy: Prevents misunderstanding of system behavior
- Precision: More technically correct terminology
- Clarity: Additional context helps readers understand mechanism

**Research Supporting Changes**:
- WebRTC verification: Confirmed via web search that CRD uses WebRTC for P2P connections + Chromoting protocol
- CRD authentication: Code analysis shows CRD command authenticates user's Google account for VM access
- Subscription filter: AWS CloudWatch documentation confirms pattern-based triggering

### Decision 5: Add Missing Flows and Context

**What**: Add edges and annotations for missing architectural details

**Additions**:

1. **Logging Pipeline**: Admin viewing logs
   - Add: User("Admin") → Edge("View logs (web UI)") → Database
   - Why: Shows complete logging story (collection → storage → viewing)

2. **VM Provisioning**: VM feedback to allocator
   - Add: Client VM → Edge("4. Status updates (POST /api/vm-metrics)") → Allocator
   - Add: Allocator → Edge("5. Store provisioning metrics") → Database
   - Why: Shows two-way communication, not just one-way provisioning

3. **CRD Connection**: Authentication context
   - Add annotation to Client VM: "Client VM (Admin-provisioned)"
   - Add note: "CRD command authenticates user's Google account for remote access"
   - Why: Clarifies that VMs are pre-provisioned and CRD is about authentication, not VM creation

**Why These Additions**:
- User feedback explicitly requested missing flows
- Code analysis confirms these flows exist in actual system
- Complete story improves reader comprehension

**Alternative Considered**:
- Keep diagrams minimal: Rejected, missing critical context
- Create separate sequence diagrams: Rejected, architecture diagrams can show this

### Decision 6: Font Size Selection

**What**: Increase node text from 11pt to 14pt, edge text from 12pt to 14pt, keep title at 32pt

**Why**:
- Publication quality: 11pt is too small for printed papers at typical sizes
- Readability: 14pt is minimum for comfortable reading in print
- Hierarchy: 32pt title → 14pt labels maintains clear visual hierarchy
- Testing: Will validate with sample prints

**Alternatives Considered**:
- 16pt nodes: May cause layout overflow, 14pt is safer starting point
- 18pt edges: Too large, would dominate diagram
- Uniform 14pt: Selected as balanced compromise

**Testing Strategy**:
1. Generate with 14pt, check layout
2. If text overlaps or diagram too cramped, try 13pt
3. If text still too small visually, try 15pt
4. Settle on size that balances readability vs. layout constraints

## Risks / Trade-offs

### Risk 1: Font Size Causes Layout Overflow
**Likelihood**: Medium  
**Impact**: Medium (diagrams may become too crowded or text may overlap)  
**Mitigation**: 
- Test iteratively with each diagram
- Adjust ranksep and nodesep to increase spacing if needed
- Fall back to 13pt if 14pt doesn't work
- Use shorter labels where possible

### Risk 2: Custom Icons Don't Integrate Well
**Likelihood**: Low  
**Impact**: Low (visual inconsistency)  
**Mitigation**:
- Use diagrams.custom.Custom class properly
- Ensure icon dimensions match library icons (~256x256px)
- Test rendering before committing
- Fall back to Blank nodes if custom doesn't work

### Risk 3: Edge Label Positioning Still Problematic
**Likelihood**: Medium  
**Impact**: Low (aesthetic issue, not functional)  
**Mitigation**:
- Accept GraphViz limitation and document it
- Use `labelfloat=true` for best-effort improvement
- Consider `xlabel` for most critical labels if needed
- User expectation management: "Consistent positioning" means "consistently better", not "perfectly above line"

### Risk 4: Changes Break Existing Layout
**Likelihood**: Low  
**Impact**: Medium (diagrams may need rework)  
**Mitigation**:
- Version control: Can always revert if changes break layout
- Test each diagram individually before committing
- Visual inspection before finalizing

### Trade-off 1: Icon Accuracy vs. Simplicity
- **Pro accuracy**: PostgreSQL icon for pg_notify() is technically correct
- **Pro simplicity**: Generic database icon is simpler, less cluttered
- **Decision**: Use PostgreSQL icon - accuracy is more important for technical diagrams

### Trade-off 2: Comprehensive Context vs. Diagram Clarity
- **Pro comprehensive**: Show all flows (admin viewing logs, VM feedback, etc.)
- **Pro simple**: Keep diagrams minimal, only core flows
- **Decision**: Add missing flows - user explicitly requested this context

## Migration Plan

No migration needed - this is output generation, not a deployed service.

### Rollout Strategy
1. Implement changes incrementally (global styling → icon replacements → missing flows)
2. Regenerate each diagram after changes
3. Visual inspection and comparison with previous versions
4. Final validation with paper authors before merging

### Verification Steps
1. Generate all 4 diagrams with new code
2. Compare side-by-side with current versions
3. Check file sizes (should be similar, ~100-300KB per PNG)
4. Verify 300 DPI resolution maintained
5. Print test at actual paper size (typically 6-8 inches wide)
6. Confirm text is readable in print

### Rollback
If changes cause unacceptable layout issues:
1. Git revert to previous commit
2. Identify specific problematic change (font size? icons? edge labels?)
3. Adjust parameters and retry
4. Document any GraphViz limitations that prevent desired outcome

## Open Questions

### Q1: Should we use custom Terraform icon or library equivalent?
**Options**:
- A) Custom terraform.png (distinctive, recognizable)
- B) `onprem.iac.Terraform` if exists in library (simpler)
- C) Generic `Blank` with label (fallback)

**Investigation needed**: Check diagrams library for Terraform icon
**Recommendation**: Custom icon if library doesn't have it - Terraform logo is well-known

### Q2: What icon for CloudWatch Agent?
**Options**:
- A) `onprem.monitoring.Prometheus` (monitoring service analogy)
- B) `aws.management.Cloudwatch` (AWS service)
- C) Custom agent icon
- D) Keep as `Blank`

**Recommendation**: Try option B first (AWS Cloudwatch icon), fall back to D if layout is poor

### Q3: How to represent database TRIGGER and pg_notify()?
**Options**:
- A) Two separate RDS nodes in cluster
- B) One RDS node with edge to itself (trigger fires notify)
- C) Keep as Blank nodes with labels
- D) Custom database + lightning bolt icon for trigger

**Recommendation**: Option B (RDS with self-edge) - shows trigger mechanism clearly

### Q4: Should phase nodes in VM provisioning be numbered Blank nodes or clustered?
**Options**:
- A) Keep as 3 separate Blank nodes (current)
- B) Create sub-cluster "3-Phase Startup" with 3 Blank nodes inside
- C) Use actual icons (Docker for phase 2, checkmark for phase 3)

**Recommendation**: Option B (sub-cluster) - groups related phases, maintains clarity

### Q5: What's acceptable edge label positioning?
**Options**:
- A) Perfect: Always N pixels above line (not possible in GraphViz)
- B) Good enough: `labelfloat=true` + increased fontsize (achievable)
- C) Manual: Use `xlabel` for specific problematic labels (complex)

**Recommendation**: Option B as default, Option C for specific problematic cases if needed

## Implementation Notes

### Code Organization
```
src/diagram_gen/generator.py:
  - LabLinkDiagramBuilder class:
    - _create_graph_attr() [NEW]
    - _create_node_attr() [NEW]
    - _create_edge_attr() [NEW]
    - build_main_diagram() [MODIFIED: use helpers]
    - build_crd_connection_diagram() [MODIFIED: icons + labels]
    - build_logging_pipeline_diagram() [MODIFIED: icons + missing flow]
    - build_vm_provisioning_diagram() [MODIFIED: icons + feedback + title]
```

### Testing Strategy
```python
# Test each diagram individually
def test_main_diagram_improved():
    builder = LabLinkDiagramBuilder(config)
    builder.build_main_diagram(output_path)
    
    # Verify file generated
    assert output_path.exists()
    
    # Verify file size reasonable (100-300KB)
    assert 100_000 < output_path.stat().st_size < 300_000
    
    # Visual inspection required (automated tests can't verify layout quality)
```

### Documentation Requirements
- Update `figures/main/diagram_metadata.txt` with improvement details
- Create `RESEARCH.md` documenting WebRTC verification and icon choices
- Update README with guidance on diagram usage
- Document GraphViz limitations in comments

## References

- GraphViz labelloc documentation: https://graphviz.org/docs/attrs/labelloc/
- GraphViz edge attributes: https://graphviz.org/docs/edges/
- Chrome Remote Desktop WebRTC research: Multiple sources confirming WebRTC usage
- Diagrams library icon catalog: https://diagrams.mingrammer.com/docs/nodes/
- User feedback: Provided in task description (title placement, text size, edge labels, missing icons, conceptual errors)
