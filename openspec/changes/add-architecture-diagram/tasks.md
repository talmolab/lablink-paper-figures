# Implementation Tasks

## 1. Setup and Dependencies

- [ ] 1.1 Add `diagrams` library to pyproject.toml dependencies
- [ ] 1.2 Add `pyyaml` for optional config file support
- [ ] 1.3 Run `uv sync` to install new dependencies
- [ ] 1.4 Create `src/terraform_parser/__init__.py`
- [ ] 1.5 Create `src/diagrams/__init__.py`

## 2. Terraform Parser Implementation

- [ ] 2.1 Implement `src/terraform_parser/parser.py` with `parse_terraform_file()` function
- [ ] 2.2 Add regex patterns to extract EC2 resources (instance type, AMI, tags, security groups)
- [ ] 2.3 Add regex patterns to extract networking resources (ALB, EIP, security groups, Route53)
- [ ] 2.4 Add regex patterns to extract Lambda and CloudWatch resources
- [ ] 2.5 Add regex patterns to extract IAM roles and policies
- [ ] 2.6 Implement `parse_directory()` to handle multiple .tf files
- [ ] 2.7 Create data structures to represent parsed resources and relationships
- [ ] 2.8 Add error handling for missing or malformed Terraform files

## 3. Diagram Generation Core

- [ ] 3.1 Implement `src/diagrams/generator.py` with base diagram generation logic
- [ ] 3.2 Create `LabLinkDiagramBuilder` class for constructing architecture diagrams
- [ ] 3.3 Implement component rendering for EC2 instances
- [ ] 3.4 Implement component rendering for networking (ALB, EIP, security groups)
- [ ] 3.5 Implement component rendering for Lambda functions
- [ ] 3.6 Implement component rendering for CloudWatch and logging flow
- [ ] 3.7 Implement component rendering for IAM roles (with optional visibility toggle)
- [ ] 3.8 Add component relationship/connection logic (arrows between components)

## 4. Diagram Variants

- [ ] 4.1 Implement `generate_main_diagram()` for simplified paper view
- [ ] 4.2 Implement filtering logic to hide IAM and security group details in main view
- [ ] 4.3 Implement `generate_detailed_diagram()` showing all components
- [ ] 4.4 Implement `generate_network_flow_diagram()` focusing on request routing
- [ ] 4.5 Add consistent styling and layout configuration across all variants

## 5. Output and Export

- [ ] 5.1 Implement PNG export at configurable DPI (default 300)
- [ ] 5.2 Implement SVG export for vector graphics
- [ ] 5.3 Implement PDF export option
- [ ] 5.4 Add output directory handling (create if doesn't exist)
- [ ] 5.5 Save main diagrams to `figures/main/`
- [ ] 5.6 Save detailed diagrams to `figures/supplementary/`
- [ ] 5.7 Add metadata annotation (source Terraform path, generation timestamp)

## 6. Command-Line Script

- [ ] 6.1 Create `scripts/plotting/generate_architecture_diagram.py`
- [ ] 6.2 Add argparse configuration for CLI arguments:
  - [ ] `--terraform-dir` (path to Terraform files)
  - [ ] `--output-dir` (where to save diagrams)
  - [ ] `--diagram-type` (main, detailed, network-flow, or all)
  - [ ] `--format` (png, svg, pdf, or all)
  - [ ] `--dpi` (resolution for PNG output)
- [ ] 6.3 Add environment variable fallback for terraform-dir
- [ ] 6.4 Implement main execution flow: parse → generate → export
- [ ] 6.5 Add progress logging and error reporting

## 7. Testing

- [ ] 7.1 Create `tests/test_terraform_parser.py`
- [ ] 7.2 Add test for parsing EC2 instance resources
- [ ] 7.3 Add test for parsing networking resources
- [ ] 7.4 Add test for parsing Lambda and CloudWatch resources
- [ ] 7.5 Add test for error handling with missing files
- [ ] 7.6 Create `tests/test_diagram_generation.py`
- [ ] 7.7 Add test for main diagram generation (verify output file created)
- [ ] 7.8 Add test for detailed diagram generation
- [ ] 7.9 Add test for network flow diagram generation
- [ ] 7.10 Add test for multi-format export
- [ ] 7.11 Run `uv run pytest` and ensure all tests pass

## 8. Integration and Documentation

- [ ] 8.1 Test script with actual lablink-template Terraform files
- [ ] 8.2 Verify diagram output meets publication quality standards
- [ ] 8.3 Update `.gitignore` to track generated diagrams (don't ignore figures/)
- [ ] 8.4 Add usage instructions to README.md
- [ ] 8.5 Document configuration options and customization
- [ ] 8.6 Run `ruff check .` and `ruff format .` to ensure code quality
- [ ] 8.7 Create example diagram generation workflow documentation

## 9. Validation

- [ ] 9.1 Generate all diagram variants from lablink-template infrastructure
- [ ] 9.2 Review diagrams for accuracy against actual Terraform configuration
- [ ] 9.3 Verify DPI and sizing meet publication requirements
- [ ] 9.4 Test reproducibility (run script twice, verify identical output)
- [ ] 9.5 Validate against all scenarios in spec.md