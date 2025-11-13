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
from src.terraform_parser.parser import parse_directory

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
        default=os.getenv(
            "LABLINK_TERRAFORM_DIR",
            Path(__file__).parent.parent.parent.parent
            / "lablink-template"
            / "lablink-infrastructure",
        ),
        help="Path to Terraform configuration directory (default: ../lablink-template/lablink-infrastructure or LABLINK_TERRAFORM_DIR env var)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "figures",
        help="Output directory for generated diagrams (default: figures/)",
    )

    parser.add_argument(
        "--diagram-type",
        choices=["main", "detailed", "network-flow", "all"],
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
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate Terraform directory
    if not args.terraform_dir.exists():
        logger.error(f"Terraform directory not found: {args.terraform_dir}")
        logger.info("Please specify --terraform-dir or set LABLINK_TERRAFORM_DIR")
        sys.exit(1)

    logger.info(f"Parsing Terraform files from: {args.terraform_dir}")

    try:
        # Parse Terraform configuration
        config = parse_directory(args.terraform_dir)
        logger.info(
            f"Parsed {len(config.get_all_resources())} resources from Terraform files"
        )
        logger.debug(f"  - EC2 instances: {len(config.ec2_instances)}")
        logger.debug(f"  - Security groups: {len(config.security_groups)}")
        logger.debug(f"  - ALBs: {len(config.albs)}")
        logger.debug(f"  - Lambda functions: {len(config.lambda_functions)}")
        logger.debug(f"  - CloudWatch logs: {len(config.cloudwatch_logs)}")
        logger.debug(f"  - IAM roles: {len(config.iam_roles)}")

    except Exception as e:
        logger.error(f"Failed to parse Terraform files: {e}")
        sys.exit(1)

    # Determine output formats
    formats = ["png", "svg", "pdf"] if args.format == "all" else [args.format]

    # Determine diagram types to generate
    diagram_types = (
        ["main", "detailed", "network-flow"]
        if args.diagram_type == "all"
        else [args.diagram_type]
    )

    # Create output directories
    main_dir = args.output_dir / "main"
    supp_dir = args.output_dir / "supplementary"
    main_dir.mkdir(parents=True, exist_ok=True)
    supp_dir.mkdir(parents=True, exist_ok=True)

    # Generate diagrams
    success_count = 0
    total_count = len(diagram_types) * len(formats)

    for diagram_type in diagram_types:
        for fmt in formats:
            try:
                if diagram_type == "main":
                    output_path = main_dir / "lablink-architecture"
                    logger.info(
                        f"Generating main architecture diagram ({fmt})..."
                    )
                    generate_main_diagram(config, output_path, format=fmt, dpi=args.dpi)

                elif diagram_type == "detailed":
                    output_path = supp_dir / "lablink-architecture-detailed"
                    logger.info(f"Generating detailed diagram ({fmt})...")
                    generate_detailed_diagram(
                        config, output_path, format=fmt, dpi=args.dpi
                    )

                elif diagram_type == "network-flow":
                    output_path = supp_dir / "lablink-network-flow"
                    logger.info(f"Generating network flow diagram ({fmt})...")
                    generate_network_flow_diagram(
                        config, output_path, format=fmt, dpi=args.dpi
                    )

                # Verify file was created
                expected_file = Path(str(output_path) + f".{fmt}")
                if expected_file.exists():
                    logger.info(f"  ✓ Created: {expected_file}")
                    success_count += 1
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

    # Add metadata file
    metadata_file = args.output_dir / "diagram_metadata.txt"
    with open(metadata_file, "w") as f:
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Terraform source: {args.terraform_dir}\n")
        f.write(f"Total resources parsed: {len(config.get_all_resources())}\n")
        f.write(f"Diagram types: {', '.join(diagram_types)}\n")
        f.write(f"Formats: {', '.join(formats)}\n")
        f.write(f"DPI: {args.dpi}\n")

    logger.info(f"Metadata saved to: {metadata_file}")

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