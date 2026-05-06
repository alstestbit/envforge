"""CLI command for linting .env files against a schema."""

import argparse
import sys

from envforge.schema import Schema
from envforge.parser import parse_env_file
from envforge.linter import lint_env


def cmd_lint(args: argparse.Namespace) -> int:
    """Run lint checks on an env file against a schema. Returns exit code."""
    try:
        schema = Schema.from_json(args.schema)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError as exc:
        print(f"Error loading env file: {exc}", file=sys.stderr)
        return 2

    report = lint_env(env, schema)

    if not report.issues:
        print("No lint issues found.")
        return 0

    for issue in report.issues:
        print(str(issue))

    print()
    print(report.summary())

    return 0 if report.passed else 1


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "lint",
        help="Lint a .env file for style and convention issues",
    )
    parser.add_argument(
        "schema",
        help="Path to the JSON schema file",
    )
    parser.add_argument(
        "env_file",
        help="Path to the .env file to lint",
    )
    parser.set_defaults(func=cmd_lint)
