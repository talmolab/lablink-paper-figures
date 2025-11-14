#!/usr/bin/env python3
"""Generate LabLink architecture diagrams from Terraform configuration files."""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.diagram_gen.generator import (
    generate_detailed_diagram,
    generate_main_diagram,
    generate_network_flow_diagram,
)
from src.diagram_gen.generator import LabLinkDiagramBuilder
from src.terraform_parser.parser import parse_directory, parse_lablink_architecture

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate LabLink architecture diagrams from Terraform files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all diagram types in PNG format
  python generate_architecture_diagram.py \\
      --terraform-dir ../../lablink-template/lablink-infrastructure \\
      --diagram-type all

  # Generate main diagram only in SVG format
  python generate_architecture_diagram.py \\
      --terraform-dir /path/to/terraform \\
      --output-dir ../../figures/main \\
      --diagram-type main \\
      --format svg

  # Generate with custom DPI
  python generate_architecture_diagram.py \\
      --terraform-dir ../lablink-template/lablink-infrastructure \\
      --dpi 600
        """,
    )

    parser.add_argument(
        "--terraform-dir",
        type=Path,
        default=os.getenv("LABLINK_TERRAFORM_DIR"),
        help="Path to infrastructure Terraform directory (env: LABLINK_TERRAFORM_DIR)",
    )

    parser.add_argument(
        "--client-vm-terraform-dir",
        type=Path,
        default=os.getenv("LABLINK_CLIENT_VM_TERRAFORM_DIR"),
        help="Path to client VM Terraform directory (optional, env: LABLINK_CLIENT_VM_TERRAFORM_DIR)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "figures",
        help="Output directory for generated diagrams (default: figures/)",
    )

    parser.add_argument(
        "--diagram-type",
        choices=[
            "main",
            "detailed",
            "network-flow",
            "vm-provisioning",
            "crd-connection",
            "logging-pipeline",
            "cicd-workflow",
            "api-architecture",
            "network-flow-enhanced",
            "monitoring",
            "data-collection",
            "all",
            "all-essential",
            "all-supplementary",
        ],
        default="all",
        help="Type of diagram to generate (default: all)",
    )

    parser.add_argument(
        "--format",
        choices=["png", "svg", "pdf", "all"],
        default="png",
        help="Output format (default: png)",
    )

    parser.add_argument(
        "--dpi", type=int, default=300, help="DPI for PNG output (default: 300)"
    )

    parser.add_argument(
        "--fontsize-preset",
        choices=["paper", "poster", "presentation"],
        default="paper",
        help="Font size preset: paper (14pt), poster (20pt), presentation (16pt) (default: paper)"
    )

    parser.add_argument(
        "--timestamp-runs",
        action="store_true",
        default=True,
        help="Create timestamped run folders (default: enabled)"
    )

    parser.add_argument(
        "--no-timestamp-runs",
        action="store_false",
        dest="timestamp_runs",
        help="Disable timestamped run folders"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate Terraform directory
    if not args.terraform_dir:
        logger.error("No Terraform directory specified")
        logger.info("Please specify --terraform-dir or set LABLINK_TERRAFORM_DIR environment variable")
        sys.exit(1)

    if not args.terraform_dir.exists():
        logger.error(f"Terraform directory not found: {args.terraform_dir}")
        sys.exit(1)

    # Parse Terraform configuration(s)
    try:
        if args.client_vm_terraform_dir and args.client_vm_terraform_dir.exists():
            # Multi-tier parsing: infrastructure + client VMs
            logger.info(f"Parsing infrastructure Terraform from: {args.terraform_dir}")
            logger.info(f"Parsing client VM Terraform from: {args.client_vm_terraform_dir}")

            infra_config, client_config = parse_lablink_architecture(
                args.terraform_dir,
                args.client_vm_terraform_dir
            )

            # For now, use only infrastructure config (Phase 3+ will merge them)
            config = infra_config

            logger.info(f"Parsed infrastructure: {len(infra_config.get_all_resources())} resources")
            logger.info(f"Parsed client VMs: {len(client_config.get_all_resources())} resources")
            logger.debug(f"  Infrastructure EC2: {len(infra_config.ec2_instances)}")
            logger.debug(f"  Client VM EC2: {len(client_config.ec2_instances)}")
        else:
            # Single-tier parsing: infrastructure only
            logger.info(f"Parsing Terraform files from: {args.terraform_dir}")
            config = parse_directory(args.terraform_dir)
            logger.info(f"Parsed {len(config.get_all_resources())} resources")

        logger.debug(f"  - EC2 instances: {len(config.ec2_instances)}")
        logger.debug(f"  - Security groups: {len(config.security_groups)}")
        logger.debug(f"  - ALBs: {len(config.albs)}")
        logger.debug(f"  - Lambda functions: {len(config.lambda_functions)}")
        logger.debug(f"  - CloudWatch logs: {len(config.cloudwatch_logs)}")
        logger.debug(f"  - Subscription filters: {len(config.subscription_filters)}")
        logger.debug(f"  - IAM roles: {len(config.iam_roles)}")

    except Exception as e:
        logger.error(f"Failed to parse Terraform files: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Determine output formats
    formats = ["png", "svg", "pdf"] if args.format == "all" else [args.format]

    # Determine diagram types to generate
    all_essential = ["main", "vm-provisioning", "crd-connection", "logging-pipeline"]
    all_supplementary = ["cicd-workflow", "api-architecture", "network-flow-enhanced", "monitoring", "data-collection"]

    if args.diagram_type == "all":
        diagram_types = ["main", "detailed", "network-flow"] + all_essential[1:] + all_supplementary
    elif args.diagram_type == "all-essential":
        diagram_types = all_essential
    elif args.diagram_type == "all-supplementary":
        diagram_types = all_supplementary
    else:
        diagram_types = [args.diagram_type]

    # Create output directory structure
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped run folder if enabled
    if args.timestamp_runs:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create timestamped run folder at figures/ level, not under main/supplementary
        figures_dir = args.output_dir.parent if args.output_dir.name in ["main", "supplementary"] else args.output_dir
        base_run_dir = figures_dir / f"run_{timestamp}"
        base_run_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Creating timestamped run folder: {base_run_dir}")

        # Determine which category subdirectory to use
        category = args.output_dir.name if args.output_dir.name in ["main", "supplementary"] else "diagrams"
        run_dir = base_run_dir / category
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = args.output_dir

    # Generate diagrams
    success_count = 0
    total_count = len(diagram_types) * len(formats)

    # Create builder for new diagram types
    builder = LabLinkDiagramBuilder(config)

    for diagram_type in diagram_types:
        for fmt in formats:
            try:
                if diagram_type == "main":
                    output_path = run_dir / "lablink-architecture"
                    logger.info(
                        f"Generating main architecture diagram ({fmt})..."
                    )
                    generate_main_diagram(config, output_path, format=fmt, dpi=args.dpi)

                elif diagram_type == "detailed":
                    output_path = run_dir / "lablink-architecture-detailed"
                    logger.info(f"Generating detailed diagram ({fmt})...")
                    generate_detailed_diagram(
                        config, output_path, format=fmt, dpi=args.dpi
                    )

                elif diagram_type == "network-flow":
                    output_path = run_dir / "lablink-network-flow"
                    logger.info(f"Generating network flow diagram ({fmt})...")
                    generate_network_flow_diagram(
                        config, output_path, format=fmt, dpi=args.dpi
                    )

                elif diagram_type == "vm-provisioning":
                    output_path = run_dir / "lablink-vm-provisioning"
                    logger.info(f"Generating VM provisioning diagram ({fmt})...")
                    builder.build_vm_provisioning_diagram(output_path, format=fmt, dpi=args.dpi, fontsize_preset=args.fontsize_preset)

                elif diagram_type == "crd-connection":
                    output_path = run_dir / "lablink-crd-connection"
                    logger.info(f"Generating CRD connection diagram ({fmt})...")
                    builder.build_crd_connection_diagram(output_path, format=fmt, dpi=args.dpi, fontsize_preset=args.fontsize_preset)

                elif diagram_type == "logging-pipeline":
                    output_path = run_dir / "lablink-logging-pipeline"
                    logger.info(f"Generating logging pipeline diagram ({fmt})...")
                    builder.build_logging_pipeline_diagram(output_path, format=fmt, dpi=args.dpi, fontsize_preset=args.fontsize_preset)

                elif diagram_type == "cicd-workflow":
                    output_path = run_dir / "lablink-cicd-workflow"
                    logger.info(f"Generating CI/CD workflow diagram ({fmt})...")
                    builder.build_cicd_workflow_diagram(output_path, format=fmt, dpi=args.dpi)

                elif diagram_type == "api-architecture":
                    output_path = run_dir / "lablink-api-architecture"
                    logger.info(f"Generating API architecture diagram ({fmt})...")
                    builder.build_api_architecture_diagram(output_path, format=fmt, dpi=args.dpi)
                
                elif diagram_type == "network-flow-enhanced":
                    output_path = run_dir / "lablink-network-flow-enhanced"
                    logger.info(f"Generating enhanced network flow diagram ({fmt})...")
                    builder.build_network_flow_enhanced_diagram(output_path, format=fmt, dpi=args.dpi)

                elif diagram_type == "monitoring":
                    output_path = run_dir / "lablink-monitoring"
                    logger.info(f"Generating monitoring diagram ({fmt})...")
                    builder.build_monitoring_diagram(output_path, format=fmt, dpi=args.dpi)

                elif diagram_type == "data-collection":
                    output_path = run_dir / "lablink-data-collection"
                    logger.info(f"Generating data collection diagram ({fmt})...")
                    builder.build_data_collection_diagram(output_path, format=fmt, dpi=args.dpi)

                # Verify file was created
                expected_file = Path(str(output_path) + f".{fmt}")
                if expected_file.exists():
                    logger.info(f"  ✓ Created: {expected_file}")
                    success_count += 1

                    # Copy to top-level directory if using timestamped runs
                    if args.timestamp_runs:
                        import shutil
                        top_level_file = args.output_dir / expected_file.name
                        shutil.copy2(expected_file, top_level_file)
                        logger.debug(f"  → Copied to: {top_level_file}")
                else:
                    logger.warning(f"  ✗ Expected file not found: {expected_file}")

            except Exception as e:
                logger.error(
                    f"Failed to generate {diagram_type} diagram in {fmt}: {e}"
                )
                if args.verbose:
                    import traceback

                    traceback.print_exc()

    # Summary
    logger.info(f"\nDiagram generation complete: {success_count}/{total_count} successful")

    # Add metadata file (both in run dir and top-level if using timestamps)
    metadata_content = (
        f"Generated: {datetime.now().isoformat()}\n"
        f"Terraform source: {args.terraform_dir}\n"
        f"Total resources parsed: {len(config.get_all_resources())}\n"
        f"Diagram types: {', '.join(diagram_types)}\n"
        f"Formats: {', '.join(formats)}\n"
        f"DPI: {args.dpi}\n"
        f"Font preset: {args.fontsize_preset}\n"
        f"Timestamped runs: {args.timestamp_runs}\n"
    )

    metadata_file = run_dir / "diagram_metadata.txt"
    with open(metadata_file, "w") as f:
        f.write(metadata_content)
    logger.info(f"Metadata saved to: {metadata_file}")

    # Also save to top-level if using timestamped runs
    if args.timestamp_runs:
        import shutil
        top_level_metadata = args.output_dir / "diagram_metadata.txt"
        with open(top_level_metadata, "w") as f:
            f.write(metadata_content)
        logger.info(f"Metadata also saved to: {top_level_metadata}")

    if success_count == total_count:
        logger.info("All diagrams generated successfully!")
        sys.exit(0)
    else:
        logger.warning(
            f"Some diagrams failed to generate ({total_count - success_count} failed)"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()