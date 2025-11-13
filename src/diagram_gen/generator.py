"""Generate architecture diagrams from parsed Terraform resources."""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.management import CloudwatchLogs
from diagrams.aws.network import ALB, ELB, Route53
from diagrams.aws.security import IAMRole
from diagrams.onprem.client import Users

from src.terraform_parser.parser import ParsedTerraformConfig


class LabLinkDiagramBuilder:
    """Builder class for creating LabLink architecture diagrams."""

    def __init__(
        self,
        config: ParsedTerraformConfig,
        client_config: ParsedTerraformConfig | None = None,
        show_iam: bool = True,
        show_security_groups: bool = True,
    ):
        """
        Initialize diagram builder.

        Args:
            config: Parsed infrastructure Terraform configuration
            client_config: Optional parsed client VM Terraform configuration
            show_iam: Whether to show IAM roles in diagram
            show_security_groups: Whether to show security groups in diagram
        """
        self.config = config
        self.client_config = client_config
        self.show_iam = show_iam
        self.show_security_groups = show_security_groups

    def _get_node_style(self, resource):
        """
        Get visual styling for a node based on resource properties.

        Returns:
            dict: Node styling attributes
        """
        # Default style (always-present infrastructure)
        style = {"style": "solid"}

        # Conditional resources: dashed border, green fill
        if resource.is_conditional:
            style.update({
                "style": "dashed",
                "color": "#28a745",  # Green border
                "penwidth": "2.0"
            })

        # Runtime-provisioned resources: dotted border, orange fill
        elif resource.tier == "client_vm":
            style.update({
                "style": "dotted",
                "color": "#fd7e14",  # Orange border
                "penwidth": "2.0"
            })

        return style

    def _format_label_with_annotation(self, base_label: str, resource):
        """
        Add annotations to node labels based on resource properties.

        Args:
            base_label: Base label text
            resource: TerraformResource to annotate

        Returns:
            str: Formatted label with annotations
        """
        if resource.is_conditional and resource.condition:
            # Clean up condition for display
            condition = resource.condition.replace("local.", "").replace("&&", "&")
            return f"{base_label}\n(When {condition})"
        elif resource.tier == "client_vm":
            return f"{base_label}\n(Runtime-provisioned)"
        return base_label

    def _create_compute_components(self, cluster=None):
        """Create compute resource components (EC2, Lambda)."""
        components = {}

        # EC2 instances
        for ec2 in self.config.ec2_instances:
            instance_type = ec2.attributes.get("instance_type", "unknown")
            base_label = f"{ec2.name}\n({instance_type})"
            label = self._format_label_with_annotation(base_label, ec2)
            components[f"ec2_{ec2.name}"] = EC2(label)

        # Lambda functions
        for lambda_fn in self.config.lambda_functions:
            runtime = lambda_fn.attributes.get("runtime", "")
            base_label = f"{lambda_fn.name}\n{runtime}"
            label = self._format_label_with_annotation(base_label, lambda_fn)
            components[f"lambda_{lambda_fn.name}"] = Lambda(label)

        return components

    def _create_network_components(self):
        """Create networking components (ALB, EIP, Route53)."""
        components = {}

        # ALBs
        for alb in self.config.albs:
            base_label = alb.name
            label = self._format_label_with_annotation(base_label, alb)
            components[f"alb_{alb.name}"] = ALB(label)

        # Route53 records
        for r53 in self.config.route53_records:
            domain = r53.attributes.get("domain", r53.name)
            label = self._format_label_with_annotation(domain, r53)
            components[f"r53_{r53.name}"] = Route53(label)

        return components

    def _create_observability_components(self):
        """Create observability components (CloudWatch)."""
        components = {}

        # CloudWatch Log Groups
        for cw in self.config.cloudwatch_logs:
            log_name = cw.attributes.get("log_group_name", cw.name)
            # Shorten long names
            display_name = log_name.split("/")[-1] if "/" in log_name else log_name
            label = self._format_label_with_annotation(display_name, cw)
            components[f"cw_{cw.name}"] = CloudwatchLogs(label)

        return components

    def _create_iam_components(self):
        """Create IAM components (roles, policies)."""
        if not self.show_iam:
            return {}

        components = {}

        # IAM Roles
        for role in self.config.iam_roles:
            role_name = role.attributes.get("role_name", role.name)
            components[f"iam_{role.name}"] = IAMRole(role_name)

        return components

    def build_main_diagram(
        self, output_path: Path, format: str = "png", dpi: int = 300
    ):
        """
        Build simplified main architecture diagram for paper/poster.

        Args:
            output_path: Path where diagram will be saved (without extension)
            format: Output format (png, svg, pdf)
            dpi: DPI for PNG output
        """
        graph_attr = {
            "fontsize": "18",  # Larger for poster
            "fontname": "Helvetica-Bold",  # Bold font
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": "0.8",
            "ranksep": "1.0",
        }

        edge_attr = {
            "fontsize": "16",
            "fontname": "Helvetica-Bold",
        }

        node_attr = {
            "fontsize": "16",
            "fontname": "Helvetica-Bold",
        }

        with Diagram(
            "LabLink Architecture",
            filename=str(output_path),
            outformat=format,
            show=False,
            direction="TB",
            graph_attr=graph_attr,
            edge_attr=edge_attr,
            node_attr=node_attr,
        ):
            # External users (outside clusters)
            users = Users("Researchers")

            # Cluster 1: Access Layer (Configurable) - DNS/SSL with 4 patterns
            with Cluster("Access Layer\n(Configurable: 4 DNS/SSL Patterns)"):
                dns_components = self._create_network_components()

                # Check what's actually configured
                has_route53 = len([k for k in dns_components.keys() if k.startswith("r53_")]) > 0
                has_alb = len([k for k in dns_components.keys() if k.startswith("alb_")]) > 0

                if has_route53 or has_alb:
                    # Show actual configuration with annotations
                    if has_route53:
                        route53 = (
                            dns_components.get("r53_lablink_alb_record")
                            or dns_components.get("r53_lablink_a_record")
                            or dns_components.get("r53_allocator_dns")
                            or next((v for k, v in dns_components.items() if k.startswith("r53_")), Route53("Route53\nDNS"))
                        )
                    if has_alb:
                        alb = dns_components.get("alb_allocator_alb") or ALB("ALB\n(ACM SSL)")
                else:
                    # Fallback: show it's configurable
                    route53 = Route53("DNS\n(Optional)")
                    alb = None

            # Cluster 2: LabLink Infrastructure - Core allocator service
            with Cluster("LabLink Infrastructure\n(Always Present)"):
                compute_components = self._create_compute_components()
                # Get allocator EC2 instance
                allocator = (
                    compute_components.get("ec2_lablink_allocator_server")
                    or compute_components.get("ec2_allocator_server")
                    or EC2("Allocator\nServer")
                )

            # Cluster 3: Dynamic Compute - Runtime-provisioned client VMs
            with Cluster("Dynamic Compute\n(Runtime-Provisioned)"):
                # Client VMs - these are provisioned by allocator via Terraform subprocess
                client_vm = EC2("Client VMs\n(Provisioned per experiment)")

            # Cluster 4: Observability & Logging
            with Cluster("Observability & Logging"):
                obs_components = self._create_observability_components()
                cloudwatch = (
                    obs_components.get("cw_client_vm_logs")
                    or obs_components.get("cw_lambda_logs")
                    or obs_components.get("cw_client_logs")
                    or CloudwatchLogs("CloudWatch\nLogs")
                )

                # Lambda log processor
                log_processor = (
                    compute_components.get("lambda_log_processor")
                    or Lambda("Log\nProcessor")
                )

            # Define request flow through access layer
            users >> Edge(label="HTTP(S)", fontsize="16") >> route53

            if has_alb and alb:
                route53 >> alb
                alb >> Edge(label="HTTP:5000", fontsize="16") >> allocator
            else:
                route53 >> Edge(label="HTTP(S):5000", fontsize="16") >> allocator

            # Runtime provisioning flow: Allocator provisions client VMs
            allocator >> Edge(
                label="provisions via\nTerraform subprocess",
                style="dashed",
                fontsize="16",
                color="#fd7e14"  # Orange for runtime provisioning
            ) >> client_vm

            # Logging flow: Client VMs → CloudWatch → Lambda → Allocator
            client_vm >> Edge(label="CloudWatch\nAgent", fontsize="16") >> cloudwatch

            # Subscription filter as edge (not node)
            cloudwatch >> Edge(
                label="subscription filter\ntriggers",
                fontsize="16",
                style="dotted"
            ) >> log_processor

            log_processor >> Edge(label="POST\n/api/vm-logs", fontsize="16") >> allocator

    def build_detailed_diagram(self, output_path: Path, format: str = "png", dpi: int = 300):
        """
        Build detailed architecture diagram showing all components from both tiers.

        Args:
            output_path: Path where diagram will be saved (without extension)
            format: Output format (png, svg, pdf)
            dpi: DPI for PNG output
        """
        graph_attr = {
            "fontsize": "12",
            "bgcolor": "white",
            "dpi": str(dpi),
        }

        with Diagram(
            "LabLink Detailed Architecture",
            filename=str(output_path),
            outformat=format,
            show=False,
            direction="TB",
            graph_attr=graph_attr,
        ):
            users = Users("External Users")

            # Cluster 1: Access Layer (with annotations)
            with Cluster("Access Layer (Configurable)"):
                dns_components = self._create_network_components()
                route53_nodes = [
                    v for k, v in dns_components.items() if k.startswith("r53_")
                ]
                if not route53_nodes:
                    route53_nodes = [Route53("DNS (Optional)")]

                alb_nodes = [
                    v for k, v in dns_components.items() if k.startswith("alb_")
                ]
                if not alb_nodes:
                    alb_nodes = [ALB("ALB (When ACM)")]

                # Target groups
                target_group = ELB("Target Group")

            # Cluster 2: LabLink Infrastructure
            with Cluster("LabLink Infrastructure"):
                compute_components = self._create_compute_components()
                ec2_nodes = [
                    v for k, v in compute_components.items() if k.startswith("ec2_")
                ]
                if not ec2_nodes:
                    ec2_nodes = [EC2("Allocator Server")]

            # Cluster 3: Dynamic Compute (Runtime-provisioned)
            with Cluster("Dynamic Compute (Runtime-Provisioned)"):
                client_vms = EC2("Client VMs\n(Provisioned per experiment)")

            # Cluster 4: Observability & Logging
            with Cluster("Observability & Logging"):
                obs_components = self._create_observability_components()
                cw_nodes = [
                    v for k, v in obs_components.items() if k.startswith("cw_")
                ]
                if not cw_nodes:
                    cw_nodes = [CloudwatchLogs("CloudWatch Logs")]

                lambda_nodes = [
                    v for k, v in compute_components.items() if k.startswith("lambda_")
                ]
                if not lambda_nodes:
                    lambda_nodes = [Lambda("Log Processor")]

            # Cluster 5: IAM & Permissions (if enabled)
            if self.show_iam:
                with Cluster("IAM & Permissions"):
                    iam_components = self._create_iam_components()
                    iam_nodes = [
                        v for k, v in iam_components.items() if k.startswith("iam_")
                    ]
                    if not iam_nodes:
                        iam_nodes = [IAMRole("IAM Roles")]

            # Define connections
            users >> route53_nodes[0]
            if alb_nodes and len(alb_nodes) > 0:
                route53_nodes[0] >> alb_nodes[0]
                alb_nodes[0] >> target_group >> ec2_nodes[0]
            else:
                route53_nodes[0] >> ec2_nodes[0]

            # Allocator provisions client VMs via Terraform subprocess
            ec2_nodes[0] >> Edge(
                style="dashed",
                label="provisions via\nTerraform",
                color="#fd7e14"
            ) >> client_vms

            # Logging flow with subscription filter as edge
            client_vms >> Edge(label="CloudWatch Agent") >> cw_nodes[0]

            if lambda_nodes:
                # Subscription filter as edge (not node)
                cw_nodes[0] >> Edge(
                    style="dotted",
                    label="subscription filter"
                ) >> lambda_nodes[0]

                lambda_nodes[0] >> Edge(label="POST /api/vm-logs") >> ec2_nodes[0]

            # IAM connections (show permissions with dotted lines)
            if self.show_iam and iam_nodes:
                for ec2 in ec2_nodes:
                    iam_nodes[0] >> Edge(style="dotted", label="assumes") >> ec2
                if lambda_nodes:
                    for lambda_fn in lambda_nodes:
                        iam_nodes[0] >> Edge(style="dotted", label="assumes") >> lambda_fn
                # Client VMs also have IAM role
                iam_nodes[0] >> Edge(style="dotted", label="assumes") >> client_vms

    def build_network_flow_diagram(
        self, output_path: Path, format: str = "png", dpi: int = 300
    ):
        """
        Build network flow diagram focusing on request routing.

        Args:
            output_path: Path where diagram will be saved (without extension)
            format: Output format (png, svg, pdf)
            dpi: DPI for PNG output
        """
        graph_attr = {
            "fontsize": "14",
            "bgcolor": "white",
            "dpi": str(dpi),
            "rankdir": "LR",
        }

        with Diagram(
            "LabLink Network Flow",
            filename=str(output_path),
            outformat=format,
            show=False,
            direction="LR",
            graph_attr=graph_attr,
        ):
            users = Users("Client Request")

            # DNS resolution
            route53 = Route53("Route53\nDNS Lookup")

            # Load balancer
            alb = ALB("Application LB\nSSL Termination")

            # Allocator
            allocator = EC2("Allocator Server\nPort 5000")

            # API response
            api_response = Users("API Response")

            # Flow
            users >> Edge(label="1. HTTPS\nexample.com") >> route53
            route53 >> Edge(label="2. Resolve to\nALB DNS") >> alb
            alb >> Edge(label="3. HTTP:5000\nTarget Group") >> allocator
            allocator >> Edge(label="4. JSON\nResponse") >> api_response


def generate_main_diagram(
    config: ParsedTerraformConfig,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
):
    """
    Generate main architecture diagram.

    Args:
        config: Parsed Terraform configuration
        output_path: Output file path (without extension)
        format: Output format (png, svg, pdf)
        dpi: DPI for PNG output
    """
    builder = LabLinkDiagramBuilder(config, show_iam=False, show_security_groups=False)
    builder.build_main_diagram(output_path, format=format, dpi=dpi)


def generate_detailed_diagram(
    config: ParsedTerraformConfig,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
):
    """
    Generate detailed architecture diagram.

    Args:
        config: Parsed Terraform configuration
        output_path: Output file path (without extension)
        format: Output format (png, svg, pdf)
        dpi: DPI for PNG output
    """
    builder = LabLinkDiagramBuilder(config, show_iam=True, show_security_groups=True)
    builder.build_detailed_diagram(output_path, format=format, dpi=dpi)


def generate_network_flow_diagram(
    config: ParsedTerraformConfig,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
):
    """
    Generate network flow diagram.

    Args:
        config: Parsed Terraform configuration
        output_path: Output file path (without extension)
        format: Output format (png, svg, pdf)
        dpi: DPI for PNG output
    """
    builder = LabLinkDiagramBuilder(config, show_iam=False, show_security_groups=False)
    builder.build_network_flow_diagram(output_path, format=format, dpi=dpi)