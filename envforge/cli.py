"""Command-line interface for envforge."""

from __future__ import annotations

import argparse
import sys

from envforge.generator import generate_env_file, generate_env_string
from envforge.schema import Schema
from envforge.parser import parse_env_file
from envforge.validator import Validator


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envforge",
        description="Generate and validate .env files from schema definitions.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a .env file from a schema.")
    gen.add_argument("schema", help="Path to the JSON schema file.")
    gen.add_argument("-o", "--output", help="Output .env file path (default: stdout).")
    gen.add_argument("-e", "--environment", help="Environment name for the header comment.")
    gen.add_argument(
        "--no-comments", action="store_true", help="Omit descriptive comments."
    )
    gen.add_argument(
        "--no-defaults", action="store_true", help="Do not fill in default values."
    )

    val = sub.add_parser("validate", help="Validate a .env file against a schema.")
    val.add_argument("schema", help="Path to the JSON schema file.")
    val.add_argument("env", help="Path to the .env file to validate.")

    return parser


def cmd_generate(args: argparse.Namespace) -> int:
    try:
        schema = Schema.from_json(args.schema)
    except Exception as exc:
        print(f"[envforge] Failed to load schema: {exc}", file=sys.stderr)
        return 1

    content = generate_env_string(
        schema,
        environment=args.environment,
        include_comments=not args.no_comments,
        use_defaults=not args.no_defaults,
    )

    if args.output:
        try:
            generate_env_file(
                schema,
                args.output,
                environment=args.environment,
                include_comments=not args.no_comments,
                use_defaults=not args.no_defaults,
            )
            print(f"[envforge] Written to {args.output}")
        except OSError as exc:
            print(f"[envforge] Could not write file: {exc}", file=sys.stderr)
            return 1
    else:
        print(content, end="")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        schema = Schema.from_json(args.schema)
    except Exception as exc:
        print(f"[envforge] Failed to load schema: {exc}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(args.env)
    except OSError as exc:
        print(f"[envforge] Failed to read .env file: {exc}", file=sys.stderr)
        return 1

    validator = Validator(schema)
    result = validator.validate(env)
    if result.is_valid:
        print("[envforge] Validation passed.")
        return 0

    print("[envforge] Validation failed:")
    for err in result.errors:
        print(f"  - {err}")
    return 1


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    dispatch = {"generate": cmd_generate, "validate": cmd_validate}
    sys.exit(dispatch[args.command](args))


if __name__ == "__main__":
    main()
