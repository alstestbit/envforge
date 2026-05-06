"""CLI command for exporting .env files to alternate formats."""

import argparse
import sys
from typing import Optional

from envforge.parser import parse_env_file
from envforge.exporter import export_env, SUPPORTED_FORMATS


def cmd_export(args: argparse.Namespace) -> int:
    """Handle the 'export' subcommand.

    Reads a .env file and writes it out in the requested format.
    Returns an exit code (0 = success, 1 = error).
    """
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: env file not found: {args.env_file}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 1

    try:
        result = export_env(env, fmt=args.format, output_path=args.output)
    except (ValueError, RuntimeError) as exc:
        print(f"Export error: {exc}", file=sys.stderr)
        return 1

    if not args.output:
        print(result)

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'export' subcommand onto an existing subparser group."""
    parser = subparsers.add_parser(
        "export",
        help="Export a .env file to JSON, YAML, or TOML format.",
    )
    parser.add_argument(
        "env_file",
        help="Path to the .env file to export.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS,
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    parser.set_defaults(func=cmd_export)
