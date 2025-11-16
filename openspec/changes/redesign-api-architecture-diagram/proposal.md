# Proposal: Redesign API Architecture Diagram

## Problem Statement

The current API architecture diagram (`lablink-api-architecture.png`) has severe rendering issues that make it unusable for publication:

1. **Vertical column layout**: Despite `direction="LR"` setting, the diagram renders as an extremely long vertical column due to the Python `diagrams` library's cluster nesting behavior (6 nested clusters override the LR direction)
2. **Broken/compressed arrows**: Edges are extremely short and vertically compressed, making data flows hard to follow
3. **Too many individual nodes**: Showing 18+ individual endpoint nodes creates visual clutter and poor space utilization
4. **Not industry standard**: Professional API documentation (Stripe, AWS, Kong) uses actor-centric or layered views, not endpoint-by-endpoint node graphs

The diagram fails to communicate the architecture effectively and does not meet publication quality standards.

## Proposed Solution

Redesign the API architecture diagram using an **actor-centric flow pattern** that:

1. Shows 4 external actors (User, Admin, Client VM, Lambda) interacting with the Allocator infrastructure
2. Replaces 18+ individual endpoint nodes with 5 grouped API categories within the Allocator
3. Clearly indicates security boundaries (Public, Authenticated, Validated)
4. Uses color coding to distinguish access levels and authentication requirements
5. Follows industry best practices for visualizing REST APIs with 20+ endpoints

## Key Changes

### Visual Structure
- **Before**: 18+ endpoint nodes + 6 nested clusters → vertical column
- **After**: 4 actors + Allocator cluster (with 5 functional groups) + database → horizontal flow

### Security Visibility
- **Public endpoints**: Clear visual indication (green)
- **Authenticated endpoints**: HTTP Basic Auth required (yellow/gold with lock icon)
- **Validated endpoints**: VM hostname validation (blue with validation indicator)

### Diagram Elements
- **4 External actor nodes**: User, Admin, Client VM, Lambda (left side)
- **1 Allocator cluster** (center): Contains:
  - Flask API server node (22 routes total)
  - 5 Functional API group boxes (not individual endpoint nodes):
    - User Interface (2 endpoints) - Public
    - Admin Management (10 endpoints) - @auth.login_required
    - VM-to-Allocator API (5 endpoints) - Public with hostname validation
    - Query API (4 endpoints) - Public
    - Lambda Callback (1 endpoint) - Internal validation
  - HTTP Basic Auth security component
- **1 Database node**: PostgreSQL (right side or within Allocator)
- **Color-coded edges**: Show which actors access which API groups

## Benefits

1. **Readable**: Horizontal flow, clear actor interactions
2. **Scalable**: Works for 10 or 100 endpoints
3. **Industry standard**: Matches how Stripe, AWS, Google document APIs
4. **Publication quality**: Clean, professional appearance
5. **Security clarity**: Visual distinction between public, authenticated, and validated access
6. **Maintainable**: Easy to update as API evolves
7. **Architectural clarity**: Shows Allocator as central infrastructure component

## Scope

This change replaces the `build_api_architecture_diagram()` method in `src/diagram_gen/generator.py` with a new implementation using the actor-centric pattern.

The existing comprehensive endpoint documentation in `analysis/api-architecture-analysis.md` remains as the authoritative reference for all 22 endpoints.

## Success Criteria

1. Diagram renders horizontally (LR direction actually works)
2. All edges visible and properly routed
3. Security levels (public, authenticated, validated) clearly indicated with visual markers
4. Allocator shown as central infrastructure component
5. Fits on single page without extreme scaling
6. Passes user review for publication quality
7. Generates successfully with poster, paper, and presentation font presets

## Related Work

- Analysis document: `analysis/api-architecture-analysis.md` (comprehensive endpoint inventory)
- Related change: `correct-crd-workflow` (similar diagram redesign)
