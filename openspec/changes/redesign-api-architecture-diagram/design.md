# Design: Actor-Centric API Architecture Diagram

## Design Rationale

### Why Actor-Centric Instead of Endpoint-by-Endpoint?

**Research findings** from analyzing industry leaders (Stripe, AWS, Kong, Postman):
- None show all endpoints as individual nodes in a single diagram
- Standard patterns: actor-centric flows, layered architecture, or grouped resources
- **Key principle**: Diagrams show architectural patterns, not exhaustive inventories

**Technical constraint**: Python `diagrams` library doesn't expose full GraphViz control
- Nested clusters stack vertically regardless of `direction` setting
- 18+ nodes + 6 clusters = poor layout even with raw GraphViz
- Solution: Reduce node count and cluster depth

### Root Cause of Current Issues

1. **Vertical stacking**: 6 nested clusters (User Interface → Admin Management → VM API → Query API → Lambda Callback → Security) override LR direction
2. **Edge routing failure**: Too many nodes (18+) overwhelm GraphViz orthogonal routing algorithm
3. **Fighting best practices**: 22 individual endpoint nodes is not how professionals visualize APIs

## Proposed Architecture

### Layout Structure (Left to Right)

```
┌─────────────┐      ┌────────────────────────────────────────────┐      ┌──────────────┐
│  Actors     │      │  LabLink Allocator (EC2)                   │      │  Data        │
│  (External) │      │                                            │      │  Storage     │
│             │      │  ┌──────────────────────────────────────┐  │      │              │
│  User       │─────▶│  │ Flask API (22 Routes)                │  │─────▶│  PostgreSQL  │
│  Admin      │─────▶│  │                                      │  │      │  Database    │
│  Client VM  │─────▶│  │ • User Interface (2) - Public        │  │      │              │
│  Lambda     │─────▶│  │ • Admin Mgmt (10) - @auth required   │  │      └──────────────┘
│             │      │  │ • VM Callbacks (5) - Validated       │  │
└─────────────┘      │  │ • Query API (4) - Public             │  │
                     │  │ • Lambda Callback (1) - Internal     │  │
                     │  └──────────────────────────────────────┘  │
                     │                                            │
                     │  ┌──────────────────────────────────────┐  │
                     │  │ HTTP Basic Auth (bcrypt)             │  │
                     │  └──────────────────────────────────────┘  │
                     └────────────────────────────────────────────┘
```

### Node Count Reduction

- **Before**: 18+ endpoint nodes + 6 clusters + 4 actors + 2 infrastructure = 30+ elements
- **After**: 4 actors + 1 Flask API node + 1 auth component + 1 database = 7 main elements
  - 5 API groups shown as text labels within Flask API node or simple boxes (not full nodes)

### Cluster Depth Reduction

- **Before**: 6 levels of nesting (Allocator → Security → User Interface/Admin/VM/Query/Lambda)
- **After**: 2 levels maximum (Allocator cluster → Flask API + Auth components)

### Security Visualization Strategy

Use **color-coded edges** and **visual markers** to show security requirements:

1. **Public endpoints (green edges)**:
   - User → User Interface group
   - User/Admin → Query API group
   - No special marker needed

2. **Authenticated endpoints (gold/yellow edges + lock icon)**:
   - Admin → Auth component → Admin Management group
   - IAM/lock icon shows authentication required
   - Edge label: "@auth.login_required"

3. **Validated endpoints (blue edges + checkmark icon)**:
   - Client VM → VM Callbacks group
   - Small validation icon (checkmark or shield)
   - Edge label: "hostname validated"

4. **Internal endpoints (purple edges)**:
   - Lambda → Lambda Callback group
   - Dashed edge style to show internal-only

### API Group Representation

Two options for showing the 5 functional groups within the Allocator:

**Option A: Text annotations on Flask API node**
```python
flask_api = Flask("Flask API\n(22 Routes)\n\n• User Interface (2)\n• Admin Mgmt (10) [AUTH]\n• VM Callbacks (5)\n• Query API (4)\n• Lambda (1)")
```

**Option B: Simple labeled boxes within Allocator cluster**
```python
with Cluster("LabLink Allocator"):
    flask_api = Flask("Flask API")

    # Lightweight group boxes (using Blank or minimal styling)
    user_interface = Blank("User Interface\n(2 endpoints)")
    admin_mgmt = Blank("Admin Management\n(10 endpoints)\n@auth required")
    vm_callbacks = Blank("VM Callbacks\n(5 endpoints)")
    query_api = Blank("Query API\n(4 endpoints)")
    lambda_callback = Blank("Lambda Callback\n(1 endpoint)")
```

**Recommendation**: Option B with `fontcolor="black"` to avoid white text issues

### Edge Routing Strategy

To ensure all edges render properly:

1. **Minimize crossings**: Arrange actors in order of primary API group usage
   - User (top) → User Interface, Query API
   - Admin (mid-top) → Admin Management
   - Client VM (mid-bottom) → VM Callbacks
   - Lambda (bottom) → Lambda Callback

2. **Use edge minlen**: Add `minlen="2"` to edges crossing cluster boundaries

3. **Color coding**: Distinct colors prevent visual confusion
   - Green: User flows (#28a745)
   - Gold: Admin flows (#ffc107)
   - Blue: VM flows (#007bff)
   - Purple: Lambda flows (#6f42c1)
   - Gray: Database operations (#6c757d)

4. **Label placement**: Use `fontsize` from preset, position labels clearly

### Database Positioning

**Option 1**: Database outside Allocator cluster (right side)
- Shows database as separate infrastructure component
- Clearer separation of concerns
- **Recommended** for publication clarity

**Option 2**: Database inside Allocator cluster
- Shows database as integral to Allocator
- More compact layout

## Implementation Details

### Graph Attributes

```python
graph_attr = {
    "direction": "LR",  # Left-to-right (will actually work now!)
    "nodesep": "0.8",   # Horizontal spacing
    "ranksep": "1.2",   # Cluster spacing
    "splines": "ortho", # Orthogonal edge routing
    # ... fontsize_preset settings
}
```

### Node Styling

```python
node_attr = {
    "fontcolor": "black",  # Critical: avoid white text
    # ... fontsize_preset settings
}
```

### API Group Boxes (if using Option B)

```python
# Override Blank node default white color
group_attr = {
    "fontcolor": "black",
    "style": "rounded",
    "fillcolor": "#f8f9fa",  # Light gray background
    "color": "#dee2e6",      # Border color
}
```

## Alternative Approaches Considered

### 1. Layered Architecture (Horizontal Layers)
```
┌─────────────────────────────────────┐
│ Public Layer (12 endpoints)         │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Authenticated Layer (10 endpoints)  │
└─────────────────────────────────────┘
```
**Rejected**: Less clear about which actors use which endpoints

### 2. Sequence Diagrams for Key Workflows
```
User → Allocator: POST /api/request_vm
Allocator → Database: UPDATE vm_table
Database → Allocator: pg_notify()
```
**Rejected**: Would need multiple diagrams to show all flows, doesn't show complete API surface

### 3. Fix Current Diagram with Raw GraphViz
**Rejected**: Still fundamentally too many nodes, fighting against best practices

### 4. Hybrid: Small Flow Diagram + Endpoint Table
**Rejected**: Harder to generate programmatically, table not well-suited for diagrams library

## Testing Strategy

Generate with all three font presets to verify scalability:
```bash
# Poster (20pt) - primary use case
uv run python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type api-architecture \
  --fontsize-preset poster

# Paper (14pt)
uv run python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type api-architecture \
  --fontsize-preset paper

# Presentation (16pt)
uv run python scripts/plotting/generate_architecture_diagram.py \
  --diagram-type api-architecture \
  --fontsize-preset presentation
```

## Success Metrics

1. **Visual**:
   - Horizontal layout (width > height)
   - All 4 actors visible on left
   - Allocator cluster centered
   - Database on right
   - All edges rendered and not overlapping

2. **Readability**:
   - All text legible at 100% zoom
   - Security requirements clear from colors/icons
   - Endpoint counts visible for each group
   - Edge labels readable

3. **Technical**:
   - Generates without errors
   - File size reasonable (< 2MB PNG)
   - Works with all font presets
   - Renders in < 5 seconds

## Future Enhancements (Out of Scope)

- Interactive version with clickable endpoints linking to documentation
- Separate diagrams for specific workflows (VM provisioning, log collection)
- Animation showing request/response flows
- Integration with OpenAPI/Swagger specification