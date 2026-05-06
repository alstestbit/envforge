"""CLI command for redacting sensitive values from a .env file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envforge.parser import parse_env_file
from envforge.redactor import redact_env
from envforge.schema import Schema


def cmd_redact(args: argparse.Namespace) -> int:
    """Handle the `envforge redact` subcommand."""
    env = parse_env_file(args.env_file)

    schema: Schema | None = None
    if args.schema:
        schema = Schema.from_json(Path(args.schema).read_text())

    extra_patterns = args.pattern or []
    mask = args.mask

    result = redact_env(env, schema=schema, extra_patterns=extra_patterns, mask=mask)

    if args.format == "json":
        sys.stdout.write(json.dumps(result.redacted, indent=2) + "\n")
    else:
        for key, value in result.redacted.items():
            sys.stdout.write(f"{key}={value}\n")

    if args.verbose:
        sys.stderr.write(result.summary() + "\n")

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "redact",
        help="Mask sensitive values in a .env file",
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument("--schema", help="Optional schema JSON file")
    parser.add_argument(
        "--pattern",
        action="append",
        metavar="PATTERN",
        help="Additional keyword patterns to treat as sensitive (repeatable)",
    )
    parser.add_argument(
        "--mask",
        default="***REDACTED***",
        help="Mask string to use (default: ***REDACTED***)",
    )
    parser.add_argument(
        "--format",
        choices=["env", "json"],
        default="env",
        help="Output format (default: env)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print redaction summary to stderr",
    )
    parser.set_defaults(func=cmd_redact)
