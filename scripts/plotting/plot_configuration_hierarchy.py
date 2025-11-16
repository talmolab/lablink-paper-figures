#!/usr/bin/env python3
"""Generate LabLink configuration hierarchy tree diagram."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Use graphviz directly for tree diagram
import graphviz


def create_configuration_tree(
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper"
):
    """
    Create a hierarchical tree diagram showing LabLink's configuration parameters.

    Args:
        output_path: Path to output file (without extension)
        format: Output format (png, svg, pdf)
        dpi: Resolution for raster outputs
        fontsize_preset: Font size preset (paper, poster, presentation)
    """
    # Font size presets
    font_presets = {
        "paper": {"title": 16, "node": 14, "edge": 12},
        "poster": {"title": 24, "node": 20, "edge": 18},
        "presentation": {"title": 20, "node": 16, "edge": 14},
    }

    fonts = font_presets.get(fontsize_preset, font_presets["paper"])

    # Create directed graph (tree structure)
    dot = graphviz.Digraph(
        comment='LabLink Configuration Hierarchy',
        format=format,
        engine='dot'
    )

    # Graph attributes
    dot.attr(
        rankdir='TB',  # Top to bottom
        splines='ortho',  # Orthogonal edges
        nodesep='0.5',
        ranksep='0.75',
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
        margin='0.2,0.1'
    )

    # Default edge attributes
    dot.attr('edge',
        fontname='Arial',
        fontsize=str(fonts["edge"]),
        arrowsize='0.7'
    )

    # Root node
    dot.node('root', 'LabLink Configuration',
        fillcolor='#5D6D7E',
        fontcolor='white',
        shape='box',
        style='rounded,filled',
        fontsize=str(fonts["title"]),
        width='3.5',
        height='0.6'
    )

    # Level 1: Primary Configuration Categories
    categories = {
        'env': ('Deployment\nEnvironment', '#7FB3D5'),
        'ssl': ('SSL/Network\nStrategy', '#C39BD3'),
        'compute': ('Compute\nConfiguration', '#EC7063'),
        'app': ('Application\nSettings', '#F8C471'),
        'scale': ('Scaling &\nReliability', '#76D7C4'),
        'infra': ('AWS\nInfrastructure', '#85929E'),
        'auth': ('Authentication\n& Security', '#E59866'),
        'monitor': ('Monitoring\n& Logging', '#7DCEA0')
    }

    for cat_id, (label, color) in categories.items():
        dot.node(cat_id, label,
            fillcolor=color,
            fontcolor='white',
            width='2.2',
            height='0.5'
        )
        dot.edge('root', cat_id, penwidth='2.0')

    # Level 2: Environment options
    env_options = [
        ('dev', 'dev\n(local, no S3)'),
        ('test', 'test\n(S3, auto-deploy)'),
        ('prod', 'prod\n(S3, manual)'),
        ('ci-test', 'ci-test\n(CI testing)')
    ]

    for opt_id, label in env_options:
        dot.node(f'env_{opt_id}', label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            shape='box',
            width='1.8',
            height='0.5'
        )
        dot.edge('env', f'env_{opt_id}')

    # Level 2: SSL Strategy options
    ssl_options = [
        ('none', 'none\n(HTTP:80 → 5000)', 'Development'),
        ('letsencrypt', 'letsencrypt\n(Caddy auto-SSL)', 'Production'),
        ('cloudflare', 'cloudflare\n(CF proxy)', 'Production'),
        ('acm', 'acm\n(AWS ALB + cert)', 'Enterprise')
    ]

    for opt_id, label, use_case in ssl_options:
        dot.node(f'ssl_{opt_id}', label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            shape='box',
            width='2.0',
            height='0.5'
        )
        dot.edge('ssl', f'ssl_{opt_id}', label=use_case, fontsize=str(fonts["edge"]-2))

    # ACM requires certificate
    dot.node('ssl_acm_req', 'requires:\ncertificate_arn\nRoute53',
        fillcolor='#FFF9E6',
        fontcolor='#9A7D0A',
        shape='note',
        width='1.5',
        height='0.5',
        fontsize=str(fonts["node"]-2)
    )
    dot.edge('ssl_acm', 'ssl_acm_req', style='dashed', arrowhead='none')

    # Level 2: Compute Configuration
    dot.node('compute_gpu', 'GPU Instances',
        fillcolor='#E8F8F5',
        fontcolor='#52BE80',
        width='2.0'
    )
    dot.node('compute_cpu', 'CPU Instances',
        fillcolor='#E8F8F5',
        fontcolor='#52BE80',
        width='2.0'
    )
    dot.edge('compute', 'compute_gpu')
    dot.edge('compute', 'compute_cpu')

    # GPU types
    gpu_types = [
        ('g4dn.xlarge\n(1 GPU)'),
        ('p3.8xlarge\n(4 GPUs, high-perf)'),
        ('other GPU types')
    ]
    for i, label in enumerate(gpu_types):
        node_id = f'gpu_{i}'
        dot.node(node_id, label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            width='2.2',
            height='0.5',
            fontsize=str(fonts["node"]-1)
        )
        dot.edge('compute_gpu', node_id)

    # GPU auto-detection note
    dot.node('gpu_auto', 'gpu_support: true\n(auto-detected)',
        fillcolor='#FFF9E6',
        fontcolor='#9A7D0A',
        shape='note',
        width='2.0',
        fontsize=str(fonts["node"]-2)
    )
    dot.edge('gpu_0', 'gpu_auto', style='dashed', arrowhead='none')

    # CPU types
    cpu_types = [
        ('t3.medium'),
        ('t3.large'),
        ('other CPU types')
    ]
    for i, label in enumerate(cpu_types):
        node_id = f'cpu_{i}'
        dot.node(node_id, label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            width='1.8',
            fontsize=str(fonts["node"]-1)
        )
        dot.edge('compute_cpu', node_id)

    # CPU auto-detection note
    dot.node('cpu_auto', 'gpu_support: false\n(auto-detected)',
        fillcolor='#FFF9E6',
        fontcolor='#9A7D0A',
        shape='note',
        width='2.0',
        fontsize=str(fonts["node"]-2)
    )
    dot.edge('cpu_0', 'cpu_auto', style='dashed', arrowhead='none')

    # Level 2: Application Settings
    app_options = [
        ('sleap', 'SLEAP\n.slp files\nsleap-tutorial-data'),
        ('custom', 'Custom App\ncustom extension\ncustom repo')
    ]

    for opt_id, label in app_options:
        dot.node(f'app_{opt_id}', label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            width='2.2',
            height='0.6'
        )
        dot.edge('app', f'app_{opt_id}')

    # Level 2: Scaling & Reliability
    dot.node('scale_count', 'instance_count\n(1-N VMs)',
        fillcolor='#F8F9F9',
        fontcolor='#2c3e50',
        width='2.0'
    )
    dot.node('scale_error', 'startup_on_error\n(continue | fail)',
        fillcolor='#F8F9F9',
        fontcolor='#2c3e50',
        width='2.0'
    )
    dot.edge('scale', 'scale_count')
    dot.edge('scale', 'scale_error')

    # Level 2: AWS Infrastructure
    infra_items = [
        ('region\n(us-west-2, us-east-1, ...)'),
        ('client_ami_id\n(AMI selection)'),
        ('image_name\n(Docker image)'),
        ('EIP strategy\n(persistent | dynamic)')
    ]

    for i, label in enumerate(infra_items):
        dot.node(f'infra_{i}', label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            width='2.2',
            fontsize=str(fonts["node"]-1)
        )
        dot.edge('infra', f'infra_{i}')

    # Level 2: Authentication & Security
    auth_items = [
        ('admin credentials\n(username, password)'),
        ('database_password\n(PostgreSQL)'),
        ('AWS credentials\n(access_key, secret_key)'),
        ('Security groups\n(HTTP, SSH, ALB)')
    ]

    for i, label in enumerate(auth_items):
        dot.node(f'auth_{i}', label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            width='2.2',
            fontsize=str(fonts["node"]-1)
        )
        dot.edge('auth', f'auth_{i}')

    # Level 2: Monitoring & Logging
    monitor_items = [
        ('cloud_init_output_log_group\n(CloudWatch)'),
        ('Log retention policy'),
        ('Lambda log processor'),
        ('Polling intervals\n(GPU: 20s, usage: 20s)')
    ]

    for i, label in enumerate(monitor_items):
        dot.node(f'monitor_{i}', label,
            fillcolor='#F8F9F9',
            fontcolor='#2c3e50',
            width='2.4',
            fontsize=str(fonts["node"]-1)
        )
        dot.edge('monitor', f'monitor_{i}')

    # Render the diagram
    output_str = str(output_path)
    dot.render(output_str, format=format, cleanup=True)

    print(f"Generated configuration hierarchy diagram: {output_str}.{format}")
    return dot


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate LabLink configuration hierarchy tree diagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate configuration tree in PNG format
  python plot_configuration_hierarchy.py --output-dir ../../figures/main

  # Generate in SVG format with poster fonts
  python plot_configuration_hierarchy.py \\
      --format svg \\
      --fontsize-preset poster

  # High resolution for publication
  python plot_configuration_hierarchy.py --dpi 600
        """
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "figures" / "main",
        help="Output directory for generated diagram (default: figures/main/)"
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
        help="Font size preset: paper (14pt), poster (20pt), presentation (16pt) (default: paper)"
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate diagram
    output_path = args.output_dir / "lablink-configuration-hierarchy"

    try:
        create_configuration_tree(
            output_path,
            format=args.format,
            dpi=args.dpi,
            fontsize_preset=args.fontsize_preset
        )

        # Create metadata file
        metadata_content = (
            f"Generated: {datetime.now().isoformat()}\n"
            f"Type: Configuration Hierarchy Tree\n"
            f"Format: {args.format}\n"
            f"DPI: {args.dpi}\n"
            f"Font preset: {args.fontsize_preset}\n"
            f"Source: LabLink infrastructure config.yaml and terraform.runtime.tfvars\n"
        )

        metadata_file = args.output_dir / "configuration_hierarchy_metadata.txt"
        with open(metadata_file, "w") as f:
            f.write(metadata_content)

        print(f"Metadata saved to: {metadata_file}")
        print("Configuration hierarchy diagram generated successfully!")

    except Exception as e:
        print(f"Error generating diagram: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
