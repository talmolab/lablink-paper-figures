"""Terraform configuration file parser for extracting infrastructure resources."""

from .parser import parse_directory, parse_terraform_file

__all__ = ["parse_terraform_file", "parse_directory"]