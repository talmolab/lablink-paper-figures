"""Generate architecture diagrams from parsed Terraform resources."""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.management import CloudwatchLogs
from diagrams.aws.network import ALB, ELB, Route53
from diagrams.aws.security import IAMRole
from diagrams.custom import Custom
from diagrams.onprem.client import User, Users

from src.terraform_parser.parser import ParsedTerraformConfig


class LabLinkDiagramBuilder:
    """Builder class for creating LabLink architecture diagrams."""

    # Font size presets for different output contexts
    FONT_PRESETS = {
        "paper": {"title": 32, "node": 14, "edge": 14},
        "poster": {"title": 48, "node": 20, "edge": 20},
        "presentation": {"title": 40, "node": 16, "edge": 16},  # Future use
    }

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

    def _create_graph_attr(
        self, dpi: int = 300, title_on_top: bool = True, fontsize_preset: str = "paper"
    ) -> dict:
        """Create consistent graph attributes for all diagrams.

        Args:
            dpi: Dots per inch for output resolution
            title_on_top: Whether to place title at top (True) or bottom (False)
            fontsize_preset: Font size preset ("paper", "poster", or "presentation")

        Returns:
            Dictionary of graph attributes for Diagram constructor
        """
        fonts = self.FONT_PRESETS[fontsize_preset]

        # Dynamic spacing based on font preset
        # Larger fonts need more space to prevent overlap
        spacing = {
            "paper": {"nodesep": "1.0", "ranksep": "1.5"},  # Increased significantly to prevent overlap
            "poster": {"nodesep": "1.5", "ranksep": "2.0"},  # Even more space for 20pt fonts
            "presentation": {"nodesep": "1.2", "ranksep": "1.7"},  # Intermediate spacing
        }[fontsize_preset]

        return {
            "fontsize": str(fonts["title"]),
            "fontname": "Helvetica",
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": spacing["nodesep"],
            "ranksep": spacing["ranksep"],
            "splines": "ortho",
            "labelloc": "t" if title_on_top else "b",  # Title placement
        }

    def _create_node_attr(self, fontsize_preset: str = "paper") -> dict:
        """Create consistent node attributes.

        Args:
            fontsize_preset: Font size preset ("paper", "poster", or "presentation")

        Returns:
            Dictionary of node attributes
        """
        fonts = self.FONT_PRESETS[fontsize_preset]
        return {
            "fontsize": str(fonts["node"]),
            "fontname": "Helvetica",
        }

    def _create_edge_attr(self, fontsize_preset: str = "paper") -> dict:
        """Create consistent edge attributes.

        Args:
            fontsize_preset: Font size preset ("paper", "poster", or "presentation")

        Returns:
            Dictionary of edge attributes
        """
        fonts = self.FONT_PRESETS[fontsize_preset]
        return {
            "fontsize": str(fonts["edge"]),
            "fontname": "Helvetica",
            "labeldistance": "2.0",
            "labelangle": "0",
            "labelfloat": "true",  # Allow labels to float for clarity
        }

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
        self, output_path: Path, format: str = "png", dpi: int = 300, fontsize_preset: str = "paper"
    ):
        """
        Build simplified main architecture diagram for paper/poster.

        Args:
            output_path: Path where diagram will be saved (without extension)
            format: Output format (png, svg, pdf)
            dpi: DPI for PNG output
            fontsize_preset: Font size preset ("paper", "poster", or "presentation")
        """
        # Use helper methods for consistent attributes
        graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)
        node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
        edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)
        edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])

        with Diagram(
            "LabLink Core Architecture",
            filename=str(output_path),
            outformat=format,
            show=False,
            direction="LR",  # Left to right for better space use
            graph_attr=graph_attr,
            edge_attr=edge_attr,
            node_attr=node_attr,
        ):
            # External access (single admin user)
            admin = User("Admin")

            # Cluster 1: LabLink Infrastructure
            with Cluster("LabLink Infrastructure"):
                # Create allocator manually (don't use _create_compute_components to avoid Lambda duplication)
                allocator = EC2("Allocator")

            # Cluster 2: Dynamic Compute - Show multiple VMs to illustrate multi-tenancy
            with Cluster("Dynamic Compute"):
                client_vm1 = EC2("Client VM")
                client_vm2 = EC2("Client VM")
                client_vm3 = EC2("Client VM")

            # Cluster 3: Observability (AWS CloudWatch)
            with Cluster("Observability"):
                # AWS CloudWatch Logs - collects from client VMs
                cloudwatch = CloudwatchLogs("Client VM Logs\n(AWS CloudWatch)")

                # Lambda processes logs and calls back to allocator
                log_processor = Lambda("Log Processor")

            # Simple, clean flows
            admin >> Edge(label="API Requests", fontsize=edge_fontsize) >> allocator

            # Allocator provisions multiple VMs
            allocator >> Edge(label="Provisions", fontsize=edge_fontsize, color="#fd7e14") >> client_vm1
            allocator >> Edge(label="Provisions", fontsize=edge_fontsize, color="#fd7e14") >> client_vm2
            allocator >> Edge(label="Provisions", fontsize=edge_fontsize, color="#fd7e14") >> client_vm3

            # All VMs send logs to CloudWatch
            client_vm1 >> Edge(label="Logs", fontsize=edge_fontsize) >> cloudwatch
            client_vm2 >> Edge(label="Logs", fontsize=edge_fontsize) >> cloudwatch
            client_vm3 >> Edge(label="Logs", fontsize=edge_fontsize) >> cloudwatch

            cloudwatch >> Edge(label="Triggers", fontsize=edge_fontsize) >> log_processor

            log_processor >> Edge(label="Callback", fontsize=edge_fontsize) >> allocator

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

    def build_vm_provisioning_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
        fontsize_preset: str = "paper",
    ) -> None:
        """Generate VM provisioning diagram (Priority 1).

        Shows: Admin → Allocator → Terraform subprocess → AWS EC2
        with 3-phase startup sequence and timing metrics.

        Code references:
        - main.py::launch() - Terraform subprocess execution
        - terraform/main.tf - Client VM provisioning
        - user_data.sh - Cloud-init phase
        - start.sh - Container startup phase
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.onprem.client import User
        from diagrams.onprem.container import Docker
        from diagrams.generic.blank import Blank
        from diagrams.custom import Custom
        from pathlib import Path as FilePath

        graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)
        node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
        edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)

        # Get edge label font size for consistency
        edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])

        with Diagram(
            "LabLink VM Provisioning Workflow",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            admin = User("Admin")

            with Cluster("LabLink Infrastructure"):
                allocator = EC2("Allocator")
                database = RDS("PostgreSQL")

            with Cluster("Provisioning"):
                # Use official Terraform icon (PNG) with fallback to Blank
                terraform_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "terraform.png"
                if terraform_icon_path.exists():
                    terraform = Custom("Terraform\nSubprocess", str(terraform_icon_path))
                else:
                    terraform = Blank("Terraform\nSubprocess")

            with Cluster("Dynamic Compute"):
                client_vm = EC2("Client VM")

            with Cluster("3-Phase Startup Sequence"):
                # Phase 1: Cloud-init with OS icon
                cloud_init_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "cloud-init.png"
                if cloud_init_icon_path.exists():
                    phase1 = Custom("1. Cloud-init\nInstall agents", str(cloud_init_icon_path))
                else:
                    phase1 = Blank("1. Cloud-init\nInstall agents")

                # Phase 2: Docker
                phase2 = Docker("2. Docker\nPull image")

                # Phase 3: Application ready with app icon
                app_icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "application.png"
                if app_icon_path.exists():
                    phase3 = Custom("3. Application\nSoftware ready", str(app_icon_path))
                else:
                    phase3 = Blank("3. Application\nSoftware ready")

            # Main provisioning flow
            admin >> Edge(label="1. POST /api/launch", fontsize=edge_fontsize) >> allocator
            allocator >> Edge(
                label="2. Execute terraform apply",
                fontsize=edge_fontsize,
                color="#fd7e14",
            ) >> terraform
            terraform >> Edge(
                label="3. Provisions",
                fontsize=edge_fontsize,
                color="#fd7e14",
            ) >> client_vm

            # Startup sequence
            client_vm >> Edge(label="Starts", fontsize=edge_fontsize) >> phase1
            phase1 >> Edge(fontsize=edge_fontsize) >> phase2
            phase2 >> Edge(fontsize=edge_fontsize) >> phase3

            # VM feedback flow
            phase3 >> Edge(
                label="4. Status updates\n(POST /api/vm-metrics)",
                fontsize=edge_fontsize,
                style="dashed",
                color="#28a745",
            ) >> allocator
            allocator >> Edge(
                label="5. Store provisioning metrics",
                fontsize=edge_fontsize,
            ) >> database

        print(f"VM provisioning diagram saved to {output_path}")

    def build_crd_connection_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
        fontsize_preset: str = "paper",
    ) -> None:
        """Generate CRD connection setup diagram (Priority 1).

        Shows: User → Allocator → PostgreSQL (TRIGGER) → Client VM (subscribe)
        → Chrome Remote Desktop

        Code references:
        - main.py::submit_vm_details() - User request handling
        - database.py::assign_vm() - UPDATE VM record
        - generate_init_sql.py - TRIGGER definition
        - subscribe.py - LISTEN for notifications
        - connect_crd.py - Execute CRD command
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.onprem.client import User, Client
        from diagrams.onprem.database import Postgresql
        from diagrams.programming.language import Python

        graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)
        node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
        edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)

        # Get edge label font size for consistency
        edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])

        with Diagram(
            "LabLink CRD Connection via PostgreSQL LISTEN/NOTIFY",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            user = User("User")

            with Cluster("LabLink Infrastructure"):
                allocator = EC2("Allocator")

            with Cluster("PostgreSQL Database"):
                vm_table = RDS("VM Table")
                trigger = RDS("Database TRIGGER\n(on CrdCommand)")
                pg_notify = Postgresql("pg_notify()")

                vm_table >> Edge(label="UPDATE", fontsize=edge_fontsize) >> trigger
                trigger >> Edge(label="Fires", fontsize=edge_fontsize) >> pg_notify

            with Cluster("Client VM (Admin-provisioned)"):
                client_vm = EC2("Client VM")
                subscribe_service = Python("subscribe.py\n(LISTEN)")
                crd_connector = Python("connect_crd.py")

            crd_app = Client("Chrome Remote\nDesktop")

            # Main flow
            user >> Edge(label="1. Request VM", fontsize=edge_fontsize) >> allocator
            allocator >> Edge(label="2. Assign VM\nUPDATE vm_table", fontsize=edge_fontsize) >> vm_table
            pg_notify >> Edge(
                label="3. Notification\n(async, channel 'vm_updates')",
                fontsize=edge_fontsize,
                style="dashed",
            ) >> subscribe_service
            subscribe_service >> Edge(label="4. Execute CRD command", fontsize=edge_fontsize) >> crd_connector
            crd_connector >> Edge(label="5. Authenticates & Connects", fontsize=edge_fontsize, color="#28a745") >> crd_app
            crd_app >> Edge(
                label="6. Chrome Remote Desktop Connection",
                fontsize=edge_fontsize,
                color="#28a745",
                style="dashed",
            ) >> user

        print(f"CRD connection diagram saved to {output_path}")

    def build_logging_pipeline_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
        fontsize_preset: str = "paper",
    ) -> None:
        """Generate enhanced logging pipeline diagram (Priority 1).

        Shows: Client VM → CloudWatch Agent → CloudWatch Logs →
        Subscription Filter → Lambda → Allocator API → PostgreSQL

        Code references:
        - user_data.sh - CloudWatch agent installation
        - lambda_function.py - Log processing
        - main.py::receive_vm_logs() - Log storage
        - database.py::save_logs_by_hostname() - Database persistence
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.aws.compute import EC2, Lambda
        from diagrams.aws.management import CloudwatchLogs, CloudwatchEventEventBased, Cloudwatch
        from diagrams.aws.database import RDS
        from diagrams.onprem.client import User

        graph_attr = self._create_graph_attr(dpi=dpi, title_on_top=True, fontsize_preset=fontsize_preset)
        node_attr = self._create_node_attr(fontsize_preset=fontsize_preset)
        edge_attr = self._create_edge_attr(fontsize_preset=fontsize_preset)

        # Get edge label font size for consistency
        edge_fontsize = str(self.FONT_PRESETS[fontsize_preset]["edge"])

        with Diagram(
            "LabLink Logging Pipeline",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            admin = User("Admin")

            with Cluster("Dynamic Compute"):
                client_vm = EC2("Client VM")
                cw_agent = Cloudwatch("CloudWatch\nAgent")

            with Cluster("Observability"):
                log_group = CloudwatchLogs("Client VM Logs\n(AWS CloudWatch)")
                subscription = CloudwatchEventEventBased("Subscription\nFilter\n(pattern: all events)")
                log_processor = Lambda("Log Processor")

            with Cluster("LabLink Infrastructure"):
                allocator = EC2("Allocator")
                database = RDS("PostgreSQL")

            # Logging flow
            client_vm >> Edge(label="1. Application logs", fontsize=edge_fontsize) >> cw_agent
            cw_agent >> Edge(
                label="2. PutLogEvents API\n(gzip compressed)",
                fontsize=edge_fontsize,
            ) >> log_group
            log_group >> Edge(
                label="3. Triggers (on pattern match)",
                fontsize=edge_fontsize,
                style="dashed",
            ) >> subscription
            subscription >> Edge(label="4. Invokes", fontsize=edge_fontsize) >> log_processor
            log_processor >> Edge(
                label="5. POST /api/vm-logs\n(parsed JSON)",
                fontsize=edge_fontsize,
            ) >> allocator
            allocator >> Edge(label="6. Store logs", fontsize=edge_fontsize) >> database
            database >> Edge(label="7. View logs (web UI)", fontsize=edge_fontsize, style="dashed") >> admin

        print(f"Logging pipeline diagram saved to {output_path}")

    def build_cicd_workflow_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
    ) -> None:
        """Generate CI/CD pipeline and GitHub workflows diagram (Priority 2).

        Shows: GitHub Actions workflows for continuous integration, testing,
        building, deployment, and infrastructure destruction.

        Workflows:
        - ci.yml - Lint, test, build
        - lablink-images.yml - Docker image builds
        - publish-pip.yml - PyPI publishing
        - terraform-deploy.yml - Infrastructure deployment
        - terraform-destroy.yml - Infrastructure teardown
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.onprem.vcs import Github
        from diagrams.programming.language import Python
        from diagrams.onprem.container import Docker
        from diagrams.aws.compute import EC2
        from diagrams.generic.blank import Blank

        graph_attr = {
            "fontsize": "32",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": "0.6",
            "ranksep": "0.8",
            "splines": "ortho",
        }

        node_attr = {
            "fontsize": "11",
            "fontname": "Helvetica",
        }

        edge_attr = {
            "fontsize": "12",
            "fontname": "Helvetica",
            "labeldistance": "2.0",
            "labelangle": "0",
        }

        with Diagram(
            "LabLink CI/CD Pipeline",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            pr_event = Github("Pull Request /\nPush Event")

            with Cluster("Continuous Integration"):
                ci_workflow = Blank("ci.yml")
                lint = Blank("Lint\n(ruff)")
                test = Blank("Test\n(pytest 90% coverage)")
                build_test = Blank("Docker Build Test")

            with Cluster("Image Building"):
                images_workflow = Blank("lablink-images.yml")
                dev_build = Docker("Build Dev Images")
                prod_build = Docker("Build Prod Images")

            with Cluster("Package Publishing"):
                publish_workflow = Blank("publish-pip.yml")
                pypi = Python("PyPI\n(Trusted Publishing)")

            with Cluster("Infrastructure Deployment"):
                deploy_workflow = Blank("terraform-deploy.yml")
                terraform_deploy = Blank("Terraform Apply")
                allocator = EC2("Allocator\nDeployed")

            with Cluster("Infrastructure Teardown"):
                destroy_workflow = Blank("terraform-destroy.yml")
                terraform_destroy = Blank("Terraform Destroy")

            # CI flow
            pr_event >> Edge(label="Triggers", fontsize="14") >> ci_workflow
            ci_workflow >> Edge(fontsize="12") >> lint
            ci_workflow >> Edge(fontsize="12") >> test
            ci_workflow >> Edge(fontsize="12") >> build_test

            # Image building flow
            pr_event >> Edge(label="Triggers", fontsize="14") >> images_workflow
            images_workflow >> Edge(fontsize="12") >> dev_build
            images_workflow >> Edge(fontsize="12", label="On release") >> prod_build

            # Publishing flow
            pr_event >> Edge(label="Triggers\n(on release)", fontsize="14") >> publish_workflow
            publish_workflow >> Edge(fontsize="12", label="OIDC Auth") >> pypi

            # Deployment flow
            pr_event >> Edge(label="Manual trigger\n(workflow_dispatch)", fontsize="14") >> deploy_workflow
            deploy_workflow >> Edge(fontsize="12") >> terraform_deploy
            terraform_deploy >> Edge(fontsize="12", color="#28a745") >> allocator

            # Destruction flow
            pr_event >> Edge(label="Manual trigger\n(workflow_dispatch)", fontsize="14") >> destroy_workflow
            destroy_workflow >> Edge(fontsize="12", color="#dc3545") >> terraform_destroy
            terraform_destroy >> Edge(fontsize="12", color="#dc3545") >> allocator

        print(f"CI/CD workflow diagram saved to {output_path}")

    def build_api_architecture_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
    ) -> None:
        """Generate API endpoint architecture diagram (Priority 2).

        Shows: All 22 Flask API endpoints categorized by function:
        - Public endpoints (12): /, /api/request_vm, /vm_startup, etc.
        - Admin endpoints (10): /admin, /api/launch, /destroy, etc.
        With HTTP methods, auth requirements, and data flow.
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.onprem.client import User, Client
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.generic.blank import Blank
        from diagrams.programming.framework import Flask

        graph_attr = {
            "fontsize": "32",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": "0.6",
            "ranksep": "0.8",
        }

        node_attr = {
            "fontsize": "10",
            "fontname": "Helvetica",
        }

        edge_attr = {
            "fontsize": "11",
            "fontname": "Helvetica",
        }

        with Diagram(
            "LabLink API Architecture",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            user = User("User")
            admin = User("Admin")

            with Cluster("Allocator Flask API"):
                api_server = Flask("Flask API\nServer")

                with Cluster("Public Endpoints (12)"):
                    home = Blank("GET /")
                    request_vm = Blank("POST /api/request_vm")
                    vm_startup = Blank("POST /vm_startup")
                    update_inuse = Blank("POST /api/update_inuse_status")
                    gpu_health = Blank("POST /api/gpu_health")
                    vm_status_api = Blank("GET /api/vm-status")
                    vm_logs_api = Blank("POST /api/vm-logs")
                    vm_metrics = Blank("POST /api/vm-metrics")

                with Cluster("Admin Endpoints (10)"):
                    admin_panel = Blank("GET /admin\n(HTTP Basic Auth)")
                    create_vm = Blank("POST /admin/create")
                    instances = Blank("GET /admin/instances")
                    launch = Blank("POST /api/launch")
                    destroy = Blank("POST /destroy")
                    scp_client = Blank("POST /api/scp-client")

            database = RDS("PostgreSQL")
            client_vm = EC2("Client VM")

            # Public endpoint flows
            user >> Edge(label="Request VM", fontsize="11") >> request_vm
            request_vm >> Edge(fontsize="11") >> database

            client_vm >> Edge(label="Startup info", fontsize="11") >> vm_startup
            vm_startup >> Edge(fontsize="11") >> database

            client_vm >> Edge(label="Health data", fontsize="11") >> gpu_health
            gpu_health >> Edge(fontsize="11") >> database

            # Admin endpoint flows
            admin >> Edge(label="HTTP Basic Auth", fontsize="11", color="#ffc107") >> admin_panel
            admin >> Edge(label="Provision VM", fontsize="11", color="#ffc107") >> launch
            launch >> Edge(fontsize="11") >> database

            admin >> Edge(label="Teardown", fontsize="11", color="#dc3545") >> destroy
            destroy >> Edge(fontsize="11", color="#dc3545") >> database

            admin >> Edge(label="Collect data", fontsize="11", color="#28a745") >> scp_client
            scp_client >> Edge(fontsize="11", color="#28a745") >> client_vm

        print(f"API architecture diagram saved to {output_path}")

    def build_network_flow_enhanced_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
    ) -> None:
        """Generate enhanced network flow diagram with ports & protocols (Priority 2).

        Shows: Complete network topology with:
        - All ports (22, 53, 80, 443, 5000, 5432)
        - Protocols (HTTP/HTTPS, SSH, PostgreSQL, DNS, CloudWatch API)
        - Data payloads at each step
        - SSL termination strategies (4 configurations)
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.onprem.client import User
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.aws.network import Route53, ELB
        from diagrams.generic.blank import Blank

        graph_attr = {
            "fontsize": "32",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": "0.8",
            "ranksep": "1.0",
            "splines": "ortho",
        }

        node_attr = {
            "fontsize": "11",
            "fontname": "Helvetica",
        }

        edge_attr = {
            "fontsize": "12",
            "fontname": "Helvetica",
            "labeldistance": "2.0",
            "labelangle": "0",
        }

        with Diagram(
            "LabLink Network Flow with Ports & Protocols",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            user = User("User")

            with Cluster("Access Layer (Configuration-Dependent)"):
                dns = Route53("Route53\n(DNS: port 53)")
                alb = ELB("Application\nLoad Balancer\n(HTTPS: 443)")

            with Cluster("LabLink Infrastructure"):
                allocator = EC2("Allocator")
                caddy = Blank("Caddy\n(Let's Encrypt/\nCloudflare)")
                flask_app = Blank("Flask API\n(HTTP: 5000)")
                database = RDS("PostgreSQL\n(port 5432)")

            with Cluster("Dynamic Compute"):
                client_vm = EC2("Client VM\n(SSH: 22)")

            # Configuration 1: ACM with ALB (shown in blue)
            user >> Edge(
                label="HTTPS: 443\n(ACM SSL)",
                fontsize="12",
                color="#007bff",
            ) >> dns
            dns >> Edge(fontsize="12", color="#007bff") >> alb
            alb >> Edge(
                label="HTTP: 5000\n(internal)",
                fontsize="12",
                color="#007bff",
            ) >> flask_app

            # Configuration 2: Let's Encrypt/Cloudflare with Caddy (shown in green)
            user >> Edge(
                label="HTTPS: 443\n(Let's Encrypt)",
                fontsize="12",
                color="#28a745",
                style="dashed",
            ) >> dns
            dns >> Edge(
                fontsize="12",
                color="#28a745",
                style="dashed",
            ) >> caddy
            caddy >> Edge(
                label="HTTP: 5000\n(reverse proxy)",
                fontsize="12",
                color="#28a745",
                style="dashed",
            ) >> flask_app

            # Configuration 3: IP-only (shown in orange)
            user >> Edge(
                label="HTTP: 80\n(no SSL)",
                fontsize="12",
                color="#fd7e14",
                style="dotted",
            ) >> flask_app

            # Internal connections
            flask_app >> Edge(label="PostgreSQL: 5432", fontsize="12") >> database
            allocator >> Edge(label="SSH: 22\n(data collection)", fontsize="12") >> client_vm

        print(f"Enhanced network flow diagram saved to {output_path}")

    def build_monitoring_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
    ) -> None:
        """Generate VM status & health monitoring diagram (Priority 2).

        Shows: Three parallel monitoring services:
        - vm_status.py - Polls AWS EC2 API for instance state
        - health_monitoring.py - Checks GPU health and VM responsiveness
        - data_export.py - Monitors experiment completion
        With timing intervals and database updates.
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.generic.blank import Blank

        graph_attr = {
            "fontsize": "32",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": "0.8",
            "ranksep": "1.0",
        }

        node_attr = {
            "fontsize": "11",
            "fontname": "Helvetica",
        }

        edge_attr = {
            "fontsize": "12",
            "fontname": "Helvetica",
            "labeldistance": "2.0",
            "labelangle": "0",
        }

        with Diagram(
            "LabLink VM Monitoring Services",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="TB",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            with Cluster("LabLink Infrastructure"):
                allocator = EC2("Allocator")

            with Cluster("Monitoring Services (Parallel)"):
                with Cluster("VM Status Monitoring"):
                    vm_status_service = Blank("vm_status.py\n(every 60s)")
                    ec2_api = Blank("AWS EC2 API\n(DescribeInstances)")

                with Cluster("Health Monitoring"):
                    health_service = Blank("health_monitoring.py\n(every 60s)")
                    gpu_check = Blank("GPU Health Check")

                with Cluster("Data Export Monitoring"):
                    export_service = Blank("data_export.py\n(periodic)")
                    completion_check = Blank("Experiment\nCompletion Check")

            database = RDS("PostgreSQL")

            with Cluster("Dynamic Compute"):
                client_vm = EC2("Client VM")

            # VM Status monitoring flow
            vm_status_service >> Edge(label="Poll", fontsize="12", color="#007bff") >> ec2_api
            ec2_api >> Edge(label="Instance state", fontsize="12", color="#007bff") >> vm_status_service
            vm_status_service >> Edge(label="Update status", fontsize="12", color="#007bff") >> database

            # Health monitoring flow
            health_service >> Edge(label="Check health", fontsize="12", color="#28a745") >> client_vm
            client_vm >> Edge(label="GPU metrics", fontsize="12", color="#28a745") >> gpu_check
            gpu_check >> Edge(label="Health data", fontsize="12", color="#28a745") >> health_service
            health_service >> Edge(label="Update health", fontsize="12", color="#28a745") >> database

            # Data export monitoring flow
            export_service >> Edge(label="Check completion", fontsize="12", color="#fd7e14") >> client_vm
            client_vm >> Edge(label="Completion status", fontsize="12", color="#fd7e14") >> completion_check
            completion_check >> Edge(label="Trigger export", fontsize="12", color="#fd7e14") >> export_service
            export_service >> Edge(label="Update", fontsize="12", color="#fd7e14") >> database

        print(f"VM monitoring diagram saved to {output_path}")

    def build_data_collection_diagram(
        self,
        output_path: Path,
        format: str = "png",
        dpi: int = 300,
    ) -> None:
        """Generate data collection & export diagram (Priority 2).

        Shows: SSH → Docker → rsync flow:
        - Admin triggers data collection via /api/scp-client
        - Allocator SSHs to client VM
        - Docker cp extracts data from container
        - rsync transfers to allocator
        - zip packages for download
        """
        from diagrams import Diagram, Cluster, Edge
        from diagrams.onprem.client import User
        from diagrams.aws.compute import EC2
        from diagrams.onprem.container import Docker
        from diagrams.generic.blank import Blank
        from diagrams.generic.storage import Storage

        graph_attr = {
            "fontsize": "32",
            "fontname": "Helvetica",
            "bgcolor": "white",
            "dpi": str(dpi),
            "pad": "0.5",
            "nodesep": "0.8",
            "ranksep": "1.0",
            "splines": "ortho",
        }

        node_attr = {
            "fontsize": "11",
            "fontname": "Helvetica",
        }

        edge_attr = {
            "fontsize": "12",
            "fontname": "Helvetica",
            "labeldistance": "2.0",
            "labelangle": "0",
        }

        with Diagram(
            "LabLink Data Collection & Export",
            filename=str(output_path.with_suffix("")),
            show=False,
            direction="LR",
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
            outformat=format,
        ):
            admin = User("Admin")

            with Cluster("LabLink Infrastructure"):
                allocator = EC2("Allocator")
                scp_service = Blank("scp_client.py")
                zip_package = Storage("Data.zip")

            with Cluster("Dynamic Compute"):
                client_vm = EC2("Client VM")
                docker_container = Docker("Subject\nContainer")
                experiment_data = Storage("Experiment\nData")

            # Data collection flow
            admin >> Edge(label="1. POST /api/scp-client", fontsize="14") >> allocator
            allocator >> Edge(label="2. Trigger", fontsize="14") >> scp_service
            scp_service >> Edge(
                label="3. SSH (port 22)",
                fontsize="14",
                color="#007bff",
            ) >> client_vm
            client_vm >> Edge(label="4. Docker cp", fontsize="14") >> docker_container
            docker_container >> Edge(label="5. Extract files", fontsize="14") >> experiment_data
            experiment_data >> Edge(
                label="6. rsync to allocator",
                fontsize="14",
                color="#28a745",
            ) >> scp_service
            scp_service >> Edge(label="7. Create zip", fontsize="14") >> zip_package
            zip_package >> Edge(label="8. Download", fontsize="14", color="#28a745") >> admin

        print(f"Data collection diagram saved to {output_path}")


def generate_main_diagram(
    config: ParsedTerraformConfig,
    output_path: Path,
    format: str = "png",
    dpi: int = 300,
    fontsize_preset: str = "paper",
):
    """
    Generate main architecture diagram.

    Args:
        config: Parsed Terraform configuration
        output_path: Output file path (without extension)
        format: Output format (png, svg, pdf)
        dpi: DPI for PNG output
        fontsize_preset: Font size preset ("paper", "poster", or "presentation")
    """
    builder = LabLinkDiagramBuilder(config, show_iam=False, show_security_groups=False)
    builder.build_main_diagram(output_path, format=format, dpi=dpi, fontsize_preset=fontsize_preset)


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