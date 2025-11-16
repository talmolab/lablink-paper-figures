#!/usr/bin/env python3
"""Generate simplified LabLink configuration hierarchy diagram (collapsed view)."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import graphviz


def create_simple_configuration_tree(
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper"
):
    """
    Create a simplified configuration hierarchy with collapsed details.

    Args:
        output_path: Path to output file (without extension)
        format: Output format (png, svg, pdf)
        dpi: Resolution for raster outputs
        fontsize_preset: Font size preset (paper, poster, presentation)
    """
    # Font size presets
    font_presets = {
        "paper": {"title": 16, "node": 13, "edge": 11, "annotation": 10},
        "poster": {"title": 24, "node": 18, "edge": 16, "annotation": 14},
        "presentation": {"title": 20, "node": 16, "edge": 14, "annotation": 12},
    }

    fonts = font_presets.get(fontsize_preset, font_presets["paper"])

    # Create directed graph
    dot = graphviz.Digraph(
        comment='LabLink Configuration Hierarchy (Simplified)',
        format=format,
        engine='dot'
    )

    # Graph attributes
    dot.attr(
        rankdir='TB',
        splines='ortho',
        nodesep='0.6',
        ranksep='0.9',
        dpi=str(dpi),
        bgcolor='white',
        fontname='Arial',
        fontsize=str(fonts["title"])
    )

    # Default node attributes
    dot.attr('node',
        shape='box',
        style='rounded,filled',
        fontname='Arial',
        fontsize=str(fonts["node"]),
        margin='0.25,0.15'
    )

    # Default edge attributes
    dot.attr('edge',
        fontname='Arial',
        fontsize=str(fonts["edge"]),
        arrowsize='0.7',
        penwidth='1.5'
    )

    # Root node
    dot.node('root', 'LabLink Configuration',
        fillcolor='#5D6D7E',
        fontcolor='white',
        shape='box',
        style='rounded,filled',
        fontsize=str(fonts["title"]),
        width='3.5',
        height='0.6',
        penwidth='2.5'
    )

    # Category 1: Deployment Environment
    env_label = 'Deployment Environment\n\nOptions: dev | test | prod | ci-test'
    dot.node('env', env_label,
        fillcolor='#7FB3D5',
        fontcolor='white',
        width='3.2',
        height='1.0',
        penwidth='2.5'
    )
    dot.edge('root', 'env', penwidth='2.5', color='#5D6D7E')

    # Category 2: SSL Strategy
    ssl_label = 'SSL/Network Strategy\n\nOptions: none | letsencrypt | cloudflare | acm*\n*requires ACM cert + Route53'
    dot.node('ssl', ssl_label,
        fillcolor='#C39BD3',
        fontcolor='white',
        width='3.5',
        height='1.0',
        penwidth='2.5'
    )
    dot.edge('root', 'ssl', penwidth='2.5', color='#5D6D7E')

    # Category 3: Compute Configuration
    compute_label = 'Compute Configuration\n\nGPU: g4dn.xlarge | p3.8xlarge | ...\nCPU: t3.medium | t3.large | ...'
    dot.node('compute', compute_label,
        fillcolor='#EC7063',
        fontcolor='white',
        width='3.2',
        height='1.0',
        penwidth='2.5'
    )
    dot.edge('root', 'compute', penwidth='2.5', color='#5D6D7E')

    # Category 4: Application Settings
    app_label = 'Application Settings\n\nSoftware: SLEAP | Custom\nFiles: .slp | .h5 | custom\nRepository: Git URL'
    dot.node('app', app_label,
        fillcolor='#F8C471',
        fontcolor='white',
        width='2.8',
        height='1.0',
        penwidth='2.0'
    )
    dot.edge('root', 'app', penwidth='2.0', color='#5D6D7E')

    # Category 5: Scaling & Reliability
    scale_label = 'Scaling & Reliability\n\nInstance count: 1-N VMs\nError handling: continue | fail'
    dot.node('scale', scale_label,
        fillcolor='#76D7C4',
        fontcolor='white',
        width='2.8',
        height='0.9',
        penwidth='2.0'
    )
    dot.edge('root', 'scale', penwidth='2.0', color='#5D6D7E')

    # Category 6: AWS Infrastructure (Secondary)
    infra_label = 'AWS Infrastructure\n\nRegion, AMI, Docker image\nEIP strategy'
    dot.node('infra', infra_label,
        fillcolor='#D5D8DC',
        fontcolor='#2c3e50',
        width='2.4',
        height='0.8',
        penwidth='1.5'
    )
    dot.edge('root', 'infra', penwidth='1.5', color='#95A5A6')

    # Category 7: Authentication & Security (Secondary)
    auth_label = 'Authentication & Security\n\nAdmin credentials, DB password\nAWS credentials, Security groups'
    dot.node('auth', auth_label,
        fillcolor='#D5D8DC',
        fontcolor='#2c3e50',
        width='3.0',
        height='0.8',
        penwidth='1.5'
    )
    dot.edge('root', 'auth', penwidth='1.5', color='#95A5A6')

    # Category 8: Monitoring & Logging (Secondary)
    monitor_label = 'Monitoring & Logging\n\nCloudWatch logs, Lambda processor\nPolling: GPU (20s), usage (20s)'
    dot.node('monitor', monitor_label,
        fillcolor='#D5D8DC',
        fontcolor='#2c3e50',
        width='3.0',
        height='0.8',
        penwidth='1.5'
    )
    dot.edge('root', 'monitor', penwidth='1.5', color='#95A5A6')

    # Render
    output_str = str(output_path)
    dot.render(output_str, format=format, cleanup=True)

    print(f"Generated simplified configuration diagram: {output_str}.{format}")
    return dot


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate simplified LabLink configuration hierarchy diagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate simplified diagram in PNG format
  python plot_configuration_hierarchy_simple.py --output-dir ../../figures/main

  # Generate poster version
  python plot_configuration_hierarchy_simple.py \\
      --format svg \\
      --fontsize-preset poster
        """
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "figures" / "main",
        help="Output directory (default: figures/main/)"
    )

    parser.add_argument(
        "--format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output format (default: png)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PNG output (default: 300)"
    )

    parser.add_argument(
        "--fontsize-preset",
        choices=["paper", "poster", "presentation"],
        default="paper",
        help="Font size preset (default: paper)"
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate diagram
    output_path = args.output_dir / "lablink-configuration-hierarchy-simple"

    try:
        create_simple_configuration_tree(
            output_path,
            format=args.format,
            dpi=args.dpi,
            fontsize_preset=args.fontsize_preset
        )

        # Create metadata
        metadata_content = (
            f"Generated: {datetime.now().isoformat()}\n"
            f"Type: Configuration Hierarchy Tree (Simplified)\n"
            f"Format: {args.format}\n"
            f"DPI: {args.dpi}\n"
            f"Font preset: {args.fontsize_preset}\n"
            f"Description: Collapsed view with annotations for digestibility\n"
            f"Source: LabLink config.yaml and terraform.runtime.tfvars\n"
        )

        metadata_file = args.output_dir / "configuration_hierarchy_simple_metadata.txt"
        with open(metadata_file, "w") as f:
            f.write(metadata_content)

        print(f"Metadata saved to: {metadata_file}")
        print("Simplified configuration hierarchy generated successfully!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
