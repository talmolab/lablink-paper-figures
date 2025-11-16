# Tasks: Fix Diagram Quality Issues

## Implementation Tasks

Based on actual visual inspection of `figures/run_20251115_203338/diagrams/`.

---

### Priority 1: Critical Fixes

#### Task 1.1: Fix missing database edges in API architecture

**File**: `src/diagram_gen/generator.py`
**Method**: `build_api_architecture_diagram()` (lines 976-1123)
**Issue**: 5 edges to database defined but not rendering

**Actions** (try in order):
- [ ] **Option A**: Increase intra-cluster spacing
  ```python
  # After line 1020 (after creating edge_fontsize)
  # Override spacing for intra-cluster database edges
  graph_attr["nodesep"] = "1.5"  # Increase node separation
  graph_attr["ranksep"] = "1.5"  # Increase rank separation
  ```

- [ ] **Option B**: Add constraint=false to database edges
  ```python
  # Lines 1076, 1078, 1086, 1094, 1109
  # Change from:
  user_interface >> Edge(fontsize=edge_fontsize, color="#6c757d") >> database
  # To:
  user_interface >> Edge(fontsize=edge_fontsize, color="#6c757d", constraint="false") >> database
  ```

- [ ] **Option C**: Move database outside Allocator cluster
  ```python
  # Move database definition (lines 1038-1039) outside the "with Cluster" block
  # This makes it a separate external node
  ```

**Validation**:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type api-architecture \
  --fontsize-preset poster
```

**Expected**: All 5 gray arrows from API groups to database visible

**Estimated Effort**: 1-2 hours (may need experimentation)

---

#### Task 1.2: Fix detailed architecture - Add preset support and fix edges

**File**: `src/diagram_gen/generator.py`
**Method**: `build_detailed_diagram()` (lines 317-433)

**Actions**:
- [ ] Add `fontsize_preset` parameter to function signature (line 318):
  ```python
  def build_detailed_diagram(
      self,
      output_path: Path,
      format: str = "png",
      dpi: int = 300,
      fontsize_preset: str = "paper",  # ADD THIS
  ) -> None:
  ```

- [ ] Replace hardcoded attrs (lines 327-350) with preset system:
  ```python
  graph_attr = self._create_graph_attr(dpi=dpi, fontsize_preset=fontsize_preset)
  graph_attr["nodesep"] = "1.2"  # Override for dense clusters
  graph_attr["ranksep"] = "2.0"  # Override for multiple layers
  node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
  edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)
  edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])
  ```

- [ ] Remove hardcoded dictionaries for graph_attr, node_attr, edge_attr
- [ ] Update Diagram instantiation to use new attrs

**Validation**:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type architecture-detailed \
  --fontsize-preset paper
```

**Expected**: All edges render, no text overlap, supports both presets

**Estimated Effort**: 2-3 hours

---

#### Task 1.3: Fix VM provisioning - Use Python icon instead of Flask

**File**: `src/diagram_gen/generator.py`
**Method**: `build_vm_provisioning_diagram()` (lines 481-590)

**Actions**:
- [ ] Add Python import at top of method (after line 490):
  ```python
  from diagrams.programming.language import Python
  ```

- [ ] Replace Blank fallback with Python icon (lines 554-559):
  ```python
  # Phase 3: Application ready with Python fallback
  app_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "application.png"
  if app_icon_path.exists():
      phase3 = Custom("3. Application
Software ready", str(app_icon_path))
  else:
      phase3 = Python("3. Application
Software ready")  # CHANGE: Python instead of Blank
  ```

**Validation**:
```bash
uv run python scripts/plotting/generate_architecture_diagram.py \
  --terraform-dir c:/repos/lablink-template/lablink-infrastructure \
  --diagram-type vm-provisioning \
  --fontsize-preset poster
```

**Expected**: Shows Python icon, NOT Flask icon

**Estimated Effort**: 30 minutes

---

### Priority 2: Quality Improvements

#### Task 2.1: Increase CRD connection spacing (optional)

**File**: `src/diagram_gen/generator.py`
**Method**: `build_crd_connection_diagram()` (lines 592-786)

**Actions**:
- [ ] Add conditional spacing override for poster preset (after line 640):
  ```python
  # Override spacing for poster preset to prevent label overlap
  if fontsize_preset == "poster":
      graph_attr["ranksep"] = "3.0"  # Increase from default 2.5
      graph_attr["sep"] = "+30,30"   # Adjust edge clearance
  ```

**Validation**: Generate with poster preset, check for label overlap

**Estimated Effort**: 15 minutes

---

#### Task 2.2: Refactor network-flow to use preset system

**File**: `src/diagram_gen/generator.py`
**Method**: `build_network_flow_diagram()` (lines 435-479)

**Actions**:
- [ ] Add `fontsize_preset` parameter to function signature
- [ ] Replace hardcoded graph_attr with `self._create_graph_attr(...)`
- [ ] Replace hardcoded node_attr with `self._create_node_attr(...)`
- [ ] Replace hardcoded edge_attr with `self._create_edge_attr(...)`

**Estimated Effort**: 20 minutes

---

#### Task 2.3: Refactor CI/CD workflow to use preset system

**File**: `src/diagram_gen/generator.py`
**Method**: `build_cicd_workflow_diagram()` (lines 865-974)

**Actions**:
- [ ] Add `fontsize_preset` parameter
- [ ] Replace hardcoded attrs (lines 891, 902, 907) with helper methods

**Estimated Effort**: 20 minutes

---

#### Task 2.4: Refactor network-flow-enhanced to use preset system

**File**: `src/diagram_gen/generator.py`
**Method**: `build_network_flow_enhanced_diagram()` (lines 1125-1238)

**Actions**:
- [ ] Add `fontsize_preset` parameter
- [ ] Replace hardcoded attrs with helper methods

**Estimated Effort**: 20 minutes

---

#### Task 2.5: Refactor monitoring diagram to use preset system

**File**: `src/diagram_gen/generator.py`
**Method**: `build_monitoring_diagram()` (lines 1240-1329)

**Actions**:
- [ ] Add `fontsize_preset` parameter
- [ ] Replace hardcoded attrs with helper methods

**Estimated Effort**: 20 minutes

---

#### Task 2.6: Refactor data-collection diagram to use preset system

**File**: `src/diagram_gen/generator.py`
**Method**: `build_data_collection_diagram()` (lines 1331-1416)

**Actions**:
- [ ] Add `fontsize_preset` parameter
- [ ] Replace hardcoded attrs with helper methods

**Estimated Effort**: 20 minutes

---

### Priority 3: Validation and Documentation

#### Task 3.1: Generate complete diagram set for visual review

**Actions**:
- [ ] Generate all diagrams with poster preset
- [ ] Generate all diagrams with paper preset
- [ ] Visual inspection of all 22 diagrams (11 × 2 presets)

**Validation Checklist**:
- [ ] API architecture: 5 database edges visible
- [ ] Detailed architecture: All edges render, no overlap
- [ ] VM provisioning: Python icon (not Flask)
- [ ] CRD connection: No label overlap
- [ ] All diagrams: Both presets work

**Estimated Effort**: 1 hour

---

#### Task 3.2: Update analysis documentation

**File**: `analysis/graphviz-settings-reference.md`

**Actions**:
- [ ] Add note about intra-cluster edge routing issues (if applicable after Task 1.1)
- [ ] Document spacing recommendations for complex diagrams
- [ ] Add troubleshooting section for missing edges

**Estimated Effort**: 30 minutes

---

## Summary

**Total Estimated Effort**: 6-8 hours

**Breakdown by Priority**:
- Priority 1 (Critical): 3.5-5.5 hours (3 tasks)
- Priority 2 (Quality): 2 hours (6 tasks)
- Priority 3 (Validation): 1.5 hours (2 tasks)

**Dependencies**:
- Task 1.1 may require experimentation (try options A, B, C in order)
- Tasks 2.2-2.6 can run in parallel (all same pattern)
- Task 3.1 depends on all implementation tasks
- Task 3.2 can run after Task 1.1 is complete

**Critical Path**: Priority 1 → Priority 2 → Priority 3

**Success Criteria**:
- ✅ All 5 database edges visible in API architecture
- ✅ Detailed architecture: all edges render, supports both presets
- ✅ VM provisioning: shows Python icon
- ✅ All 11 diagrams support poster and paper presets
- ✅ No text overlap, no broken arrows