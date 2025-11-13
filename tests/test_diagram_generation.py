"""Tests for diagram generation module."""


import pytest

from src.diagram_gen.generator import (
    LabLinkDiagramBuilder,
    generate_detailed_diagram,
    generate_main_diagram,
    generate_network_flow_diagram,
)
from src.terraform_parser.parser import ParsedTerraformConfig, TerraformResource


@pytest.fixture
def sample_config():
    """Create a sample Terraform configuration for testing."""
    config = ParsedTerraformConfig()

    # Add EC2 instance
    config.ec2_instances.append(
        TerraformResource(
            resource_type="aws_instance",
            name="allocator_server",
            attributes={"instance_type": "t3.large", "ami": "ami-12345678"},
        )
    )

    # Add security group
    config.security_groups.append(
        TerraformResource(
            resource_type="aws_security_group",
            name="allow_http_https",
            attributes={
                "ingress_rules": [
                    {"from_port": 80, "to_port": 80, "protocol": "tcp"},
                    {"from_port": 443, "to_port": 443, "protocol": "tcp"},
                ]
            },
        )
    )

    # Add ALB
    config.albs.append(
        TerraformResource(
            resource_type="aws_lb",
            name="allocator_alb",
            attributes={"type": "application"},
        )
    )

    # Add Lambda
    config.lambda_functions.append(
        TerraformResource(
            resource_type="aws_lambda_function",
            name="log_processor",
            attributes={"function_name": "lablink_log_processor", "runtime": "python3.11"},
        )
    )

    # Add CloudWatch
    config.cloudwatch_logs.append(
        TerraformResource(
            resource_type="aws_cloudwatch_log_group",
            name="client_logs",
            attributes={"log_group_name": "/aws/lambda/lablink-client"},
        )
    )

    # Add IAM role
    config.iam_roles.append(
        TerraformResource(
            resource_type="aws_iam_role",
            name="instance_role",
            attributes={"role_name": "lablink_instance_role"},
        )
    )

    # Add Route53
    config.route53_records.append(
        TerraformResource(
            resource_type="aws_route53_record",
            name="allocator_dns",
            attributes={"domain": "lablink.example.com", "record_type": "A"},
        )
    )

    return config


def test_diagram_builder_initialization(sample_config):
    """Test LabLinkDiagramBuilder initialization."""
    builder = LabLinkDiagramBuilder(sample_config)
    assert builder.config == sample_config
    assert builder.show_iam is True
    assert builder.show_security_groups is True

    builder_no_iam = LabLinkDiagramBuilder(sample_config, show_iam=False)
    assert builder_no_iam.show_iam is False


def test_generate_main_diagram(sample_config, tmp_path):
    """Test generating main architecture diagram."""
    output_path = tmp_path / "test-main"

    # Generate PNG
    generate_main_diagram(sample_config, output_path, format="png", dpi=150)

    # Check that file was created
    assert (tmp_path / "test-main.png").exists()


def test_generate_detailed_diagram(sample_config, tmp_path):
    """Test generating detailed architecture diagram."""
    output_path = tmp_path / "test-detailed"

    # Generate PNG
    generate_detailed_diagram(sample_config, output_path, format="png", dpi=150)

    # Check that file was created
    assert (tmp_path / "test-detailed.png").exists()


def test_generate_network_flow_diagram(sample_config, tmp_path):
    """Test generating network flow diagram."""
    output_path = tmp_path / "test-flow"

    # Generate PNG
    generate_network_flow_diagram(sample_config, output_path, format="png", dpi=150)

    # Check that file was created
    assert (tmp_path / "test-flow.png").exists()


def test_generate_svg_format(sample_config, tmp_path):
    """Test generating diagram in SVG format."""
    output_path = tmp_path / "test-svg"

    generate_main_diagram(sample_config, output_path, format="svg")

    # Check that SVG file was created
    assert (tmp_path / "test-svg.svg").exists()


def test_generate_with_custom_dpi(sample_config, tmp_path):
    """Test generating diagram with custom DPI."""
    output_path = tmp_path / "test-dpi"

    # Should not raise error with high DPI
    generate_main_diagram(sample_config, output_path, format="png", dpi=600)

    assert (tmp_path / "test-dpi.png").exists()


def test_diagram_with_minimal_config(tmp_path):
    """Test generating diagram with minimal configuration."""
    # Empty config
    config = ParsedTerraformConfig()

    # Add just one EC2 instance
    config.ec2_instances.append(
        TerraformResource(
            resource_type="aws_instance",
            name="server",
            attributes={"instance_type": "t2.micro"},
        )
    )

    output_path = tmp_path / "test-minimal"

    # Should not raise error even with minimal resources
    generate_main_diagram(config, output_path, format="png", dpi=150)
    assert (tmp_path / "test-minimal.png").exists()


def test_create_compute_components(sample_config):
    """Test creating compute components."""
    builder = LabLinkDiagramBuilder(sample_config)
    components = builder._create_compute_components()

    # Should have EC2 and Lambda components
    assert "ec2_allocator_server" in components
    assert "lambda_log_processor" in components


def test_create_network_components(sample_config):
    """Test creating network components."""
    builder = LabLinkDiagramBuilder(sample_config)
    components = builder._create_network_components()

    # Should have ALB and Route53 components
    assert "alb_allocator_alb" in components
    assert "r53_allocator_dns" in components


def test_create_observability_components(sample_config):
    """Test creating observability components."""
    builder = LabLinkDiagramBuilder(sample_config)
    components = builder._create_observability_components()

    # Should have CloudWatch components
    assert "cw_client_logs" in components


def test_create_iam_components(sample_config):
    """Test creating IAM components."""
    builder = LabLinkDiagramBuilder(sample_config, show_iam=True)
    components = builder._create_iam_components()

    # Should have IAM role
    assert "iam_instance_role" in components

    # Test with IAM disabled
    builder_no_iam = LabLinkDiagramBuilder(sample_config, show_iam=False)
    components_no_iam = builder_no_iam._create_iam_components()

    assert len(components_no_iam) == 0