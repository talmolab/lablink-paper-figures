# Add LabLink Architecture Diagram Generation

## Why

The LabLink paper requires publication-quality architecture diagrams that accurately represent the distributed system across multiple repositories. Manual diagram creation is error-prone and becomes outdated as the Terraform infrastructure evolves. We need automated diagram generation that stays synchronized with the actual infrastructure-as-code definitions in lablink-template.

## What Changes

- Add Python-based architecture diagram generation from Terraform configuration files
- Generate multiple diagram types:
  - High-level architecture diagram for main paper text
  - Detailed component diagram for supplementary materials
  - Network flow diagram showing request routing paths
- Support multiple output formats (PNG at publication DPI, SVG, PDF)
- Parse Terraform files from `C:\repos\lablink-template\lablink-infrastructure\` to extract:
  - Compute resources (EC2, Lambda)
  - Networking components (Security Groups, ALB, EIP, Route53)
  - Observability infrastructure (CloudWatch Logs)
  - IAM roles and policies
  - Client VM interactions with allocator
- Create reusable modules for Terraform parsing and diagram rendering

## Impact

- **Affected specs**: `architecture-visualization` (new capability)
- **Affected code**:
  - New: `src/terraform_parser/` - Parse .tf files and extract resource definitions
  - New: `src/diagrams/` - Diagram generation and rendering logic
  - New: `scripts/plotting/generate_architecture_diagram.py` - Main script
  - Updated: `pyproject.toml` - Add diagram library dependencies
  - New: `figures/main/lablink-architecture.png` - Main text figure
  - New: `figures/supplementary/lablink-architecture-detailed.png` - Detailed diagram
  - New: `tests/test_terraform_parser.py` - Parser tests
  - New: `tests/test_diagram_generation.py` - Diagram generation tests
- **External dependencies**: Requires read access to lablink-template repository Terraform files