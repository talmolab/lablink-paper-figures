# Design Updates for Comprehensive LabLink Architecture Diagrams

## Overview

This document details the design changes needed to fix the critical issues identified in the initial implementation and create comprehensive, accurate architecture diagrams.

## Key Design Decisions (Revised)

### 1. Two-Tier Terraform Parsing

**Decision**: Parse BOTH Terraform directories and distinguish between infrastructure and runtime resources

**Rationale**:
- LabLink uses a two-tier architecture:
  - **Tier 1**: Infrastructure Terraform deploys the allocator server and supporting services
  - **Tier 2**: Client VM Terraform is called by the allocator at runtime to provision client VMs
- Initial implementation only parsed Tier 1, leading to incomplete architecture representation
- Client VMs shown in diagram were hardcoded placeholders, not actual parsed resources

**Implementation**:
```python
class ParsedTerraformConfig:
    # Add tier designation
    tier: str  # "infrastructure" or "client_vm"
    is_runtime_provisioned: bool  # True for client VM resources

def parse_lablink_architecture(
    infrastructure_dir: Path,
    client_vm_dir: Path
) -> tuple[ParsedTerraformConfig, ParsedTerraformConfig]:
    """Parse both Terraform tiers and return configs."""
    infra_config = parse_directory(infrastructure_dir)
    infra_config.tier = "infrastructure"

    client_config = parse_directory(client_vm_dir)
    client_config.tier = "client_vm"
    client_config.is_runtime_provisioned = True

    return infra_config, client_config
```

### 2. Locals Block Parsing and Variable Resolution

**Decision**: Parse `locals {}` blocks first, then resolve variable references in resource attributes

**Rationale**:
- Terraform uses `local.variable_name` references extensively
- Parser regex only matched quoted strings: `instance_type = "t3.large"`
- Actual code uses: `instance_type = local.allocator_instance_type`
- This caused "unknown" to appear in diagrams

**Implementation**:
```python
def parse_terraform_file(file_path: Path) -> ParsedTerraformConfig:
    content = file_path.read_text(encoding='utf-8')
    config = ParsedTerraformConfig()

    # FIRST: Parse locals block
    locals_dict = parse_locals_block(content)

    # THEN: Parse resources, resolving references
    # ... existing parsing code ...

    # FINALLY: Resolve all local.X references in attributes
    resolve_variable_references(config, locals_dict)

    return config

def parse_locals_block(content: str) -> dict[str, str]:
    """Extract locals block and parse key-value pairs."""
    locals_pattern = r'locals\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    match = re.search(locals_pattern, content, re.DOTALL)
    if not match:
        return {}

    locals_body = match.group(1)
    locals_dict = {}

    # Parse simple assignments: name = "value" or name = value
    for m in re.finditer(r'(\w+)\s*=\s*(?:"([^"]+)"|(\S+))', locals_body):
        name = m.group(1)
        value = m.group(2) or m.group(3)
        locals_dict[name] = value

    return locals_dict

def resolve_variable_references(config: ParsedTerraformConfig, locals_dict: dict):
    """Replace local.variable_name with actual values."""
    for resource_list in [config.ec2_instances, config.lambda_functions, ...]:
        for resource in resource_list:
            for key, value in resource.attributes.items():
                if isinstance(value, str) and value.startswith('local.'):
                    var_name = value.replace('local.', '')
                    if var_name in locals_dict:
                        resource.attributes[key] = locals_dict[var_name]
```

### 3. Conditional Resource Detection

**Decision**: Parse `count` and `for_each` expressions to mark resources as conditional

**Rationale**:
- ALB only exists when `ssl.provider = "acm"`
- Route53 records only exist when `dns.terraform_managed = true`
- Initial diagrams showed all resources as always-present
- Need to visually distinguish conditional resources

**Implementation**:
```python
@dataclass
class TerraformResource:
    resource_type: str
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    is_conditional: bool = False  # NEW
    condition: str = ""  # NEW: Store the count expression

def parse_resource_with_conditionals(match, locals_dict):
    """Parse resource and detect conditional creation."""
    resource_type = match.group(1)
    name = match.group(2)
    body = match.group(3)

    # Check for count parameter
    count_match = re.search(r'count\s*=\s*(.+?)(?:\n|$)', body)
    is_conditional = False
    condition = ""

    if count_match:
        count_expr = count_match.group(1).strip()
        # Detect conditional: count = condition ? 1 : 0
        if '?' in count_expr and ':' in count_expr:
            is_conditional = True
            condition = count_expr.split('?')[0].strip()
            # Resolve local variables in condition
            for var_name, var_value in locals_dict.items():
                condition = condition.replace(f'local.{var_name}', var_value)

    return TerraformResource(
        resource_type=resource_type,
        name=name,
        is_conditional=is_conditional,
        condition=condition
    )
```

### 4. CloudWatch Subscription Filter Parsing

**Decision**: Add new resource type for subscription filters to show CloudWatch → Lambda triggers

**Rationale**:
- User reported "triggers look like they are floating"
- CloudWatch and Lambda appeared disconnected
- The subscription filter IS a Terraform resource that creates the trigger

**Implementation**:
```python
@dataclass
class ParsedTerraformConfig:
    # ... existing fields ...
    subscription_filters: list[TerraformResource] = field(default_factory=list)  # NEW

def parse_subscription_filters(content: str, config: ParsedTerraformConfig):
    """Parse aws_cloudwatch_log_subscription_filter resources."""
    pattern = r'resource\s+"aws_cloudwatch_log_subscription_filter"\s+"([^"]+)"\s*\{([^}]+)\}'

    for match in re.finditer(pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'destination_arn\s*=\s*(\S+)', body):
            attrs['destination_arn'] = m.group(1)  # e.g., aws_lambda_function.log_processor.arn
        if m := re.search(r'log_group_name\s*=\s*(\S+)', body):
            attrs['log_group_name'] = m.group(1)  # e.g., aws_cloudwatch_log_group.client_vm_logs.name

        config.subscription_filters.append(
            TerraformResource(
                resource_type='aws_cloudwatch_log_subscription_filter',
                name=name,
                attributes=attrs
            )
        )
```

### 5. Visual Encoding Strategy

**Decision**: Use color, border style, and annotations to encode resource characteristics

**Rationale**:
- Diagrams must communicate 4 different deployment patterns
- Users need to understand what's always present vs. conditional
- Runtime-provisioned resources must be clearly distinguished from infrastructure

**Encoding Scheme**:

| Resource Type | Border Style | Background Color | Annotation |
|---------------|--------------|------------------|------------|
| Always-present infrastructure | Solid | Light blue | None |
| Conditional infrastructure | Dashed | Light green | "(When ssl.provider=acm)" |
| Runtime-provisioned | Dotted | Light orange | "Dynamically provisioned" |
| External/manual | Dotted | Light gray | "Configured externally" |

**Implementation**:
```python
def _create_node_with_encoding(self, resource: TerraformResource, label: str):
    """Create diagram node with visual encoding based on resource type."""

    # Determine styling
    if resource.is_conditional:
        style = "dashed"
        fillcolor = "#d4edda"  # Light green
        annotation = f"\n({resource.condition})"
    elif hasattr(resource, 'is_runtime_provisioned') and resource.is_runtime_provisioned:
        style = "dotted"
        fillcolor = "#fff3cd"  # Light orange
        annotation = "\n(Runtime-provisioned)"
    else:
        style = "solid"
        fillcolor = "#d1ecf1"  # Light blue
        annotation = ""

    node_attr = {
        "style": style,
        "fillcolor": fillcolor,
        "fontsize": "16",
        "fontname": "Helvetica-Bold"
    }

    return self._create_node(label + annotation, **node_attr)
```

### 6. Redesigned Cluster Architecture

**Decision**: Reorganize clusters to reflect actual architectural layers, not arbitrary groupings

**Old Clustering** (WRONG):
- "LabLink Core" (mixed allocator EC2, client VMs, Lambda)
- "DNS & SSL" (generic Route53 + ALB)
- "Observability" (CloudWatch only)

**New Clustering** (CORRECT):
```
┌─────────────────────────────────────────────────────────────┐
│ Access Layer (Configurable - 4 deployment patterns)        │
│ ┌─────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│ │ Route53     │  │ ALB           │  │ Caddy (on EC2)  │   │
│ │ (dashed)    │  │ (dashed)      │  │ (annotation)    │   │
│ │ "When       │  │ "ACM only"    │  │ "Let's Encrypt" │   │
│ │ managed"    │  │               │  │                 │   │
│ └─────────────┘  └───────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LabLink Infrastructure (Always present)                     │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ Allocator EC2 (t3.large)                               │  │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│ │ │ Flask    │ │PostgreSQL│ │Terraform │ │Caddy*    │   │  │
│ │ │ API      │ │ DB       │ │ binary   │ │          │   │  │
│ │ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│ └────────────────────────────────────────────────────────┘  │
│ [Elastic IP] [Security Groups] [IAM Role]                   │
└─────────────────────────────────────────────────────────────┘
                           ↓ (Terraform subprocess)
┌─────────────────────────────────────────────────────────────┐
│ Dynamic Compute (Runtime-provisioned - dotted border)       │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ Client EC2 (count=N, dotted orange)                    │  │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐    │  │
│ │ │ Docker   │ │Subject   │ │CloudWatch Agent     │    │  │
│ │ │ Runtime  │ │Software  │ │                     │    │  │
│ │ └──────────┘ └──────────┘ └──────────────────────┘    │  │
│ └────────────────────────────────────────────────────────┘  │
│ [Client Security Group] [Client IAM Role] [SSH Key]         │
│ Note: "Provisioned via allocator Terraform subprocess"      │
└─────────────────────────────────────────────────────────────┘
                           ↓ (logs)
┌─────────────────────────────────────────────────────────────┐
│ Observability & Logging (Always present)                    │
│ ┌──────────────────┐   ┌─────────────────────────┐          │
│ │ CloudWatch Logs  │ → │ Subscription Filter     │ →        │
│ │ (client_vm_logs) │   │ (trigger - shown as     │          │
│ │                  │   │  labeled edge)          │          │
│ └──────────────────┘   └─────────────────────────┘          │
│                                   ↓                          │
│                        ┌──────────────────┐                  │
│                        │ Lambda           │                  │
│                        │ (log_processor)  │                  │
│                        └──────────────────┘                  │
│                                   ↓ POST /api/vm-logs        │
│                        (back to Allocator API)               │
└─────────────────────────────────────────────────────────────┘
```

### 7. Configuration Matrix Diagram

**Decision**: Create a new diagram type showing all 4 deployment patterns side-by-side

**Rationale**:
- Single diagram can't accurately represent 4 mutually exclusive configurations
- Users need to understand deployment options
- Table/matrix format is clearer than trying to show all options in one graph

**Implementation**:
Use Python Diagrams + custom table rendering, or use matplotlib to create:

```
┌────────────────┬────────────┬──────────────┬────────────┬────────────┐
│ Component      │ IP-Only    │ Let's Encrypt│ Cloudflare │ ACM        │
├────────────────┼────────────┼──────────────┼────────────┼────────────┤
│ Allocator EC2  │     ✓      │      ✓       │     ✓      │     ✓      │
│ Elastic IP     │     ✓      │      ✓       │     ✓      │     ✓      │
│ Route53 DNS    │     ✗      │      ✓       │     ✗      │     ✓      │
│ ALB            │     ✗      │      ✗       │     ✗      │     ✓      │
│ Caddy (SSL)    │     ✗      │      ✓       │     ✓      │     ✗      │
│ SSL Provider   │   None     │  Let's Enc.  │ Cloudflare │    ACM     │
│ DNS Management │   N/A      │  Terraform   │   Manual   │ Terraform  │
│ Access URL     │ http://IP  │https://domain│https://dom │https://dom │
│ Port           │   :5000    │   (auto)     │  (auto)    │  (auto)    │
└────────────────┴────────────┴──────────────┴────────────┴────────────┘
```

## Updated Diagram Types

### 1. Main Architecture (Comprehensive)
**Purpose**: Show complete LabLink system with both infrastructure and runtime tiers

**Includes**:
- All 5 clusters (Access, Infrastructure, Dynamic Compute, Observability, IAM)
- Visual encoding (colors, borders, annotations)
- Subscription filter shown as labeled edge
- Nested components inside EC2 nodes
- Clear distinction between infrastructure and runtime resources

**Excludes** (for simplicity):
- Security group details
- Detailed IAM policies
- Target group internals

### 2. Configuration Matrix
**Purpose**: Compare 4 DNS/SSL deployment patterns

**Includes**:
- Table format
- Check marks for present components
- Access URLs for each pattern
- Notes on manual vs. automated setup

### 3. Detailed Infrastructure
**Purpose**: Show ALL Terraform resources from both tiers

**Includes**:
- All security groups
- All IAM roles and policy attachments
- EIP associations
- Target group attachments
- TLS keys and SSH key pairs
- Both infrastructure and client VM resources
- All conditional resources with conditions noted

### 4. Network Flow (Multi-Config)
**Purpose**: Show request routing for all 4 configurations

**Includes**:
- 4 separate flow paths
- Numbered steps for each path
- Decision points showing which config leads to which path

### 5. Logging Flow
**Purpose**: Detail the observability data flow

**Includes**:
- Client VM → CloudWatch agent → Log Group
- Log Group → Subscription filter → Lambda
- Lambda → POST request → Allocator API
- Allocator → PostgreSQL storage
- Show CloudWatch agent configuration
- Show Lambda environment variables

## Implementation Priority

### Phase 1: Fix Critical Parser Issues (Immediate)
1. ✅ Fix instance_type parsing (parse locals + resolve references)
2. ✅ Add subscription filter parsing
3. ✅ Parse conditional resources (count detection)

### Phase 2: Multi-Tier Architecture (High Priority)
4. ⬜ Parse both Terraform directories
5. ⬜ Distinguish infrastructure vs. runtime resources
6. ⬜ Add tier designation to ParsedTerraformConfig

### Phase 3: Visual Encoding (High Priority)
7. ⬜ Implement border styles (solid/dashed/dotted)
8. ⬜ Implement color coding
9. ⬜ Add condition annotations
10. ⬜ Show nested components inside EC2 nodes

### Phase 4: Redesigned Diagrams (Medium Priority)
11. ⬜ Redesign main architecture with new clusters
12. ⬜ Show subscription filter as edge, not node
13. ⬜ Add runtime provisioning annotations
14. ⬜ Update detailed diagram with all resources

### Phase 5: New Diagram Types (Lower Priority)
15. ⬜ Create configuration matrix diagram
16. ⬜ Create logging flow diagram
17. ⬜ Update network flow to show all 4 configs

### Phase 6: Testing & Documentation
18. ⬜ Update tests for new parser features
19. ⬜ Test with all 4 configuration YAMLs
20. ⬜ Verify diagrams match actual deployments
21. ⬜ Update README with diagram descriptions

## Risk Mitigation

### Risk: Locals parsing too complex
**Mitigation**: Start with simple key="value" parsing, expand to expressions later

### Risk: Conditional detection false positives
**Mitigation**: Only mark as conditional if `count` contains ternary operator `? :`

### Risk: Diagram too cluttered with all resources
**Mitigation**: Keep main diagram simple, put ALL resources in detailed diagram only

### Risk: Client VM Terraform changes independently
**Mitigation**: Document both Terraform paths in code comments, fail gracefully if files move

## Success Criteria

1. ✅ Instance type shows "t3.large" not "unknown"
2. ✅ Subscription filter visible as edge connecting CloudWatch to Lambda
3. ✅ Client VMs clearly marked as "Runtime-provisioned" with orange/dotted styling
4. ✅ ALB and Route53 shown with dashed borders and condition annotations
5. ✅ Diagram includes resources from BOTH Terraform tiers
6. ✅ Configuration matrix clearly shows 4 deployment options
7. ✅ All diagrams render without errors
8. ✅ Diagrams accurately match actual deployed architecture
9. ✅ User can understand deployment options from diagrams alone
10. ✅ Diagrams remain synchronized with Terraform changes (automated generation)