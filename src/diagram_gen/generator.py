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
        show_iam: bool = True,
        show_security_groups: bool = True,
    ):
        """
        Initialize diagram builder.

        Args:
            config: Parsed Terraform configuration
            show_iam: Whether to show IAM roles in diagram
            show_security_groups: Whether to show security groups in diagram
        """
        self.config = config
        self.show_iam = show_iam
        self.show_security_groups = show_security_groups

    def _create_compute_components(self, cluster=None):
        """Create compute resource components (EC2, Lambda)."""
        components = {}

        # EC2 instances
        for ec2 in self.config.ec2_instances:
            instance_type = ec2.attributes.get("instance_type", "unknown")
            label = f"{ec2.name}\n({instance_type})"
            components[f"ec2_{ec2.name}"] = EC2(label)

        # Lambda functions
        for lambda_fn in self.config.lambda_functions:
            runtime = lambda_fn.attributes.get("runtime", "")
            label = f"{lambda_fn.name}\n{runtime}"
            components[f"lambda_{lambda_fn.name}"] = Lambda(label)

        return components

    def _create_network_components(self):
        """Create networking components (ALB, EIP, Route53)."""
        components = {}

        # ALBs
        for alb in self.config.albs:
            components[f"alb_{alb.name}"] = ALB(alb.name)

        # Route53 records
        for r53 in self.config.route53_records:
            domain = r53.attributes.get("domain", r53.name)
            components[f"r53_{r53.name}"] = Route53(domain)

        return components

    def _create_observability_components(self):
        """Create observability components (CloudWatch)."""
        components = {}

        # CloudWatch Log Groups
        for cw in self.config.cloudwatch_logs:
            log_name = cw.attributes.get("log_group_name", cw.name)
            # Shorten long names
            display_name = log_name.split("/")[-1] if "/" in log_name else log_name
            components[f"cw_{cw.name}"] = CloudwatchLogs(display_name)

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
            # External users
            users = Users("Researchers")

            # Configurable DNS/SSL Layer (show it's optional)
            with Cluster("DNS & SSL\n(Configurable)"):
                dns_components = self._create_network_components()

                # Check what's actually configured
                has_route53 = len([k for k in dns_components.keys() if k.startswith("r53_")]) > 0
                has_alb = len([k for k in dns_components.keys() if k.startswith("alb_")]) > 0

                if has_route53 or has_alb:
                    # Show actual configuration
                    if has_route53:
                        # Try multiple possible Route53 key names
                        route53 = (
                            dns_components.get("r53_lablink_alb_record")
                            or dns_components.get("r53_lablink_a_record")
                            or dns_components.get("r53_allocator_dns")
                            or next((v for k, v in dns_components.items() if k.startswith("r53_")), Route53("Route53\nDNS"))
                        )
                    if has_alb:
                        alb = dns_components.get("alb_allocator_alb") or ALB("ALB\n(ACM SSL)")
                else:
                    # Show it's configurable with options
                    route53 = Route53("DNS\n(Optional)")

            with Cluster("LabLink Core"):
                compute_components = self._create_compute_components()
                # Get allocator EC2 instance (use actual parsed resource name)
                allocator = (
                    compute_components.get("ec2_lablink_allocator_server")
                    or compute_components.get("ec2_allocator_server")
                    or EC2("Allocator\nServer")
                )

                # Client VMs (representative)
                client_vm = EC2("Client VMs\n(Dynamic)")

                # Get lambda from already-created compute_components
                log_processor = (
                    compute_components.get("lambda_log_processor")
                    or Lambda("Log\nProcessor")
                )

            with Cluster("Observability"):
                obs_components = self._create_observability_components()
                cloudwatch = (
                    obs_components.get("cw_client_vm_logs")
                    or obs_components.get("cw_lambda_logs")
                    or obs_components.get("cw_client_logs")
                    or CloudwatchLogs("CloudWatch\nLogs")
                )

            # Define flow based on what's configured
            users >> Edge(label="HTTP(S)", fontsize="16") >> route53

            if has_alb:
                route53 >> alb
                alb >> Edge(label="HTTP:5000", fontsize="16") >> allocator
            else:
                route53 >> Edge(label="HTTP(S):5000", fontsize="16") >> allocator

            # Allocator provisions client VMs
            allocator >> Edge(label="provisions", style="dashed", fontsize="16") >> client_vm

            # Logging flow
            client_vm >> Edge(label="logs", fontsize="16") >> cloudwatch
            cloudwatch >> Edge(label="triggers", fontsize="16") >> log_processor
            log_processor >> Edge(label="POST\n/api/vm-logs", fontsize="16") >> allocator

    def build_detailed_diagram(self, output_path: Path, format: str = "png", dpi: int = 300):
        """
        Build detailed architecture diagram showing all components.

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

            with Cluster("DNS Layer"):
                dns_components = self._create_network_components()
                route53_nodes = [
                    v for k, v in dns_components.items() if k.startswith("r53_")
                ]
                if not route53_nodes:
                    route53_nodes = [Route53("DNS")]

            with Cluster("Load Balancing"):
                alb_nodes = [
                    v for k, v in dns_components.items() if k.startswith("alb_")
                ]
                if not alb_nodes:
                    alb_nodes = [ALB("Application LB")]

                # Target groups
                target_group = ELB("Target Group")

            with Cluster("Compute"):
                compute_components = self._create_compute_components()
                ec2_nodes = [
                    v for k, v in compute_components.items() if k.startswith("ec2_")
                ]
                if not ec2_nodes:
                    ec2_nodes = [EC2("Allocator Server")]

                client_vms = EC2("Client VMs (dynamic)")

                lambda_nodes = [
                    v for k, v in compute_components.items() if k.startswith("lambda_")
                ]

            with Cluster("Observability & Logging"):
                obs_components = self._create_observability_components()
                cw_nodes = [
                    v for k, v in obs_components.items() if k.startswith("cw_")
                ]
                if not cw_nodes:
                    cw_nodes = [CloudwatchLogs("Log Groups")]

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
            route53_nodes[0] >> alb_nodes[0]
            alb_nodes[0] >> target_group >> ec2_nodes[0]

            # Allocator to client VMs
            ec2_nodes[0] >> Edge(style="dashed", label="provisions") >> client_vms

            # Logging flow
            client_vms >> cw_nodes[0]
            if lambda_nodes:
                cw_nodes[0] >> lambda_nodes[0] >> ec2_nodes[0]

            # IAM connections
            if self.show_iam and iam_nodes:
                for ec2 in ec2_nodes:
                    iam_nodes[0] >> Edge(style="dotted") >> ec2
                if lambda_nodes:
                    for lambda_fn in lambda_nodes:
                        iam_nodes[0] >> Edge(style="dotted") >> lambda_fn

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