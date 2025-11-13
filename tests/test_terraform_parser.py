"""Tests for Terraform parser module."""

from pathlib import Path

import pytest

from src.terraform_parser.parser import (
    parse_directory,
    parse_terraform_file,
)


@pytest.fixture
def sample_terraform_content():
    """Sample Terraform configuration content."""
    return '''
resource "aws_instance" "test_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.large"
  vpc_security_group_ids = [aws_security_group.test_sg.id]
  iam_instance_profile = aws_iam_instance_profile.test_profile.name

  tags = {
    Name = "test-server"
  }
}

resource "aws_security_group" "test_sg" {
  name        = "test-security-group"
  description = "Test security group"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "test_alb" {
  name               = "test-alb"
  load_balancer_type = "application"
}

resource "aws_lambda_function" "test_lambda" {
  function_name = "test-function"
  role          = aws_iam_role.test_role.arn
  runtime       = "python3.11"
  handler       = "lambda_function.lambda_handler"
}

resource "aws_cloudwatch_log_group" "test_logs" {
  name = "/aws/lambda/test-function"
  retention_in_days = 14
}

resource "aws_iam_role" "test_role" {
  name = "test-lambda-role"
}

resource "aws_route53_record" "test_dns" {
  zone_id = "Z1234567890"
  name    = "test.example.com"
  type    = "A"
}
'''


def test_parse_ec2_instance(tmp_path, sample_terraform_content):
    """Test parsing EC2 instance resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.ec2_instances) == 1
    ec2 = config.ec2_instances[0]
    assert ec2.name == "test_instance"
    assert ec2.attributes["instance_type"] == "t3.large"
    assert ec2.attributes["ami"] == "ami-12345678"


def test_parse_security_group(tmp_path, sample_terraform_content):
    """Test parsing security group resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.security_groups) == 1
    sg = config.security_groups[0]
    assert sg.name == "test_sg"
    assert len(sg.attributes["ingress_rules"]) == 2
    assert sg.attributes["ingress_rules"][0]["from_port"] == 80
    assert sg.attributes["ingress_rules"][1]["from_port"] == 443


def test_parse_alb(tmp_path, sample_terraform_content):
    """Test parsing ALB resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.albs) == 1
    alb = config.albs[0]
    assert alb.name == "test_alb"
    assert alb.attributes["type"] == "application"


def test_parse_lambda(tmp_path, sample_terraform_content):
    """Test parsing Lambda function resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.lambda_functions) == 1
    lambda_fn = config.lambda_functions[0]
    assert lambda_fn.name == "test_lambda"
    assert lambda_fn.attributes["function_name"] == "test-function"
    assert lambda_fn.attributes["runtime"] == "python3.11"


def test_parse_cloudwatch_logs(tmp_path, sample_terraform_content):
    """Test parsing CloudWatch log group resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.cloudwatch_logs) == 1
    cw = config.cloudwatch_logs[0]
    assert cw.name == "test_logs"
    assert cw.attributes["log_group_name"] == "/aws/lambda/test-function"


def test_parse_iam_role(tmp_path, sample_terraform_content):
    """Test parsing IAM role resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.iam_roles) == 1
    role = config.iam_roles[0]
    assert role.name == "test_role"
    assert role.attributes["role_name"] == "test-lambda-role"


def test_parse_route53(tmp_path, sample_terraform_content):
    """Test parsing Route53 record resources."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)

    assert len(config.route53_records) == 1
    r53 = config.route53_records[0]
    assert r53.name == "test_dns"
    assert r53.attributes["domain"] == "test.example.com"
    assert r53.attributes["record_type"] == "A"


def test_parse_missing_file():
    """Test error handling for missing files."""
    with pytest.raises(FileNotFoundError):
        parse_terraform_file(Path("/nonexistent/file.tf"))


def test_parse_directory(tmp_path, sample_terraform_content):
    """Test parsing multiple Terraform files in a directory."""
    # Create multiple .tf files
    (tmp_path / "main.tf").write_text(sample_terraform_content)
    (tmp_path / "alb.tf").write_text(
        'resource "aws_lb" "another_alb" { name = "alb2" }'
    )

    config = parse_directory(tmp_path)

    # Should have resources from both files
    assert len(config.ec2_instances) == 1
    assert len(config.albs) == 2  # One from main.tf, one from alb.tf


def test_parse_directory_no_tf_files(tmp_path):
    """Test error handling when directory has no .tf files."""
    with pytest.raises(ValueError, match="No .tf files found"):
        parse_directory(tmp_path)


def test_parse_directory_missing_directory():
    """Test error handling for missing directory."""
    with pytest.raises(FileNotFoundError):
        parse_directory(Path("/nonexistent/directory"))


def test_get_all_resources(tmp_path, sample_terraform_content):
    """Test getting all resources as a flat list."""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(sample_terraform_content)

    config = parse_terraform_file(tf_file)
    all_resources = config.get_all_resources()

    # Should have all resource types
    assert len(all_resources) == 7  # EC2, SG, ALB, Lambda, CW, IAM, Route53