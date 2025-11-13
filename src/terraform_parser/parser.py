"""Parse Terraform configuration files to extract infrastructure resources."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TerraformResource:
    """Represents a Terraform resource definition."""

    resource_type: str
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    is_conditional: bool = False  # True if resource has count with conditional
    condition: str = ""  # The condition expression (e.g., "ssl_provider == acm")
    tier: str = "infrastructure"  # "infrastructure" or "client_vm"


@dataclass
class ParsedTerraformConfig:
    """Collection of parsed Terraform resources."""

    ec2_instances: list[TerraformResource] = field(default_factory=list)
    security_groups: list[TerraformResource] = field(default_factory=list)
    albs: list[TerraformResource] = field(default_factory=list)
    eips: list[TerraformResource] = field(default_factory=list)
    route53_records: list[TerraformResource] = field(default_factory=list)
    lambda_functions: list[TerraformResource] = field(default_factory=list)
    cloudwatch_logs: list[TerraformResource] = field(default_factory=list)
    iam_roles: list[TerraformResource] = field(default_factory=list)
    iam_policies: list[TerraformResource] = field(default_factory=list)
    target_groups: list[TerraformResource] = field(default_factory=list)
    subscription_filters: list[TerraformResource] = field(default_factory=list)  # NEW
    tier: str = "infrastructure"  # "infrastructure" or "client_vm"
    locals: dict[str, str] = field(default_factory=dict)  # Parsed locals variables

    def get_all_resources(self) -> list[TerraformResource]:
        """Get all resources as a flat list."""
        return (
            self.ec2_instances
            + self.security_groups
            + self.albs
            + self.eips
            + self.route53_records
            + self.lambda_functions
            + self.cloudwatch_logs
            + self.iam_roles
            + self.iam_policies
            + self.target_groups
        )


def parse_terraform_file(file_path: Path) -> ParsedTerraformConfig:
    """
    Parse a single Terraform file and extract resource definitions.

    Args:
        file_path: Path to the .tf file

    Returns:
        ParsedTerraformConfig with extracted resources

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be parsed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Terraform file not found: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        raise ValueError(f"Failed to read {file_path}: {e}")

    config = ParsedTerraformConfig()

    # Parse EC2 instances
    ec2_pattern = r'resource\s+"aws_instance"\s+"([^"]+)"\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    for match in re.finditer(ec2_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        # Extract instance_type (handle both quoted strings AND local references)
        if m := re.search(r'instance_type\s*=\s*"([^"]+)"', body):
            attrs["instance_type"] = m.group(1)
        elif m := re.search(r'instance_type\s*=\s*(local\.\w+)', body):
            attrs["instance_type"] = m.group(1)  # Will be resolved later
        # Extract AMI
        if m := re.search(r'ami\s*=\s*"([^"]+)"', body):
            attrs["ami"] = m.group(1)
        # Extract security groups
        sg_matches = re.findall(r'vpc_security_group_ids\s*=\s*\[([^\]]+)\]', body)
        if sg_matches:
            attrs["security_groups"] = [
                sg.strip().strip('"')
                for sg in sg_matches[0].split(",")
                if sg.strip()
            ]
        # Extract IAM instance profile
        if m := re.search(r'iam_instance_profile\s*=\s*[^.]+\.([^.]+)\.name', body):
            attrs["iam_role"] = m.group(1)

        config.ec2_instances.append(
            TerraformResource(
                resource_type="aws_instance", name=name, attributes=attrs
            )
        )

    # Parse security groups
    sg_pattern = r'resource\s+"aws_security_group"\s+"([^"]+)"\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    for match in re.finditer(sg_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        # Extract ingress rules
        ingress_rules = []
        for ing in re.finditer(
            r'ingress\s*\{([^}]+)\}', body, re.DOTALL
        ):
            rule = {}
            ing_body = ing.group(1)
            if m := re.search(r'from_port\s*=\s*(\d+)', ing_body):
                rule["from_port"] = int(m.group(1))
            if m := re.search(r'to_port\s*=\s*(\d+)', ing_body):
                rule["to_port"] = int(m.group(1))
            if m := re.search(r'protocol\s*=\s*"([^"]+)"', ing_body):
                rule["protocol"] = m.group(1)
            ingress_rules.append(rule)
        if ingress_rules:
            attrs["ingress_rules"] = ingress_rules

        config.security_groups.append(
            TerraformResource(
                resource_type="aws_security_group", name=name, attributes=attrs
            )
        )

    # Parse ALBs
    alb_pattern = r'resource\s+"aws_lb"\s+"([^"]+)"\s*\{([^}]+)\}'
    for match in re.finditer(alb_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'load_balancer_type\s*=\s*"([^"]+)"', body):
            attrs["type"] = m.group(1)

        config.albs.append(
            TerraformResource(resource_type="aws_lb", name=name, attributes=attrs)
        )

    # Parse EIPs
    eip_pattern = r'resource\s+"aws_eip"\s+"([^"]+)"\s*\{([^}]+)\}'
    for match in re.finditer(eip_pattern, content, re.DOTALL):
        name = match.group(1)
        config.eips.append(
            TerraformResource(resource_type="aws_eip", name=name, attributes={})
        )

    # Parse Route53 records
    r53_pattern = r'resource\s+"aws_route53_record"\s+"([^"]+)"\s*\{([^}]+)\}'
    for match in re.finditer(r53_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'type\s*=\s*"([^"]+)"', body):
            attrs["record_type"] = m.group(1)
        if m := re.search(r'name\s*=\s*"([^"]+)"', body):
            attrs["domain"] = m.group(1)

        config.route53_records.append(
            TerraformResource(
                resource_type="aws_route53_record", name=name, attributes=attrs
            )
        )

    # Parse Lambda functions
    lambda_pattern = r'resource\s+"aws_lambda_function"\s+"([^"]+)"\s*\{([^}]+)\}'
    for match in re.finditer(lambda_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'function_name\s*=\s*"([^"]+)"', body):
            attrs["function_name"] = m.group(1)
        if m := re.search(r'runtime\s*=\s*"([^"]+)"', body):
            attrs["runtime"] = m.group(1)
        if m := re.search(r'role\s*=\s*[^.]+\.([^.]+)\.arn', body):
            attrs["iam_role"] = m.group(1)

        config.lambda_functions.append(
            TerraformResource(
                resource_type="aws_lambda_function", name=name, attributes=attrs
            )
        )

    # Parse CloudWatch Log Groups
    cw_pattern = r'resource\s+"aws_cloudwatch_log_group"\s+"([^"]+)"\s*\{([^}]+)\}'
    for match in re.finditer(cw_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'name\s*=\s*"([^"]+)"', body):
            attrs["log_group_name"] = m.group(1)

        config.cloudwatch_logs.append(
            TerraformResource(
                resource_type="aws_cloudwatch_log_group", name=name, attributes=attrs
            )
        )

    # Parse IAM Roles
    iam_role_pattern = r'resource\s+"aws_iam_role"\s+"([^"]+)"\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    for match in re.finditer(iam_role_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'name\s*=\s*"([^"]+)"', body):
            attrs["role_name"] = m.group(1)

        config.iam_roles.append(
            TerraformResource(
                resource_type="aws_iam_role", name=name, attributes=attrs
            )
        )

    # Parse IAM Policies
    iam_policy_pattern = (
        r'resource\s+"aws_iam_policy"\s+"([^"]+)"\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    )
    for match in re.finditer(iam_policy_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'name\s*=\s*"([^"]+)"', body):
            attrs["policy_name"] = m.group(1)

        config.iam_policies.append(
            TerraformResource(
                resource_type="aws_iam_policy", name=name, attributes=attrs
            )
        )

    # Parse Target Groups
    tg_pattern = r'resource\s+"aws_lb_target_group"\s+"([^"]+)"\s*\{([^}]+)\}'
    for match in re.finditer(tg_pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}
        if m := re.search(r'port\s*=\s*(\d+)', body):
            attrs["port"] = int(m.group(1))
        if m := re.search(r'protocol\s*=\s*"([^"]+)"', body):
            attrs["protocol"] = m.group(1)

        config.target_groups.append(
            TerraformResource(
                resource_type="aws_lb_target_group", name=name, attributes=attrs
            )
        )

    # PHASE 1: Parse locals block FIRST
    config.locals = parse_locals_block(content)

    # PHASE 2: Parse subscription filters
    parse_subscription_filters(content, config)

    # PHASE 3: Detect conditional resources and resolve variable references
    detect_conditional_resources(content, config)
    resolve_variable_references(config)

    return config


def parse_locals_block(content: str) -> dict[str, str]:
    """
    Parse the locals {} block and extract variable definitions.

    Args:
        content: Terraform file content

    Returns:
        Dictionary mapping local variable names to their values
    """
    locals_dict = {}

    # Strategy: Search the entire file content for specific patterns
    # This is more robust than trying to extract the locals block perfectly

    # Parse simple string assignments anywhere: name = "value"
    for m in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', content):
        name = m.group(1)
        value = m.group(2)
        locals_dict[name] = value

    # Parse simple equals comparisons: name = something == "value"
    for m in re.finditer(r'(\w+)\s*=\s*(\S+)\s*==\s*"([^"]+)"', content):
        name = m.group(1)
        # Store the whole expression for now
        locals_dict[name] = f'{m.group(2)} == "{m.group(3)}"'

    return locals_dict


def parse_subscription_filters(content: str, config: ParsedTerraformConfig):
    """
    Parse CloudWatch subscription filter resources.

    Args:
        content: Terraform file content
        config: Config object to add subscription filters to
    """
    pattern = r'resource\s+"aws_cloudwatch_log_subscription_filter"\s+"([^"]+)"\s*\{([^}]+)\}'

    for match in re.finditer(pattern, content, re.DOTALL):
        name = match.group(1)
        body = match.group(2)

        attrs = {}

        # Parse destination_arn (Lambda function reference)
        if m := re.search(r'destination_arn\s*=\s*(\S+)', body):
            attrs['destination_arn'] = m.group(1)

        # Parse log_group_name (CloudWatch log group reference)
        if m := re.search(r'log_group_name\s*=\s*(\S+)', body):
            attrs['log_group_name'] = m.group(1)

        # Parse filter_pattern
        if m := re.search(r'filter_pattern\s*=\s*"([^"]*)"', body):
            attrs['filter_pattern'] = m.group(1)

        config.subscription_filters.append(
            TerraformResource(
                resource_type='aws_cloudwatch_log_subscription_filter',
                name=name,
                attributes=attrs
            )
        )


def detect_conditional_resources(content: str, config: ParsedTerraformConfig):
    """
    Detect resources with count conditionals and mark them.

    Args:
        content: Terraform file content
        config: Config object with resources to check
    """
    # Pattern to match resource blocks with their full content
    resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'

    for match in re.finditer(resource_pattern, content, re.DOTALL):
        resource_type = match.group(1)
        resource_name = match.group(2)
        body = match.group(3)

        # Check for count parameter
        count_match = re.search(r'count\s*=\s*(.+?)(?:\n|$)', body)

        if count_match:
            count_expr = count_match.group(1).strip()

            # Detect ternary conditional: condition ? 1 : 0
            if '?' in count_expr and ':' in count_expr:
                # Extract condition (before the ?)
                condition = count_expr.split('?')[0].strip()

                # Find the matching resource and mark it
                for resource_list in [
                    config.ec2_instances, config.albs, config.route53_records,
                    config.lambda_functions, config.cloudwatch_logs, config.target_groups
                ]:
                    for resource in resource_list:
                        if resource.resource_type == resource_type and resource.name == resource_name:
                            resource.is_conditional = True
                            resource.condition = condition


def resolve_variable_references(config: ParsedTerraformConfig):
    """
    Resolve local.variable_name references in resource attributes.

    Args:
        config: Config object with locals and resources
    """
    # Get all resources
    all_resources = config.get_all_resources()

    for resource in all_resources:
        for key, value in resource.attributes.items():
            if isinstance(value, str):
                # Check if it's a local variable reference
                if value.startswith('local.'):
                    var_name = value.replace('local.', '')
                    if var_name in config.locals:
                        # Resolve the reference
                        resource.attributes[key] = config.locals[var_name]

                # Also handle embedded local references (e.g., in interpolations)
                for var_name, var_value in config.locals.items():
                    value = value.replace(f'local.{var_name}', var_value)
                    resource.attributes[key] = value

        # Also resolve in condition strings
        if resource.condition:
            for var_name, var_value in config.locals.items():
                resource.condition = resource.condition.replace(f'local.{var_name}', var_value)


def parse_directory(directory_path: Path) -> ParsedTerraformConfig:
    """
    Parse all Terraform files in a directory.

    Args:
        directory_path: Path to directory containing .tf files

    Returns:
        ParsedTerraformConfig with all extracted resources

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If no .tf files found or parsing fails
    """
    if not directory_path.exists() or not directory_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    tf_files = list(directory_path.glob("*.tf"))
    if not tf_files:
        raise ValueError(f"No .tf files found in {directory_path}")

    combined_config = ParsedTerraformConfig()

    for tf_file in tf_files:
        try:
            file_config = parse_terraform_file(tf_file)

            # Merge resources
            combined_config.ec2_instances.extend(file_config.ec2_instances)
            combined_config.security_groups.extend(file_config.security_groups)
            combined_config.albs.extend(file_config.albs)
            combined_config.eips.extend(file_config.eips)
            combined_config.route53_records.extend(file_config.route53_records)
            combined_config.lambda_functions.extend(file_config.lambda_functions)
            combined_config.cloudwatch_logs.extend(file_config.cloudwatch_logs)
            combined_config.iam_roles.extend(file_config.iam_roles)
            combined_config.iam_policies.extend(file_config.iam_policies)
            combined_config.target_groups.extend(file_config.target_groups)
            combined_config.subscription_filters.extend(file_config.subscription_filters)

            # Merge locals (later files override earlier ones)
            combined_config.locals.update(file_config.locals)

        except Exception as e:
            raise ValueError(f"Failed to parse {tf_file}: {e}")

    return combined_config