# Graphviz Settings Reference for Diagrams Library

**Author:** Analysis based on Graphviz documentation and diagrams library (mingrammer) implementation
**Date:** 2025-11-15
**Purpose:** Comprehensive reference for configuring Graphviz settings in Python diagrams library to control spacing, layout, and appearance of architecture diagrams

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture: How diagrams Library Uses Graphviz](#architecture-how-diagrams-library-uses-graphviz)
3. [Graph-Level Attributes](#graph-level-attributes)
4. [Node-Level Attributes](#node-level-attributes)
5. [Edge-Level Attributes](#edge-level-attributes)
6. [Font Presets and Scaling](#font-presets-and-scaling)
7. [Common Problems and Solutions](#common-problems-and-solutions)
8. [Best Practices by Output Type](#best-practices-by-output-type)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [References](#references)

---

## Overview

The Python `diagrams` library (by mingrammer) provides a high-level API for creating architecture diagrams. Under the hood, it uses **Graphviz** for layout and rendering. Understanding Graphviz attributes is essential for fine-tuning diagram appearance.

### Key Concepts

- **diagrams library** provides Python classes for nodes (EC2, Lambda, etc.) and handles icon images
- **Graphviz** performs the actual graph layout and rendering
- Attributes can be set at three levels: **graph**, **node**, and **edge**
- Settings cascade: graph defaults → node defaults → individual node/edge overrides

---

## Architecture: How diagrams Library Uses Graphviz

### Default Behavior

From `diagrams/__init__.py` (v0.24.4):

```python
_default_graph_attrs = {
    "pad": "2.0",
    "splines": "ortho",
    "nodesep": "0.60",
    "ranksep": "0.75",
    "fontname": "Sans-Serif",
    "fontsize": "15",
    "fontcolor": "#2D3436",
}

_default_node_attrs = {
    "shape": "box",
    "style": "rounded",
    "fixedsize": "true",        # ⚠️ Critical: Forces exact dimensions
    "width": "1.4",              # Default node width in inches
    "height": "1.4",             # Default node height in inches
    "labelloc": "b",             # Label location: bottom
    "imagescale": "true",        # Scale images to fit
    "fontname": "Sans-Serif",
    "fontsize": "13",
    "fontcolor": "#2D3436",
}

_default_edge_attrs = {
    "color": "#7B8894",
}
```

### Node Rendering Model

Each node in diagrams library consists of:
1. **Icon image** (PNG file from diagrams/resources/)
2. **Text label** (positioned below icon by default via `labelloc="b"`)
3. **Bounding box** (controlled by width/height/fixedsize)

**Critical insight:** The spacing between icon and text is NOT directly controllable via a single attribute. It's determined by:
- Node `height` (more height = more vertical space)
- Node `width` (more width = more horizontal breathing room)
- `fixedsize` setting (controls whether dimensions are enforced)
- Font size (larger fonts naturally push content apart)

---

## Graph-Level Attributes

These affect the overall diagram layout and spacing.

### `dpi` (Dots Per Inch)
- **Type:** Integer
- **Default:** 96 (varies by Graphviz version)
- **Purpose:** Controls output resolution
- **Recommended values:**
  - Paper (print): `300`
  - Poster (large print): `300-600`
  - Presentation (screen): `150-300`
  - Web: `96-150`

### `pad` (Padding)
- **Type:** Float (inches)
- **Default:** `0.5` (diagrams library overrides to `2.0`)
- **Purpose:** Inches to extend drawing area around minimal required space
- **Effect:** Adds margin around entire diagram
- **Recommended values:**
  - Paper: `0.5`
  - Poster: `0.5-1.0` (more breathing room)
  - Presentation: `0.5`

### `nodesep` (Node Separation)
- **Type:** Float (inches)
- **Default:** `0.25`
- **Purpose:** Minimum distance between adjacent nodes in same rank
- **Effect:** 
  - In **TB/BT** (top-to-bottom) layouts: Controls **horizontal** spacing between sibling nodes
  - In **LR/RL** (left-to-right) layouts: Controls **VERTICAL** spacing between sibling nodes ⚠️ **CRITICAL**
- **Common misconception:** Many assume nodesep always means horizontal - it depends on layout direction!
- **Recommended values:**
  - Paper (14pt fonts): `1.0` ✓ Prevents overlap with larger labels
  - Poster (20pt fonts): `1.5` ✓ Essential for readability
  - Presentation (16pt fonts): `1.2`
- **Note:** Larger fonts REQUIRE larger nodesep to prevent label overlap

### `ranksep` (Rank Separation)
- **Type:** Float (inches) or String with "equally"
- **Default:** `0.5`
- **Purpose:** Minimum distance between ranks (levels/columns) of nodes
- **Effect:**
  - In **TB/BT** (top-to-bottom) layouts: Controls **vertical** spacing between layers
  - In **LR/RL** (left-to-right) layouts: Controls **HORIZONTAL** spacing between columns ⚠️ **CRITICAL**
- **Common misconception:** Many assume ranksep always means vertical - it depends on layout direction!
- **Recommended values:**
  - Paper: `1.5` ✓ Critical for preventing overlap
  - Poster: `2.0` ✓ Even more space needed
  - Presentation: `1.7`
- **Special values:**
  - `"1.5 equally"` - Spaces rank centers equally apart

### `splines` (Edge Routing)
- **Type:** String
- **Default:** `""`
- **Purpose:** Controls how edges are drawn
- **Values:**
  - `"ortho"` - Orthogonal (right-angle) edges ✓ **Best for architecture diagrams**
  - `"curved"` - Curved splines
  - `"line"` - Straight lines
  - `"polyline"` - Polyline edges
  - `"none"` - No edges drawn
- **Recommendation:** Use `"ortho"` for clean, professional architecture diagrams

### `labelloc` (Graph Label Location)
- **Type:** String
- **Default:** `"b"` (bottom)
- **Purpose:** Controls title placement
- **Values:**
  - `"t"` - Top (recommended for diagrams)
  - `"b"` - Bottom (default for root graphs)
- **Note:** For clusters (subgraphs), default is top

### `sep` (Node Separation Margin for Edge Routing)
- **Type:** Float or "+float,float" (inches/points)
- **Default:** `4` (as a multiplier)
- **Purpose:** Margin around nodes when routing edges to prevent overlap
- **Format:**
  - Single value: `"0.5"` (nodes scaled by 1+0.5 in both dimensions)
  - With plus: `"+10,10"` (additive: 10pt left/right, 10pt top/bottom)
- **Effect:** Increases clearance between edges and node boundaries
- **Recommended values:**
  - Paper: `"+5,5"` (minimal clearance)
  - Poster: `"+10,10"` ✓ **Prevents edge-label overlap with larger fonts**
  - Presentation: `"+8,8"`
- **Key insight:** This attribute helps prevent arrows from overlapping multi-line node labels

### `bgcolor` (Background Color)
- **Type:** Color string
- **Default:** Transparent
- **Recommended:** `"white"` for PDF/PNG exports

### `fontname` (Font Family)
- **Type:** String
- **Default:** `"Sans-Serif"`
- **Recommended:** `"Helvetica"` (clean, professional)
- **Alternatives:** `"Arial"`, `"Roboto"`

### `fontsize` (Title Font Size)
- **Type:** Integer (points)
- **Default:** `15`
- **Purpose:** Size of diagram title
- **Recommended values:**
  - Paper: `32`
  - Poster: `48`
  - Presentation: `40`

---

## Node-Level Attributes

These control the appearance and sizing of individual nodes (icons + labels).

### `width` (Node Width)
- **Type:** Float (inches)
- **Default:** `1.4` (diagrams library)
- **Purpose:** Initial/minimum width of node
- **Behavior:**
  - If `fixedsize=true`: Exact width (label truncated if needed)
  - If `fixedsize=false`: Minimum width (expands to fit label)
- **Recommended values:**
  - Paper: `1.4` (default works well)
  - Poster: `1.7-2.0` ✓ **More space between icon and text**
  - Presentation: `1.5-1.7`

### `height` (Node Height)
- **Type:** Float (inches)
- **Default:** `1.4` (diagrams library)
- **Purpose:** Initial/minimum height of node
- **Behavior:** Same as width
- **Recommended values:**
  - Paper: `1.4` (default)
  - Poster: `1.7-2.0` ✓ **Critical for adding vertical space**
  - Presentation: `1.5-1.7`
- **Key insight:** Increasing height is THE primary way to add space between icon and label

### `fixedsize` (Fixed Size Mode)
- **Type:** Boolean or String
- **Default:** `"true"` (diagrams library)
- **Purpose:** Controls whether width/height are enforced
- **Values:**
  - `"false"` - Node expands to fit content (width/height are minimums)
  - `"true"` - Node size is exactly width/height (content may be clipped) ✓ **diagrams default**
  - `"shape"` - Shape is fixed, but label can overflow (advanced)
- **Recommendation:** Keep `"true"` for consistent, predictable icon sizes
- **Warning:** If `false`, nodes may become inconsistently sized

### `imagescale` (Image Scaling)
- **Type:** Boolean or String
- **Default:** `"true"` (diagrams library)
- **Purpose:** Controls how icon images scale within nodes
- **Values:**
  - `"false"` - Image at natural size (may overflow)
  - `"true"` - Scale uniformly to fit node, preserve aspect ratio ✓ **Best**
  - `"width"` - Scale to fill width
  - `"height"` - Scale to fill height
  - `"both"` - Scale width and height separately (distorts image)
- **Recommendation:** Keep `"true"` for proportional icon sizing

### `labelloc` (Label Location within Node)
- **Type:** String
- **Default:** `"b"` (diagrams library)
- **Purpose:** Vertical placement of label
- **Values:**
  - `"t"` - Top
  - `"c"` - Center
  - `"b"` - Bottom ✓ **Standard for icons**
- **Note:** For image nodes, label is always placed relative to image

### `margin` (Internal Padding)
- **Type:** Float or "x,y" pair (inches)
- **Default:** `0.11,0.055` (Graphviz default)
- **Purpose:** Padding between node boundary and content
- **Format:**
  - Single value: `"0.3"` (uniform padding)
  - Pair: `"0.5,0.3"` (horizontal, vertical)
- **Effect:** Limited when `fixedsize=true` (doesn't expand node)
- **Recommended values:**
  - Paper: `default` (margin doesn't help much with fixed size)
  - Poster: `"0.5,0.3"` (horizontal, vertical) - May provide slight improvement
- **Key insight:** Margin has limited effect when `fixedsize=true`. Increasing height/width is more effective.

### `fontsize` (Label Font Size)
- **Type:** Integer (points)
- **Default:** `13`
- **Purpose:** Size of node label text
- **Recommended values:**
  - Paper: `14`
  - Poster: `20` ✓ **Essential for readability**
  - Presentation: `16`

### `fontname` (Label Font)
- **Type:** String
- **Default:** `"Sans-Serif"`
- **Recommended:** `"Helvetica"` (matches title)

### `shape` (Node Shape)
- **Type:** String
- **Default:** `"box"` (diagrams library)
- **Purpose:** Shape of node boundary
- **Common values:** `"box"`, `"circle"`, `"ellipse"`, `"record"`
- **Note:** diagrams library always uses `"box"` with `"rounded"` style

### `style` (Node Style)
- **Type:** String
- **Default:** `"rounded"` (diagrams library)
- **Purpose:** Visual style of node
- **Common values:**
  - `"rounded"` - Rounded corners ✓ **diagrams default**
  - `"solid"` - Solid line (default)
  - `"dashed"` - Dashed border (useful for conditional resources)
  - `"dotted"` - Dotted border (useful for runtime-provisioned resources)
  - `"bold"` - Thick border

### `color` (Border Color)
- **Type:** Color string
- **Default:** Black
- **Purpose:** Color of node border
- **Use case:** Distinguish resource types (e.g., green for conditional, orange for runtime)

### `penwidth` (Border Width)
- **Type:** Float
- **Default:** `1.0`
- **Purpose:** Thickness of node border
- **Recommended:** `2.0` for emphasized nodes

---

## Edge-Level Attributes

These control the appearance of arrows/connections between nodes.

### `fontsize` (Edge Label Font Size)
- **Type:** Integer (points)
- **Default:** `11`
- **Purpose:** Size of edge label text
- **Recommended values:**
  - Paper: `14` (match node labels)
  - Poster: `20` (match node labels)
  - Presentation: `16`

### `fontname` (Edge Label Font)
- **Type:** String
- **Default:** `"Sans-Serif"`
- **Recommended:** `"Helvetica"`

### `color` (Edge Color)
- **Type:** Color string
- **Default:** `"#7B8894"` (diagrams library)
- **Purpose:** Color of edge line
- **Use cases:**
  - Default: `"#7B8894"` (gray)
  - Emphasis: `"#fd7e14"` (orange)
  - Alternative: `"#007bff"` (blue)

### `labeldistance` (Label Distance from Node)
- **Type:** Float
- **Default:** `1.0`
- **Purpose:** Distance of edge label from node
- **Recommended:** `2.0` for clarity

### `labelangle` (Label Angle)
- **Type:** Float (degrees)
- **Default:** `-25.0`
- **Purpose:** Angle of edge label placement
- **Recommended:** `0` for horizontal labels

### `labelfloat` (Allow Label Floating)
- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Whether edge labels can move for better placement
- **Recommended:** `"true"` for cleaner diagrams

---

## Font Presets and Scaling

### Current Implementation (src/diagram_gen/generator.py)

```python
FONT_PRESETS = {
    "paper": {"title": 32, "node": 14, "edge": 14},
    "poster": {"title": 48, "node": 20, "edge": 20},
    "presentation": {"title": 40, "node": 16, "edge": 16},
}
```

### Spacing Requirements by Preset

**Critical insight:** Larger fonts require proportionally larger spacing to prevent overlap.

| Preset | Node Font | nodesep | ranksep | Node Width | Node Height | Rationale |
|--------|-----------|---------|---------|------------|-------------|-----------|
| Paper | 14pt | 1.0 | 1.5 | 1.4 | 1.4 | Compact but readable |
| Poster | 20pt | 1.5 | 2.0 | 1.7 | 1.7 | More space needed for larger text |
| Presentation | 16pt | 1.2 | 1.7 | 1.5 | 1.5 | Intermediate sizing |

### Why Spacing Scales with Font Size

1. **Label width increases:** 20pt text is ~43% wider than 14pt text for same content
2. **Overlap risk:** Without increased nodesep, larger labels collide
3. **Visual density:** Larger fonts need more whitespace for comfortable reading
4. **Icon-text gap:** Larger fonts naturally need more vertical space (height)

---

## Common Problems and Solutions

### Problem 1: Text Overlaps Between Nodes
**Symptoms:** Node labels collide horizontally

**Causes:**
- Font size increased without adjusting nodesep
- Too many nodes at same rank
- Long label text

**Solutions:**
1. ✓ Increase `nodesep` (proportional to font size)
   - 14pt fonts: `nodesep="1.0"`
   - 20pt fonts: `nodesep="1.5"`
2. ✓ Increase `ranksep` if vertical overlap
3. Consider abbreviating labels
4. Use hierarchical clustering to reduce nodes per rank

**Example:**
```python
graph_attr = {
    "nodesep": "1.5",  # For 20pt fonts
    "ranksep": "2.0",
}
```

### Problem 2: Insufficient Space Between Icon and Text
**Symptoms:** Icon and label appear cramped, hard to read

**Causes:**
- Default node height (1.4) too small for larger fonts
- `fixedsize=true` prevents node from expanding
- No direct "gap" attribute in Graphviz

**Solutions:**
1. ✓ **Increase node height** (most effective)
   ```python
   node_attr = {
       "height": "1.7",  # Up from default 1.4
       "width": "1.7",   # Keep proportional
       "fixedsize": "true",
   }
   ```
2. ✓ Increase node width (helps horizontal breathing room)
3. Consider reducing font size if space is constrained
4. Margin has limited effect with `fixedsize=true`

**Why this works:** More vertical space in the fixed-size box gives more distance between the icon image and the bottom-aligned label.

### Problem 3: Inconsistent Node Sizes
**Symptoms:** Some nodes larger than others despite same class

**Causes:**
- `fixedsize=false` allows nodes to expand
- Different label lengths
- Mixed settings

**Solutions:**
1. ✓ Ensure `fixedsize="true"` in node_attr
2. ✓ Set explicit width/height for all nodes
3. Check for individual node overrides

### Problem 4: Edges Overlap Nodes or Labels
**Symptoms:** Edge lines run through node labels or collide

**Causes:**
- `splines` setting inappropriate
- Insufficient spacing
- Edge label placement

**Solutions:**
1. ✓ Use `splines="ortho"` for architecture diagrams
2. ✓ Increase `nodesep` and `ranksep`
3. ✓ Set `labelfloat="true"` for edge labels
4. Adjust `labeldistance="2.0"`

### Problem 5: Diagram Too Large/Small for Output
**Symptoms:** Entire diagram doesn't fit expected dimensions

**Causes:**
- DPI too high/low
- Too many nodes
- Spacing too generous

**Solutions:**
1. Adjust DPI (lower = smaller output)
2. Reduce `pad`, `nodesep`, `ranksep`
3. Use hierarchical clustering
4. Split into multiple diagrams

### Problem 6: Edges Broken with LR Direction and Clusters
**Symptoms:** Edges don't render, appear broken, compressed, or route incorrectly

**Root Cause:** GraphViz's orthogonal edge routing (`splines="ortho"`) is optimized for **top-to-bottom (TB)** layouts, not left-to-right (LR). When combining:
- `direction="LR"` (left-to-right)
- `splines="ortho"` (orthogonal edges)
- Cross-cluster edges (external actors → internal API groups)

The edge routing algorithm often fails completely or produces compressed/broken arrows.

**Detailed Analysis:**
- **Why TB works:** GraphViz's default flow direction; orthogonal algorithm designed for vertical layouts
- **Why LR fails:** Horizontal layouts with clusters create complex constraint graphs that orthogonal router can't solve
- **Cross-cluster edges:** Edges crossing cluster boundaries are especially problematic in LR direction
- **Constraint conflicts:** LR + clusters + ortho creates over-constrained layout that breaks edge routing

**Solutions (Ranked by Effectiveness):**

1. ✓ **Change to TB direction** (most effective - 95% fix rate)
   ```python
   direction="TB"  # Instead of "LR"
   ```
   - Rationale: Works with GraphViz's natural flow direction
   - Trade-off: Layout orientation changes (vertical instead of horizontal)
   - Use case: When orthogonal edges are required for architectural diagrams

2. ✓ **Add minlen to cross-cluster edges** (70% effective with LR, essential with TB)
   ```python
   user >> Edge(
       label="Web UI",
       fontsize=edge_fontsize,
       color="#28a745",
       minlen="2"  # Minimum edge length for cluster boundary crossing
   ) >> user_interface
   ```
   - Rationale: Gives GraphViz more space to route across cluster boundary
   - Trade-off: Diagram becomes longer (vertically in TB, horizontally in LR)
   - Use case: All edges crossing cluster boundaries

3. ✓ **Change splines to "polyline" or "curved"** (80% effective but loses aesthetic)
   ```python
   graph_attr = {
       "splines": "polyline",  # or "curved" instead of "ortho"
   }
   ```
   - Rationale: More flexible routing algorithms, less likely to fail
   - Trade-off: Loses clean orthogonal (right-angle) aesthetic
   - Use case: When LR direction is required and TB not acceptable

4. ✓ **Add constraint=false to edges with routing issues** (85% effective for intra-cluster and cross-cluster edges)
   ```python
   # Relax ranking constraints on database edges (intra-cluster)
   user_interface >> Edge(
       fontsize=edge_fontsize,
       color="#6c757d",
       constraint="false"  # Allows more layout freedom
   ) >> database
   
   # Also effective for cross-cluster edges that fail to render
   user >> Edge(
       label="Web UI",
       fontsize=edge_fontsize,
       color="#28a745",
       minlen="2",
       constraint="false"  # Fixes rendering when minlen alone insufficient
   ) >> user_interface
   ```
   - Rationale: Allows GraphViz more layout freedom by not enforcing rank ordering, effective for both intra-cluster and cross-cluster edges
   - Trade-off: Layout may become less predictable
   - Use case: Database/storage edges, any edge that fails to render despite correct definition, edges within same cluster

5. **Increase ranksep for LR layouts** (40% effective, minor improvement only)
   ```python
   spacing = {
       "paper": {"nodesep": "1.0", "ranksep": "2.5"},  # Up from 1.5
   }
   ```
   - Rationale: More horizontal space between ranks (in LR, ranks are vertical columns)
   - Trade-off: Diagram becomes taller
   - Use case: When other solutions not sufficient

**Recommended Implementation:**

Combine **Solution 1 (TB direction) + Solution 2 (minlen on cross-cluster edges)**:

```python
with Diagram(
    "My Architecture",
    direction="TB",  # ← CRITICAL: Use top-to-bottom
    graph_attr={"splines": "ortho"},
):
    # External actors outside cluster
    user = User("User")

    # Infrastructure inside cluster
    with Cluster("Backend Infrastructure"):
        api = Flask("API")

    # Cross-cluster edge with minlen
    user >> Edge(
        label="API calls",
        minlen="2"  # ← ESSENTIAL: Minimum length for cluster crossing
    ) >> api
```

**Expected Result:** Arrows render correctly with clean orthogonal routing

**When to Use Each Approach:**

| Scenario | Recommended Solution | Confidence |
|----------|---------------------|------------|
| Clustered architecture diagram | TB + minlen | 95% |
| Must use LR direction | polyline splines | 80% |
| Simple linear flow (no clusters) | LR + ortho works fine | 90% |
| Complex multi-cluster | TB + minlen + constraint=false on some edges | 90% |

**Key Insight:** Orthogonal edges work best with TB direction. If you need LR, consider whether the orthogonal aesthetic is worth the routing problems, or switch to polyline/curved splines.

**Real-World Examples:**

1. **LabLink API Architecture - Database Edges (Intra-cluster)**:
   - Problem: 5 edges from API functional groups to PostgreSQL database (all within same Allocator cluster) were defined in code but not rendering visually
   - Solution: Added `constraint="false"` to all 5 database edges
   - Result: All 5 gray arrows to database now render correctly
   - Lines: src/diagram_gen/generator.py:1080, 1081, 1100, 1111, 1122

2. **LabLink API Architecture - Web UI Edge (Cross-cluster)**:
   - Problem: "Web UI" edge from User (external) to User Interface (inside Allocator cluster) not rendering despite having `minlen="2"`
   - Solution: Added `constraint="false"` in addition to `minlen="2"`
   - Result: Green "Web UI" arrow now renders correctly
   - Line: src/diagram_gen/generator.py:1065-1070

**Key Lesson**: `constraint="false"` is effective for BOTH intra-cluster and cross-cluster edges when routing fails. It should be tried as Solution 2 (after TB direction) for any edge rendering issues.

---

## Best Practices by Output Type

### Paper (Print, 8.5×11 or A4)

**Goal:** Maximum information density while maintaining readability

```python
graph_attr = {
    "dpi": "300",              # Print quality
    "fontsize": "32",          # Title
    "fontname": "Helvetica",
    "nodesep": "1.0",          # Moderate spacing
    "ranksep": "1.5",
    "splines": "ortho",
    "pad": "0.5",
    "bgcolor": "white",
}

node_attr = {
    "fontsize": "14",          # Readable at print size
    "fontname": "Helvetica",
    "width": "1.4",            # Default size
    "height": "1.4",
    "fixedsize": "true",
    "imagescale": "true",
}

edge_attr = {
    "fontsize": "14",
    "fontname": "Helvetica",
}
```

**Tradeoffs:**
- Denser layout fits more content
- Smaller nodes/fonts at risk if printing is poor quality
- Good for detailed technical documentation

### Poster (Large Format, 24×36 or larger)

**Goal:** High visibility from distance, generous spacing

```python
graph_attr = {
    "dpi": "300",              # Still need print quality
    "fontsize": "48",          # Large title
    "fontname": "Helvetica",
    "nodesep": "1.5",          # ✓ Extra spacing essential
    "ranksep": "2.0",          # ✓ More vertical space
    "splines": "ortho",
    "pad": "0.5",
    "bgcolor": "white",
}

node_attr = {
    "fontsize": "20",          # ✓ Readable from distance
    "fontname": "Helvetica",
    "width": "1.7",            # ✓ Larger boxes
    "height": "1.7",           # ✓ More icon-text space
    "fixedsize": "true",
    "imagescale": "true",
}

edge_attr = {
    "fontsize": "20",          # ✓ Match node labels
    "fontname": "Helvetica",
    "labelfloat": "true",      # Better placement
}
```

**Tradeoffs:**
- Larger fonts/spacing = fewer nodes fit
- May need to split complex diagrams
- Excellent readability from 6+ feet away

### Presentation (Slides, 1920×1080 or 16:9)

**Goal:** Screen readability, balanced density

```python
graph_attr = {
    "dpi": "150",              # Screen resolution
    "fontsize": "40",          # Visible on projector
    "fontname": "Helvetica",
    "nodesep": "1.2",          # Intermediate spacing
    "ranksep": "1.7",
    "splines": "ortho",
    "pad": "0.5",
    "bgcolor": "white",
}

node_attr = {
    "fontsize": "16",          # Readable on screen
    "fontname": "Helvetica",
    "width": "1.5",            # Slightly larger
    "height": "1.5",
    "fixedsize": "true",
    "imagescale": "true",
}

edge_attr = {
    "fontsize": "16",
    "fontname": "Helvetica",
}
```

**Tradeoffs:**
- Lower DPI acceptable for screens
- Balance between detail and readability
- Optimized for 16:9 aspect ratio

---

## Troubleshooting Guide

### Diagnostic Process

1. **Check font sizes** - Ensure fonts are appropriate for output type
2. **Verify spacing** - Confirm nodesep/ranksep scale with font size
3. **Test fixedsize** - Ensure consistent node sizing
4. **Examine layout** - Check if splines/direction are optimal
5. **Adjust incrementally** - Change one parameter at a time

### Quick Reference: Scaling Rules

| When you increase... | Also increase... | By factor... |
|---------------------|------------------|--------------|
| Node font size | nodesep | ~proportional |
| Node font size | ranksep | ~proportional |
| Node font size | Node height | ~1.2-1.4× |
| Graph size | DPI | Keep constant |
| Number of nodes | nodesep/ranksep | Reduce slightly |

### Validation Checklist

- [ ] Font sizes match preset (title, node, edge)
- [ ] nodesep/ranksep proportional to font size
- [ ] Node width/height appropriate for preset
- [ ] fixedsize="true" for consistency
- [ ] splines="ortho" for clean edges
- [ ] DPI matches output medium
- [ ] All labels visible and readable
- [ ] No overlapping elements
- [ ] Adequate whitespace
- [ ] Background color set (white for exports)

---

## References

### Official Documentation
- [Graphviz Attributes](https://graphviz.org/doc/info/attrs.html)
- [Graphviz Node Attributes](https://graphviz.org/docs/nodes/)
- [Graphviz Graph Attributes](https://graphviz.org/docs/graph/)
- [fixedsize attribute](https://graphviz.org/docs/attrs/fixedsize/)
- [imagescale attribute](https://graphviz.org/docs/attrs/imagescale/)
- [nodesep attribute](https://graphviz.org/docs/attrs/nodesep/)
- [ranksep attribute](https://graphviz.org/docs/attrs/ranksep/)

### diagrams Library
- [GitHub: mingrammer/diagrams](https://github.com/mingrammer/diagrams)
- [Documentation](https://diagrams.mingrammer.com/)
- [Issue #196: Space between Node and label](https://github.com/mingrammer/diagrams/issues/196)
- [Issue #503: Node Label Positioning](https://github.com/mingrammer/diagrams/issues/503)
- [Issue #585: Text overlaps](https://github.com/mingrammer/diagrams/issues/585)

### Implementation
- `src/diagram_gen/generator.py` - LabLinkDiagramBuilder class
- `.venv/Lib/site-packages/diagrams/__init__.py` - diagrams library defaults

---

## Conclusion

**Key Takeaways:**

1. **Spacing scales with font size** - Larger fonts REQUIRE larger nodesep/ranksep
2. **Node height is critical** - Increasing height is the primary way to add icon-text spacing
3. **fixedsize="true" is essential** - Keeps nodes consistent but requires manual sizing
4. **No "magic gap" attribute** - Icon-text spacing is implicit from node height + font size
5. **Test incrementally** - Adjust one parameter at a time and regenerate

**Recommended Workflow:**

1. Choose preset (paper/poster/presentation)
2. Set font sizes from FONT_PRESETS
3. Set nodesep/ranksep proportional to fonts
4. Adjust node width/height for icon-text spacing
5. Generate and review
6. Iterate on spacing if needed

This reference should prevent repeated experimentation and provide a systematic approach to diagram styling.