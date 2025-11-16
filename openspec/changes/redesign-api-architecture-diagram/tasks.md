# Tasks: Redesign API Architecture Diagram

## Implementation Tasks

### 1. Update `build_api_architecture_diagram()` method structure

**File**: `src/diagram_gen/generator.py`

**Actions**:
- [ ] Remove existing implementation (lines ~954-1089)
- [ ] Create new method signature (keep same parameters: output_path, format, dpi, fontsize_preset)
- [ ] Update docstring with new description and reference to `analysis/api-architecture-analysis.md`
- [ ] Import required diagram components:
  - `from diagrams import Diagram, Cluster, Edge`
  - `from diagrams.onprem.client import User`
  - `from diagrams.aws.compute import EC2, Lambda`
  - `from diagrams.aws.database import RDS`
  - `from diagrams.programming.framework import Flask`
  - `from diagrams.aws.security import IAM`
  - `from diagrams.generic.blank import Blank` (for API group boxes if needed)

**Validation**: Code compiles without import errors

**Estimated effort**: 30 minutes

---

### 2. Configure diagram attributes for horizontal layout

**File**: `src/diagram_gen/generator.py` (within method)

**Actions**:
- [ ] Use helper methods to create consistent attributes:
  ```python
  graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)
  node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
  edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)
  ```
- [ ] Override node fontcolor to black: `node_attr["fontcolor"] = "black"`
- [ ] Get edge fontsize for labels: `edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])`
- [ ] Create Diagram context with:
  - Title: `"LabLink API Architecture (22 Endpoints)"`
  - `direction="LR"` (left-to-right)
  - All configured attributes
  - Output format from parameter

**Validation**: Diagram initialization succeeds, LR direction set

**Estimated effort**: 20 minutes

---

### 3. Create 4 external actor nodes

**File**: `src/diagram_gen/generator.py` (within Diagram context)

**Actions**:
- [ ] Create User actor: `user = User("User")`
- [ ] Create Admin actor: `admin = User("Admin")`
- [ ] Create Client VM actor: `client_vm = EC2("Client VM")`
- [ ] Create Lambda actor: `lambda_processor = Lambda("Lambda\nLog Processor")`

**Validation**: All 4 actors render on the left side of diagram

**Estimated effort**: 10 minutes

---

### 4. Create Allocator infrastructure cluster

**File**: `src/diagram_gen/generator.py` (within Diagram context)

**Actions**:
- [ ] Create Allocator cluster: `with Cluster("LabLink Allocator (EC2)"):`
- [ ] Inside cluster, create Flask API node: `flask_api = Flask("Flask API\n(22 Routes)")`
- [ ] Create HTTP Basic Auth component: `auth = IAM("HTTP Basic Auth\n(bcrypt)")`
- [ ] Create 5 API group boxes using Blank nodes with black font:
  ```python
  user_interface = Blank("User Interface\n(2 endpoints)\nPublic")
  admin_mgmt = Blank("Admin Management\n(10 endpoints)\n@auth.login_required")
  vm_callbacks = Blank("VM-to-Allocator API\n(5 endpoints)\nValidated")
  query_api = Blank("Query API\n(4 endpoints)\nPublic")
  lambda_callback = Blank("Lambda Callback\n(1 endpoint)\nInternal")
  ```

**Note**: API group boxes may need custom styling:
```python
# Before Diagram context:
group_attr = {"fontcolor": "black", "style": "rounded", "fillcolor": "#f8f9fa"}
```

**Validation**: Allocator cluster renders in center with all components visible

**Estimated effort**: 30 minutes

---

### 5. Create database node

**File**: `src/diagram_gen/generator.py` (within Diagram context, outside Allocator cluster)

**Actions**:
- [ ] Create PostgreSQL database node: `database = RDS("PostgreSQL\nDatabase")`

**Validation**: Database renders on the right side or clearly separate from actors

**Estimated effort**: 5 minutes

---

### 6. Create User flow edges (green)

**File**: `src/diagram_gen/generator.py` (after all nodes created)

**Actions**:
- [ ] User → User Interface group:
  ```python
  user >> Edge(label="Web UI", fontsize=edge_fontsize, color="#28a745") >> user_interface
  ```
- [ ] User → Query API group:
  ```python
  user >> Edge(label="Query status", fontsize=edge_fontsize, color="#28a745") >> query_api
  ```
- [ ] User Interface → Database:
  ```python
  user_interface >> Edge(fontsize=edge_fontsize, color="#6c757d") >> database
  ```
- [ ] Query API → Database:
  ```python
  query_api >> Edge(fontsize=edge_fontsize, color="#6c757d") >> database
  ```

**Validation**: Green edges visible from User to public endpoints

**Estimated effort**: 15 minutes

---

### 7. Create Admin flow edges (gold/yellow)

**File**: `src/diagram_gen/generator.py`

**Actions**:
- [ ] Admin → Auth component:
  ```python
  admin >> Edge(label="Authenticate", fontsize=edge_fontsize, color="#ffc107") >> auth
  ```
- [ ] Admin → Admin Management group:
  ```python
  admin >> Edge(label="Provision/Manage", fontsize=edge_fontsize, color="#ffc107") >> admin_mgmt
  ```
- [ ] Admin Management → Database:
  ```python
  admin_mgmt >> Edge(fontsize=edge_fontsize, color="#6c757d") >> database
  ```

**Validation**: Gold edges visible showing authenticated access through auth component

**Estimated effort**: 15 minutes

---

### 8. Create Client VM flow edges (blue)

**File**: `src/diagram_gen/generator.py`

**Actions**:
- [ ] Client VM → VM Callbacks group:
  ```python
  client_vm >> Edge(label="Status/Metrics\n(hostname validated)", fontsize=edge_fontsize, color="#007bff") >> vm_callbacks
  ```
- [ ] VM Callbacks → Database:
  ```python
  vm_callbacks >> Edge(fontsize=edge_fontsize, color="#6c757d") >> database
  ```

**Validation**: Blue edges visible showing validated VM callbacks

**Estimated effort**: 10 minutes

---

### 9. Create Lambda flow edges (purple)

**File**: `src/diagram_gen/generator.py`

**Actions**:
- [ ] Lambda → Lambda Callback group:
  ```python
  lambda_processor >> Edge(label="CloudWatch logs", fontsize=edge_fontsize, color="#6f42c1") >> lambda_callback
  ```
- [ ] Lambda Callback → Database:
  ```python
  lambda_callback >> Edge(fontsize=edge_fontsize, color="#6c757d") >> database
  ```

**Validation**: Purple edges visible showing internal log processing

**Estimated effort**: 10 minutes

---

### 10. Update success message with documentation reference

**File**: `src/diagram_gen/generator.py` (end of method)

**Actions**:
- [ ] Replace simple print statement with:
  ```python
  print(f"API architecture diagram saved to {output_path}")
  print("See analysis/api-architecture-analysis.md for complete endpoint documentation (22 endpoints)")
  ```

**Validation**: Success message includes reference to analysis doc

**Estimated effort**: 5 minutes

---

### 11. Test diagram generation with all font presets

**Command line testing**

**Actions**:
- [ ] Generate with poster preset (primary use case):
  ```bash
  cd c:/repos/lablink-paper-figures
  uv run python scripts/plotting/generate_architecture_diagram.py \
    --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
    --diagram-type api-architecture \
    --fontsize-preset poster
  ```
- [ ] Generate with paper preset:
  ```bash
  uv run python scripts/plotting/generate_architecture_diagram.py \
    --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
    --diagram-type api-architecture \
    --fontsize-preset paper
  ```
- [ ] Generate with presentation preset:
  ```bash
  uv run python scripts/plotting/generate_architecture_diagram.py \
    --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
    --diagram-type api-architecture \
    --fontsize-preset presentation
  ```

**Validation criteria** for all three outputs:
- ✅ Image width > height (horizontal layout)
- ✅ All 4 actors visible on left
- ✅ Allocator cluster in center
- ✅ All 5 API groups visible with endpoint counts summing to 22
- ✅ Database visible (right side or within Allocator)
- ✅ All edges rendered (no broken/missing arrows)
- ✅ Color-coded edges distinguishable
- ✅ All text readable at 100% zoom
- ✅ Security indicators visible (auth component, validation labels)

**Estimated effort**: 30 minutes (includes review and adjustments)

---

### 12. Visual review and refinement

**Manual review by user**

**Actions**:
- [ ] User reviews generated diagrams
- [ ] Check readability of endpoint counts
- [ ] Check clarity of security levels (public vs authenticated vs validated)
- [ ] Verify no overlapping text or edges
- [ ] Confirm publication quality

**If issues found**:
- [ ] Adjust spacing (nodesep, ranksep in graph_attr)
- [ ] Adjust edge routing (add minlen parameters if needed)
- [ ] Adjust label positions (labeldistance, labelangle)
- [ ] Adjust API group box styling (fillcolor, fontsize)
- [ ] Regenerate and review again

**Validation**: User approves diagram for publication

**Estimated effort**: 30-60 minutes (iterative)

---

### 13. Update existing run folders (optional)

**Post-implementation**

**Actions**:
- [ ] Regenerate all diagrams in new timestamped run folder for complete set:
  ```bash
  uv run python scripts/plotting/generate_architecture_diagram.py \
    --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
    --diagram-type all \
    --fontsize-preset poster
  ```
- [ ] User reviews complete diagram set including new API architecture

**Validation**: All 11 diagrams generate successfully with new API architecture diagram

**Estimated effort**: 15 minutes

---

## Summary

**Total estimated effort**: 3-4 hours

**Dependencies**: None (all tasks are in sequence within same method)

**Parallelizable work**: None (diagram generation is inherently sequential)

**Critical path**: Tasks 1-10 must be completed in order, then tasks 11-13 for validation

**Rollback strategy**: If new design fails, can revert to previous commit (7b0591d) which had working (though problematic) endpoint-by-endpoint approach