"""CLI command for pinning live env values as schema defaults."""

import argparse
import sys

from envforge.parser import parse_env_file
from envforge.schema import Schema
from envforge.pinner import pin_env
from envforge.generator import generate_env_string


def cmd_pin(args: argparse.Namespace) -> int:
    try:
        schema = Schema.from_json(args.schema)
    except Exception as exc:
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(args.env)
    except FileNotFoundError:
        print(f"error: env file not found: {args.env}", file=sys.stderr)
        return 1

    result = pin_env(schema, env)

    if args.verbose:
        for entry in result.entries:
            print(entry)
        if result.skipped:
            for key in result.skipped:
                print(f"  ? {key}: not in schema, skipped")
        print()

    print(f"Pin result: {result.summary()}", file=sys.stderr)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(generate_env_string(schema))
    else:
        print(generate_env_string(schema))

    return 0


def register(subparsers) -> None:
    parser = subparsers.add_parser(
        "pin",
        help="Pin live env values as defaults in a schema",
    )
    parser.add_argument("schema", help="Path to schema JSON file")
    parser.add_argument("env", help="Path to .env file to pin from")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show per-key changes")
    parser.set_defaults(func=cmd_pin)
