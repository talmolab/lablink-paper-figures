# Architecture Diagram Generation - Design

## Context

The LabLink system is defined across multiple repositories with infrastructure-as-code in Terraform. The paper needs accurate, publication-quality diagrams that reflect the actual deployed architecture. Manual diagram maintenance is error-prone as infrastructure evolves, so we need automated generation from the Terraform source of truth.

**Stakeholders**: Paper authors, reviewers, researchers deploying LabLink

**Constraints**:
- Must work with existing Terraform 1.x syntax
- Diagrams must meet journal publication standards (300+ DPI, proper sizing)
- Must handle multi-repo architecture (lablink, lablink-template, sleap-lablink)
- Initial implementation focuses on lablink-template infrastructure

## Goals / Non-Goals

**Goals**:
- Parse Terraform HCL files to extract resource definitions and relationships
- Generate publication-quality diagrams in PNG, SVG, and PDF formats
- Create both simplified (main paper) and detailed (supplementary) views
- Integrate into existing figure generation workflow
- Make diagrams reproducible and maintainable

**Non-Goals**:
- Real-time diagram updates (batch generation is sufficient)
- Interactive diagram exploration (static images only)
- Parsing Terraform state files (use .tf source only)
- Full Terraform AST parsing (extract relevant resources only)
- Generating diagrams for all LabLink repos in first iteration (focus on lablink-template)

## Decisions

### Decision 1: Use Python Diagrams library over Graphviz

**Choice**: Use [Diagrams](https://diagrams.mingrammer.com/) library

**Why**:
- Python-native (matches project tech stack)
- Built-in AWS component icons (EC2, Lambda, ALB, Route53, etc.)
- Clean, declarative API for creating architecture diagrams
- Automatically handles layout and rendering
- Exports to PNG and SVG natively

**Alternatives considered**:
- **Graphviz/DOT**: Lower-level, requires manual icon management, steeper learning curve
- **Mermaid**: Less control over AWS-specific styling, would need Node.js tooling
- **PlantUML**: Java dependency, less flexible for custom AWS layouts
- **draw.io Python API**: Overly complex for scripted generation

### Decision 2: Regex-based Terraform parsing over full HCL parser

**Choice**: Use regular expressions to extract resource blocks from Terraform files

**Why**:
- Simple, straightforward for extracting resource definitions
- No heavy dependencies (python-hcl2 adds complexity)
- We only need basic resource info (type, name, key attributes), not full AST
- Easier to maintain and debug
- Sufficient for current Terraform structure

**Alternatives considered**:
- **python-hcl2**: Full HCL parser, but overkill for our needs and adds dependency
- **Terraform JSON output**: Requires running Terraform, not purely static parsing
- **Manual mapping**: Not maintainable as infrastructure evolves

**Trade-off**: Regex parsing is less robust to complex Terraform syntax, but our infrastructure files follow standard patterns that make this acceptable.

### Decision 3: Generate multiple diagram variants from single source

**Choice**: Create diagram variants by filtering/grouping same parsed data

**Why**:
- Main paper needs simplified view (hide IAM details, group networking)
- Supplementary needs complete view (show all resources)
- Network flow diagram focuses on request routing
- Single parser, multiple renderers keeps code DRY

**Implementation**:
```python
# Shared parsing
resources = parse_terraform_files(tf_dir)

# Different renderers
generate_main_diagram(resources, filter=["EC2", "ALB", "Lambda", "CloudWatch"])
generate_detailed_diagram(resources, filter=None)  # All resources
generate_network_flow(resources, focus="routing")
```

### Decision 4: Configuration file path via CLI argument or environment variable

**Choice**: Accept Terraform directory path as CLI argument with fallback to environment variable

**Why**:
- Flexible for different development environments
- Works in CI/CD pipelines
- Doesn't hardcode paths in source code

**Example**:
```bash
python scripts/plotting/generate_architecture_diagram.py \
    --terraform-dir ../lablink-template/lablink-infrastructure \
    --output-dir figures/main \
    --diagram-type main
```

## Risks / Trade-offs

### Risk 1: Terraform syntax changes breaking regex parser

**Mitigation**:
- Add comprehensive tests with current Terraform examples
- Document expected Terraform patterns
- Provide clear error messages when parsing fails
- Consider upgrade to python-hcl2 if regex becomes unmaintainable

### Risk 2: Diagram layout issues with complex architectures

**Mitigation**:
- Start with current lablink-template infrastructure (well-defined scope)
- Test with different Terraform configurations
- Allow manual layout hints via configuration if needed
- Diagrams library handles most layout automatically

### Risk 3: Publication DPI/sizing requirements vary by journal

**Mitigation**:
- Make DPI and dimensions configurable via CLI arguments
- Default to conservative values (300 DPI, standard sizes)
- Document how to adjust for specific journal requirements
- Export vector formats (SVG, PDF) as fallback

## Migration Plan

**Phase 1: Initial Implementation**
1. Add Diagrams library to dependencies
2. Implement Terraform parser for lablink-template/main.tf and alb.tf
3. Create main architecture diagram generator
4. Add tests for parsing and diagram generation

**Phase 2: Enhanced Features**
1. Add detailed diagram variant
2. Add network flow diagram
3. Support multiple output formats (PNG, SVG, PDF)
4. Add configuration options for customization

**Phase 3: Integration**
1. Integrate into figure generation workflow
2. Document usage in README
3. Add to paper figure list

**Rollback**: No rollback needed (purely additive feature). If diagrams aren't suitable, fall back to manual diagram creation.

## Open Questions

1. **Which journal will the paper target?** - Affects DPI and sizing requirements
   - Action: Use flexible configuration to support multiple journals

2. **Should we include client VM architecture in diagrams?** - Client VMs are dynamically created
   - Action: Show representative client VM in diagrams with annotation indicating "N client VMs"

3. **Do we need to show multiple environment configurations (dev/prod)?** - Different backend configs exist
   - Action: Start with single representative configuration, add multi-env support if needed later

4. **Should diagrams show cost or performance annotations?** - Could add VM types, data flow sizes
   - Action: Keep initial diagrams purely architectural, add performance data in separate figures if needed